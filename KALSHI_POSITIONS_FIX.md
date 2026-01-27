# Kalshi API get_positions() Fix

## Problem
The `get_positions()` method from the kalshi-python library returns `positions=None cursor=''` even when the user has active positions visible in the Kalshi app.

## Root Cause
The kalshi-python library (version 2.1.4) uses deprecated parameter names:
- Library uses: `count_down` and `count_up`
- API expects: `count_filter`

According to the Kalshi OpenAPI documentation, the `count_filter` parameter:
> "Restricts the positions to those with any of following fields with non-zero values, as a comma separated list. The following values are accepted: position, total_traded"

When the library sends unrecognized parameters (`count_down`, `count_up`), the API likely:
1. Ignores the unrecognized parameters
2. Applies default filtering (positions with zero `position` and `total_traded` are excluded)
3. Returns empty result if all positions have zero values

## Why get_fills() Works
`get_fills()` returns trade history regardless of current position values, so it correctly shows the user's trades.

## The Fix

### Option 1: Direct API Calls (Recommended)
Bypass the kalshi-python library and make direct HTTP requests with the correct `count_filter` parameter:

```python
def get_positions_direct():
    params = {'count_filter': 'position,total_traded'}
    response = make_kalshi_request("GET", "/portfolio/positions", params)
    # ... process response
```

### Option 2: Updated kalshi-trader.py
I've created `kalshi-trader-fixed.py` that:
- Uses direct API calls instead of the kalshi-python library
- Includes the `count_filter='position,total_traded'` parameter
- Properly handles authentication and signing

### Option 3: Monkey-patch the Library
If you must use the kalshi-python library, you can monkey-patch it:

```python
# Monkey-patch to use correct parameters
original_get_positions = PortfolioApi.get_positions

def patched_get_positions(self, **kwargs):
    # Remove deprecated params, add count_filter
    kwargs.pop('count_down', None)
    kwargs.pop('count_up', None)
    kwargs['count_filter'] = 'position,total_traded'
    return original_get_positions(self, **kwargs)

PortfolioApi.get_positions = patched_get_positions
```

## How to Use the Fix

1. **Replace the existing tool**:
   ```bash
   cp kalshi-trader-fixed.py tools/kalshi-trader.py
   ```

2. **Or use the fixed version directly**:
   ```bash
   python kalshi-trader-fixed.py positions
   ```

3. **Ensure environment variables are set**:
   ```bash
   export KALSHI_API_KEY_ID="your-key-id"
   export KALSHI_PRIVATE_KEY_PATH="$HOME/.kalshi/private_key.pem"
   ```

## Testing the Fix
The fix includes the `count_filter='position,total_traded'` parameter which tells the API to return all positions, including those with zero values in the `position` and `total_traded` fields.

## Additional Notes
- The user's Super Bowl bets (Denver, LA Rams, New England) might have special settlement status
- Position values might be 0 if markets have settled
- The `position` field represents current contract holdings
- The `total_traded` field represents total contracts traded (buys + sells)

## Files Created
1. `analyze_issue.md` - Detailed analysis of the problem
2. `fix_kalshi_positions.py` - Demonstration of the fix with multiple approaches
3. `kalshi-trader-fixed.py` - Complete replacement for the original tool
4. `KALSHI_POSITIONS_FIX.md` - This summary document