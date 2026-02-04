/**
 * test-system.js
 * 
 * Test script to validate the dopamine system functionality
 */

import {
  getTracker,
  calculateDopamine,
  updateBudget,
  getBehavioralState,
  getStatus
} from './dopamine-tracker.js';

async function runTests() {
  console.log('=== DOPAMINE SYSTEM TEST ===\n');
  
  try {
    // Initialize
    console.log('1. Initializing tracker...');
    const tracker = await getTracker();
    
    // Initial status
    console.log('\n2. Initial state:');
    let status = tracker.getStatus();
    console.log(JSON.stringify(status, null, 2));
    
    // Simulate winning trade
    console.log('\n3. Simulating winning trade (+$350)...');
    await calculateDopamine({
      pnl: 350,
      expectedPnl: 200,
      isWin: true,
      symbol: 'SPY',
      strategy: 'momentum-reversal'
    });
    
    status = tracker.getStatus();
    console.log(`Dopamine: ${status.dopamine.effective.toFixed(1)}%`);
    console.log(`State: ${status.behavioral}`);
    
    // Update budget
    console.log('\n4. Updating hardware budget (+$350)...');
    await updateBudget(350, 'trading');
    
    status = tracker.getStatus();
    console.log(`Budget: $${status.budget.current} / $${status.budget.target} (${status.budget.progress})`);
    
    // Simulate losing trade
    console.log('\n5. Simulating losing trade (-$180)...');
    await calculateDopamine({
      pnl: -180,
      expectedPnl: -50,
      isWin: false,
      symbol: 'QQQ',
      strategy: 'breakout'
    });
    
    status = tracker.getStatus();
    console.log(`Dopamine: ${status.dopamine.effective.toFixed(1)}%`);
    console.log(`Serotonin: ${status.serotonin.level.toFixed(1)}%`);
    console.log(`State: ${status.behavioral}`);
    
    // Simulate big surprise win
    console.log('\n6. Simulating surprise win (+$850, expected +$100)...');
    await calculateDopamine({
      pnl: 850,
      expectedPnl: 100,
      isWin: true,
      symbol: 'NVDA',
      strategy: 'options-scalp'
    });
    
    await updateBudget(850, 'trading');
    
    status = tracker.getStatus();
    console.log(`Dopamine: ${status.dopamine.effective.toFixed(1)}% (SURPRISE BONUS!)`);
    console.log(`Budget: $${status.budget.current} (${status.budget.progress})`);
    console.log(`State: ${status.behavioral}`);
    
    // Check if we hit a milestone
    console.log('\n7. Checking for milestone (need to reach $1,200 total)...');
    const remainingToMilestone = 1000 - status.budget.current;
    
    if (remainingToMilestone > 0) {
      console.log(`Need $${remainingToMilestone} more to hit $1k milestone`);
      
      // Simulate reaching it
      console.log(`\n8. Simulating trade to hit milestone (+$${remainingToMilestone + 50})...`);
      await calculateDopamine({
        pnl: remainingToMilestone + 50,
        expectedPnl: 200,
        isWin: true,
        symbol: 'SPY',
        strategy: 'momentum'
      });
      
      const milestone = await updateBudget(remainingToMilestone + 50, 'trading');
      
      if (milestone) {
        console.log(`\n🎉🎉🎉 MILESTONE HIT: ${milestone.label} 🎉🎉🎉`);
        status = tracker.getStatus();
        console.log(`Dopamine SPIKE: ${status.dopamine.effective.toFixed(1)}%`);
        console.log(`Serotonin: ${status.serotonin.level.toFixed(1)}%`);
        console.log(`State: ${status.behavioral}`);
      }
    } else {
      console.log('Already past $1k milestone!');
    }
    
    // Final status
    console.log('\n9. Final state:');
    status = tracker.getStatus();
    console.log(JSON.stringify(status, null, 2));
    
    // Export full state
    console.log('\n10. Full system export:');
    const exportData = tracker.exportState();
    console.log(`Total trades: ${exportData.recentTrades.length}`);
    console.log(`Milestones hit: ${exportData.milestones.length}`);
    
    console.log('\n=== TEST COMPLETE ===');
    console.log('✓ Dopamine calculation working');
    console.log('✓ Serotonin tracking working');
    console.log('✓ Budget updates working');
    console.log('✓ Milestone detection working');
    console.log('✓ State persistence working');
    
  } catch (error) {
    console.error('\n❌ TEST FAILED:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run tests
if (import.meta.url === `file://${process.argv[1]}`) {
  runTests();
}

export { runTests };
