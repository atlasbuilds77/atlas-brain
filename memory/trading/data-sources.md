# Trading Data Sources - CONFIRMED 2026-02-03

## Tradier API
- USE FOR: Market data, quotes, options chains, prices
- NOT FOR: Account balances, positions, P&L
- Token: jj8L3RuSVG5MUwUpz2XHrjXjAFrq
- Account: 6YB58399 (but not used for trading)

## Webull API (WORKING)
- USE FOR: Account data, positions, P&L, balances
- This is where Hunter actually trades
- Account ID: CUZ2MHT5
- DID: antgwo00z4dtifv56casauvbtfiaahbs
- Path: /Users/atlasbuilds/clawd/.venv-webull/

### Quick Check Command:
```bash
cd /Users/atlasbuilds/clawd && .venv-webull/bin/python3 -c "
import sys
sys.path.insert(0, '/Users/atlasbuilds/clawd/webull')
from webull import webull
wb = webull()
wb._set_did('antgwo00z4dtifv56casauvbtfiaahbs')
wb._access_token = 'dc_us_tech1.19c1fd34b6c-b878712ef1bc4c259fe7071c2189409f'
acct = wb.get_account()
print('Balance:', acct.get('netLiquidation'))
print('Cash:', acct['accounts'][0]['accountMembers'][1]['value'])
print('Unsettled:', acct['accounts'][0]['accountMembers'][5]['value'])
"
```

## Example Flow
1. Check prices → Tradier API
2. Check account/P&L → Webull API
3. Execute trades → Webull

Note: Webull doesn't have a direct "day P&L" field. Check unsettled funds or calculate from trade history.
