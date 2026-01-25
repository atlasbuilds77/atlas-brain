// Quick test of the Alpaca client
import 'dotenv/config';
import * as alpaca from './src/alpaca.js';

async function test() {
  console.log('Testing Alpaca connection...\n');
  
  // Account
  const account = await alpaca.getAccount();
  console.log('✅ Account:', account.account_number);
  console.log('   Cash:', account.cash);
  console.log('   Buying Power:', account.buying_power);
  console.log('   Options Level:', account.options_trading_level);
  
  // Clock
  const clock = await alpaca.getClock();
  console.log('\n✅ Market:', clock.is_open ? 'OPEN' : 'CLOSED');
  console.log('   Next Open:', clock.next_open);
  console.log('   Next Close:', clock.next_close);
  
  // Positions
  const positions = await alpaca.getPositions();
  console.log('\n✅ Positions:', positions.length);
  
  // Open orders
  const orders = await alpaca.getOrders('open');
  console.log('✅ Open Orders:', orders.length);
  
  // Test stock quote
  const quote = await alpaca.getStockQuote('AAPL');
  console.log('\n✅ AAPL Quote:', quote.quote?.ap || 'N/A');
  
  // Test options search
  const options = await alpaca.getOptionsContracts({ underlying_symbols: 'AAPL', limit: 5 });
  console.log('✅ AAPL Options found:', options.option_contracts?.length || 0);
  
  console.log('\n🎉 All tests passed!');
}

test().catch(console.error);
