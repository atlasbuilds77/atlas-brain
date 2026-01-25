# API Integration Skill

## Purpose
Add new broker/API integrations to trading systems.

## Steps
1. Research API documentation
2. Create adapter file in `brokers/` folder
3. Add config template to `accounts.json`
4. Implement auth flow
5. Implement core methods:
   - `connect()` - establish connection
   - `place_order()` - order execution
   - `get_positions()` - current positions
   - `get_account_info()` - balance, margin
6. Add error handling
7. Document in `docs/BROKER_SETUP.md`
8. Test with paper trading first

## Template Structure
```python
class NewBrokerAdapter(BaseBroker):
    def __init__(self, config):
        self.api_key = config.get('apiKey')
        self.api_secret = config.get('apiSecret')
    
    async def connect(self):
        pass
    
    async def place_order(self, symbol, side, qty, order_type='market'):
        pass
    
    async def get_positions(self):
        pass
```

## Checklist
- [ ] API docs reviewed
- [ ] Auth flow working
- [ ] Order placement tested
- [ ] Position tracking working
- [ ] Error handling complete
- [ ] Documentation added
