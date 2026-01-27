// Direct check without full SDK initialization
const { Connection, PublicKey } = require('@solana/web3.js');

async function checkDriftAccount() {
  try {
    const walletAddress = '7UKP7mofxSk6mn4z4jQNNE7HZSdXTPkMY8VKypZcrafx';
    console.log(`Checking if wallet has Drift account: ${walletAddress}`);
    
    // Drift program ID
    const DRIFT_PROGRAM_ID = new PublicKey('dRiftyHA39MWEi3m9aunc5MzRF1JYuBsbn6VPcn33UH');
    
    // Use a different RPC
    const connection = new Connection('https://rpc.ankr.com/solana', 'confirmed');
    
    // Check if there are any Drift user accounts for this wallet
    console.log('Querying on-chain data...');
    
    // Get program accounts for the Drift program owned by this wallet
    const accounts = await connection.getProgramAccounts(DRIFT_PROGRAM_ID, {
      filters: [
        {
          memcmp: {
            offset: 40, // Authority offset in Drift user account
            bytes: walletAddress
          }
        }
      ]
    });
    
    console.log(`Found ${accounts.length} Drift user account(s) for this wallet`);
    
    if (accounts.length === 0) {
      console.log('\nCONCLUSION: This wallet does not have any Drift Protocol positions.');
      console.log('The wallet has not initialized a Drift account or has no open positions.');
      return;
    }
    
    console.log('\nThe wallet has Drift account(s). However, to get detailed position info,');
    console.log('we would need to parse the account data or use the Drift SDK.');
    console.log('\nGiven the RPC rate limiting issues, here are the options:');
    console.log('1. Use a private RPC endpoint with higher rate limits');
    console.log('2. Check positions directly on the Drift app (app.drift.trade)');
    console.log('3. Run a local Drift Gateway instance');
    
    // Provide risk management advice anyway
    console.log('\n=== RISK MANAGEMENT REMINDER ===');
    console.log('If you have positions:');
    console.log('- Session PnL <= -$50: Size down to $25 positions');
    console.log('- Daily loss cap: $100 (close all positions if reached)');
    console.log('- Check SOL, BTC, ETH perpetuals specifically');
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

checkDriftAccount();