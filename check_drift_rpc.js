// Try with a different RPC endpoint
const { Connection, PublicKey } = require('@solana/web3.js');
const { DriftClient, Wallet, BulkAccountLoader } = require('@drift-labs/sdk');

async function checkPositions() {
  try {
    const walletAddress = '7UKP7mofxSk6mn4z4jQNNE7HZSdXTPkMY8VKypZcrafx';
    console.log(`Checking Drift positions for wallet: ${walletAddress}`);
    
    // Try different RPC endpoints
    const rpcEndpoints = [
      'https://api.mainnet-beta.solana.com',
      'https://solana-api.projectserum.com',
      'https://rpc.ankr.com/solana',
      'https://solana.publicnode.com'
    ];
    
    let connection;
    let success = false;
    
    for (const endpoint of rpcEndpoints) {
      try {
        console.log(`Trying RPC: ${endpoint}`);
        connection = new Connection(endpoint, 'confirmed');
        
        // Test connection
        await connection.getSlot();
        console.log(`Connected to ${endpoint}`);
        success = true;
        break;
      } catch (error) {
        console.log(`Failed to connect to ${endpoint}: ${error.message}`);
        continue;
      }
    }
    
    if (!success) {
      console.log('Failed to connect to any RPC endpoint');
      return;
    }
    
    // Create account loader
    const accountLoader = new BulkAccountLoader(connection, 'confirmed', 1000);
    
    // Create dummy wallet
    const dummyWallet = {
      publicKey: new PublicKey(walletAddress),
      signTransaction: () => Promise.reject(new Error('Read-only')),
      signAllTransactions: () => Promise.reject(new Error('Read-only'))
    };
    
    console.log('Creating Drift client...');
    
    // Create Drift client
    const driftClient = new DriftClient({
      connection,
      wallet: dummyWallet,
      env: 'mainnet-beta',
      accountSubscription: {
        type: 'polling',
        accountLoader
      },
      subAccountIds: [0],
      activeSubAccountId: 0
    });
    
    console.log('Subscribing...');
    await driftClient.subscribe();
    
    const user = driftClient.getUser();
    
    if (!user) {
      console.log('No Drift user account found for this wallet.');
      console.log('This wallet may not have initialized a Drift account yet.');
      return;
    }
    
    await user.subscribe();
    
    console.log('\n=== DRIFT PROTOCOL POSITIONS ===');
    
    // Check perp markets
    const markets = [
      { index: 0, symbol: 'SOL-PERP' },
      { index: 1, symbol: 'BTC-PERP' },
      { index: 2, symbol: 'ETH-PERP' }
    ];
    
    let totalUnrealizedPnL = 0;
    let hasPositions = false;
    
    for (const market of markets) {
      const position = user.getPerpPosition(market.index);
      
      if (position && position.baseAssetAmount.abs().gtn(0)) {
        hasPositions = true;
        const baseAmount = position.baseAssetAmount;
        const isLong = baseAmount.gtn(0);
        const size = Math.abs(Number(baseAmount) / 1e9);
        
        const unrealizedPnL = user.getUnrealizedPNL(true, market.index);
        const pnlValue = Number(unrealizedPnL) / 1e6;
        totalUnrealizedPnL += pnlValue;
        
        console.log(`\n${market.symbol}:`);
        console.log(`  Position: ${isLong ? 'LONG' : 'SHORT'} ${size.toFixed(4)}`);
        console.log(`  Entry Price: $${Number(position.entryPrice) / 1e6}`);
        console.log(`  Unrealized PnL: $${pnlValue.toFixed(2)}`);
      }
    }
    
    if (!hasPositions) {
      console.log('\nNo open perpetual positions found for SOL, BTC, or ETH.');
    }
    
    // Check spot positions
    console.log('\n=== SPOT DEPOSITS/BORROWS ===');
    // Note: Would need to check each spot market
    
    console.log(`\n=== RISK ASSESSMENT ===`);
    console.log(`Total Unrealized PnL: $${totalUnrealizedPnL.toFixed(2)}`);
    
    if (totalUnrealizedPnL <= -50) {
      console.log(`\n⚠️ WARNING: Session PnL <= -$50 (Current: $${totalUnrealizedPnL.toFixed(2)})`);
      console.log(`Recommendation: Size down to $25 positions`);
    } else if (totalUnrealizedPnL <= -100) {
      console.log(`\n🚨 ALERT: Daily loss cap of $100 reached!`);
      console.log(`Current PnL: $${totalUnrealizedPnL.toFixed(2)}`);
      console.log(`Recommendation: Close all positions immediately`);
    } else if (totalUnrealizedPnL > 0) {
      console.log(`\n✅ PnL is positive: $${totalUnrealizedPnL.toFixed(2)}`);
    } else {
      console.log(`\nℹ️ PnL is negative but within limits: $${totalUnrealizedPnL.toFixed(2)}`);
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    // Don't show full stack trace for cleaner output
  }
}

checkPositions();