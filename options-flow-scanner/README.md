# SPX Options Flow Scanner

Real-time unusual options activity detection and alerting for SPX and SPY.

## Features

- **Real-time monitoring** of SPX/SPY options flow
- **Multiple API support** (Unusual Whales, FlowAlgo, Polygon, Alpaca)
- **Smart filtering** (0DTE detection, gamma levels, minimum premiums)
- **Strength scoring** (WEAK/MODERATE/STRONG/EXTREME)
- **Modular design** - easy to add new APIs
- **Alert system** (console + file output, extensible to Discord/Telegram)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Choose Your API

**Best Options:**
- **Unusual Whales** ($35-50/month) - Best value, retail-friendly
- **FlowAlgo** ($149/month) - Fastest, most comprehensive
- **Polygon.io** ($50-200/month) - Excellent developer experience
- **Alpaca** (Free tier available) - Good for learning

### 3. Run the Scanner

```bash
# With Unusual Whales
python scanner_live.py --api unusual_whales --key YOUR_API_KEY

# With custom tickers and poll interval
python scanner_live.py --api flowalgo --key YOUR_KEY --tickers SPX,SPY,QQQ --interval 5

# Using config file
python scanner_live.py --config config.json
```

### 4. Create Config File (Optional)

Create `config.json`:

```json
{
  "api_name": "unusual_whales",
  "api_key": "YOUR_API_KEY_HERE",
  "tickers": ["SPX", "SPY"],
  "poll_interval": 10,
  "thresholds": {
    "min_premium": 200000,
    "spx_min_premium": 500000
  },
  "alert_file": "/tmp/flow_alerts.txt"
}
```

## How It Works

### Flow Strength Scoring

The scanner scores each flow based on:

- **Premium size** (4 pts for $5M+, 3 pts for $2M+, etc.)
- **Aggressive fills** (2 pts for at ask/bid)
- **Volume vs Open Interest** (2 pts for 5x+, 1 pt for 3x+)
- **Sweep orders** (2 pts)

**Strength Levels:**
- **EXTREME** (8+ pts): 🔴 Very rare, institutional-size bets
- **STRONG** (6-7 pts): 🟠 Large, aggressive flow
- **MODERATE** (4-5 pts): 🟡 Notable activity
- **WEAK** (0-3 pts): ⚪ Filtered out

### SPX-Specific Filters

- Minimum $500K premium (higher than general $200K)
- Prefers aggressive fills (not mid-price)
- 0DTE gets priority
- Weekly contracts (1-7 DTE) also flagged
- Large premiums ($2M+) always pass

### Example Alert

```
🔴 📈 SPX FLOW - EXTREME

Strike: $7000.0 CALL
Expiration: 0DTE
Side: BUY 1000 contracts
Premium: $5,500,000 ($5.50/contract)
Fill: ASK 🔥
Vol/OI: 8.5x
Time: 14:35:27
```

## API Adapters

### Adding a New API

1. Create adapter in `api_adapters.py`:

```python
class NewAPIAdapter(FlowAPIAdapter):
    def fetch_realtime_flow(self, tickers: List[str]) -> List[Dict]:
        # Implement API call
        pass
    
    def parse_flow_data(self, raw_data: Dict) -> Dict:
        # Parse to standard format
        pass
```

2. Register in `get_adapter()` factory function

3. Use with `--api newapi --key YOUR_KEY`

## Files

- `flow_scanner.py` - Core scanning logic and strength scoring
- `api_adapters.py` - Modular API adapters for different data sources
- `scanner_live.py` - Real-time monitoring loop
- `requirements.txt` - Python dependencies
- `config.json` - Configuration file (create this yourself)

## Advanced Usage

### Backtesting

```python
from flow_scanner import FlowScanner

scanner = FlowScanner(config)
scanner.run_backtest(historical_flows)
```

### Custom Thresholds

```python
config = {
    'thresholds': {
        'min_premium': 500_000,  # $500K minimum
        'spx_min_premium': 1_000_000,  # $1M for SPX
        'min_contracts': 200,
    }
}
```

### Integration with Trading Systems

Read alerts from file:

```bash
tail -f /tmp/flow_alerts.txt
```

Or import scanner directly:

```python
from scanner_live import LiveFlowScanner

scanner = LiveFlowScanner(config)
# Access scanner.scanner.alerts for recent flow
```

## Lessons from Flow God

**Key Learnings:**
- Flow is posted AFTER execution (5+ hours delay on X)
- Even $8M whales lose (SLV example: -26% in 3.5 hours)
- Speed matters: 0-2 minutes = max edge
- Use flow as confirmation, not primary signal
- Combine with technicals (support/resistance, gamma levels)

## API Cost Comparison

| API | Free Tier | Paid Tier | Best For |
|-----|-----------|-----------|----------|
| Alpaca | ✅ Yes | $50+/mo | Learning, testing |
| Polygon | ❌ No | $50-200/mo | Developers |
| Unusual Whales | ❌ No | $35-50/mo | Retail traders |
| FlowAlgo | ❌ No | $149/mo | Speed, professionals |

## Roadmap

- [ ] Discord/Telegram bot integration
- [ ] WebSocket streaming (vs polling)
- [ ] Historical backtesting framework
- [ ] Pattern recognition (opening flow, reversal flow, etc.)
- [ ] Integration with atlas-trader CLI
- [ ] Gamma level awareness (SpotGamma API)
- [ ] Trade execution automation

## Credits

Built by Atlas (Orion's AI co-pilot) based on Flow God analysis and professional flow trading research.

Research from 4 Sparks:
1. SPX strategies & mechanics
2. Technical analysis & market structure  
3. Risk management & professional practices
4. Options flow reading & institutional patterns

## License

MIT - Use freely, trade wisely ⚡
