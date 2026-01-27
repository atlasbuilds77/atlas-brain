#!/usr/bin/env node
/**
 * Hyperliquid ETH-PERP Trading - Working Version
 */
const { Hyperliquid } = require('hyperliquid');
const { ethers } = require('ethers');
const fs = require('fs');

async function checkBalance(sdk, address) {
  console.log('\n📊 Checking account balance...');
  
  // Get user state
  const userState = await sdk.info.perpetuals.clearinghouseState(address);
  
  console.log('Account Value:', userState.marginSummary.accountValue);
  console.log('Withdrawable:', userState.marginSummary.withdrawable);
  
  // Check positions
  if (userState.assetPositions && userState.assetPositions.length > 0) {
    console.log('\n📈 Open Positions:');
    userState.assetPositions.forEach(pos => {
      console.log(`  ${pos.position.coin}:`);
      console.log(`    Size: ${pos.position.szi}`);
      console.log(`    Entry: $${pos.position.entryPx}`);
      console.log(`    PnL: $${pos.position.unrealizedPnl}`);
    });
  } else {
    console.log('\n✅ No open positions');
  }
  
  return userState;
}

async function openETHLong(sdk, collateral, leverage) {
  console.log('\n🚀 Opening ETH LONG Position');
  console.log(`  Collateral: $${collateral}`);
  console.log(`  Leverage: ${leverage}x`);
  
  // Get current ETH price
  const allMids = await sdk.info.perpetuals.allMids();
  const ethPrice = parseFloat(allMids.ETH);
  console.log(`  Current ETH Price: $${ethPrice.toFixed(2)}`);
  
  // Calculate position
  const notional = collateral * leverage;
  const ethSize = notional / ethPrice;
  
  console.log(`  Notional Value: $${notional.toFixed(2)}`);
  console.log(`  Position Size: ${ethSize.toFixed(4)} ETH`);
  
  // Set leverage
  console.log(`\n⚙️  Setting leverage to ${leverage}x...`);
  await sdk.exchange.updateLeverage(leverage, 'ETH');
  
  // Place market order
  console.log('📤 Placing market order...');
  const order = await sdk.exchange.marketOrder(
    'ETH',
    true, // is_buy
    ethSize,
    null, // no slippage limit
  );
  
  console.log('\n✅ ORDER EXECUTED!');
  console.log('Response:', JSON.stringify(order, null, 2));
  console.log(`\n📊 Trade Summary:`);
  console.log(`  Entry: $${ethPrice.toFixed(2)}`);
  console.log(`  Size: ${ethSize.toFixed(4)} ETH`);
  console.log(`  Notional: $${notional.toFixed(2)}`);
  console.log(`  Target: $3,370 (+15% = +45% on 3x)`);
  console.log(`  Stop: $2,635 (-10% = -30% on 3x)`);
  
  return order;
}

async function main() {
  try {
    console.log('='.repeat(60));
    console.log('HYPERLIQUID ETH-PERP TRADING');
    console.log('='.repeat(60));
    
    // Load wallet
    const walletData = JSON.parse(
      fs.readFileSync('../hyperliquid-bot/.secrets/wallet.json', 'utf8')
    );
    
    console.log(`\n🔑 Wallet: ${walletData.address}`);
    
    // Initialize SDK
    const wallet = new ethers.Wallet(walletData.private_key);
    const sdk = new Hyperliquid(wallet);
    
    console.log('✅ Hyperliquid SDK initialized');
    
    // Check current balance
    const userState = await checkBalance(sdk, walletData.address);
    
    const command = process.argv[2];
    
    if (command === 'long') {
      const collateral = parseFloat(process.argv[3]) || 93;
      const leverage = parseInt(process.argv[4]) || 3;
      
      await openETHLong(sdk, collateral, leverage);
    } else if (command === 'balance') {
      // Already displayed above
      console.log('\n✅ Balance check complete');
    } else {
      console.log('\nUsage:');
      console.log('  node hl_eth_trade.js balance');
      console.log('  node hl_eth_trade.js long [collateral] [leverage]');
      console.log('\nExample:');
      console.log('  node hl_eth_trade.js long 93 3');
    }
    
    process.exit(0);
    
  } catch (error) {
    console.error('\n❌ ERROR:', error.message);
    console.error(error);
    process.exit(1);
  }
}

main();
