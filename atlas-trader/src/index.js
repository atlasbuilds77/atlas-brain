#!/usr/bin/env node
// Atlas Trader MCP Server
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import 'dotenv/config';
import * as alpaca from './alpaca.js';

const server = new Server(
  { name: 'atlas-trader', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

// Tool definitions
const tools = [
  {
    name: 'account_info',
    description: 'Get account information including buying power, equity, and options level',
    inputSchema: { type: 'object', properties: {}, required: [] },
  },
  {
    name: 'get_positions',
    description: 'Get all open positions (stocks and options)',
    inputSchema: { type: 'object', properties: {}, required: [] },
  },
  {
    name: 'get_position',
    description: 'Get details for a specific position',
    inputSchema: {
      type: 'object',
      properties: { symbol: { type: 'string', description: 'Symbol or option contract symbol' } },
      required: ['symbol'],
    },
  },
  {
    name: 'close_position',
    description: 'Close a position (fully or partially)',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: { type: 'string', description: 'Symbol to close' },
        qty: { type: 'number', description: 'Quantity to close (omit for full close)' },
      },
      required: ['symbol'],
    },
  },
  {
    name: 'get_orders',
    description: 'Get orders (open, closed, or all)',
    inputSchema: {
      type: 'object',
      properties: {
        status: { type: 'string', enum: ['open', 'closed', 'all'], default: 'open' },
        limit: { type: 'number', default: 50 },
      },
      required: [],
    },
  },
  {
    name: 'create_order',
    description: 'Create a new order for stock or option',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: { type: 'string', description: 'Stock symbol or option contract symbol (e.g., AAPL or AAPL240119C00100000)' },
        qty: { type: 'number', description: 'Number of shares/contracts' },
        side: { type: 'string', enum: ['buy', 'sell'] },
        type: { type: 'string', enum: ['market', 'limit', 'stop', 'stop_limit'], default: 'market' },
        time_in_force: { type: 'string', enum: ['day', 'gtc', 'ioc', 'fok'], default: 'day' },
        limit_price: { type: 'number', description: 'Limit price (required for limit/stop_limit)' },
        stop_price: { type: 'number', description: 'Stop price (required for stop/stop_limit)' },
      },
      required: ['symbol', 'qty', 'side'],
    },
  },
  {
    name: 'cancel_order',
    description: 'Cancel a specific order',
    inputSchema: {
      type: 'object',
      properties: { order_id: { type: 'string' } },
      required: ['order_id'],
    },
  },
  {
    name: 'cancel_all_orders',
    description: 'Cancel all open orders',
    inputSchema: { type: 'object', properties: {}, required: [] },
  },
  {
    name: 'search_options',
    description: 'Search for option contracts for a given underlying symbol',
    inputSchema: {
      type: 'object',
      properties: {
        underlying_symbol: { type: 'string', description: 'Stock symbol (e.g., AAPL, TSLA)' },
        type: { type: 'string', enum: ['call', 'put'], description: 'Option type' },
        expiration_date_gte: { type: 'string', description: 'Min expiration (YYYY-MM-DD)' },
        expiration_date_lte: { type: 'string', description: 'Max expiration (YYYY-MM-DD)' },
        strike_price_gte: { type: 'number', description: 'Min strike price' },
        strike_price_lte: { type: 'number', description: 'Max strike price' },
        limit: { type: 'number', default: 50 },
      },
      required: ['underlying_symbol'],
    },
  },
  {
    name: 'get_option_contract',
    description: 'Get details for a specific option contract',
    inputSchema: {
      type: 'object',
      properties: { symbol: { type: 'string', description: 'Option contract symbol' } },
      required: ['symbol'],
    },
  },
  {
    name: 'stock_quote',
    description: 'Get latest quote for a stock',
    inputSchema: {
      type: 'object',
      properties: { symbol: { type: 'string' } },
      required: ['symbol'],
    },
  },
  {
    name: 'stock_bars',
    description: 'Get historical price bars for a stock',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: { type: 'string' },
        timeframe: { type: 'string', default: '1Day', description: '1Min, 5Min, 15Min, 1Hour, 1Day, etc.' },
        limit: { type: 'number', default: 100 },
      },
      required: ['symbol'],
    },
  },
  {
    name: 'stock_snapshot',
    description: 'Get current snapshot (quote, trade, bar) for a stock',
    inputSchema: {
      type: 'object',
      properties: { symbol: { type: 'string' } },
      required: ['symbol'],
    },
  },
  {
    name: 'option_quote',
    description: 'Get latest quote for an option contract',
    inputSchema: {
      type: 'object',
      properties: { symbol: { type: 'string', description: 'Option contract symbol' } },
      required: ['symbol'],
    },
  },
  {
    name: 'market_clock',
    description: 'Get current market clock (is market open, next open/close times)',
    inputSchema: { type: 'object', properties: {}, required: [] },
  },
  {
    name: 'activities',
    description: 'Get account activities (trades, dividends, etc.)',
    inputSchema: {
      type: 'object',
      properties: {
        type: { type: 'string', description: 'Activity type (FILL, DIV, etc.) or omit for all' },
        limit: { type: 'number', default: 50 },
      },
      required: [],
    },
  },
];

// List tools handler
server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools }));

// Call tool handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    let result;
    
    switch (name) {
      case 'account_info':
        result = await alpaca.getAccount();
        break;
      case 'get_positions':
        result = await alpaca.getPositions();
        break;
      case 'get_position':
        result = await alpaca.getPosition(args.symbol);
        break;
      case 'close_position':
        result = await alpaca.closePosition(args.symbol, args.qty);
        break;
      case 'get_orders':
        result = await alpaca.getOrders(args.status || 'open', args.limit || 50);
        break;
      case 'create_order':
        result = await alpaca.createOrder({
          symbol: args.symbol,
          qty: String(args.qty),
          side: args.side,
          type: args.type || 'market',
          time_in_force: args.time_in_force || 'day',
          ...(args.limit_price && { limit_price: String(args.limit_price) }),
          ...(args.stop_price && { stop_price: String(args.stop_price) }),
        });
        break;
      case 'cancel_order':
        result = await alpaca.cancelOrder(args.order_id);
        break;
      case 'cancel_all_orders':
        result = await alpaca.cancelAllOrders();
        break;
      case 'search_options':
        result = await alpaca.getOptionsContracts({
          underlying_symbols: args.underlying_symbol,
          ...(args.type && { type: args.type }),
          ...(args.expiration_date_gte && { expiration_date_gte: args.expiration_date_gte }),
          ...(args.expiration_date_lte && { expiration_date_lte: args.expiration_date_lte }),
          ...(args.strike_price_gte && { strike_price_gte: args.strike_price_gte }),
          ...(args.strike_price_lte && { strike_price_lte: args.strike_price_lte }),
          limit: args.limit || 50,
        });
        break;
      case 'get_option_contract':
        result = await alpaca.getOptionsContract(args.symbol);
        break;
      case 'stock_quote':
        result = await alpaca.getStockQuote(args.symbol);
        break;
      case 'stock_bars':
        result = await alpaca.getStockBars(args.symbol, args.timeframe || '1Day', args.limit || 100);
        break;
      case 'stock_snapshot':
        result = await alpaca.getStockSnapshot(args.symbol);
        break;
      case 'option_quote':
        result = await alpaca.getOptionQuote(args.symbol);
        break;
      case 'market_clock':
        result = await alpaca.getClock();
        break;
      case 'activities':
        result = await alpaca.getActivities(args.type, args.limit || 50);
        break;
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
    
    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
    };
  } catch (error) {
    return {
      content: [{ type: 'text', text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Atlas Trader MCP server running');
}

main().catch(console.error);
