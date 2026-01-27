// Simple script to check Drift Protocol positions for a wallet
// Using the @drift-labs/sdk

const { Connection, PublicKey } = require('@solana/web3.js');
const { DriftClient, Wallet, initialize } = require('@drift-labs/sdk');

async function checkPositions() {
  try {
    const walletAddress = '7UKP7mofxSk6mn4z4jQNNE7HZSdXTPkMY8VKypZcrafx';
    
    console.log(`Checking Drift positions for wallet: ${walletAddress}`);
    
    // Create a connection to Solana mainnet
    const connection = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');
    
    // Create a dummy wallet for read-only access
    const dummyWallet = {
      publicKey: new PublicKey(walletAddress),
      signTransaction: () => Promise.reject(new Error('Read-only wallet')),
      signAllTransactions: () => Promise.reject(new Error('Read-only wallet'))
    };
    
    console.log('Initializing Drift client...');
    
    // Initialize Drift client
    const driftClient = new DriftClient({
      connection,
      wallet: dummyWallet,
      env: 'mainnet-beta',
      accountSubscription: {
        type: 'polling',
        accountLoader: {
          connection,
          commitment: 'confirmed'
        }
      }
    });
    
    await driftClient.subscribe();
    
    console.log('Drift client subscribed successfully');
    
    // Get user account
    const user = driftClient.getUser();
    
    if (!user) {
      console.log('No Drift user account found for this wallet');
      return;
    }
    
    // Get all perp positions
    const perpPositions = user.getActivePerpPositions();
    console.log(`\n=== PERPETUAL POSITIONS ===`);
    console.log(`Found ${perpPositions.length} perpetual positions`);
    
    let totalUnrealizedPnL = 0;
    let totalSessionPnL = 0;
    
    // Check SOL, BTC, ETH perpetuals (market indexes: 0=SOL-PERP, 1=BTC-PERP, 2=ETH-PERP)
    const targetMarkets = [
      { index: 0, symbol: 'SOL-PERP' },
      { index: 1, symbol: 'BTC-PERP' },
      { index: 2, symbol: 'ETH-PERP' }
    ];
    
    for (const market of targetMarkets) {
      const position = perpPositions.find(p => p.marketIndex === market.index);
      
      if (position) {
        const baseAmount = position.baseAssetAmount.toString();
        const quoteAmount = position.quoteAssetAmount.toString();
        const entryPrice = position.entryPrice.toString();
        
        // Get unrealized PnL
        const unrealizedPnL = user.getUnrealizedPNL(true, market.index);
        const unrealizedPnLNumber = unrealizedPnL ? Number(unrealizedPnL) / 1e6 : 0; // Convert from precision
        
        totalUnrealizedPnL += unrealizedPnLNumber;
        
        console.log(`\n${market.symbol}:`);
        console.log(`  Position: ${baseAmount > 0 ? 'LONG' : 'SHORT'} ${Math.abs(Number(baseAmount) / 1e9)}`);
        console.log(`  Entry Price: $${Number(entryPrice) / 1e6}`);
        console.log(`  Unrealized PnL: $${unrealizedPnLNumber.toFixed(2)}`);
      } else {
        console.log(`\n${market.symbol}: No position`);
      }
    }
    
    // Get spot positions
    console.log(`\n=== SPOT POSITIONS ===`);
    // Check for deposits/borrows in relevant markets
    
    // Get total collateral and margin info
    const totalCollateral = user.getTotalCollateral();
    const freeCollateral = user.getFreeCollateral();
    const marginRequirement = user.getMarginRequirement();
    const leverage = user.getLeverage();
    
    console.log(`\n=== ACCOUNT SUMMARY ===`);
    console.log(`Total Collateral: $${Number(totalCollateral) / 1e6}`);
    console.log(`Free Collateral: $${Number(freeCollateral) / 1e6}`);
    console.log(`Margin Requirement: $${Number(marginRequirement) / 1e6}`);
    console.log(`Leverage: ${Number(leverage)}x`);
    console.log(`Total Unrealized PnL: $${totalUnrealizedPnL.toFixed(2)}`);
    
    // Check if session PnL <= -$50 (we'll use total unrealized as proxy for session)
    if (totalUnrealizedPnL <= -50) {
      console.log(`\n⚠️ WARNING: Session PnL is <= -$50 (currently: $${totalUnrealizedPnL.toFixed(2)})`);
      console.log(`Recommendation: Size down to $25 positions`);
    }
    
    // Daily loss cap is $100
    if (totalUnrealizedPnL <= -100) {
      console.log(`\n🚨 ALERT: Daily loss cap of $100 reached or exceeded!`);
      console.log(`Current PnL: $${totalUnrealizedPnL.toFixed(2)}`);
      console.log(`Recommendation: Close all positions immediately`);
    }
    
  } catch (error) {
    console.error('Error checking positions:', error);
  }
}

checkPositions();