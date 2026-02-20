#!/usr/bin/env python3
"""
Meridian Morning Brief
Fires at 6:00 AM PT via cron → sends to @MeridianStockBot
"""
import json, requests, datetime, pytz

# --- Config ---
with open('/Users/atlasbuilds/clawd/credentials.json') as f:
    creds = json.load(f)

TG_TOKEN  = creds['telegram_meridian']['bot_token']
TG_CHAT   = creds['telegram_meridian']['chat_id']
TRADIER   = creds['tradier']['token']
OPENAI_KEY = creds['openai']['api_key']

TRADIER_BASE = "https://api.tradier.com/v1"
HEADERS = {"Authorization": f"Bearer {TRADIER}", "Accept": "application/json"}

# --- Live Data ---
def get_quotes():
    r = requests.get(f"{TRADIER_BASE}/markets/quotes",
                     params={"symbols": "QQQ,SPY,IWM,VIX"},
                     headers=HEADERS, timeout=10)
    quotes = r.json().get('quotes', {}).get('quote', [])
    if isinstance(quotes, dict):
        quotes = [quotes]
    return {q['symbol']: q for q in quotes}

def get_pm_levels():
    """Pull pre-market high/low for QQQ directly from Tradier timesales."""
    try:
        now_et = datetime.datetime.now(pytz.timezone('America/New_York'))
        today  = now_et.strftime('%Y-%m-%d')
        # Pre-market window: 4:00 AM → 9:30 AM ET
        start  = f"{today} 04:00"
        end    = f"{today} 09:29"
        r = requests.get(f"{TRADIER_BASE}/markets/timesales",
                         params={"symbol": "QQQ", "interval": "1min",
                                 "start": start, "end": end, "session_filter": "all"},
                         headers=HEADERS, timeout=10)
        data = r.json().get('series', {}).get('data', [])
        if not data:
            return None
        if isinstance(data, dict):
            data = [data]
        highs = [float(c['high']) for c in data]
        lows  = [float(c['low'])  for c in data]
        return {'pm_high': max(highs), 'pm_low': min(lows)}
    except Exception as e:
        print(f"PM levels error: {e}")
        return None

# --- Macro Events ---
def get_macro_events():
    """Pull today's high-impact USD events from ForexFactory calendar."""
    try:
        now_et = datetime.datetime.now(pytz.timezone('America/New_York'))
        today  = now_et.strftime('%m-%d-%Y')
        r = requests.get(
            "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        events = r.json()
        lines = []
        for e in events:
            # Filter: today + USD + high impact
            if e.get('country') != 'USD':
                continue
            if e.get('impact') not in ('High', 'Medium'):
                continue
            e_date = e.get('date', '')[:10]  # YYYY-MM-DD
            e_et   = datetime.datetime.fromisoformat(e['date'].replace('Z','+00:00')).astimezone(pytz.timezone('America/New_York'))
            if e_et.strftime('%m-%d-%Y') != today:
                continue
            time_str = e_et.strftime('%-I:%M %p ET')
            impact   = "⚠️" if e['impact'] == 'High' else "📅"
            title    = e.get('title', '')[:45]
            forecast = e.get('forecast', '')
            fc_str   = f" | Fcst: {forecast}" if forecast else ""
            lines.append(f"{impact} {time_str} — {title}{fc_str}")
        return '\n'.join(lines) if lines else "📅 No high-impact USD events today"
    except Exception as e:
        return f"⚠️ Calendar unavailable"

# --- GEX Clusters ---
def get_gex_clusters(current_price):
    """Pull QQQ options chain, find high-OI strike clusters above/below price."""
    try:
        # Get nearest expiration
        r = requests.get(f"{TRADIER_BASE}/markets/options/expirations",
                         params={"symbol": "QQQ", "includeAllRoots": "true"},
                         headers=HEADERS, timeout=10)
        expirations = r.json().get('expirations', {}).get('date', [])
        if not expirations:
            return None
        expiry = expirations[0] if isinstance(expirations, list) else expirations

        # Get chain
        r2 = requests.get(f"{TRADIER_BASE}/markets/options/chains",
                          params={"symbol": "QQQ", "expiration": expiry, "greeks": "false"},
                          headers=HEADERS, timeout=10)
        options = r2.json().get('options', {}).get('option', [])
        if not options:
            return None

        # Aggregate OI by strike (calls + puts)
        strike_oi = {}
        for o in options:
            strike = float(o.get('strike', 0))
            oi = int(o.get('open_interest', 0) or 0)
            strike_oi[strike] = strike_oi.get(strike, 0) + oi

        # Filter to strikes within 3% of current price
        pct = 0.03
        nearby = {s: oi for s, oi in strike_oi.items()
                  if abs(s - current_price) / current_price <= pct}

        if not nearby:
            return None

        # Sort by OI, take top 8
        top = sorted(nearby.items(), key=lambda x: x[1], reverse=True)[:8]
        top_sorted = sorted(top, key=lambda x: x[0], reverse=True)

        lines = []
        for strike, oi in top_sorted:
            if strike > current_price:
                tag = "🔴" if oi > 5000 else "🟡"
                label = "resistance" if oi > 5000 else "watch"
                lines.append(f"{tag} ${strike:.2f} ← {label} ({oi:,} OI)")
            elif abs(strike - current_price) < 0.5:
                lines.append(f"─── QQQ ${current_price:.2f} ───")
            else:
                tag = "🟢"
                label = "support"
                lines.append(f"{tag} ${strike:.2f} ← {label} ({oi:,} OI)")

        # Insert price marker if not already there
        inserted = any("QQQ" in l for l in lines)
        if not inserted:
            # Find insertion point
            final = []
            added = False
            for l in lines:
                strike_val = float(l.split('$')[1].split(' ')[0]) if '$' in l else 0
                if not added and strike_val < current_price:
                    final.append(f"─── QQQ ${current_price:.2f} ───")
                    added = True
                final.append(l)
            if not added:
                final.append(f"─── QQQ ${current_price:.2f} ───")
            lines = final

        return '\n'.join(lines)
    except Exception as e:
        return None

# --- Build Message ---
def build_brief():
    now_et = datetime.datetime.now(pytz.timezone('America/New_York'))
    date_str = now_et.strftime('%b %d').upper()

    quotes = get_quotes()

    qqq_p = quotes.get('QQQ', {}).get('last', 0)
    spy_p = quotes.get('SPY', {}).get('last', 0)
    iwm_p = quotes.get('IWM', {}).get('last', 0)
    vix_p = quotes.get('VIX', {}).get('last', 0)
    vix_c = quotes.get('VIX', {}).get('change_percentage', 0)

    vix_arrow  = "▼" if float(vix_c) < 0 else "▲"
    vix_regime = "LOW" if vix_p < 15 else "MID" if vix_p < 20 else "HIGH"

    pm = get_pm_levels()
    macro = get_macro_events()
    clusters = get_gex_clusters(qqq_p)

    if pm:
        pm_high = pm['pm_high']
        pm_low  = pm['pm_low']
        qqq_vs  = qqq_p - pm_low
        sign    = "+" if qqq_vs >= 0 else ""
        setup_block = f"""PM HIGH ${pm_high:.2f} | PM LOW ${pm_low:.2f}
QQQ now ${qqq_p:.2f} ({sign}${qqq_vs:.2f} vs PM low)

🟢 BULL → sweep ${pm_low:.2f} → reclaim → calls
🎯 ${pm_high:.2f} cluster | Stop -50%

🔴 BEAR → reject ${pm_high:.2f} → puts
🎯 ${pm_low - 2:.2f} | Stop -50%"""
    else:
        setup_block = """🟢 BULL → sweep PM low → reclaim → calls | Stop -50%

🔴 BEAR → reject PM high → puts | Stop -50%"""

    msg = f"""━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ MERIDIAN BRIEF — {date_str}
Pre-Market · 6:00 AM PT
━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MARKET
QQQ ${qqq_p:.2f} | VIX ${vix_p:.2f} {vix_arrow} ({vix_regime})
SPY ${spy_p:.2f} | IWM ${iwm_p:.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━
📍 SETUPS (QQQ)
━━━━━━━━━━━━━━━━━━━━━━━━━
{setup_block}

━━━━━━━━━━━━━━━━━━━━━━━━━
📈 GEX CLUSTERS (QQQ)
━━━━━━━━━━━━━━━━━━━━━━━━━
{clusters if clusters else "⚠️ Chain data unavailable"}

━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 MACRO & EVENTS
━━━━━━━━━━━━━━━━━━━━━━━━━
{macro}

━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 READ
━━━━━━━━━━━━━━━━━━━━━━━━━
VIX {vix_regime} regime. Wait for sweep + reclaim. No chasing opens.

━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 MERIDIAN: LIVE ✅
Scanning every 15s from 9:30 ET
━━━━━━━━━━━━━━━━━━━━━━━━━"""

    return msg.strip()

# --- Send ---
def send(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": TG_CHAT, "text": msg}, timeout=10)
    if r.status_code == 200:
        print("✅ Brief sent to @MeridianStockBot")
    else:
        print(f"❌ Failed: {r.text}")

if __name__ == "__main__":
    msg = build_brief()
    print(msg)
    print("\n--- SENDING ---")
    send(msg)
