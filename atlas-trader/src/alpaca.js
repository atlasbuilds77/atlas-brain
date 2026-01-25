// Alpaca API client for Atlas Trader
import 'dotenv/config';

const API_KEY = process.env.ALPACA_API_KEY;
const API_SECRET = process.env.ALPACA_API_SECRET;
const BASE_URL = process.env.ALPACA_BASE_URL || 'https://paper-api.alpaca.markets';
const DATA_URL = process.env.ALPACA_DATA_URL || 'https://data.alpaca.markets';

async function alpacaRequest(endpoint, options = {}, useDataUrl = false) {
  const baseUrl = useDataUrl ? DATA_URL : BASE_URL;
  const url = `${baseUrl}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'APCA-API-KEY-ID': API_KEY,
      'APCA-API-SECRET-KEY': API_SECRET,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Alpaca API error (${response.status}): ${error}`);
  }
  
  return response.json();
}

// Account
export async function getAccount() {
  return alpacaRequest('/v2/account');
}

// Positions
export async function getPositions() {
  return alpacaRequest('/v2/positions');
}

export async function getPosition(symbol) {
  return alpacaRequest(`/v2/positions/${encodeURIComponent(symbol)}`);
}

export async function closePosition(symbol, qty = null) {
  const params = qty ? `?qty=${qty}` : '';
  return alpacaRequest(`/v2/positions/${encodeURIComponent(symbol)}${params}`, { method: 'DELETE' });
}

// Orders
export async function getOrders(status = 'open', limit = 50) {
  return alpacaRequest(`/v2/orders?status=${status}&limit=${limit}`);
}

export async function getOrder(orderId) {
  return alpacaRequest(`/v2/orders/${orderId}`);
}

export async function createOrder(order) {
  return alpacaRequest('/v2/orders', {
    method: 'POST',
    body: JSON.stringify(order),
  });
}

export async function cancelOrder(orderId) {
  return alpacaRequest(`/v2/orders/${orderId}`, { method: 'DELETE' });
}

export async function cancelAllOrders() {
  return alpacaRequest('/v2/orders', { method: 'DELETE' });
}

// Options contracts
export async function getOptionsContracts(params = {}) {
  const query = new URLSearchParams(params).toString();
  return alpacaRequest(`/v2/options/contracts?${query}`);
}

export async function getOptionsContract(symbolOrId) {
  return alpacaRequest(`/v2/options/contracts/${encodeURIComponent(symbolOrId)}`);
}

// Market data - Stocks
export async function getStockQuote(symbol) {
  return alpacaRequest(`/v2/stocks/${symbol}/quotes/latest`, {}, true);
}

export async function getStockBars(symbol, timeframe = '1Day', limit = 100) {
  return alpacaRequest(`/v2/stocks/${symbol}/bars?timeframe=${timeframe}&limit=${limit}`, {}, true);
}

export async function getStockSnapshot(symbol) {
  return alpacaRequest(`/v2/stocks/${symbol}/snapshot`, {}, true);
}

// Market data - Options
export async function getOptionQuote(symbol) {
  return alpacaRequest(`/v1beta1/options/quotes/latest?symbols=${encodeURIComponent(symbol)}`, {}, true);
}

export async function getOptionBars(symbol, timeframe = '1Day', limit = 100) {
  return alpacaRequest(`/v1beta1/options/bars?symbols=${encodeURIComponent(symbol)}&timeframe=${timeframe}&limit=${limit}`, {}, true);
}

// Assets
export async function getAssets(params = {}) {
  const query = new URLSearchParams(params).toString();
  return alpacaRequest(`/v2/assets?${query}`);
}

export async function getAsset(symbol) {
  return alpacaRequest(`/v2/assets/${symbol}`);
}

// Account activities
export async function getActivities(activityType = null, limit = 50) {
  const endpoint = activityType 
    ? `/v2/account/activities/${activityType}?limit=${limit}`
    : `/v2/account/activities?limit=${limit}`;
  return alpacaRequest(endpoint);
}

// Clock & Calendar
export async function getClock() {
  return alpacaRequest('/v2/clock');
}

export async function getCalendar(start, end) {
  return alpacaRequest(`/v2/calendar?start=${start}&end=${end}`);
}
