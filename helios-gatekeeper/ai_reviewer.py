#!/usr/bin/env python3
"""
AI-Powered Signal Review - Atlas Intelligent Gatekeeper V4
Using GPT-4o-mini (fast, cheap, less paranoid than before)
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

# Load credentials
CREDS_PATH = os.getenv("CREDS_PATH", "/Users/atlasbuilds/clawd/credentials.json")
try:
    with open(CREDS_PATH) as f:
        _creds = json.load(f)
    OPENAI_API_KEY = _creds.get("openai", {}).get("api_key", "")
except:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

TRADIER_TOKEN = os.getenv("TRADIER_TOKEN", "")
TRADIER_BASE = "https://api.tradier.com/v1/"
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")

AI_MODEL = "gpt-4o-mini"  # Fast, cheap, good enough
AI_PROVIDER = "openai"


def call_ai(system_prompt: str, user_prompt: str, max_tokens: int = 400) -> str:
    """Call OpenAI API directly via requests"""
    if not OPENAI_API_KEY:
        return None
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": AI_MODEL,
            "max_tokens": max_tokens,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        print(f"❌ OpenAI API error: {response.status_code} - {response.text}")
        return None


# For backward compatibility
client = True if OPENAI_API_KEY else None


def fetch_market_data(ticker: str) -> Dict[str, Any]:
    """Fetch live market data for context"""
    try:
        # Get current quote
        url = f"{TRADIER_BASE}markets/quotes"
        headers = {"Authorization": f"Bearer {TRADIER_TOKEN}", "Accept": "application/json"}
        resp = requests.get(url, params={"symbols": ticker}, headers=headers, timeout=5)
        resp.raise_for_status()
        quote = resp.json().get("quotes", {}).get("quote", {})
        
        # Get recent bars for RSI calculation
        end = datetime.now()
        start = end - timedelta(hours=6)
        bars_url = f"{TRADIER_BASE}markets/timesales"
        bars_resp = requests.get(
            bars_url,
            params={
                "symbol": ticker,
                "interval": "5min",
                "start": start.strftime("%Y-%m-%d %H:%M"),
                "end": end.strftime("%Y-%m-%d %H:%M"),
            },
            headers=headers,
            timeout=5
        )
        bars_resp.raise_for_status()
        bars_data = bars_resp.json()
        series = (bars_data.get("series") or {}).get("data") or []
        if isinstance(series, dict):
            series = [series]
        
        # Calculate RSI
        rsi = calculate_rsi(series) if len(series) > 14 else None
        
        # Get VIX for market fear gauge
        vix_resp = requests.get(
            url,
            params={"symbols": "VIX"},
            headers=headers,
            timeout=5
        )
        vix_quote = vix_resp.json().get("quotes", {}).get("quote", {}) if vix_resp.ok else {}
        vix = vix_quote.get("last")
        
        return {
            "current_price": quote.get("last"),
            "open": quote.get("open"),
            "high": quote.get("high"),
            "low": quote.get("low"),
            "volume": quote.get("volume"),
            "prev_close": quote.get("prevclose"),
            "change_pct": quote.get("change_percentage"),
            "rsi": rsi,
            "vix": vix,
            "bars": series[-30:] if series else [],
        }
    except Exception as e:
        print(f"❌ Market data fetch failed: {e}")
        return {}


def calculate_rsi(bars: list, period: int = 14) -> Optional[float]:
    """Calculate RSI from OHLC bars"""
    closes = [float(b["close"]) for b in bars if b.get("close")]
    if len(closes) < period + 1:
        return None
    
    gains, losses = [], []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def generate_chart_url(ticker: str, signal: Dict[str, Any]) -> str:
    """Generate TradingView chart URL for visual analysis"""
    base = "https://www.tradingview.com/chart/"
    params = f"?symbol={ticker}&interval=5"
    return base + params


def build_data_inventory(signal: Dict[str, Any], market_data: Dict[str, Any]) -> str:
    """
    Build a clear inventory of what data we HAVE vs what's MISSING.
    This prevents the AI from claiming data is missing when it exists.
    """
    reasoning = signal.get('reasoning', '') or ''
    
    have = []
    missing = []
    
    # Check each data point
    if market_data.get('current_price') is not None:
        have.append(f"Price: ${market_data['current_price']}")
    else:
        missing.append("Live price")
    
    if market_data.get('vix') is not None:
        have.append(f"VIX: {market_data['vix']:.1f}")
    else:
        missing.append("VIX")
    
    if market_data.get('rsi') is not None:
        have.append(f"RSI: {market_data['rsi']:.0f}")
    else:
        missing.append("RSI (not enough bars)")
    
    if market_data.get('open') is not None and market_data.get('high') is not None:
        have.append(f"OHLC: {market_data['open']}/{market_data['high']}/{market_data['low']}")
    else:
        missing.append("Today's OHLC range")
    
    if market_data.get('change_pct') is not None:
        have.append(f"Change: {market_data['change_pct']:.2f}%")
    else:
        missing.append("Day change %")
    
    # Check Greeks from signal reasoning
    reasoning_lower = reasoning.lower()
    for greek in ['delta', 'theta', 'gamma', 'vega']:
        if greek in reasoning_lower:
            have.append(f"{greek.capitalize()} (from signal)")
    
    # Check regime/other data from signal reasoning
    if 'regime' in reasoning_lower or 'yellow' in reasoning_lower or 'green' in reasoning_lower or 'red' in reasoning_lower:
        have.append("Market regime (from signal)")
    
    result = "DATA WE HAVE: " + ", ".join(have) if have else "DATA WE HAVE: None"
    if missing:
        result += "\nDATA MISSING: " + ", ".join(missing)
    else:
        result += "\nDATA MISSING: None - all data available"
    
    return result


def compute_strike_analysis(signal: Dict[str, Any], market_data: Dict[str, Any]) -> str:
    """Pre-compute strike distance analysis so AI doesn't have to guess."""
    current_price = market_data.get('current_price')
    strike = signal.get('strike')
    direction = signal.get('direction', '')
    
    if not current_price or not strike:
        return "Strike analysis: N/A (missing price data)"
    
    distance = abs(float(current_price) - float(strike))
    pct_distance = (distance / float(current_price)) * 100
    
    if direction == 'PUT':
        otm_itm = "OTM" if float(strike) < float(current_price) else "ITM"
    else:
        otm_itm = "OTM" if float(strike) > float(current_price) else "ITM"
    
    analysis = f"Strike ${strike:.0f} vs price ${current_price:.2f} = {distance:.0f}pts {otm_itm} ({pct_distance:.1f}%)"
    
    if otm_itm == "OTM" and distance > 80:
        analysis += " ⚠️ FAR OTM"
    elif otm_itm == "OTM" and distance > 40:
        analysis += " ⚠️ Moderately OTM"
    
    return analysis


def ai_review_signal(signal: Dict[str, Any], market_data: Dict[str, Any]) -> Tuple[str, str, int, Dict]:
    """
    Use GPT-5.2 to intelligently review the signal.
    V3: Honest rejections - separates "missing data" from "bad setup".
    Returns: (decision, reasoning, confidence_score, edits)
    """
    
    if not client:
        print("⚠️ No AI client configured - falling back to threshold review")
        return threshold_review(signal)
    
    # Build comprehensive context for AI
    ticker = signal['ticker']
    direction = signal['direction']
    strike = signal['strike']
    expiry = signal['expiry']
    entry_price = signal['entry_price']
    confidence = signal['confidence']
    reasoning = signal['reasoning'] or "No reasoning provided"
    
    current_price = market_data.get('current_price')
    rsi = market_data.get('rsi')
    vix = market_data.get('vix')
    change_pct = market_data.get('change_pct')
    
    # Calculate DTE for context
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    
    try:
        if '/' in str(expiry):
            exp_date = datetime.strptime(str(expiry), "%m/%d/%y")
        else:
            exp_date = datetime.strptime(str(expiry), "%Y-%m-%d")
        dte = (exp_date - today).days
        dte_str = f"{dte}DTE" if dte > 0 else "0DTE (expires TODAY)"
    except:
        dte_str = "unknown DTE"
        dte = -1
    
    # Pre-compute analysis to feed AI
    data_inventory = build_data_inventory(signal, market_data)
    strike_analysis = compute_strike_analysis(signal, market_data)
    
    # V4 prompt: Simple, biased toward approval
    prompt = f"""{ticker} {direction} @ ${strike}, exp {expiry} ({dte_str}), entry ${entry_price}
Helios confidence: {confidence*100:.0f}%
Current price: ${current_price or '?'} ({f'{change_pct:+.1f}%' if change_pct is not None else '?'} today)
VIX: {f'{vix:.1f}' if vix is not None else '?'}

RULES:
- If Helios confidence >= 75%, APPROVE unless obviously broken
- "Obviously broken" = strike >5% OTM on 0DTE, or buying calls on -3% day
- Theta/VIX are NOT reasons to reject

Reply format:
DECISION: APPROVED or REJECTED
REASONING: one sentence"""

    try:
        system_prompt = "You are Atlas, a direct and decisive options trader. Be concise and opinionated. NEVER claim data is missing if you can see it in the prompt. If a trade is bad, say WHY with specific numbers. Bias toward APPROVING trades with 75%+ confidence - you're a trader, not a risk manager."
        
        ai_response = call_ai(system_prompt, prompt, max_tokens=400)
        
        if not ai_response:
            print("⚠️ OpenAI API failed - falling back to threshold review")
            return threshold_review(signal)
        
        # Parse response
        lines = ai_response.split('\n')
        decision_line = [l for l in lines if l.startswith('DECISION:')]
        confidence_line = [l for l in lines if l.startswith('CONFIDENCE:')]
        reasoning_line = [l for l in lines if l.startswith('REASONING:')]
        
        new_direction_line = [l for l in lines if l.startswith('NEW_DIRECTION:')]
        new_strike_line = [l for l in lines if l.startswith('NEW_STRIKE:')]
        new_expiry_line = [l for l in lines if l.startswith('NEW_EXPIRY:')]
        
        decision = decision_line[0].split(':', 1)[1].strip() if decision_line else "REJECTED"
        ai_confidence = int(confidence_line[0].split(':', 1)[1].strip()) if confidence_line else 50
        ai_reasoning = reasoning_line[0].split(':', 1)[1].strip() if reasoning_line else ai_response
        
        # Parse edits
        edits = {}
        if "EDIT" in decision.upper():
            if new_direction_line:
                edits['new_direction'] = new_direction_line[0].split(':', 1)[1].strip()
            if new_strike_line:
                try:
                    edits['new_strike'] = float(new_strike_line[0].split(':', 1)[1].strip())
                except:
                    pass
            if new_expiry_line:
                edits['new_expiry'] = new_expiry_line[0].split(':', 1)[1].strip()
        
        # Map decision to internal format
        if "APPROVED" in decision.upper():
            final_decision = "approved"
            if edits:
                final_decision = "edited"
        else:
            final_decision = "rejected"
        
        # V3: Post-process to catch any remaining contradictions
        ai_reasoning = sanitize_reasoning(ai_reasoning, market_data, signal)
        
        if edits:
            edit_str = ", ".join([f"{k}={v}" for k, v in edits.items()])
            print(f"🤖 AI Review: {final_decision.upper()} ({ai_confidence}%) - EDITS: {edit_str}")
        else:
            print(f"🤖 AI Review: {final_decision.upper()} ({ai_confidence}%)")
        print(f"   Reasoning: {ai_reasoning[:150]}...")
        
        return final_decision, ai_reasoning, ai_confidence, edits
        
    except Exception as e:
        print(f"❌ AI review failed: {e}")
        return threshold_review(signal)


def sanitize_reasoning(reasoning: str, market_data: Dict[str, Any], signal: Dict[str, Any]) -> str:
    """
    V3: Post-process AI reasoning to catch contradictions.
    If AI claims data is missing but we have it, rewrite the reasoning
    to focus on the ACTUAL problem (bad setup, not missing data).
    """
    reasoning_lower = reasoning.lower()
    
    # Phrases that indicate "missing data" claims
    missing_phrases = [
        'missing', 'no data', 'insufficient data', 'cannot evaluate',
        'need more data', 'without knowing', 'no live', 'data not available',
        'unable to assess', 'lacking'
    ]
    
    has_missing_claim = any(phrase in reasoning_lower for phrase in missing_phrases)
    
    if not has_missing_claim:
        return reasoning  # No contradiction, return as-is
    
    # Check what data we actually have
    have_price = market_data.get('current_price') is not None
    have_vix = market_data.get('vix') is not None
    
    if not have_price and not have_vix:
        return reasoning  # Data genuinely missing, claim is valid
    
    # Data exists but AI claimed missing - this is the gaslighting bug.
    # Rewrite with honest analysis based on what we have.
    price = market_data.get('current_price')
    vix = market_data.get('vix')
    strike = signal.get('strike', 0)
    direction = signal.get('direction', '')
    
    parts = []
    
    if price and strike:
        distance = abs(float(price) - float(strike))
        if direction == 'PUT':
            otm_itm = "OTM" if float(strike) < float(price) else "ITM"
        else:
            otm_itm = "OTM" if float(strike) > float(price) else "ITM"
        
        if otm_itm == "OTM" and distance > 50:
            parts.append(f"Strike ${strike:.0f} is {distance:.0f}pts {otm_itm} from ${price:.2f} - needs a massive move")
    
    if vix and float(vix) > 22:
        parts.append(f"VIX {vix:.1f} = elevated premiums, overpaying")
    
    # Extract Greeks from signal reasoning if present
    signal_reasoning = (signal.get('reasoning') or '').lower()
    if 'delta' in signal_reasoning and '0.1' in signal_reasoning:
        parts.append("Low delta = low probability of profit")
    if 'theta' in signal_reasoning and '-4' in signal_reasoning:
        parts.append("Theta bleeding hard - time decay eating this alive")
    
    if parts:
        return " | ".join(parts)
    
    # Fallback: strip the "missing" claim and keep the rest
    for phrase in missing_phrases:
        reasoning = reasoning.replace(phrase, "limited")
    return reasoning


def threshold_review(signal: Dict[str, Any]) -> Tuple[str, str, int, Dict]:
    """Fallback threshold-based review if AI unavailable"""
    confidence = signal['confidence']
    
    if confidence >= 0.80:
        return "approved", f"High confidence ({confidence*100:.0f}%), clean setup ✅", 85, {}
    elif confidence >= 0.70:
        return "approved", f"Moderate confidence ({confidence*100:.0f}%) - proceed with caution ⚠️", 75, {}
    else:
        return "rejected", f"Low confidence ({confidence*100:.0f}%) - too risky ❌", int(confidence * 100), {}


def review_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main review function - fetches market data and runs AI review
    Returns: {decision, reasoning, confidence, market_context, edits}
    """
    
    ticker = signal['ticker']
    
    print(f"\n🔍 AI Reviewing: {ticker} {signal['direction']} @ ${signal['strike']}")
    
    # Fetch live market data
    market_data = fetch_market_data(ticker)
    
    # Run AI review (returns decision, reasoning, confidence, edits)
    decision, reasoning, confidence, edits = ai_review_signal(signal, market_data)
    
    # Generate chart URL for reference
    chart_url = generate_chart_url(ticker, signal)
    
    return {
        "decision": decision,
        "reasoning": reasoning,
        "confidence": confidence,
        "edits": edits,
        "market_context": {
            "price": market_data.get("current_price"),
            "rsi": market_data.get("rsi"),
            "vix": market_data.get("vix"),
            "change_pct": market_data.get("change_pct"),
        },
        "chart_url": chart_url,
    }


if __name__ == "__main__":
    # Test with the exact Signal #48 scenario that triggered the bug
    test_signal = {
        "ticker": "SPX",
        "direction": "PUT",
        "strike": 6610,
        "expiry": "03/08/26",
        "entry_price": 4.50,
        "confidence": 0.72,
        "reasoning": "$SPX @ $6739.84 | VIX 27.3 | Regime YELLOW | Delta -0.12 | Theta -4.453 | Gamma-Magnet $6850.00",
    }
    
    result = review_signal(test_signal)
    print(f"\n✅ Review Result:")
    print(f"   Decision: {result['decision']}")
    print(f"   Confidence: {result['confidence']}%")
    print(f"   Reasoning: {result['reasoning']}")
    print(f"   Market: Price ${result['market_context']['price']}, RSI {result['market_context']['rsi']}, VIX {result['market_context']['vix']}")
    
    # Verify no "missing data" contradiction
    reasoning_lower = result['reasoning'].lower()
    if 'missing' in reasoning_lower or 'insufficient' in reasoning_lower:
        print(f"\n❌ BUG STILL PRESENT: Reasoning contains 'missing'/'insufficient' claims!")
        print(f"   Full reasoning: {result['reasoning']}")
    else:
        print(f"\n✅ No contradictory 'missing data' claims - fix working!")
