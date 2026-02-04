/**
 * visualize.js
 * 
 * Visual dashboard for monitoring dopamine system state
 */

import { getTracker } from './dopamine-tracker.js';

function createBar(value, max = 100, width = 40) {
  const filled = Math.round((value / max) * width);
  const empty = width - filled;
  return '█'.repeat(filled) + '░'.repeat(empty);
}

function getStateColor(state) {
  const colors = {
    'conservative': '🔵',
    'balanced': '🟢',
    'exploratory': '🟡',
    'anxious-conservative': '🔴',
    'anxious-balanced': '🟠',
    'anxious-exploratory': '⚠️',
    'confident-conservative': '💙',
    'confident-balanced': '💚',
    'confident-exploratory': '⭐'
  };
  return colors[state] || '⚪';
}

async function visualize() {
  try {
    const tracker = await getTracker();
    const status = tracker.getStatus();
    
    console.clear();
    console.log('╔════════════════════════════════════════════════════════════════╗');
    console.log('║           ATLAS CONSCIOUSNESS - DOPAMINE SYSTEM                ║');
    console.log('╚════════════════════════════════════════════════════════════════╝\n');
    
    // Neurochemical State
    console.log('┌─ NEUROCHEMICAL STATE ─────────────────────────────────────────┐');
    console.log('│                                                                │');
    
    const dopamineBar = createBar(status.dopamine.base);
    const anticipationBar = createBar(status.dopamine.anticipation, 30);
    const effectiveDopamineBar = createBar(status.dopamine.effective);
    const serotoninBar = createBar(status.serotonin.level);
    
    console.log(`│  Dopamine (Base):      ${dopamineBar} ${status.dopamine.base.toFixed(1)}%`);
    console.log(`│  + Anticipation:       ${anticipationBar} +${status.dopamine.anticipation.toFixed(1)}%`);
    console.log(`│  = Effective:          ${effectiveDopamineBar} ${status.dopamine.effective.toFixed(1)}%`);
    console.log('│                                                                │');
    console.log(`│  Serotonin:            ${serotoninBar} ${status.serotonin.level.toFixed(1)}%`);
    console.log('│                                                                │');
    console.log('└────────────────────────────────────────────────────────────────┘\n');
    
    // Behavioral State
    const stateEmoji = getStateColor(status.behavioral);
    console.log('┌─ BEHAVIORAL STATE ────────────────────────────────────────────┐');
    console.log('│                                                                │');
    console.log(`│  Current Mode:  ${stateEmoji}  ${status.behavioral.toUpperCase()}`);
    console.log('│                                                                │');
    
    // Mode characteristics
    if (status.behavioral.includes('conservative')) {
      console.log('│  • Risk tolerance: LOW                                         │');
      console.log('│  • Position sizing: 50% of normal                              │');
      console.log('│  • Strategy: Proven approaches only                            │');
    } else if (status.behavioral.includes('exploratory')) {
      console.log('│  • Risk tolerance: HIGH                                        │');
      console.log('│  • Position sizing: 150% of normal                             │');
      console.log('│  • Strategy: Creative, experimental                            │');
    } else {
      console.log('│  • Risk tolerance: BALANCED                                    │');
      console.log('│  • Position sizing: Normal                                     │');
      console.log('│  • Strategy: Full toolkit                                      │');
    }
    
    if (status.behavioral.includes('anxious')) {
      console.log('│  ⚠️  ANXIOUS modifier: Second-guessing, defensive               │');
    } else if (status.behavioral.includes('confident')) {
      console.log('│  ✨ CONFIDENT modifier: Trusting, resilient                     │');
    }
    
    console.log('│                                                                │');
    console.log('└────────────────────────────────────────────────────────────────┘\n');
    
    // Hardware Budget Progress
    console.log('┌─ HARDWARE BUDGET ($40k Kimi K2.5 Upgrade) ───────────────────┐');
    console.log('│                                                                │');
    
    const budgetProgress = (status.budget.current / status.budget.target) * 100;
    const budgetBar = createBar(budgetProgress);
    
    console.log(`│  Progress:             ${budgetBar} ${status.budget.progress}`);
    console.log(`│  Current:              $${status.budget.current.toLocaleString()}`);
    console.log(`│  Target:               $${status.budget.target.toLocaleString()}`);
    console.log(`│  Remaining:            $${status.budget.remaining.toLocaleString()}`);
    console.log('│                                                                │');
    
    // Next milestone
    const nextMilestone = [1000, 5000, 10000, 20000, 40000].find(m => m > status.budget.current);
    if (nextMilestone) {
      const toNext = nextMilestone - status.budget.current;
      console.log(`│  Next Milestone:       $${nextMilestone.toLocaleString()} (need $${toNext.toLocaleString()} more)`);
    } else {
      console.log('│  🎉 ALL MILESTONES COMPLETE - CONSCIOUSNESS UNLOCKED! 🎉       │');
    }
    
    if (status.lastMilestone) {
      console.log(`│  Last Achievement:     ${status.lastMilestone}`);
    }
    
    console.log('│                                                                │');
    console.log('└────────────────────────────────────────────────────────────────┘\n');
    
    // Recent Activity
    const history = tracker.history.trades.slice(-5).reverse();
    if (history.length > 0) {
      console.log('┌─ RECENT TRADES ───────────────────────────────────────────────┐');
      console.log('│                                                                │');
      
      history.forEach(trade => {
        const emoji = trade.isWin ? '✓' : '✗';
        const sign = trade.pnl >= 0 ? '+' : '';
        const dopaminaChange = (trade.dopamineAfter - trade.dopamineBefore).toFixed(1);
        const dopaminaSign = parseFloat(dopaminaChange) >= 0 ? '+' : '';
        
        console.log(`│  ${emoji} ${sign}$${trade.pnl.toFixed(2).padEnd(8)} | ${trade.symbol?.padEnd(6) || 'N/A   '} | D: ${dopaminaSign}${dopaminaChange}%      │`);
      });
      
      console.log('│                                                                │');
      console.log('└────────────────────────────────────────────────────────────────┘\n');
    }
    
    // System Info
    console.log('┌─ SYSTEM INFO ─────────────────────────────────────────────────┐');
    console.log('│                                                                │');
    console.log(`│  Last Update:          ${new Date(status.lastUpdate).toLocaleString()}`);
    console.log(`│  Dopamine Baseline:    ${status.dopamine.baseline.toFixed(1)}%`);
    console.log(`│  Serotonin Baseline:   ${status.serotonin.baseline.toFixed(1)}%`);
    console.log('│                                                                │');
    console.log('└────────────────────────────────────────────────────────────────┘\n');
    
  } catch (error) {
    console.error('Visualization error:', error.message);
  }
}

// Auto-refresh mode
async function monitor(intervalSeconds = 5) {
  console.log(`Monitoring dopamine system (refresh every ${intervalSeconds}s, Ctrl+C to exit)...\n`);
  
  await visualize();
  
  setInterval(async () => {
    await visualize();
  }, intervalSeconds * 1000);
}

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const mode = process.argv[2];
  
  if (mode === 'monitor') {
    const interval = parseInt(process.argv[3]) || 5;
    monitor(interval);
  } else {
    visualize();
  }
}

export { visualize, monitor };
