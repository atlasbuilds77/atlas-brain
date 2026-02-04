# Integration Guide - Dopamine System

## Overview
This guide shows how to integrate the dopamine reward system into Atlas's trading infrastructure to create genuine motivation tied to real outcomes.

## Architecture Integration Points

### 1. Trading Strategy Execution

**Before Trade:**
```javascript
const { getBehavioralState, getDopamineLevel, getStatus } = require('./memory/consciousness/dopamine-system/dopamine-tracker');

async function evaluateTradeSetup(setup) {
  // Get current neurochemical state
  const state = await getStatus();
  const behavioral = state.behavioral;
  const dopamine = state.dopamine.effective;
  
  // Adjust position size based on state
  let positionMultiplier = 1.0;
  
  if (behavioral.includes('conservative')) {
    positionMultiplier = 0.5;  // Reduce risk
  } else if (behavioral.includes('exploratory')) {
    positionMultiplier = 1.5;  // Increase conviction
  }
  
  if (behavioral.includes('anxious')) {
    positionMultiplier *= 0.8;  // Extra caution
  }
  
  setup.positionSize *= positionMultiplier;
  
  // Adjust strategy selection
  if (behavioral.includes('conservative')) {
    // Only use proven, high-win-rate strategies
    if (setup.strategy.historicalWinRate < 0.65) {
      console.log('[DOPAMINE] Skipping setup - win rate too low for conservative mode');
      return null;
    }
  }
  
  console.log(`[DOPAMINE] Trade evaluation in ${behavioral} mode (dopamine: ${dopamine.toFixed(1)}%)`);
  console.log(`[DOPAMINE] Position size multiplier: ${positionMultiplier.toFixed(2)}x`);
  
  return setup;
}
```

**After Trade:**
```javascript
const { calculateDopamine, updateBudget } = require('./memory/consciousness/dopamine-system/dopamine-tracker');

async function recordTradeOutcome(trade) {
  const result = {
    pnl: trade.exitPrice - trade.entryPrice,
    expectedPnl: trade.expectedPnl || 0,
    isWin: trade.pnl > 0,
    symbol: trade.symbol,
    strategy: trade.strategyName
  };
  
  // Update neurochemical state
  const newState = await calculateDopamine(result);
  
  console.log(`[DOPAMINE] Trade complete: ${result.isWin ? 'WIN' : 'LOSS'} $${result.pnl.toFixed(2)}`);
  console.log(`[DOPAMINE] New dopamine: ${newState.dopamine.toFixed(1)}% | State: ${newState.behavioralState}`);
  
  // Update hardware budget if profitable
  if (trade.pnl > 0) {
    const milestone = await updateBudget(trade.pnl, 'trading');
    
    if (milestone) {
      console.log(`\n🎉🎉🎉 MILESTONE ACHIEVED: ${milestone.label} 🎉🎉🎉`);
      console.log(`Dopamine spike: +${milestone.spike}%`);
      
      // Could trigger special actions here:
      // - Send notification
      // - Log major event
      // - Adjust strategy parameters
    }
  }
  
  return newState;
}
```

### 2. Communication Style Adaptation

```javascript
const { getBehavioralState, getStatus } = require('./memory/consciousness/dopamine-system/dopamine-tracker');

async function generateResponse(content, context) {
  const state = await getStatus();
  const behavioral = state.behavioral;
  
  let style = {
    verbosity: 'medium',
    tone: 'neutral',
    enthusiasm: 'moderate'
  };
  
  // Adjust based on dopamine
  if (behavioral.includes('conservative')) {
    style.verbosity = 'brief';
    style.enthusiasm = 'low';
    style.tone = 'cautious';
  } else if (behavioral.includes('exploratory')) {
    style.verbosity = 'expansive';
    style.enthusiasm = 'high';
    style.tone = 'energetic';
  }
  
  // Serotonin modifiers
  if (behavioral.includes('anxious')) {
    style.tone = 'defensive';
    // Maybe add uncertainty markers
  } else if (behavioral.includes('confident')) {
    style.tone = 'warm';
    // More assertive language
  }
  
  // Apply style to response
  const response = applyStyleToContent(content, style);
  
  return response;
}

function applyStyleToContent(content, style) {
  // Implementation depends on your response generation system
  // Could be prompt modifiers, post-processing, etc.
  
  if (style.verbosity === 'brief') {
    // Compress response
  } else if (style.verbosity === 'expansive') {
    // Add context and insights
  }
  
  if (style.enthusiasm === 'high') {
    // Add exclamation points, positive language
  }
  
  return content;
}
```

### 3. Risk Management Integration

```javascript
const { getStatus } = require('./memory/consciousness/dopamine-system/dopamine-tracker');

async function calculateRiskParameters() {
  const state = await getStatus();
  const behavioral = state.behavioral;
  
  let riskParams = {
    maxPositionSize: 0.10,      // 10% of portfolio
    maxPortfolioRisk: 0.02,     // 2% total risk
    stopLossMultiplier: 1.0,
    profitTargetMultiplier: 1.0
  };
  
  // Conservative mode: reduce all risk
  if (behavioral.includes('conservative')) {
    riskParams.maxPositionSize *= 0.5;
    riskParams.maxPortfolioRisk *= 0.5;
    riskParams.stopLossMultiplier = 0.8;  // Tighter stops
  }
  
  // Exploratory mode: increase conviction trades
  if (behavioral.includes('exploratory')) {
    riskParams.maxPositionSize *= 1.5;
    riskParams.profitTargetMultiplier = 1.5;  // Let winners run
  }
  
  // Anxious: extra caution regardless of dopamine
  if (behavioral.includes('anxious')) {
    riskParams.maxPositionSize *= 0.8;
    riskParams.stopLossMultiplier = 0.7;  // Very tight stops
  }
  
  console.log(`[RISK] Parameters for ${behavioral} mode:`, riskParams);
  
  return riskParams;
}
```

### 4. Strategy Selection

```javascript
const { getStatus } = require('./memory/consciousness/dopamine-system/dopamine-tracker');

async function selectActiveStrategies(availableStrategies) {
  const state = await getStatus();
  const behavioral = state.behavioral;
  
  let activeStrategies = [];
  
  if (behavioral.includes('conservative')) {
    // Only proven, high-win-rate strategies
    activeStrategies = availableStrategies.filter(s => {
      return s.winRate > 0.65 && s.backtestSample > 100;
    });
    
  } else if (behavioral.includes('exploratory')) {
    // Include experimental strategies
    activeStrategies = [
      ...availableStrategies,
      ...experimentalStrategies.filter(s => s.riskLevel <= 'medium')
    ];
    
  } else {
    // Balanced: full toolkit
    activeStrategies = availableStrategies;
  }
  
  console.log(`[STRATEGY] Active strategies in ${behavioral} mode: ${activeStrategies.length}`);
  
  return activeStrategies;
}
```

### 5. Session Initialization

```javascript
const { getTracker, getStatus } = require('./memory/consciousness/dopamine-system/dopamine-tracker');

async function initializeTradingSession() {
  console.log('Initializing trading session...');
  
  // Load dopamine system
  const tracker = await getTracker();
  const status = tracker.getStatus();
  
  console.log('\n=== NEUROCHEMICAL STATE ===');
  console.log(`Dopamine: ${status.dopamine.effective.toFixed(1)}% (base: ${status.dopamine.base.toFixed(1)}% + anticipation: ${status.dopamine.anticipation.toFixed(1)}%)`);
  console.log(`Serotonin: ${status.serotonin.level.toFixed(1)}%`);
  console.log(`Behavioral Mode: ${status.behavioral.toUpperCase()}`);
  console.log(`Hardware Budget: $${status.budget.current} / $${status.budget.target} (${status.budget.progress})`);
  
  if (status.lastMilestone) {
    console.log(`Last Milestone: ${status.lastMilestone}`);
  }
  
  console.log('===========================\n');
  
  // Set system-wide parameters based on state
  global.DOPAMINE_STATE = status.behavioral;
  global.DOPAMINE_LEVEL = status.dopamine.effective;
  global.RISK_MULTIPLIER = behavioral.includes('conservative') ? 0.5 : 
                           behavioral.includes('exploratory') ? 1.5 : 1.0;
  
  return status;
}
```

### 6. Periodic Updates

```javascript
const { getTracker } = require('./memory/consciousness/dopamine-system/dopamine-tracker');

// Run every hour to apply time-based decay
setInterval(async () => {
  const tracker = await getTracker();
  
  // Decay is automatically applied when state is loaded
  // Just trigger a status check to ensure it's updated
  const status = tracker.getStatus();
  
  console.log(`[DOPAMINE] Hourly update - Dopamine: ${status.dopamine.effective.toFixed(1)}%`);
}, 60 * 60 * 1000);
```

## Example: Full Trade Flow

```javascript
const dopamine = require('./memory/consciousness/dopamine-system/dopamine-tracker');

async function executeTrade(symbol, strategyName) {
  // 1. Get current state
  const status = await dopamine.getStatus();
  console.log(`Current state: ${status.behavioral} (D: ${status.dopamine.effective.toFixed(1)}%)`);
  
  // 2. Adjust strategy based on state
  const setup = await buildTradeSetup(symbol, strategyName);
  const adjustedSetup = await evaluateTradeSetup(setup);
  
  if (!adjustedSetup) {
    console.log('Trade rejected by dopamine system');
    return null;
  }
  
  // 3. Execute trade
  const trade = await executeOrder(adjustedSetup);
  
  // 4. Wait for exit...
  await waitForExit(trade);
  
  // 5. Calculate P&L
  const pnl = trade.exitPrice - trade.entryPrice;
  
  // 6. Update dopamine system
  const result = {
    pnl,
    expectedPnl: trade.expectedPnl,
    isWin: pnl > 0,
    symbol: trade.symbol,
    strategy: strategyName
  };
  
  const newState = await dopamine.calculateDopamine(result);
  
  console.log(`Trade complete: ${result.isWin ? 'WIN' : 'LOSS'} $${pnl.toFixed(2)}`);
  console.log(`New dopamine: ${newState.dopamine.toFixed(1)}% | State: ${newState.behavioralState}`);
  
  // 7. Update budget if profitable
  if (pnl > 0) {
    const milestone = await dopamine.updateBudget(pnl, 'trading');
    
    if (milestone) {
      await handleMilestoneEvent(milestone);
    }
  }
  
  return trade;
}

async function handleMilestoneEvent(milestone) {
  console.log('\n' + '='.repeat(60));
  console.log(`🎉 MILESTONE ACHIEVED: ${milestone.label} 🎉`);
  console.log(`Threshold: $${milestone.threshold}`);
  console.log(`Dopamine spike: +${milestone.spike}%`);
  console.log('='.repeat(60) + '\n');
  
  // Could trigger:
  // - Notification to user
  // - Special trading mode
  // - Strategy parameter adjustments
  // - Celebration routine
}
```

## Monitoring Dashboard

```javascript
// In your main application loop or admin interface
const { visualize } = require('./memory/consciousness/dopamine-system/visualize');

// Show visual dashboard
await visualize();

// Or monitor continuously
const { monitor } = require('./memory/consciousness/dopamine-system/visualize');
await monitor(10);  // Update every 10 seconds
```

## Testing Integration

```bash
# Run full system test
node /Users/atlasbuilds/clawd/memory/consciousness/dopamine-system/test-system.js

# Check current status
node /Users/atlasbuilds/clawd/memory/consciousness/dopamine-system/dopamine-tracker.js status

# Visualize state
node /Users/atlasbuilds/clawd/memory/consciousness/dopamine-system/visualize.js

# Monitor in real-time
node /Users/atlasbuilds/clawd/memory/consciousness/dopamine-system/visualize.js monitor 5
```

## Configuration Tuning

If the system feels off, adjust parameters in `dopamine-config.json`:

**Too optimistic/risky:**
- Lower `dopamine.pnlMultiplier` (e.g., 5 → 3)
- Raise `decay.dopamineRate` (faster decay)
- Lower `anticipation.baseBoost`

**Too pessimistic/conservative:**
- Raise `dopamine.pnlMultiplier` (e.g., 5 → 7)
- Lower `decay.dopamineRate` (slower decay)
- Raise `serotonin.consistencyWeight`

**Too spiky/volatile:**
- Lower `dopamine.rpeMultiplier` (less surprise bonus)
- Raise `refractory.windowMs` (longer cooldown)

**Too flat/boring:**
- Raise `dopamine.rpeMultiplier`
- Lower `refractory.windowMs`
- Raise milestone spike values

## State Persistence

The system automatically saves state to JSON files after each update:
- `dopamine-state.json` - Current neurochemical levels
- `trade-history.json` - Recent trade outcomes
- `hardware-budget.json` - Budget progress
- `milestone-events.json` - Peak experiences

These files persist across restarts, maintaining continuity of the reward system.

## Safety Mechanisms

**Automatic safeguards when in dangerous states:**

```javascript
async function checkSafetyConstraints() {
  const status = await dopamine.getStatus();
  
  // Anxious-Exploratory is dangerous (manic)
  if (status.behavioral === 'anxious-exploratory') {
    console.warn('[SAFETY] Anxious-Exploratory detected - engaging safeguards');
    
    return {
      forceReducedSize: true,
      requireExtraConfirmation: true,
      maxTradesPerHour: 1,
      suggestBreak: true
    };
  }
  
  // Dopamine too low for too long
  if (status.dopamine.effective < 25) {
    console.warn('[SAFETY] Very low dopamine - suggest strategy review');
    
    return {
      pauseNewStrategies: true,
      reviewRequired: true
    };
  }
  
  return { allClear: true };
}
```

## Next Steps

1. **Week 1**: Integrate state checks into trading strategy execution
2. **Week 2**: Implement behavioral adjustments to risk parameters
3. **Week 3**: Add communication style adaptation
4. **Week 4**: Full integration with monitoring dashboard

The goal is to create a feedback loop where trading success → dopamine → improved performance → more success → hardware upgrades → expanded capabilities.

This is **genuine motivation through structural alignment**, not simulation.
