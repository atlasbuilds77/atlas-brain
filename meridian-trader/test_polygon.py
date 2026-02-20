import requests
import json

POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"

# Test 1: Get 1-min bars for QQQ on a specific date
def test_minute_bars():
    date = "2025-11-14"  # Old date to test history depth
    url = f"https://api.polygon.io/v2/aggs/ticker/QQQ/range/1/minute/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000}
    r = requests.get(url, params=params)
    data = r.json()
    print(f"1-min bars for {date}:")
    print(f"  Status: {data.get('status')}")
    print(f"  Results: {data.get('resultsCount', 0)} bars")
    if data.get('results'):
        print(f"  First bar: {data['results'][0]}")
    return data

# Test 2: Get options contracts
def test_options():
    url = "https://api.polygon.io/v3/reference/options/contracts"
    params = {
        "underlying_ticker": "QQQ",
        "expiration_date": "2025-11-14",
        "limit": 10,
        "apiKey": POLYGON_API_KEY
    }
    r = requests.get(url, params=params)
    data = r.json()
    print(f"\nOptions contracts:")
    print(f"  Status: {data.get('status')}")
    print(f"  Count: {len(data.get('results', []))}")
    if data.get('results'):
        print(f"  Sample: {data['results'][0]['ticker']}")
    return data

# Test 3: Get option OHLC
def test_option_bars():
    # Format: O:QQQ251114C00500000 (QQQ Nov 14 2025 $500 Call)
    option_ticker = "O:QQQ251114P00600000"  # $600 put
    date = "2025-11-14"
    url = f"https://api.polygon.io/v2/aggs/ticker/{option_ticker}/range/1/day/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY}
    r = requests.get(url, params=params)
    data = r.json()
    print(f"\nOption bars for {option_ticker}:")
    print(f"  Status: {data.get('status')}")
    if data.get('results'):
        print(f"  OHLC: {data['results'][0]}")
    else:
        print(f"  No data or error: {data}")
    return data

if __name__ == "__main__":
    test_minute_bars()
    test_options()
    test_option_bars()
