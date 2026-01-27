// Simpler approach to check Drift positions
const { Connection, PublicKey } = require('@solana/web3.js');
const { DriftClient, Wallet, BulkAccountLoader } = require('@drift-labs/sdk');

async function checkPositions() {
  try {
    const walletAddress = '7UKP7mofxSk6mn4z4jQNNE7HZSdXTPkMY8VKypZcrafx';
    console.log(`Checking Drift positions for wallet: ${walletAddress}`);
    
    // Create connection
    const connection = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');
    
    // Create account loader
    const accountLoader = new BulkAccountLoader(connection, 'confirmed', 1000);
    
    // Create dummy wallet
    const dummyWallet = {
      publicKey: new PublicKey(walletAddress),
      signTransaction: () => Promise.reject(new Error('Read-only')),
      signAllTransactions: () => Promise.reject(new Error('Read-only'))
    };
    
    console.log('Creating Drift client...');
    
    // Create Drift client with polling subscription
    const driftClient = new DriftClient({
      connection,
      wallet: dummyWallet,
      env: 'mainnet-beta',
      accountSubscription: {
        type: 'polling',
        accountLoader
      },
      subAccountIds: [0], // Check sub-account 0
      activeSubAccountId: 0
    });
    
    console.log('Subscribing to Drift client...');
    await driftClient.subscribe();
    
    console.log('Getting user account...');
    const user = driftClient.getUser();
    
    if (!user) {
      console.log('No user account found. The wallet may not have a Drift account.');
      return;
    }
    
    // Subscribe to user
    await user.subscribe();
    
    console.log('\n=== CHECKING POSITIONS ===');
    
    // Check specific perp markets: 0=SOL, 1=BTC, 2=ETH
    const markets = [
      { index: 0, symbol: 'SOL-PERP' },
      { index: 1, symbol: 'BTC-PERP' },
      { index: 2, symbol: 'ETH-PERP' }
    ];
    
    let totalUnrealizedPnL = 0;
    
    for (const market of markets) {
      const position = user.getPerpPosition(market.index);
      
      if (position && position.baseAssetAmount.abs().gtn(0)) {
        const baseAmount = position.baseAssetAmount;
        const isLong = baseAmount.gtn(0);
        const size = Math.abs(Number(baseAmount) / 1e9); // Convert from precision
        
        // Get unrealized PnL
        const unrealizedPnL = user.getUnrealizedPNL(true, market.index);
        const pnlValue = Number(unrealizedPnL) / 1e6; // Convert from USDC precision
        
        totalUnrealizedPnL += pnlValue;
        
        console.log(`\n${market.symbol}:`);
        console.log(`  Position: ${isLong ? 'LONG' : 'SHORT'} ${size.toFixed(4)}`);
        console.log(`  Entry Price: $${Number(position.entryPrice) / 1e6}`);
        console.log(`  Unrealized PnL: $${pnlValue.toFixed(2)}`);
      } else {
        console.log(`\n${market.symbol}: No position`);
      }
    }
    
    console.log(`\n=== SUMMARY ===`);
    console.log(`Total Unrealized PnL: $${totalUnrealizedPnL.toFixed(2)}`);
    
    // Check risk management rules
    if (totalUnrealizedPnL <= -50) {
      console.log(`\n⚠️ WARNING: Session PnL <= -$50 (Current: $${totalUnrealizedPnL.toFixed(2)})`);
      console.log(`Recommendation: Size down to $25 positions`);
    }
    
    if (totalUnrealizedPnL <= -100) {
      console.log(`\n🚨 ALERT: Daily loss cap of $100 reached!`);
      console.log(`Current PnL: $${totalUnrealizedPnL.toFixed(2)}`);
      console.log(`Recommendation: Close all positions immediately`);
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    console.error('Full error:', error);
  }
}

checkPositions();