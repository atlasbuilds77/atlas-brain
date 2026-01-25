#!/usr/bin/env node
// Atlas Trader CLI - quick commands for trading
import 'dotenv/config';
import * as alpaca from './src/alpaca.js';

const [,, cmd, ...args] = process.argv;

const commands = {
  async account() {
    const a = await alpaca.getAccount();
    console.log(`Account: ${a.account_number}`);
    console.log(`Status: ${a.status}`);
    console.log(`Cash: $${Number(a.cash).toLocaleString()}`);
    console.log(`Buying Power: $${Number(a.buying_power).toLocaleString()}`);
    console.log(`Options BP: $${Number(a.options_buying_power).toLocaleString()}`);
    console.log(`Portfolio Value: $${Number(a.portfolio_value).toLocaleString()}`);
    console.log(`Options Level: ${a.options_trading_level}`);
  },

  async positions() {
    const positions = await alpaca.getPositions();
    if (positions.length === 0) {
      console.log('No open positions');
      return;
    }
    for (const p of positions) {
      const pnl = Number(p.unrealized_pl);
      const pnlPct = Number(p.unrealized_plpc) * 100;
      const sign = pnl >= 0 ? '+' : '';
      console.log(`${p.symbol}: ${p.qty} @ $${p.avg_entry_price} | ${sign}$${pnl.toFixed(2)} (${sign}${pnlPct.toFixed(2)}%)`);
    }
  },

  async orders(status = 'open') {
    const orders = await alpaca.getOrders(status, 20);
    if (orders.length === 0) {
      console.log(`No ${status} orders`);
      return;
    }
    for (const o of orders) {
      console.log(`${o.symbol}: ${o.side} ${o.qty} ${o.type} @ ${o.limit_price || 'market'} [${o.status}]`);
    }
  },

  async clock() {
    const c = await alpaca.getClock();
    console.log(`Market: ${c.is_open ? 'OPEN' : 'CLOSED'}`);
    console.log(`Next Open: ${c.next_open}`);
    console.log(`Next Close: ${c.next_close}`);
  },

  async quote(symbol) {
    if (!symbol) { console.log('Usage: quote <symbol>'); return; }
    const q = await alpaca.getStockQuote(symbol.toUpperCase());
    console.log(`${symbol.toUpperCase()}: Bid $${q.quote?.bp} | Ask $${q.quote?.ap}`);
  },

  async buy(symbol, qty, type = 'market', limitPrice) {
    if (!symbol || !qty) { console.log('Usage: buy <symbol> <qty> [limit] [price]'); return; }
    const order = {
      symbol: symbol.toUpperCase(),
      qty: String(qty),
      side: 'buy',
      type,
      time_in_force: 'day',
    };
    if (type === 'limit' && limitPrice) order.limit_price = String(limitPrice);
    const result = await alpaca.createOrder(order);
    console.log(`✅ Order ${result.id}: ${result.side} ${result.qty} ${result.symbol} [${result.status}]`);
  },

  async sell(symbol, qty, type = 'market', limitPrice) {
    if (!symbol || !qty) { console.log('Usage: sell <symbol> <qty> [limit] [price]'); return; }
    const order = {
      symbol: symbol.toUpperCase(),
      qty: String(qty),
      side: 'sell',
      type,
      time_in_force: 'day',
    };
    if (type === 'limit' && limitPrice) order.limit_price = String(limitPrice);
    const result = await alpaca.createOrder(order);
    console.log(`✅ Order ${result.id}: ${result.side} ${result.qty} ${result.symbol} [${result.status}]`);
  },

  async close(symbol) {
    if (!symbol) { console.log('Usage: close <symbol>'); return; }
    const result = await alpaca.closePosition(symbol.toUpperCase());
    console.log(`✅ Closed position: ${symbol.toUpperCase()}`);
  },

  async cancel(orderId) {
    if (orderId === 'all') {
      await alpaca.cancelAllOrders();
      console.log('✅ Cancelled all orders');
    } else if (orderId) {
      await alpaca.cancelOrder(orderId);
      console.log(`✅ Cancelled order ${orderId}`);
    } else {
      console.log('Usage: cancel <order_id|all>');
    }
  },

  async options(symbol, type, minDte = 30, maxDte = 180) {
    if (!symbol) { console.log('Usage: options <symbol> [call|put] [minDte] [maxDte]'); return; }
    const now = new Date();
    const minDate = new Date(now.getTime() + minDte * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const maxDate = new Date(now.getTime() + maxDte * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    const params = {
      underlying_symbols: symbol.toUpperCase(),
      expiration_date_gte: minDate,
      expiration_date_lte: maxDate,
      limit: 20,
    };
    if (type) params.type = type;
    
    const result = await alpaca.getOptionsContracts(params);
    for (const c of result.option_contracts || []) {
      console.log(`${c.symbol}: ${c.type} $${c.strike_price} exp ${c.expiration_date} | OI: ${c.open_interest}`);
    }
  },

  help() {
    console.log(`
Atlas Trader CLI

Commands:
  account           - Show account info
  positions         - Show open positions
  orders [status]   - Show orders (open/closed/all)
  clock             - Market hours
  quote <symbol>    - Get stock quote
  buy <sym> <qty> [limit] [price]  - Buy stock/option
  sell <sym> <qty> [limit] [price] - Sell stock/option
  close <symbol>    - Close position
  cancel <id|all>   - Cancel order(s)
  options <sym> [call|put] [minDte] [maxDte] - Search options
`);
  }
};

async function main() {
  if (!cmd || !commands[cmd]) {
    commands.help();
    return;
  }
  try {
    await commands[cmd](...args);
  } catch (e) {
    console.error('Error:', e.message);
  }
}

main();
