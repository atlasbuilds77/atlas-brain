#!/usr/bin/env python3
"""
TITAN Morning Scanner - Pre-market level detection for SPY/QQQ

Built during autonomous exploration session 2026-02-14 03:40 PST
This runs before market open to identify:
1. Swing highs/lows from last 10 days
2. Cluster zones (multiple touches within 0.5%)
3. Premarket high/low
4. Significance ranking (5x > 4x > 3x)

Usage: python3 titan_morning_scanner.py
       python3 titan_morning_scanner.py --symbol QQQ
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import argparse

# API Keys
TRADIER_TOKEN = 'jj8L3RuSVG5MUwUpz2XHrjXjAFrq'
POLYGON_KEY = 'h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv'

def get_daily_data(symbol: str, days: int = 15) -> list:
    """Fetch daily OHLC data from Tradier"""
    end = datetime.now()
    start = end - timedelta(days=days)
    
    url = 'https://api.tradier.com/v1/markets/history'
    headers = {'Authorization': f'Bearer {TRADIER_TOKEN}', 'Accept': 'application/json'}
    params = {
        'symbol': symbol,
        'interval': 'daily',
        'start': start.strftime('%Y-%m-%d'),
        'end': end.strftime('%Y-%m-%d')
    }
    
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    
    if 'history' in data and data['history'] and 'day' in data['history']:
        return data['history']['day']
    return []

def get_premarket_data(symbol: str, date: str = None) -> dict:
    """Fetch premarket high/low from Polygon"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}'
    params = {'apiKey': POLYGON_KEY, 'limit': 50000}
    
    r = requests.get(url, params=params)
    data = r.json()
    
    if 'results' not in data or not data['results']:
        return {'high': None, 'low': None, 'available': False}
    
    bars = []
    for m in data['results']:
        ts = datetime.fromtimestamp(m['t'] / 1000)
        # Premarket = before 9:30 ET (6:30 PST)
        if ts.hour < 9 or (ts.hour == 9 and ts.minute < 30):
            bars.append(m)
    
    if not bars:
        return {'high': None, 'low': None, 'available': False}
    
    return {
        'high': max(b['h'] for b in bars),
        'low': min(b['l'] for b in bars),
        'available': True
    }

def detect_swings(daily_data: list) -> dict:
    """Detect swing highs and lows (2-day confirmation)"""
    swings = {'highs': [], 'lows': []}
    
    for i in range(2, len(daily_data) - 2):
        curr = daily_data[i]
        h, l = curr['high'], curr['low']
        
        # Swing high: higher than 2 bars before AND after
        if (h > daily_data[i-1]['high'] and h > daily_data[i-2]['high'] and
            h > daily_data[i+1]['high'] and h > daily_data[i+2]['high']):
            swings['highs'].append({
                'date': curr['date'],
                'price': h,
                'type': 'swing_high'
            })
        
        # Swing low: lower than 2 bars before AND after
        if (l < daily_data[i-1]['low'] and l < daily_data[i-2]['low'] and
            l < daily_data[i+1]['low'] and l < daily_data[i+2]['low']):
            swings['lows'].append({
                'date': curr['date'],
                'price': l,
                'type': 'swing_low'
            })
    
    return swings

def detect_clusters(levels: list, threshold: float = 0.005) -> list:
    """Group levels within threshold (0.5% default) into clusters"""
    if not levels:
        return []
    
    # Sort by price
    sorted_levels = sorted(levels, key=lambda x: x['price'])
    
    clusters = []
    used = set()
    
    for i, level in enumerate(sorted_levels):
        if i in used:
            continue
        
        cluster = [level]
        used.add(i)
        
        for j, other in enumerate(sorted_levels):
            if j in used:
                continue
            
            # Check if within threshold of cluster average
            avg_price = sum(l['price'] for l in cluster) / len(cluster)
            if abs(other['price'] - avg_price) / avg_price < threshold:
                cluster.append(other)
                used.add(j)
        
        if len(cluster) >= 2:
            avg_price = sum(l['price'] for l in cluster) / len(cluster)
            clusters.append({
                'count': len(cluster),
                'avg_price': round(avg_price, 2),
                'levels': cluster,
                'significance': len(cluster)  # Higher = more significant
            })
    
    # Sort by significance (count) descending
    clusters.sort(key=lambda x: x['count'], reverse=True)
    return clusters

def generate_titan_levels(symbol: str = 'SPY') -> dict:
    """Generate complete TITAN level analysis"""
    print(f"\n🎯 TITAN MORNING SCANNER - {symbol}")
    print("=" * 50)
    
    # Get daily data
    daily = get_daily_data(symbol, days=15)
    if not daily:
        return {'error': 'No daily data available'}
    
    print(f"📊 Loaded {len(daily)} days of data")
    print(f"   Range: {daily[0]['date']} to {daily[-1]['date']}")
    
    # Detect swings
    swings = detect_swings(daily)
    print(f"\n📈 Swing Detection:")
    print(f"   Swing Highs: {len(swings['highs'])}")
    for s in swings['highs']:
        print(f"      {s['date']}: ${s['price']:.2f}")
    print(f"   Swing Lows: {len(swings['lows'])}")
    for s in swings['lows']:
        print(f"      {s['date']}: ${s['price']:.2f}")
    
    # Collect all levels (swings + recent daily H/L)
    all_levels = []
    
    for s in swings['highs']:
        all_levels.append({'price': s['price'], 'date': s['date'], 'type': 'swing_high'})
    for s in swings['lows']:
        all_levels.append({'price': s['price'], 'date': s['date'], 'type': 'swing_low'})
    
    # Add last 5 days high/low
    for d in daily[-5:]:
        all_levels.append({'price': d['high'], 'date': d['date'], 'type': 'daily_high'})
        all_levels.append({'price': d['low'], 'date': d['date'], 'type': 'daily_low'})
    
    # Detect clusters
    clusters = detect_clusters(all_levels)
    print(f"\n🔥 Cluster Zones (significance):")
    for c in clusters[:6]:
        types = [l['type'] for l in c['levels']]
        print(f"   {c['count']}x @ ${c['avg_price']:.2f} ({', '.join(set(types))})")
    
    # Get premarket data
    pm = get_premarket_data(symbol)
    print(f"\n🌅 Premarket Levels:")
    if pm['available']:
        print(f"   PM High: ${pm['high']:.2f}")
        print(f"   PM Low: ${pm['low']:.2f}")
        print(f"   PM Range: ${pm['high'] - pm['low']:.2f} ({(pm['high'] - pm['low']) / pm['low'] * 100:.2f}%)")
    else:
        print(f"   ⚠️ Premarket data not yet available (run after 4am ET)")
    
    # Generate trade setup
    print(f"\n💡 TITAN V3 SETUP:")
    
    if clusters:
        top_resistance = None
        top_support = None
        
        # Find highest significance resistance above current price
        # Find highest significance support below current price
        last_close = daily[-1]['close']
        
        for c in clusters:
            if c['avg_price'] > last_close and top_resistance is None:
                top_resistance = c
            elif c['avg_price'] < last_close and top_support is None:
                top_support = c
        
        if top_resistance:
            print(f"   🔺 Key Resistance: ${top_resistance['avg_price']:.2f} ({top_resistance['count']}x cluster)")
        if top_support:
            print(f"   🔻 Key Support: ${top_support['avg_price']:.2f} ({top_support['count']}x cluster)")
        
        print(f"\n   📋 TRADE LOGIC:")
        print(f"   • If PM LOW swept + reclaimed → LONG to resistance ${top_resistance['avg_price'] if top_resistance else 'N/A'}")
        print(f"   • If PM HIGH swept + rejected → SHORT to support ${top_support['avg_price'] if top_support else 'N/A'}")
        print(f"   • Multiple sweeps in 15min = SKIP (absorption, not rejection)")
    
    return {
        'symbol': symbol,
        'daily_data': daily,
        'swings': swings,
        'clusters': clusters,
        'premarket': pm,
        'last_close': daily[-1]['close']
    }

def main():
    parser = argparse.ArgumentParser(description='TITAN Morning Scanner')
    parser.add_argument('--symbol', default='SPY', help='Symbol to scan (default: SPY)')
    parser.add_argument('--both', action='store_true', help='Scan both SPY and QQQ')
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🌅 TITAN V3 MORNING SCANNER")
    print(f"   Built: 2026-02-14 | Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if args.both:
        generate_titan_levels('SPY')
        print("\n" + "-" * 60)
        generate_titan_levels('QQQ')
    else:
        generate_titan_levels(args.symbol)
    
    print("\n" + "=" * 60)
    print("✅ Scan complete. Ready for market open.")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    main()
