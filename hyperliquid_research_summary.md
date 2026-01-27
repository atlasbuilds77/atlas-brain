# Hyperliquid Python SDK Research Summary

## Research Completed

I have conducted comprehensive research on the Hyperliquid Python SDK and created a practical quick-start guide with working code examples. Here are the key findings:

## 1. Installation and Setup
- **Package**: `hyperliquid-python-sdk` available on PyPI
- **Installation**: `pip install hyperliquid-python-sdk`
- **Python Version**: 3.10 recommended (compatibility issues with 3.11)
- **Dependencies**: eth-account, websocket-client, requests, msgpack

## 2. Authentication System
- **Wallet-based**: Uses wallet addresses and private keys (not traditional API keys)
- **API Wallets**: Recommended for programmatic trading (create at app.hyperliquid.xyz/API)
- **Configuration**: Requires `account_address` (main wallet) and `secret_key` (private key)
- **Important**: When using API wallets, use main wallet address as `account_address` and API wallet private key as `secret_key`

## 3. Core Trading Functions
The SDK provides comprehensive trading capabilities:
- **Market/Limit Orders**: Full support with various time-in-force options (GTC, IOC, ALO)
- **Stop Loss/Take Profit**: Built-in trigger order types
- **Leverage Management**: Set cross or isolated leverage per coin
- **Position Management**: Get positions, balances, open orders
- **Order Management**: Cancel, modify, batch operations

## 4. Rate Limits and Best Practices
### Rate Limits:
- **IP-based**: 1200 weight per minute
- **Address-based**: 1 request per 1 USDC traded (10k initial buffer)
- **WebSocket**: Max 100 connections, 1000 subscriptions, 10 unique users

### Best Practices:
1. Use separate API wallets for different trading processes
2. Implement request batching to reduce rate limit consumption
3. Always test on testnet first (api.hyperliquid-testnet.xyz)
4. Handle WebSocket disconnections gracefully
5. Monitor request weights to avoid throttling

## 5. WebSocket for Real-time Data
- **Endpoints**: wss://api.hyperliquid.xyz/ws (mainnet), wss://api.hyperliquid-testnet.xyz/ws (testnet)
- **Subscriptions**: Order books, trades, user events, candle data
- **Features**: Low-latency real-time market data and user event streaming

## Key Files Created

1. **`hyperliquid_python_sdk_guide.md`** - Comprehensive guide covering:
   - Installation and setup
   - Authentication and API wallet creation
   - Core trading functions with code examples
   - Rate limits and best practices
   - WebSocket implementation
   - Complete trading bot example
   - Troubleshooting and security notes

2. **`hyperliquid_quick_start.py`** - Minimal working example:
   - Account information retrieval
   - Market data access
   - Trading operations (market/limit orders, stop loss, leverage)
   - Safe, commented-out examples for easy testing

3. **`config_template.json`** - Configuration template with instructions

## Important Notes for Main Agent

1. **Security First**: The authentication system uses private keys - emphasize secure storage
2. **Testnet Emphasis**: Always recommend starting with testnet to avoid financial loss
3. **Rate Limit Awareness**: The 1200 weight/minute limit requires careful request management
4. **API Wallet Strategy**: Multiple API wallets for different strategies/subaccounts
5. **WebSocket Reliability**: Must implement reconnection logic for production use

## Resources
- **Official Docs**: https://hyperliquid.gitbook.io/hyperliquid-docs
- **GitHub SDK**: https://github.com/hyperliquid-dex/hyperliquid-python-sdk
- **Testnet**: https://api.hyperliquid-testnet.xyz
- **API Wallet Creation**: https://app.hyperliquid.xyz/API

The research provides a solid foundation for building trading bots and applications on Hyperliquid using their Python SDK.