# Crypto MEV and Sandwich Trading Research
*Research conducted on January 25, 2026*

## Executive Summary

Maximal Extractable Value (MEV) represents the maximum profit that can be extracted by rearranging, including, or removing transactions from a blockchain block before finalization. MEV strategies range from beneficial (arbitrage, liquidations) to harmful (sandwich attacks, front-running). In 2025, MEV continues to be a significant force in DeFi, with sandwich attacks alone accounting for $289.76 million (51.56% of total MEV volume of $561.92 million).

## 1. MEV Extraction Strategies

### 1.1 Front-Running
- **Mechanism**: MEV searchers identify pending transactions in the mempool and place identical orders with higher gas fees to execute first
- **Profit Source**: Price impact from victim's transaction
- **Example**: Searcher notices large buy order → places buy order with higher gas → profits from price increase before victim's order executes

### 1.2 Sandwich Attacks (Most Common MEV Strategy)
- **Mechanism**: Three-step process: front-run → victim trade → back-run
- **Execution**: 
  1. MEV bot buys asset before victim's trade (front-run)
  2. Victim's trade executes at inflated price
  3. MEV bot sells asset after victim's trade (back-run)
- **Capital Requirements**: Lower for tokens with less liquidity
- **2025 Statistics**: $289.76 million in sandwich attack volume (51.56% of total MEV)

### 1.3 Arbitrage (Majority of MEV Transactions)
- **Mechanism**: Exploiting price differences between DEXs
- **Process**: 
  1. Monitor price discrepancies across exchanges
  2. Execute simultaneous buy/sell across venues
  3. Profit from price convergence
- **2025 Statistics**: $3.37 million profit over 30 days (September 2025)
- **Example**: Buy ETH on Sushiswap, sell on Uniswap when price diverges

### 1.4 Liquidations
- **Mechanism**: Monitoring DeFi lending protocols for undercollateralized positions
- **Process**: 
  1. Identify loans below liquidation threshold
  2. Purchase collateral at discount
  3. Repay loan, keep remaining funds as profit
- **Role**: Risk-free profit opportunity, maintains protocol health

### 1.5 Just-in-Time (JIT) Liquidity Provision
- **Unique to Uniswap V3**: Enabled by concentrated liquidity feature
- **Process**:
  1. Detect large pending swap in mempool
  2. Calculate price range for transaction
  3. Deposit concentrated liquidity immediately before swap
  4. Earn trading fees
  5. Remove liquidity immediately after
- **Characteristics**: 
  - Rare (8,000+ transactions May 2021-July 2022)
  - Accounts for <1% of Uniswap v3 liquidity
  - Used primarily for very large swaps (>$100k)
  - 95%+ supplied by single account

## 2. Sandwich Attack Mechanics and Profitability

### 2.1 Attack Sequence
```
1. Victim submits trade to mempool
2. MEV bot detects trade and calculates optimal attack size
3. Bot submits buy order with higher gas (front-run)
4. Victim's trade executes at inflated price
5. Bot submits sell order with lower gas (back-run)
6. Bot profits from price difference
```

### 2.2 Profitability Factors
- **Liquidity Depth**: Shallow pools = higher price impact = more profit
- **Trade Size**: Larger trades = more profit potential
- **Gas Costs**: Must exceed gas fees to be profitable
- **Competition**: Multiple bots may bid up gas prices

### 2.3 Economic Impact
- **Victim Loss**: Pays higher price due to price impact
- **Network Impact**: Gas wars during high-profit opportunities
- **Market Efficiency**: Distorts price discovery

### 2.4 2025 Statistics
- Total MEV volume: $561.92 million
- Sandwich attacks: $289.76 million (51.56%)
- Average profit per attack: Varies by pool depth and trade size

## 3. Flashbots and MEV Protection

### 3.1 Flashbots Protect
- **Primary Function**: Private mempool for Ethereum transactions
- **Key Features**:
  - Frontrunning protection: Hides transactions from public mempool
  - MEV refunds: Users earn refunds if transaction creates MEV
  - Gas fee refunds: Refunds for high priority fees
  - No failed transactions: Only included if they don't revert

### 3.2 How It Works
```
1. User submits transaction to Flashbots RPC
2. Transaction sent to private Flashbots mempool
3. Hidden from public mempool and sandwich bots
4. Direct submission to block builders
5. MEV refunds distributed if applicable
```

### 3.3 2025 Developments
- **L2 Expansion**: Protection expanding to Layer 2 solutions
- **Pricing**: Growth plan starts at $49/month for 300M compute units
- **Enterprise Scaling**: Unlimited scaling via custom builders
- **User Base**: 2+ million protected users

### 3.4 Alternative Protection Methods
- **Private RPC Endpoints**: Direct submission to block builders
- **MEV-Protected DEX Aggregators**: CoWSwap batch auctions
- **Chain-Level Solutions**: Proposer-Builder Separation (PBS)
- **MEV-Boost**: Increases staking rewards by up to 60%

## 4. JIT Liquidity Provision

### 4.1 Uniswap V3 Specific
- **Requirement**: Concentrated liquidity feature
- **Process Complexity**: Requires precise timing and calculation
- **Fixed Costs**: High gas costs limit to large swaps only

### 4.2 Economic Model
```
Revenue = LP fee earned - hedging cost
Constraints:
1. Expected profit > 0
2. Must outbid other MEV opportunities
```

### 4.3 Price Improvement Bound
- **Theoretical Maximum**: 2 × pool fee rate
- **Example**: 30bp pool → max 60bp price improvement
- **Empirical Finding**: Most JIT satisfies this bound

### 4.4 Hedging Requirements
- **Necessity**: Must hedge inventory risk on other venues
- **Common Venues**: Centralized exchanges (Coinbase, etc.)
- **Cost**: Typically 1-2bps hedging cost

### 4.5 Historical Data (May 2021-July 2022)
- **Total JIT Transactions**: 8,287 attempts
- **Successful**: 8,230 (99.3% success rate)
- **Total Liquidity Provided**: $2+ billion
- **Percentage of Total Volume**: ~0.3%
- **Top Pool Concentration**: USDC-WETH 5bps pool = 50%+ of JIT

## 5. DEX Arbitrage Bots

### 5.1 Cross-DEX Arbitrage
- **Primary Strategy**: Exploit price differences between DEXs
- **Common Pairs**: Uniswap vs Sushiswap, Raydium vs Orca
- **Execution Speed**: Critical for profitability

### 5.2 Solana Ecosystem
- **Advantage**: 400ms block times enable faster execution
- **Popular Bots**:
  - Jito Backrun Arb Bot (Jito Labs)
  - Solana Arbitrage Bot (Raydium, Orca, Meteora, Jupiter)
  - SolanaMevBot (multiple DEX monitoring)
- **Flash Loan Integration**: Borrow-execute-repay in microseconds

### 5.3 Ethereum Ecosystem
- **Challenges**: Higher gas costs, slower block times
- **Strategies**:
  - Simple arbitrage between DEXs
  - Complex multi-hop arbitrage
  - MEV bundle optimization

### 5.4 Technical Requirements
- **Infrastructure**: Low-latency nodes, optimized RPC endpoints
- **Monitoring**: Real-time price feeds across multiple DEXs
- **Execution**: Flash loan capabilities, gas optimization
- **Competition**: MEV-aware strategies to outbid competitors

### 5.5 Profitability Factors
- **Market Inefficiency**: Larger price discrepancies = more profit
- **Execution Speed**: First-mover advantage critical
- **Gas Costs**: Must exceed transaction costs
- **Capital Requirements**: Larger capital = more opportunities

## 6. Current Landscape (2025)

### 6.1 Market Trends
- **Increasing Sophistication**: Attackers chain different attack types
- **Cross-Chain MEV**: Expansion beyond Ethereum to Solana, Base, etc.
- **Institutional Participation**: Large funds operating MEV bots
- **Regulatory Scrutiny**: Growing attention to MEV's impact

### 6.2 Protection Evolution
- **Widespread Adoption**: Private mempools becoming standard
- **Protocol-Level Solutions**: PBS, MEV-Boost implementation
- **User Education**: Better understanding of slippage settings
- **DEX Improvements**: Better routing, batch processing

### 6.3 Future Outlook
- **Continued Arms Race**: Bots vs protection mechanisms
- **Decentralization Efforts**: Fairer MEV distribution
- **New Attack Vectors**: Emerging with new DeFi primitives
- **Regulatory Framework**: Potential classification and oversight

## 7. Practical Recommendations

### 7.1 For Traders
- **Use MEV-Protected RPCs**: Flashbots Protect or similar
- **Set Appropriate Slippage**: Avoid excessive slippage limits
- **Use DEX Aggregators**: CoWSwap, 1inch with MEV protection
- **Monitor Gas Prices**: Avoid trading during gas wars

### 7.2 For Developers
- **Implement PBS**: Proposer-Builder Separation
- **Use Private Mempools**: For sensitive transactions
- **Batch Processing**: Reduce MEV opportunities
- **MEV-Aware Design**: Consider MEV in protocol design

### 7.3 For Researchers
- **Monitor EigenPhi**: Real-time MEV data
- **Study New Attack Vectors**: JIT, cross-chain MEV
- **Develop Protection Mechanisms**: Novel solutions needed
- **Economic Analysis**: Impact on market efficiency

## 8. Key Statistics (2025)

| Metric | Value | Source |
|--------|-------|--------|
| Total MEV Volume | $561.92M | EigenPhi |
| Sandwich Attack Volume | $289.76M (51.56%) | EigenPhi |
| Arbitrage Profit (30 days) | $3.37M | EigenPhi |
| Sandwich Profit (30 days) | $204k | EigenPhi |
| Flashbots Protected Users | 2M+ | Flashbots |
| JIT Liquidity Percentage | <1% | Uniswap Research |
| Solana Block Time | ~400ms | RPC Fast |

## 9. References

1. Arkham Intelligence - "MEV: A 2025 guide to Maximal Extractable Value in crypto"
2. Flashbots Documentation - MEV Protection Overview
3. Uniswap Blog - "Just-In-Time Liquidity on the Uniswap Protocol"
4. EigenPhi - MEV Data Aggregator
5. ScienceDirect - "Linking MEV attacks to further maximise attackers' gains"
6. Medium - "Implementing Effective MEV Protection in 2025"
7. Solana Compass - "Solana MEV Exposed: Sandwich Attacks, Arbitrage, and Validator Behavior"
8. GitHub - Various MEV bot repositories (Jito Labs, Solana Arbitrage Bot)

## 10. Conclusion

MEV represents both a challenge and opportunity in DeFi. While harmful strategies like sandwich attacks extract value from traders, beneficial strategies like arbitrage maintain market efficiency. The 2025 landscape shows increasing sophistication in both attack and protection mechanisms, with private mempools becoming standard and cross-chain MEV expanding. Understanding MEV strategies is essential for traders, developers, and researchers operating in the DeFi space.

*Research compiled from web searches conducted on January 25, 2026, focusing on 2024-2025 developments in MEV and sandwich trading.*