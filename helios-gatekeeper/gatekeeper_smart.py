#!/usr/bin/env python3
"""
Smart Gatekeeper - Pulls market data and makes informed decisions
"""

import psycopg2
import os
import requests
from datetime import datetime
import json

DATABASE_URL = os.getenv("DATABASE_URL")
HELIOS_EXECUTE_URL = os.getenv("HELIOS_EXECUTE_URL", "https://helios-px7f.onrender.com/execute")
WEBHOOK_KEY = os.getenv("WEBHOOK_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_HELIOS_WEBHOOK")

# Load credentials
CREDS_PATH = "/Users/atlasbuilds/clawd/credentials.json"
with open(CREDS_PATH) as f:
    creds = json.load(f)
    TRADIER_TOKEN = creds['tradier']['token']

def get_market_data(ticker: str) -> dict:
    """Fetch live market data for ticker"""
    headers = {
        'Authorization': f'Bearer {TRADIER_TOKEN}',
        'Accept': 'application/json'
    }
    
    # Get quote
    quote_resp = requests.get(
        'https://api.tradier.com/v1/markets/quotes',
        params={'symbols': ticker},
        headers=headers,
        timeout=10
    )
    
    if quote_resp.status_code != 200:
        return {'error': 'Failed to fetch quote'}
    
    quote_data = quote_resp.json()
    quote = quote_data['quotes']['quote']
    
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
        vix = vix_data['quotes']['quote']['last']
    
    return {
        'price': quote['last'],
        'change': quote['change'],
        'change_pct': quote['change_percentage'],
        'high': quote['high'],
        'low': quote['low'],
        'volume': quote.get('volume', 0),
        'vix': vix
    }

def analyze_setup(signal: dict, market_data: dict) -> tuple[str, str, str]:
    """
    Analyze if setup is good
    Returns: (decision, direction, reasoning)
    decision: 'approved' | 'rejected'
    direction: 'CALL' | 'PUT' (original or flipped)
    """
    
    ticker = signal['ticker']
    original_direction = signal['direction']
    confidence = signal['confidence']
    strike = signal['strike']
    premium = signal['entry_price']
    
    price = market_data.get('price')
    change_pct = market_data.get('change_pct', 0)
    vix = market_data.get('vix')
    
    if not price:
        return 'rejected', original_direction, "No market data available"
    
    reasons = []
    
    # Check confidence first
    if confidence < 0.60:
        return 'rejected', original_direction, f"Low confidence ({confidence*100:.1f}%)"
    
    # Check premium quality
    if premium < 1.0:
        reasons.append(f"Premium too low (${premium:.2f})")
    elif premium > 100.0:
        reasons.append(f"Premium too high (${premium:.2f})")
    
    # Check if buying strength or weakness
    is_call = original_direction == 'CALL'
    is_bullish_move = change_pct > 0.5
    is_bearish_move = change_pct < -0.5
    
    # Direction analysis
    if is_call and is_bearish_move:
        # Trying to buy calls on red day
        reasons.append(f"Buying calls on -{abs(change_pct):.1f}% day - risky")
        # Consider flipping to PUT
        if change_pct < -1.5:
            return 'approved', 'PUT', f"FLIPPED to PUT: Strong selloff ({change_pct:.1f}%)"
    
    elif not is_call and is_bullish_move:
        # Trying to buy puts on green day
        reasons.append(f"Buying puts on +{change_pct:.1f}% day - risky")
        # Consider flipping to CALL
        if change_pct > 1.5:
            return 'approved', 'CALL', f"FLIPPED to CALL: Strong rally (+{change_pct:.1f}%)"
    
    # VIX check
    if vix and vix > 25:
        reasons.append(f"High VIX ({vix:.1f}) - elevated risk")
    
    # Strike sanity check
    if is_call:
        otm_pct = ((strike - price) / price) * 100
        if otm_pct > 5:
            reasons.append(f"Strike {otm_pct:.1f}% OTM - far out")
        elif otm_pct < -5:
            reasons.append(f"Strike {abs(otm_pct):.1f}% ITM")
    
    # Final decision
    if len(reasons) > 2:
        return 'rejected', original_direction, " | ".join(reasons)
    
    # Approve
    approval_text = f"Confidence {confidence*100:.1f}% | ${ticker} @ ${price:.2f} ({change_pct:+.1f}%)"
    if vix:
        approval_text += f" | VIX {vix:.1f}"
    
    return 'approved', original_direction, approval_text

def get_pending_signals():
    """Fetch pending signals"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, created_at, ticker, direction, strike, expiry, 
               entry_price, confidence, reasoning, chart_url
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

def post_to_discord(signal: dict, decision: str, review: str, final_direction: str):
    """Post to Discord"""
    if not DISCORD_WEBHOOK:
        return
    
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
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]}, timeout=10)
        print(f"✅ Posted to Discord")
    except Exception as e:
        print(f"❌ Discord failed: {e}")

def process_signal(signal: dict):
    """Process one signal"""
    print(f"\n🔍 Signal {signal['id']}: {signal['ticker']} {signal['direction']}")
    
    # Get market data
    market_data = get_market_data(signal['ticker'])
    
    if 'error' in market_data:
        decision = 'rejected'
        review = market_data['error']
        final_direction = signal['direction']
    else:
        # Analyze
        decision, final_direction, review = analyze_setup(signal, market_data)
    
    print(f"Decision: {decision} | Direction: {final_direction}")
    print(f"Review: {review}")
    
    # Update DB
    update_signal(signal['id'], decision, review, final_direction)
    
    # Post to Discord
    post_to_discord(signal, decision, review, final_direction)
    
    print(f"✅ Processed signal {signal['id']}")

def main():
    """Main entry"""
    print(f"🚀 Smart Gatekeeper started at {datetime.now()}")
    
    signals = get_pending_signals()
    
    if signals:
        print(f"⚡ Found {len(signals)} pending signal(s)")
        for signal in signals:
            process_signal(signal)
    else:
        print("✅ No pending signals")
    
    print(f"🏁 Completed at {datetime.now()}")

if __name__ == "__main__":
    main()
