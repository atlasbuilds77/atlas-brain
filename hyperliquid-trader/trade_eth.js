#!/usr/bin/env node
/**
 * Hyperliquid ETH-PERP Trading Bot
 * No rate limits, reliable execution
 */
const { ethers } = require('ethers');
const { Hyperliquid } = require('hyperliquid');
const fs = require('fs');

async function checkBalance() {
  try {
    // Load wallet
    const walletData = JSON.parse(
      fs.readFileSync('../hyperliquid-bot/.secrets/wallet.json', 'utf8')
    );
    
    console.log(`Hyperliquid Wallet: ${walletData.address}`);
    
    // Initialize Hyperliquid client
    const wallet = new ethers.Wallet(walletData.private_key);
    const sdk = new Hyperliquid(wallet, 'mainnet');
    
    // Get account info
    const accountInfo = await sdk.info.getUserState(walletData.address);
    
    console.log('\n📊 Account Status:');
    console.log(`  Total Value: $${accountInfo.marginSummary.accountValue}`);
    console.log(`  Available: $${accountInfo.marginSummary.withdrawable}`);
    
    // Check positions
    const positions = accountInfo.assetPositions || [];
    
    if (positions.length > 0) {
      console.log('\n📈 Open Positions:');
      positions.forEach(pos => {
        console.log(`  ${pos.position.coin}: ${pos.position.szi} @ $${pos.position.entryPx}`);
        console.log(`    PnL: $${pos.position.unrealizedPnl}`);
      });
    } else {
      console.log('\n✅ No open positions');
    }
    
    return accountInfo;
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    throw error;
  }
}

async function openETHLong(size, leverage) {
  try {
    // Load wallet
    const walletData = JSON.parse(
      fs.readFileSync('../hyperliquid-bot/.secrets/wallet.json', 'utf8')
    );
    
    const wallet = new ethers.Wallet(walletData.private_key);
    const sdk = new Hyperliquid(wallet, 'mainnet');
    
    console.log('\n🚀 Opening ETH LONG position...');
    console.log(`  Size: $${size}`);
    console.log(`  Leverage: ${leverage}x`);
    
    // Get current ETH price
    const markets = await sdk.info.getAllMids();
    const ethPrice = parseFloat(markets.ETH);
    console.log(`  ETH Price: $${ethPrice}`);
    
    // Calculate position size in ETH
    const notional = size * leverage;
    const ethAmount = notional / ethPrice;
    
    console.log(`  Notional: $${notional}`);
    console.log(`  Amount: ${ethAmount.toFixed(4)} ETH`);
    
    // Set leverage
    await sdk.exchange.updateLeverage('ETH', leverage);
    console.log(`✅ Leverage set to ${leverage}x`);
    
    // Place market order
    const order = await sdk.exchange.marketOrder(
      'ETH',
      true, // is_buy
      ethAmount,
      null, // slippage (null = no limit)
    );
    
    console.log('\n✅ ORDER PLACED!');
    console.log(`  Order ID: ${order.status.statuses[0].resting?.oid}`);
    console.log(`  Entry: $${ethPrice.toFixed(2)}`);
    console.log(`  Target: $3,370 (+15%)`);
    console.log(`  Stop: $2,635 (-10%)`);
    
    return order;
    
  } catch (error) {
    console.error('❌ Error opening position:', error.message);
    throw error;
  }
}

async function setStopLoss(stopPrice) {
  try {
    const walletData = JSON.parse(
      fs.readFileSync('../hyperliquid-bot/.secrets/wallet.json', 'utf8')
    );
    
    const wallet = new ethers.Wallet(walletData.private_key);
    const sdk = new Hyperliquid(wallet, 'mainnet');
    
    // Get current position
    const accountInfo = await sdk.info.getUserState(walletData.address);
    const ethPos = accountInfo.assetPositions?.find(p => p.position.coin === 'ETH');
    
    if (!ethPos) {
      console.log('No ETH position found');
      return;
    }
    
    const size = Math.abs(parseFloat(ethPos.position.szi));
    
    // Place stop loss order
    await sdk.exchange.stopLimitOrder(
      'ETH',
      false, // is_buy (selling to close long)
      size,
      stopPrice,
      stopPrice * 0.995, // trigger slightly before
    );
    
    console.log(`✅ Stop loss set at $${stopPrice}`);
    
  } catch (error) {
    console.error('❌ Error setting stop loss:', error.message);
  }
}

async function setTakeProfit(targetPrice) {
  try {
    const walletData = JSON.parse(
      fs.readFileSync('../hyperliquid-bot/.secrets/wallet.json', 'utf8')
    );
    
    const wallet = new ethers.Wallet(walletData.private_key);
    const sdk = new Hyperliquid(wallet, 'mainnet');
    
    // Get current position
    const accountInfo = await sdk.info.getUserState(walletData.address);
    const ethPos = accountInfo.assetPositions?.find(p => p.position.coin === 'ETH');
    
    if (!ethPos) {
      console.log('No ETH position found');
      return;
    }
    
    const size = Math.abs(parseFloat(ethPos.position.szi));
    
    // Place limit order at target
    await sdk.exchange.limitOrder(
      'ETH',
      false, // is_buy (selling to close long)
      size,
      targetPrice,
      { reduceOnly: true }
    );
    
    console.log(`✅ Take profit set at $${targetPrice}`);
    
  } catch (error) {
    console.error('❌ Error setting take profit:', error.message);
  }
}

// Main execution
const command = process.argv[2];

(async () => {
  console.log('='.repeat(60));
  console.log('HYPERLIQUID ETH-PERP TRADING');
  console.log('='.repeat(60));
  
  try {
    switch (command) {
      case 'balance':
        await checkBalance();
        break;
        
      case 'long':
        const size = parseFloat(process.argv[3]) || 93;
        const leverage = parseInt(process.argv[4]) || 3;
        await openETHLong(size, leverage);
        break;
        
      case 'stop':
        const stopPrice = parseFloat(process.argv[3]) || 2635;
        await setStopLoss(stopPrice);
        break;
        
      case 'target':
        const targetPrice = parseFloat(process.argv[3]) || 3370;
        await setTakeProfit(targetPrice);
        break;
        
      default:
        console.log('\nUsage:');
        console.log('  node trade_eth.js balance');
        console.log('  node trade_eth.js long [size] [leverage]');
        console.log('  node trade_eth.js stop [price]');
        console.log('  node trade_eth.js target [price]');
        console.log('\nExample:');
        console.log('  node trade_eth.js long 93 3   # $93 collateral, 3x leverage');
    }
    
    process.exit(0);
    
  } catch (error) {
    console.error('\n❌ FAILED:', error.message);
    process.exit(1);
  }
})();
