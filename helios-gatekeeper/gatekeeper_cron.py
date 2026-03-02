#!/usr/bin/env python3
"""
Smart Gatekeeper V2 - Fixed duplicate posting issue
Uses GPT-4o for intelligent signal analysis
"""

import psycopg2
import os
import requests
from datetime import datetime
import json
import sys

DATABASE_URL = os.getenv("DATABASE_URL")
HELIOS_EXECUTE_URL = os.getenv("HELIOS_EXECUTE_URL", "https://helios-px7f.onrender.com/execute")
WEBHOOK_KEY = os.getenv("WEBHOOK_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_HELIOS_WEBHOOK")

# Load tokens from env (Render) or credentials file (local)
TRADIER_TOKEN = os.getenv("TRADIER_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TRADIER_TOKEN or not OPENAI_API_KEY:
    # Fallback to local credentials file
    CREDS_PATH = "/Users/atlasbuilds/clawd/credentials.json"
    try:
        with open(CREDS_PATH) as f:
            creds = json.load(f)
            TRADIER_TOKEN = TRADIER_TOKEN or creds.get('tradier', {}).get('token')
            OPENAI_API_KEY = OPENAI_API_KEY or creds.get('openai', {}).get('api_key')
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        sys.exit(1)

if not TRADIER_TOKEN:
    raise ValueError("TRADIER_TOKEN not found in env or credentials.json")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in env or credentials.json")

# Role ID to tag in Discord
HELIOS_ROLE_ID = "1440026585053794465"


def get_market_data(ticker: str) -> dict:
    """Fetch live market data for ticker"""
    headers = {
        'Authorization': f'Bearer {TRADIER_TOKEN}',
        'Accept': 'application/json'
    }
    
    try:
        # Get quote
        quote_resp = requests.get(
            'https://api.tradier.com/v1/markets/quotes',
            params={'symbols': ticker},
            headers=headers,
            timeout=10
        )
        
        if quote_resp.status_code != 200:
            return {'error': f'Failed to fetch quote: {quote_resp.status_code}'}
        
        quote_data = quote_resp.json()
        quote = quote_data.get('quotes', {}).get('quote', {})
        
        if not quote:
            return {'error': 'No quote data returned'}
        
        # Get VIX
        vix_resp = requests.get(
            'https://api.tradier.com/v1/markets/quotes',
            params={'symbols': 'VIX'},
            headers=headers,
            timeout=10
        )
        
        vix = None
        if vix_resp.status_code == 200:
            vix_data = vix_resp.json()
            vix_quote = vix_data.get('quotes', {}).get('quote', {})
            vix = vix_quote.get('last')
        
        return {
            'price': quote.get('last'),
            'change': quote.get('change'),
            'change_pct': quote.get('change_percentage'),
            'high': quote.get('high'),
            'low': quote.get('low'),
            'volume': quote.get('volume', 0),
            'vix': vix
        }
    except Exception as e:
        return {'error': f'Exception fetching market data: {str(e)}'}


def analyze_with_ai(signal: dict, market_data: dict) -> tuple[str, str, str]:
    """
    Use GPT-4o to analyze the signal
    Returns: (decision, final_direction, reasoning)
    """
    
    # Build analysis prompt
    prompt = f"""You are a professional options trader analyzing a trade setup. Provide a clear decision.

SIGNAL:
- Ticker: {signal['ticker']}
- Direction: {signal['direction']} (CALL or PUT)
- Strike: ${signal['strike']:.2f}
- Expiry: {signal['expiry']}
- Entry Price: ${signal['entry_price']:.2f}
- Confidence: {signal['confidence']*100:.1f}%
- Reasoning: {signal['reasoning']}

CURRENT MARKET DATA:
- Current Price: ${market_data.get('price', 'N/A')}
- Change: {market_data.get('change_pct', 'N/A')}%
- High: ${market_data.get('high', 'N/A')}
- Low: ${market_data.get('low', 'N/A')}
- Volume: {market_data.get('volume', 'N/A'):,}
- VIX: {market_data.get('vix', 'N/A')}

TASK:
1. Analyze if this is a good setup based on:
   - Confidence level (>60% preferred)
   - Premium value (avoid < $1 or > $100)
   - Market conditions (price action, VIX)
   - Strike selection (not too far OTM)
   - Entry timing (buying calls on red day? puts on green day?)

2. If the original direction seems wrong given market conditions, you may FLIP it:
   - Example: Strong selloff (-2%+) → flip CALL to PUT
   - Example: Strong rally (+2%+) → flip PUT to CALL

3. Provide:
   - DECISION: "APPROVED" or "REJECTED"
   - FINAL_DIRECTION: "CALL" or "PUT" (keep or flip)
   - REASONING: 1-2 sentence explanation

Format response EXACTLY as:
DECISION: [APPROVED/REJECTED]
DIRECTION: [CALL/PUT]
REASONING: [Your explanation]"""

    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o',  # Use GPT-4o (latest stable model)
                'messages': [
                    {'role': 'system', 'content': 'You are a professional options trader.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 300
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ OpenAI API error: {response.status_code}")
            print(response.text)
            # Fallback to basic analysis
            return basic_analysis(signal, market_data)
        
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        
        # Parse response
        lines = content.split('\n')
        decision = None
        direction = signal['direction']
        reasoning = ""
        
        for line in lines:
            if line.startswith('DECISION:'):
                decision = 'approved' if 'APPROVED' in line.upper() else 'rejected'
            elif line.startswith('DIRECTION:'):
                if 'CALL' in line.upper():
                    direction = 'CALL'
                elif 'PUT' in line.upper():
                    direction = 'PUT'
            elif line.startswith('REASONING:'):
                reasoning = line.replace('REASONING:', '').strip()
        
        if not decision:
            print(f"⚠️ Could not parse AI response, using fallback")
            return basic_analysis(signal, market_data)
        
        return decision, direction, reasoning
        
    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        return basic_analysis(signal, market_data)


def basic_analysis(signal: dict, market_data: dict) -> tuple[str, str, str]:
    """
    Fallback basic analysis if AI fails
    """
    confidence = signal['confidence']
    premium = signal['entry_price']
    direction = signal['direction']
    
    # Confidence check
    if confidence < 0.60:
        return 'rejected', direction, f"Low confidence ({confidence*100:.1f}%)"
    
    # Premium check
    if premium < 1.0:
        return 'rejected', direction, f"Premium too low (${premium:.2f})"
    elif premium > 100.0:
        return 'rejected', direction, f"Premium too high (${premium:.2f})"
    
    # Simple approval
    return 'approved', direction, f"Basic approval: {confidence*100:.1f}% confidence"


def get_pending_signals():
    """Fetch pending signals that haven't been reviewed"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, created_at, ticker, direction, strike, expiry, 
               entry_price, confidence, reasoning, chart_url, discord_message_id
        FROM pending_signals
        WHERE status = 'pending'
        ORDER BY created_at ASC;
    """)
    
    columns = [desc[0] for desc in cursor.description]
    signals = []
    for row in cursor.fetchall():
        signals.append(dict(zip(columns, row)))
    
    cursor.close()
    conn.close()
    
    return signals


def update_signal(signal_id: int, decision: str, review: str, final_direction: str = None):
    """Update signal in database"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    if final_direction and final_direction != '':
        cursor.execute("""
            UPDATE pending_signals
            SET status = %s,
                atlas_review = %s,
                atlas_decision = %s,
                edited_direction = %s,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (decision, review, decision, final_direction, signal_id))
    else:
        cursor.execute("""
            UPDATE pending_signals
            SET status = %s,
                atlas_review = %s,
                atlas_decision = %s,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (decision, review, decision, signal_id))
    
    conn.commit()
    cursor.close()
    conn.close()


def post_to_discord(signal: dict, decision: str, review: str, final_direction: str) -> str:
    """
    Post to Discord and return message ID
    
    CRITICAL: This prevents duplicate posts by returning the Discord message ID
    which gets stored in pending_signals.discord_message_id
    """
    if not DISCORD_WEBHOOK:
        print("⚠️ No Discord webhook configured")
        return None
    
    # Check if already posted
    if signal.get('discord_message_id'):
        print(f"⚠️ Signal {signal['id']} already posted to Discord (message {signal['discord_message_id']})")
        return signal['discord_message_id']
    
    color = 0x00FF00 if decision == "approved" else 0xFF0000
    
    direction_display = final_direction if final_direction != signal['direction'] else signal['direction']
    if final_direction != signal['direction']:
        direction_display = f"~~{signal['direction']}~~ → **{final_direction}**"
    
    embed = {
        "title": f"🎯 Gatekeeper: {decision.upper()}",
        "description": f"**{signal['ticker']} {direction_display}**",
        "color": color,
        "fields": [
            {"name": "Strike", "value": f"${signal['strike']:.2f}", "inline": True},
            {"name": "Expiry", "value": signal['expiry'], "inline": True},
            {"name": "Premium", "value": f"${signal['entry_price']:.2f}", "inline": True},
            {"name": "Confidence", "value": f"{signal['confidence']*100:.0f}%", "inline": True},
            {"name": "Analysis", "value": review, "inline": False}
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": f"Signal ID: {signal['id']}"}
    }
    
    # Add role mention for approved signals
    content = None
    if decision == "approved":
        content = f"<@&{HELIOS_ROLE_ID}>"
    
    payload = {
        "embeds": [embed]
    }
    if content:
        payload["content"] = content
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        
        if response.status_code in [200, 204]:
            # Discord returns the message object on success (200) or empty (204)
            message_id = None
            if response.status_code == 200 and response.text:
                response_data = response.json()
                message_id = response_data.get('id')
            elif response.status_code == 204:
                # Discord returned 204 No Content - success but no message ID
                # Generate a synthetic ID to prevent duplicates
                message_id = f"synthetic_{signal['id']}_{int(datetime.now().timestamp())}"
            
            print(f"✅ Posted to Discord (message ID: {message_id})")
            
            # Store message ID in database to prevent duplicates
            if message_id:
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE pending_signals 
                    SET discord_message_id = %s, posted_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                """, (message_id, signal['id']))
                conn.commit()
                cursor.close()
                conn.close()
            
            return message_id
        else:
            print(f"❌ Discord error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Discord post failed: {e}")
        return None


def process_signal(signal: dict):
    """Process one signal"""
    print(f"\n🔍 Signal {signal['id']}: {signal['ticker']} {signal['direction']}")
    print(f"   Created: {signal['created_at']}")
    print(f"   Confidence: {signal['confidence']*100:.1f}%")
    
    # Get market data
    print(f"   Fetching market data for {signal['ticker']}...")
    market_data = get_market_data(signal['ticker'])
    
    if 'error' in market_data:
        decision = 'rejected'
        review = market_data['error']
        final_direction = signal['direction']
        print(f"   ❌ Market data error: {review}")
    else:
        # Analyze with AI
        print(f"   Analyzing with AI...")
        decision, final_direction, review = analyze_with_ai(signal, market_data)
        print(f"   Decision: {decision.upper()}")
        print(f"   Direction: {final_direction}")
        print(f"   Reasoning: {review}")
    
    # Update DB
    update_signal(signal['id'], decision, review, final_direction)
    
    # Post to Discord (this now prevents duplicates)
    message_id = post_to_discord(signal, decision, review, final_direction)
    
    print(f"✅ Processed signal {signal['id']}")


def main():
    """Main entry"""
    print(f"\n{'='*60}")
    print(f"🚀 Smart Gatekeeper V2 started")
    print(f"   Time: {datetime.now()}")
    print(f"{'='*60}\n")
    
    # Verify database connection
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        print("✅ Database connection verified")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Get pending signals
    signals = get_pending_signals()
    
    if signals:
        print(f"⚡ Found {len(signals)} pending signal(s)\n")
        for signal in signals:
            try:
                process_signal(signal)
            except Exception as e:
                print(f"❌ Error processing signal {signal['id']}: {e}")
                import traceback
                traceback.print_exc()
    else:
        print("✅ No pending signals")
    
    print(f"\n{'='*60}")
    print(f"🏁 Completed at {datetime.now()}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
