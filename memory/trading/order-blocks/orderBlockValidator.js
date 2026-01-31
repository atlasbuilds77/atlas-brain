/**
 * Order Block Validator - Node.js Integration Module
 * 
 * Simple wrapper to check order blocks before trade execution
 * Integrates with Python detector backend
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');

const execPromise = promisify(exec);

const DETECTOR_PATH = path.join(__dirname, 'order_block_detector.py');
const TEMP_DIR = '/tmp/order-blocks';

class OrderBlockValidator {
  constructor(options = {}) {
    this.minStrength = options.minStrength || 7;
    this.timeframe = options.timeframe || '1h';
    this.cacheTimeout = options.cacheTimeout || 300000; // 5 minutes
    this.cache = new Map();
  }

  /**
   * Check if a trade entry conflicts with order blocks
   * @param {string} symbol - Trading symbol
   * @param {string} direction - 'long' or 'short'
   * @param {number} currentPrice - Current/entry price
   * @param {string} timeframe - Optional timeframe override
   * @returns {Promise<{safe: boolean, reason: string, orderBlocks: array}>}
   */
  async validateTrade(symbol, direction, currentPrice, timeframe = null) {
    try {
      const tf = timeframe || this.timeframe;
      
      // Check cache first
      const cacheKey = `${symbol}_${tf}`;
      const cached = this.cache.get(cacheKey);
      
      if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
        console.log(`📦 Using cached order blocks for ${symbol}`);
        return this._analyzeOrderBlocks(cached.data, direction, currentPrice);
      }

      // Fetch fresh order blocks
      console.log(`🔍 Fetching order blocks for ${symbol} (${tf})...`);
      const result = await this.getOrderBlocks(symbol, tf);
      
      // Cache result
      this.cache.set(cacheKey, {
        data: result,
        timestamp: Date.now()
      });

      return this._analyzeOrderBlocks(result, direction, currentPrice);

    } catch (error) {
      console.error('Order block validation error:', error);
      return {
        safe: true,  // Fail open (don't block trades on system error)
        reason: `Order block check failed: ${error.message}`,
        orderBlocks: []
      };
    }
  }

  /**
   * Get order blocks for a symbol (raw data)
   * @param {string} symbol - Trading symbol
   * @param {string} timeframe - Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
   * @returns {Promise<object>} Order block detection result
   */
  async getOrderBlocks(symbol, timeframe = '1h') {
    try {
      // Ensure temp directory exists
      await fs.mkdir(TEMP_DIR, { recursive: true });

      const outputFile = path.join(TEMP_DIR, `${symbol.replace('/', '-')}_${timeframe}_${Date.now()}.json`);
      
      // Run Python detector
      const cmd = `python3 "${DETECTOR_PATH}" "${symbol}" --timeframe ${timeframe} --min-strength ${this.minStrength} --output "${outputFile}"`;
      
      await execPromise(cmd, { timeout: 30000 });

      // Read result
      const data = await fs.readFile(outputFile, 'utf8');
      const result = JSON.parse(data);

      // Clean up temp file
      await fs.unlink(outputFile).catch(() => {});

      return result;

    } catch (error) {
      throw new Error(`Failed to get order blocks: ${error.message}`);
    }
  }

  /**
   * Analyze order blocks against trade direction and price
   * @private
   */
  _analyzeOrderBlocks(result, direction, currentPrice) {
    const { order_blocks, summary } = result;

    if (!order_blocks || order_blocks.length === 0) {
      return {
        safe: true,
        reason: 'No significant order blocks detected',
        orderBlocks: []
      };
    }

    // Check each order block
    for (const ob of order_blocks) {
      const inZone = currentPrice >= ob.zone_low && currentPrice <= ob.zone_high;
      const strength = ob.adjusted_strength;

      // CRITICAL: Block trades entering INTO strong opposing order blocks
      if (direction === 'long' && ob.type === 'bearish' && inZone && strength >= this.minStrength) {
        return {
          safe: false,
          reason: `🚨 BLOCKED: Entering LONG at bearish order block ($${ob.zone_low.toFixed(2)}-$${ob.zone_high.toFixed(2)}, strength: ${strength.toFixed(1)}/10). This is a SUPPLY zone - expect strong selling pressure!`,
          orderBlock: ob,
          orderBlocks: order_blocks
        };
      }

      if (direction === 'short' && ob.type === 'bullish' && inZone && strength >= this.minStrength) {
        return {
          safe: false,
          reason: `🚨 BLOCKED: Entering SHORT at bullish order block ($${ob.zone_low.toFixed(2)}-$${ob.zone_high.toFixed(2)}, strength: ${strength.toFixed(1)}/10). This is a DEMAND zone - expect strong buying pressure!`,
          orderBlock: ob,
          orderBlocks: order_blocks
        };
      }

      // WARNING: Near strong opposing order block (within 2%)
      const priceToZoneDistance = direction === 'long' 
        ? ((ob.zone_low - currentPrice) / currentPrice) * 100
        : ((currentPrice - ob.zone_high) / currentPrice) * 100;

      if (Math.abs(priceToZoneDistance) <= 2) {
        if ((direction === 'long' && ob.type === 'bearish' && currentPrice < ob.zone_low) ||
            (direction === 'short' && ob.type === 'bullish' && currentPrice > ob.zone_high)) {
          
          return {
            safe: false,
            reason: `⚠️ WARNING: Entering ${direction.toUpperCase()} near strong ${ob.type} order block ($${ob.zone_low.toFixed(2)}-$${ob.zone_high.toFixed(2)}, strength: ${strength.toFixed(1)}/10). Price is ${Math.abs(priceToZoneDistance).toFixed(1)}% away - high risk of reversal!`,
            orderBlock: ob,
            orderBlocks: order_blocks
          };
        }
      }
    }

    // No conflicts found
    return {
      safe: true,
      reason: `✅ No conflicting order blocks. ${summary}`,
      orderBlocks: order_blocks
    };
  }

  /**
   * Calculate smart stop loss based on order blocks
   * @param {string} symbol - Trading symbol
   * @param {string} direction - 'long' or 'short'
   * @param {number} entryPrice - Entry price
   * @returns {Promise<{stopLoss: number, reason: string}>}
   */
  async calculateSmartStop(symbol, direction, entryPrice) {
    try {
      const result = await this.getOrderBlocks(symbol, this.timeframe);
      const { order_blocks } = result;

      if (!order_blocks || order_blocks.length === 0) {
        return {
          stopLoss: null,
          reason: 'No order blocks found for stop calculation'
        };
      }

      if (direction === 'long') {
        // Find nearest bullish order block below entry
        const bullishBelow = order_blocks
          .filter(ob => ob.type === 'bullish' && ob.zone_high < entryPrice)
          .sort((a, b) => b.zone_high - a.zone_high);

        if (bullishBelow.length > 0) {
          const nearest = bullishBelow[0];
          const buffer = (nearest.zone_high - nearest.zone_low) * 0.15; // 15% buffer
          const stopLoss = nearest.zone_low - buffer;

          return {
            stopLoss,
            reason: `Stop placed below bullish order block at $${nearest.zone_low.toFixed(2)}-$${nearest.zone_high.toFixed(2)}`
          };
        }
      } else {
        // Find nearest bearish order block above entry
        const bearishAbove = order_blocks
          .filter(ob => ob.type === 'bearish' && ob.zone_low > entryPrice)
          .sort((a, b) => a.zone_low - b.zone_low);

        if (bearishAbove.length > 0) {
          const nearest = bearishAbove[0];
          const buffer = (nearest.zone_high - nearest.zone_low) * 0.15;
          const stopLoss = nearest.zone_high + buffer;

          return {
            stopLoss,
            reason: `Stop placed above bearish order block at $${nearest.zone_low.toFixed(2)}-$${nearest.zone_high.toFixed(2)}`
          };
        }
      }

      return {
        stopLoss: null,
        reason: `No suitable order block found for ${direction} stop placement`
      };

    } catch (error) {
      return {
        stopLoss: null,
        reason: `Stop calculation failed: ${error.message}`
      };
    }
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }
}

// Example usage
async function example() {
  const validator = new OrderBlockValidator({
    minStrength: 7,
    timeframe: '1h'
  });

  // Before entering a trade
  const symbol = 'AAPL';
  const direction = 'long';
  const currentPrice = 185.50;

  const validation = await validator.validateTrade(symbol, direction, currentPrice);

  if (!validation.safe) {
    console.error('🚫 Trade rejected:', validation.reason);
    return;
  }

  console.log('✅ Trade approved:', validation.reason);

  // Calculate smart stop
  const stopInfo = await validator.calculateSmartStop(symbol, direction, currentPrice);
  if (stopInfo.stopLoss) {
    console.log(`🛡️ Suggested stop loss: $${stopInfo.stopLoss.toFixed(2)} - ${stopInfo.reason}`);
  }

  // Proceed with trade...
}

// Uncomment to run example
// example().catch(console.error);

module.exports = { OrderBlockValidator };
