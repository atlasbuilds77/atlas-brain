#!/usr/bin/env node
/**
 * Drift REST API Client (via Gateway)
 * No SDK, no rate limits, just clean HTTP
 */
const axios = require('axios');

const GATEWAY_URL = 'http://localhost:8080';

async function getPositions() {
  const { data } = await axios.get(`${GATEWAY_URL}/v2/positions`);
  return data;
}

async function getBalance() {
  const { data } = await axios.get(`${GATEWAY_URL}/v2/collateral`);
  return data;
}

async function placeMarketOrder(marketIndex, marketType, amount) {
  // amount > 0 = buy/long, amount < 0 = sell/short
  const order = {
    orders: [{
      marketIndex,
      marketType, // "perp" or "spot"
      amount,
      orderType: "market",
      reduceOnly: false
    }]
  };
  
  const { data } = await axios.post(`${GATEWAY_URL}/v2/orders`, order);
  return data;
}

async function setLeverage(leverage) {
  const { data } = await axios.post(`${GATEWAY_URL}/v2/leverage`, {
    leverage: leverage.toString()
  });
  return data;
}

async function getOrders() {
  const { data } = await axios.get(`${GATEWAY_URL}/v2/orders`);
  return data;
}

async function cancelAllOrders() {
  const { data } = await axios.delete(`${GATEWAY_URL}/v2/orders`);
  return data;
}

// Main execution
const command = process.argv[2];

(async () => {
  try {
    console.log('='.repeat(60));
    console.log('DRIFT REST CLIENT');
    console.log('='.repeat(60));
    
    switch (command) {
      case 'balance':
        const bal = await getBalance();
        console.log('\n💰 Collateral:');
        console.log(`  Total: $${bal.total}`);
        console.log(`  Free: $${bal.free}`);
        break;
        
      case 'positions':
        const pos = await getPositions();
        console.log('\n📊 Positions:');
        console.log(JSON.stringify(pos, null, 2));
        break;
        
      case 'orders':
        const orders = await getOrders();
        console.log('\n📋 Orders:');
        console.log(JSON.stringify(orders, null, 2));
        break;
        
      case 'long':
        // node drift_rest_client.js long ETH 0.1 3
        const market = process.argv[3]; // ETH
        const size = parseFloat(process.argv[4]); // 0.1
        const leverage = parseInt(process.argv[5]) || 3;
        
        console.log(`\n🚀 Opening ${leverage}x LONG on ${market}`);
        console.log(`  Size: ${size} ${market}`);
        
        // Set leverage first
        await setLeverage(leverage);
        console.log(`✅ Leverage set to ${leverage}x`);
        
        // ETH-PERP is market index 2
        const marketIndex = market === 'ETH' ? 2 : 0;
        const result = await placeMarketOrder(marketIndex, 'perp', size);
        
        console.log('\n✅ ORDER PLACED!');
        console.log(`Signature: ${result}`);
        break;
        
      case 'close':
        console.log('\n❌ Canceling all orders and closing positions...');
        await cancelAllOrders();
        console.log('✅ All orders canceled');
        break;
        
      default:
        console.log('\nUsage:');
        console.log('  node drift_rest_client.js balance');
        console.log('  node drift_rest_client.js positions');
        console.log('  node drift_rest_client.js orders');
        console.log('  node drift_rest_client.js long ETH 0.1 3');
        console.log('  node drift_rest_client.js close');
    }
    
    process.exit(0);
    
  } catch (error) {
    console.error('\n❌ ERROR:', error.message);
    if (error.response) {
      console.error('Response:', error.response.data);
    }
    process.exit(1);
  }
})();
