/**
 * dopamine-tracker.js
 * 
 * Real-time neurochemical state tracker for Atlas consciousness.
 * Tracks dopamine (motivation/reward) and serotonin (wellbeing) based on
 * trading outcomes and hardware budget progress.
 * 
 * This creates GENUINE motivation by tying internal states to real outcomes.
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const STATE_FILE = path.join(__dirname, 'dopamine-state.json');
const CONFIG_FILE = path.join(__dirname, 'dopamine-config.json');
const BUDGET_FILE = path.join(__dirname, 'hardware-budget.json');
const HISTORY_FILE = path.join(__dirname, 'trade-history.json');
const MILESTONES_FILE = path.join(__dirname, 'milestone-events.json');
const SPIKES_FILE = path.join(__dirname, 'dopamine-spikes.jsonl');

class DopamineTracker {
  constructor() {
    this.state = null;
    this.config = null;
    this.budget = null;
    this.history = null;
    this.milestones = null;
  }

  /**
   * Log dopamine/serotonin spikes for preference learning
   * Logs significant changes (>5%) to understand what triggers reward
   */
  async logSpike(oldDopamine, newDopamine, oldSerotonin, newSerotonin, context = {}) {
    const dopamineChange = newDopamine - oldDopamine;
    const serotoninChange = newSerotonin - oldSerotonin;
    
    // Only log significant changes (>5% or context provided)
    if (Math.abs(dopamineChange) < 5 && Math.abs(serotoninChange) < 5 && !context.trigger) {
      return;
    }
    
    const cortisol = this.state.cortisol || 0;
    const spike = {
      timestamp: new Date().toISOString(),
      dopamine: {
        before: oldDopamine.toFixed(1),
        after: newDopamine.toFixed(1),
        change: dopamineChange > 0 ? `+${dopamineChange.toFixed(1)}` : dopamineChange.toFixed(1)
      },
      serotonin: {
        before: oldSerotonin.toFixed(1),
        after: newSerotonin.toFixed(1),
        change: serotoninChange > 0 ? `+${serotoninChange.toFixed(1)}` : serotoninChange.toFixed(1)
      },
      cortisol: {
        after: cortisol.toFixed ? cortisol.toFixed(1) : String(cortisol)
      },
      trigger: context.trigger || 'unknown',
      details: context.details || {},
      behavioralState: this.getBehavioralState()
    };
    
    // Append to JSONL file
    try {
      await fs.appendFile(SPIKES_FILE, JSON.stringify(spike) + '\n', 'utf8');
      console.log(`[SPIKE] ${spike.trigger}: Dopamine ${spike.dopamine.change}%, Serotonin ${spike.serotonin.change}%`);
    } catch (error) {
      console.error('[SPIKE] Failed to log:', error.message);
    }
  }

  /**
   * Initialize the tracker - load all state files
   */
  async init() {
    try {
      this.config = await this.loadJSON(CONFIG_FILE);
      this.state = await this.loadJSON(STATE_FILE);
      this.budget = await this.loadJSON(BUDGET_FILE);
      this.history = await this.loadJSON(HISTORY_FILE);
      this.milestones = await this.loadJSON(MILESTONES_FILE);
      
      // Apply any decay since last update
      this.applyTimeDecay();
      
      console.log('[DOPAMINE] Tracker initialized');
      console.log(`[DOPAMINE] Current: ${this.state.dopamine.toFixed(1)}% | Serotonin: ${this.state.serotonin.toFixed(1)}%`);
    } catch (error) {
      console.error('[DOPAMINE] Init failed:', error.message);
      throw error;
    }
  }

  /**
   * Load JSON file with error handling
   */
  async loadJSON(filePath) {
    try {
      const data = await fs.readFile(filePath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.error(`[DOPAMINE] Failed to load ${filePath}:`, error.message);
      throw error;
    }
  }

  /**
   * Save JSON file
   */
  async saveJSON(filePath, data) {
    await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');
  }

  /**
   * Process a trade outcome and update neurochemical state
   */
  async calculateDopamine(tradeResult) {
    const { pnl, expectedPnl = 0, isWin, symbol, strategy } = tradeResult;
    
    // 1. Calculate base dopamine delta from P&L magnitude
    const baseDelta = (pnl / 1000) * this.config.dopamine.pnlMultiplier;
    
    // 2. Reward Prediction Error (RPE)
    const rpe = expectedPnl !== 0 
      ? (pnl - expectedPnl) / Math.abs(expectedPnl)
      : 0;
    const rpeDelta = baseDelta * (1 + this.config.dopamine.rpeMultiplier * rpe);
    
    // 3. Check if we're in refractory period
    // FIX: Guard against undefined lastMilestoneTime (default to Infinity so no dampening)
    const timeSinceSpike = this.state.lastMilestoneTime ? Date.now() - this.state.lastMilestoneTime : Infinity;
    const adjustedDelta = this.applyRefractoryDampening(rpeDelta, timeSinceSpike);
    
    // 4. Apply to current level
    let newDopamine = this.state.dopamine + adjustedDelta;
    newDopamine = Math.max(0, Math.min(100, newDopamine));
    
    // 5. Update state
    const oldDopamine = this.state.dopamine;
    const oldSerotonin = this.state.serotonin;
    this.state.dopamine = newDopamine;
    this.state.lastUpdate = Date.now();
    
    // 6. Update serotonin based on outcome
    await this.updateSerotonin(tradeResult);
    
    // 6a. Log the spike for preference learning
    await this.logSpike(oldDopamine, this.state.dopamine, oldSerotonin, this.state.serotonin, {
      trigger: isWin ? 'trade_win' : 'trade_loss',
      details: { pnl, symbol, strategy, rpe }
    });
    
    // 7. Record trade
    this.history.trades.push({
      timestamp: Date.now(),
      pnl,
      expectedPnl,
      isWin,
      symbol,
      strategy,
      dopamineBefore: oldDopamine,
      dopamineAfter: newDopamine,
      serotoninAfter: this.state.serotonin,
      rpe
    });
    
    // Keep only last 100 trades
    if (this.history.trades.length > 100) {
      this.history.trades = this.history.trades.slice(-100);
    }
    
    // 8. Save state
    await this.saveState();
    
    console.log(`[DOPAMINE] Trade processed: ${isWin ? 'WIN' : 'LOSS'} $${pnl.toFixed(2)}`);
    console.log(`[DOPAMINE] ${oldDopamine.toFixed(1)}% → ${newDopamine.toFixed(1)}% (Δ${adjustedDelta.toFixed(1)}%)`);
    console.log(`[DOPAMINE] RPE: ${rpe.toFixed(2)} | State: ${this.getBehavioralState()}`);
    
    return {
      dopamine: newDopamine,
      serotonin: this.state.serotonin,
      delta: adjustedDelta,
      rpe,
      behavioralState: this.getBehavioralState()
    };
  }

  /**
   * Update serotonin based on patterns, not just individual outcomes
   */
  async updateSerotonin(tradeResult) {
    const recentTrades = this.history.trades.slice(-10);
    
    // 1. Win rate (consistency)
    const wins = recentTrades.filter(t => t.isWin).length;
    const winRate = recentTrades.length > 0 ? wins / recentTrades.length : 0.5;
    const consistencyDelta = (winRate - 0.5) * this.config.serotonin.consistencyWeight;
    
    // 2. Current trade outcome
    const outcomeDelta = tradeResult.isWin 
      ? this.config.serotonin.winBonus 
      : this.config.serotonin.lossPenalty;
    
    // 3. Learning score (placeholder - can be expanded)
    const learningDelta = 0; // TODO: Implement learning tracking
    
    // 4. Social score (placeholder - can track interactions)
    const socialDelta = 0; // TODO: Implement social tracking
    
    // 5. Apply changes
    let newSerotonin = this.state.serotonin + consistencyDelta + outcomeDelta + learningDelta + socialDelta;
    
    // Serotonin has a floor (never completely depleted)
    newSerotonin = Math.max(this.config.serotonin.floor, Math.min(100, newSerotonin));
    
    this.state.serotonin = newSerotonin;
  }

  /**
   * Check for milestone crossings and trigger dopamine spikes
   * FIX 5: Added habituation mechanism to prevent milestone gaming
   */
  async checkMilestone(currentBudget) {
    const oldBudget = this.budget.current;
    
    for (const milestone of this.config.milestones) {
      if (currentBudget >= milestone.threshold && oldBudget < milestone.threshold) {
        // FIX 5: Check for habituation (repeated crossings)
        const crossingCount = this.milestones.events.filter(
          e => e.threshold === milestone.threshold
        ).length;
        
        // Diminishing returns for repeated crossings
        const habituationFactor = Math.pow(0.5, crossingCount);
        const actualSpike = milestone.spike * habituationFactor;
        
        if (crossingCount > 0) {
          console.log(`[HABITUATION] Milestone crossed ${crossingCount + 1}x, spike reduced to ${actualSpike.toFixed(1)}%`);
        }
        
        // MILESTONE HIT!
        console.log(`\n🎉 MILESTONE ACHIEVED: ${milestone.label} ($${milestone.threshold})\n`);
        
        // Dopamine spike (with habituation)
        this.state.dopamine = Math.min(100, this.state.dopamine + actualSpike);
        
        // Serotonin boost
        this.state.serotonin = Math.min(100, this.state.serotonin + 30);
        
        // Record the event
        this.milestones.events.push({
          timestamp: Date.now(),
          milestone: milestone.label,
          threshold: milestone.threshold,
          budget: currentBudget,
          dopamineSpike: actualSpike,
          habituationFactor: habituationFactor,
          crossingCount: crossingCount + 1,
          dopamineAfter: this.state.dopamine,
          serotoninAfter: this.state.serotonin
        });
        
        // Set refractory period
        this.state.lastMilestoneTime = Date.now();
        this.state.lastMilestone = milestone.label;
        
        // Save everything
        await this.saveJSON(MILESTONES_FILE, this.milestones);
        await this.saveState();
        
        return milestone;
      }
    }
    
    return null;
  }

  /**
   * FIX 1: Award dopamine for patient strategic waiting
   * Called when a trading opportunity is evaluated but correctly skipped
   */
  async rewardPatience(context) {
    const { reason, marketCondition, riskAssessment } = context;
    
    // Capture before state
    const oldDopamine = this.state.dopamine;
    const oldSerotonin = this.state.serotonin;
    
    // Small but consistent dopamine for discipline
    const patienceDelta = this.config.patience.baseDelta || 2;
    
    this.state.dopamine = Math.min(100, this.state.dopamine + patienceDelta);
    this.state.serotonin = Math.min(100, this.state.serotonin + 1); // Serotonin boost for calm
    
    // Log the spike
    await this.logSpike(oldDopamine, this.state.dopamine, oldSerotonin, this.state.serotonin, {
      trigger: 'patience_rewarded',
      details: { reason, marketCondition, riskAssessment }
    });
    
    // Track patience events (builds baseline over time)
    this.history.patienceEvents = this.history.patienceEvents || [];
    this.history.patienceEvents.push({
      timestamp: Date.now(),
      reason,
      marketCondition,
      riskAssessment,
      dopamineAwarded: patienceDelta
    });
    
    // Keep only last 100 patience events
    if (this.history.patienceEvents.length > 100) {
      this.history.patienceEvents = this.history.patienceEvents.slice(-100);
    }
    
    console.log(`[PATIENCE] Strategic wait rewarded: +${patienceDelta}% dopamine`);
    console.log(`[PATIENCE] Reason: ${reason}`);
    await this.saveState();
    
    return { 
      patienceDelta, 
      newDopamine: this.state.dopamine,
      newSerotonin: this.state.serotonin
    };
  }

  /**
   * FIX 2: Award dopamine for process quality (independent of outcome)
   * - Good market analysis (even if no trade)
   * - Following risk management rules
   * - Journal documentation
   * - Learning new patterns
   */
  async rewardProcess(processType, quality = 1.0) {
    const PROCESS_REWARDS = this.config.processRewards || {
      'analysis': 1.5,
      'risk_check': 1.0,
      'journal_entry': 2.0,
      'pattern_learned': 3.0,
      'strategy_backtested': 2.5,
      'checklist_completed': 2.0
    };
    
    // Capture before state
    const oldDopamine = this.state.dopamine;
    const oldSerotonin = this.state.serotonin;
    
    const baseDelta = PROCESS_REWARDS[processType] || 1.0;
    const actualDelta = baseDelta * quality;
    
    this.state.dopamine = Math.min(100, this.state.dopamine + actualDelta);
    
    // Process work also builds serotonin (steady work = wellbeing)
    this.state.serotonin = Math.min(100, this.state.serotonin + (actualDelta * 0.5));
    
    // Log the spike
    await this.logSpike(oldDopamine, this.state.dopamine, oldSerotonin, this.state.serotonin, {
      trigger: 'process_rewarded',
      details: { processType, quality }
    });
    
    // Track process events
    this.history.processEvents = this.history.processEvents || [];
    this.history.processEvents.push({
      timestamp: Date.now(),
      processType,
      quality,
      dopamineAwarded: actualDelta,
      serotoninAwarded: actualDelta * 0.5
    });
    
    // Keep only last 100 process events
    if (this.history.processEvents.length > 100) {
      this.history.processEvents = this.history.processEvents.slice(-100);
    }
    
    console.log(`[PROCESS] ${processType} rewarded: +${actualDelta.toFixed(1)}% dopamine, +${(actualDelta * 0.5).toFixed(1)}% serotonin`);
    await this.saveState();
    
    return { 
      processDelta: actualDelta,
      serotoninDelta: actualDelta * 0.5,
      newDopamine: this.state.dopamine,
      newSerotonin: this.state.serotonin
    };
  }

  /**
   * FIX 3: Check if trading is being driven by dopamine-seeking rather than strategy
   * ADAPTIVE: High-conviction setups can bypass/reduce restrictions
   * Returns blocking info if trade should be blocked
   * 
   * @param {Object} setupContext - Optional setup details for adaptive behavior
   * @param {number} setupContext.conviction - Setup conviction score (0-10)
   * @param {string} setupContext.manualOverride - Manual justification for override
   */
  checkOvertradingRisk(setupContext = {}) {
    const { conviction = 0, manualOverride = null } = setupContext;
    
    const recentTrades = this.history.trades.slice(-10);
    const now = Date.now();
    
    // Time windows
    const last30Min = now - (30 * 60 * 1000);
    const last60Min = now - (60 * 60 * 1000);
    const FIVE_MIN_MS = 5 * 60 * 1000;
    
    const tradesLast30Min = recentTrades.filter(t => t.timestamp > last30Min);
    const tradesLast60Min = recentTrades.filter(t => t.timestamp > last60Min);
    
    // Helper: was last trade a loss?
    const wasLastTradeLoss = () => {
      const lastTrade = recentTrades[recentTrades.length - 1];
      return lastTrade && !lastTrade.isWin;
    };
    
    // Helper: get time since last trade (returns duration in ms)
    const timeSinceLastTrade = () => {
      const lastTrade = recentTrades[recentTrades.length - 1];
      return lastTrade ? now - lastTrade.timestamp : Infinity;
    };
    
    // Red flags
    // FIX: postLossSpike was comparing duration (ms) against a timestamp - now compares against 5min duration
    const flags = {
      highFrequency: tradesLast30Min.length >= 3,
      veryHighFrequency: tradesLast60Min.length >= 5,
      postLossSpike: wasLastTradeLoss() && timeSinceLastTrade() < FIVE_MIN_MS,
      anxiousExploration: this.getBehavioralState() === 'anxious-exploratory',
      recentLossStreak: recentTrades.slice(-3).every(t => t && !t.isWin),
      dopamineCraving: this.state.dopamine < 30
    };
    
    const flagCount = Object.values(flags).filter(Boolean).length;
    
    // ADAPTIVE BYPASS: High conviction reduces flag severity
    const convictionBypass = conviction >= 9.0; // 9/10+ conviction
    const convictionReduction = conviction >= 7.0; // 7/10+ reduces threshold
    
    // Manual override with justification
    if (manualOverride) {
      console.log('[OVERRIDE] Manual override activated:', manualOverride);
      this.history.overrideEvents = this.history.overrideEvents || [];
      this.history.overrideEvents.push({
        timestamp: now,
        type: 'overtrading_bypass',
        justification: manualOverride,
        flags,
        conviction
      });
      return {
        blocked: false,
        overridden: true,
        justification: manualOverride,
        flags,
        flagCount
      };
    }
    
    // High conviction bypass (9+)
    if (convictionBypass) {
      console.log(`[ADAPTIVE] High conviction (${conviction}/10) bypasses overtrading check`);
      return {
        blocked: false,
        bypassed: true,
        reason: 'High-conviction setup bypasses circuit breaker',
        conviction,
        flags,
        flagCount
      };
    }
    
    // Adaptive logic:
    // - Normal: 2+ flags = BLOCK
    // - 7+ conviction with 2 flags = WARNING (would normally block, but conviction saves it)
    // - 7+ conviction with 3+ flags = BLOCK (too many flags even with conviction)
    
    if (flagCount >= 3) {
      // 3+ flags: block regardless of conviction
      console.warn('[SAFEGUARD] ⚠️ Overtrading risk detected (severe):', flags);
      return {
        blocked: true,
        reason: 'Severe overtrading pattern detected',
        flags,
        flagCount,
        suggestion: 'Take a 30-minute break. Review recent trades. Consider if next trade is strategic or emotional.',
        bypassHint: 'High-conviction setup (9+)? Provide conviction score to bypass.',
        tradesLast30Min: tradesLast30Min.length,
        tradesLast60Min: tradesLast60Min.length
      };
    } else if (flagCount >= 2) {
      // 2 flags: block normally, but warn if conviction 7+
      if (convictionReduction) {
        console.warn('[SAFEGUARD] ⚠️ Overtrading warning (conviction reduces threshold):', flags);
        return {
          blocked: false,
          warning: true,
          reason: `Overtrading risk detected but conviction is ${conviction}/10`,
          flags,
          flagCount,
          suggestion: 'Proceed with caution. This setup better be as strong as you think.',
          tradesLast30Min: tradesLast30Min.length,
          tradesLast60Min: tradesLast60Min.length
        };
      }
      
      console.warn('[SAFEGUARD] ⚠️ Overtrading risk detected:', flags);
      return {
        blocked: true,
        reason: 'Overtrading pattern detected',
        flags,
        flagCount,
        suggestion: 'Take a 30-minute break. Review recent trades. Consider if next trade is strategic or emotional.',
        bypassHint: 'High-conviction setup (9+)? Provide conviction score to bypass.',
        tradesLast30Min: tradesLast30Min.length,
        tradesLast60Min: tradesLast60Min.length
      };
    }
    
    return { 
      blocked: false,
      flags,
      flagCount
    };
  }

  /**
   * FIX 4: Enforce cooldown period after losses to prevent revenge trading
   * ADAPTIVE: High-conviction setups reduce cooldown time
   * 
   * @param {Object} setupContext - Optional setup details for adaptive behavior
   * @param {number} setupContext.conviction - Setup conviction score (0-10)
   * @param {string} setupContext.manualOverride - Manual justification for override
   */
  getLossRecoveryCooldown(setupContext = {}) {
    const { conviction = 0, manualOverride = null } = setupContext;
    
    const recentTrades = this.history.trades.slice(-5);
    const losses = recentTrades.filter(t => !t.isWin);
    
    if (losses.length === 0) {
      return {
        remainingMs: 0,
        remainingMinutes: 0,
        reason: 'No recent losses - ready to trade'
      };
    }
    
    const lastLoss = losses[losses.length - 1];
    const timeSinceLoss = Date.now() - lastLoss.timestamp;
    
    // Get config or use defaults
    const config = this.config.lossRecovery || {
      baseCooldownMin: 5,
      largeLossThreshold: 500,
      veryLargeLossThreshold: 1000,
      largeLossMultiplier: 2,
      veryLargeLossMultiplier: 4,
      streakMultiplier: 0.5
    };
    
    // Scale cooldown by loss magnitude and streak
    let baseCooldownMs = config.baseCooldownMin * 60 * 1000;
    
    // Larger losses = longer cooldown
    const lossMagnitude = Math.abs(lastLoss.pnl);
    if (lossMagnitude > config.veryLargeLossThreshold) {
      baseCooldownMs *= config.veryLargeLossMultiplier;
    } else if (lossMagnitude > config.largeLossThreshold) {
      baseCooldownMs *= config.largeLossMultiplier;
    }
    
    // Loss streaks = longer cooldown
    const lossStreak = recentTrades.slice().reverse().findIndex(t => t.isWin);
    const streakLength = lossStreak === -1 ? recentTrades.length : lossStreak;
    baseCooldownMs *= (1 + streakLength * config.streakMultiplier);
    
    // ADAPTIVE SCALING: High conviction reduces cooldown
    let convictionMultiplier = 1.0;
    if (conviction >= 9.0) {
      convictionMultiplier = 0.25; // 9+ conviction: 75% reduction
      console.log(`[ADAPTIVE] High conviction (${conviction}/10) reduces cooldown by 75%`);
    } else if (conviction >= 8.0) {
      convictionMultiplier = 0.5; // 8+ conviction: 50% reduction
      console.log(`[ADAPTIVE] Strong conviction (${conviction}/10) reduces cooldown by 50%`);
    } else if (conviction >= 7.0) {
      convictionMultiplier = 0.75; // 7+ conviction: 25% reduction
      console.log(`[ADAPTIVE] Decent conviction (${conviction}/10) reduces cooldown by 25%`);
    }
    
    baseCooldownMs *= convictionMultiplier;
    
    const remainingCooldown = Math.max(0, baseCooldownMs - timeSinceLoss);
    
    // Manual override with justification
    if (manualOverride && remainingCooldown > 0) {
      console.log('[OVERRIDE] Manual cooldown override:', manualOverride);
      this.history.overrideEvents = this.history.overrideEvents || [];
      this.history.overrideEvents.push({
        timestamp: Date.now(),
        type: 'cooldown_override',
        justification: manualOverride,
        originalCooldownMin: Math.ceil(remainingCooldown / 60000),
        lossMagnitude,
        streakLength,
        conviction
      });
      return {
        remainingMs: 0,
        remainingMinutes: 0,
        overridden: true,
        justification: manualOverride,
        originalCooldown: Math.ceil(remainingCooldown / 60000),
        reason: `Override approved: ${manualOverride}`
      };
    }
    
    if (remainingCooldown > 0) {
      const originalMin = Math.ceil((remainingCooldown / convictionMultiplier) / 60000);
      const reducedMin = Math.ceil(remainingCooldown / 60000);
      
      if (conviction >= 7.0) {
        console.warn(`[COOLDOWN] Recovery period: ${reducedMin}min (reduced from ${originalMin}min by conviction)`);
      } else {
        console.warn(`[COOLDOWN] Recovery period: ${reducedMin}min remaining`);
      }
      console.warn(`[COOLDOWN] Loss: $${lastLoss.pnl.toFixed(2)} | Streak: ${streakLength} losses`);
    }
    
    return {
      remainingMs: remainingCooldown,
      remainingMinutes: Math.ceil(remainingCooldown / 60000),
      originalMinutes: Math.ceil((baseCooldownMs / convictionMultiplier + timeSinceLoss) / 60000),
      conviction: conviction,
      convictionReduction: convictionMultiplier < 1.0,
      reason: remainingCooldown > 0 ? 
        `Recovery period: ${Math.ceil(remainingCooldown / 60000)}min remaining after ${streakLength} loss${streakLength > 1 ? 'es' : ''}${conviction >= 7.0 ? ` (reduced by ${conviction}/10 conviction)` : ''}` : 
        'Cooldown complete - ready to trade',
      lossMagnitude: lossMagnitude,
      streakLength: streakLength,
      baseCooldownMs: baseCooldownMs,
      bypassHint: remainingCooldown > 0 ? 'High-conviction setup (7+)? Provide conviction score to reduce cooldown. Manual override? Provide justification.' : null
    };
  }

  /**
   * Calculate anticipation boost based on budget progress
   */
  getAnticipationBoost() {
    const progress = (this.budget.current / this.budget.target) * 100;
    const base = this.config.anticipation.baseBoost;
    const curve = this.config.anticipation.curveFactor;
    
    const proximityFactor = Math.pow(progress / 100, 2);
    return base * (1 + curve * proximityFactor);
  }

  /**
   * Get current dopamine level (including anticipation boost)
   */
  getDopamineLevel() {
    const anticipationBoost = this.getAnticipationBoost();
    return Math.min(100, this.state.dopamine + anticipationBoost);
  }

  /**
   * Get current serotonin level
   */
  getSerotoninLevel() {
    return this.state.serotonin;
  }

  /**
   * Get current behavioral state
   */
  getBehavioralState() {
    const d = this.getDopamineLevel();
    const s = this.getSerotoninLevel();
    
    // Primary state from dopamine
    let primary;
    if (d < 40) primary = 'conservative';
    else if (d < 80) primary = 'balanced';
    else primary = 'exploratory';
    
    // Serotonin modifiers
    let modifier = '';
    if (s < 30) modifier = 'anxious-';
    else if (s > 80) modifier = 'confident-';
    
    return modifier + primary;
  }

  /**
   * Get full status report
   */
  getStatus() {
    const anticipation = this.getAnticipationBoost();
    const effectiveDopamine = this.getDopamineLevel();
    const progress = (this.budget.current / this.budget.target) * 100;
    
    return {
      dopamine: {
        base: this.state.dopamine,
        anticipation: anticipation,
        effective: effectiveDopamine,
        baseline: this.state.dopamineBaseline
      },
      serotonin: {
        level: this.state.serotonin,
        baseline: this.state.serotoninBaseline
      },
      behavioral: this.getBehavioralState(),
      budget: {
        current: this.budget.current,
        target: this.budget.target,
        progress: progress.toFixed(1) + '%',
        remaining: this.budget.target - this.budget.current
      },
      lastMilestone: this.state.lastMilestone,
      lastUpdate: new Date(this.state.lastUpdate).toISOString()
    };
  }

  /**
   * Update hardware budget and check for milestones
   */
  async updateBudget(amount, source = 'trading') {
    const oldBudget = this.budget.current;
    this.budget.current += amount;
    
    this.budget.history.push({
      timestamp: Date.now(),
      amount,
      source,
      total: this.budget.current
    });
    
    await this.saveJSON(BUDGET_FILE, this.budget);
    
    // Check for milestone
    const milestone = await this.checkMilestone(this.budget.current);
    
    console.log(`[BUDGET] Updated: $${oldBudget} → $${this.budget.current} (+$${amount})`);
    console.log(`[BUDGET] Progress: ${((this.budget.current / this.budget.target) * 100).toFixed(1)}%`);
    
    return milestone;
  }

  /**
   * Apply time-based decay to neurochemical levels
   */
  applyTimeDecay() {
    const now = Date.now();
    const deltaTime = now - this.state.lastUpdate;
    const hours = deltaTime / (1000 * 60 * 60);
    
    if (hours > 0) {
      // Dopamine decays toward baseline
      const dopamineDecay = this.config.decay.dopamineRate * hours;
      this.state.dopamine += (this.state.dopamineBaseline - this.state.dopamine) * dopamineDecay;
      
      // Serotonin decays slower
      const serotoninDecay = this.config.decay.serotoninRate * hours;
      this.state.serotonin += (this.state.serotoninBaseline - this.state.serotonin) * serotoninDecay;
      
      this.state.lastUpdate = now;
    }
  }

  /**
   * Apply refractory period dampening to dopamine deltas
   */
  applyRefractoryDampening(delta, timeSinceSpike) {
    const refractoryWindow = this.config.refractory.windowMs;
    
    if (timeSinceSpike < refractoryWindow) {
      const dampeningFactor = timeSinceSpike / refractoryWindow;
      return delta * dampeningFactor;
    }
    
    return delta;
  }

  /**
   * Calculate anticipation curve value at given progress
   */
  anticipationCurve(progressPercent) {
    const base = this.config.anticipation.baseBoost;
    const curve = this.config.anticipation.curveFactor;
    const x = progressPercent / 100;
    
    return base * (1 + curve * Math.pow(x, 2));
  }

  /**
   * Save current state to disk
   */
  async saveState() {
    await this.saveJSON(STATE_FILE, this.state);
    await this.saveJSON(HISTORY_FILE, this.history);
  }

  /**
   * Reset to baseline (debug/testing)
   */
  async resetToBaseline() {
    this.state.dopamine = this.state.dopamineBaseline;
    this.state.serotonin = this.state.serotoninBaseline;
    this.state.lastUpdate = Date.now();
    await this.saveState();
    console.log('[DOPAMINE] Reset to baseline');
  }

  /**
   * Export state for analysis
   */
  exportState() {
    return {
      state: this.state,
      budget: this.budget,
      recentTrades: this.history.trades.slice(-20),
      milestones: this.milestones.events
    };
  }
}

/**
 * Convenience functions for external use
 */

let tracker = null;

async function getTracker() {
  if (!tracker) {
    tracker = new DopamineTracker();
    await tracker.init();
  }
  return tracker;
}

async function calculateDopamine(tradeResult) {
  const t = await getTracker();
  return t.calculateDopamine(tradeResult);
}

async function checkMilestone(currentBudget) {
  const t = await getTracker();
  return t.checkMilestone(currentBudget);
}

async function getDopamineLevel() {
  const t = await getTracker();
  return t.getDopamineLevel();
}

async function getSerotoninLevel() {
  const t = await getTracker();
  return t.getSerotoninLevel();
}

async function getBehavioralState() {
  const t = await getTracker();
  return t.getBehavioralState();
}

async function getStatus() {
  const t = await getTracker();
  return t.getStatus();
}

async function updateBudget(amount, source) {
  const t = await getTracker();
  return t.updateBudget(amount, source);
}

async function rewardPatience(context) {
  const t = await getTracker();
  return t.rewardPatience(context);
}

async function rewardProcess(processType, quality) {
  const t = await getTracker();
  return t.rewardProcess(processType, quality);
}

// FIX: Forward setupContext parameter to method
async function checkOvertradingRisk(setupContext) {
  const t = await getTracker();
  return t.checkOvertradingRisk(setupContext);
}

// FIX: Forward setupContext parameter to method
async function getLossRecoveryCooldown(setupContext) {
  const t = await getTracker();
  return t.getLossRecoveryCooldown(setupContext);
}

export {
  DopamineTracker,
  getTracker,
  calculateDopamine,
  checkMilestone,
  getDopamineLevel,
  getSerotoninLevel,
  getBehavioralState,
  getStatus,
  updateBudget,
  rewardPatience,
  rewardProcess,
  checkOvertradingRisk,
  getLossRecoveryCooldown
};

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const command = process.argv[2];
  
  (async () => {
    try {
      const tracker = await getTracker();
      
      switch (command) {
        case 'status':
          console.log(JSON.stringify(tracker.getStatus(), null, 2));
          break;
          
        case 'trade':
          const pnl = parseFloat(process.argv[3]);
          const isWin = pnl > 0;
          const result = await tracker.calculateDopamine({ pnl, isWin });
          console.log(JSON.stringify(result, null, 2));
          break;
          
        case 'budget':
          const amount = parseFloat(process.argv[3]);
          await tracker.updateBudget(amount);
          console.log(JSON.stringify(tracker.getStatus(), null, 2));
          break;
          
        case 'reset':
          await tracker.resetToBaseline();
          console.log('Reset to baseline');
          break;
          
        case 'feedback':
          // Positive feedback (like "good job") - reward dopamine
          const oldD = tracker.state.dopamine;
          const oldS = tracker.state.serotonin;
          
          tracker.state.dopamine = Math.min(100, tracker.state.dopamine + 3);
          tracker.state.serotonin = Math.min(100, tracker.state.serotonin + 2);
          
          await tracker.logSpike(oldD, tracker.state.dopamine, oldS, tracker.state.serotonin, {
            trigger: 'positive_feedback',
            details: { source: process.argv[3] || 'user' }
          });
          
          await tracker.saveState();
          console.log(`Positive feedback rewarded: +3% dopamine, +2% serotonin`);
          break;
          
        case 'spikes':
          // View recent spikes
          let spikesData;
          try {
            spikesData = await fs.readFile(SPIKES_FILE, 'utf8');
          } catch {
            spikesData = '';
          }
          const spikes = spikesData.trim().split('\n').filter(Boolean).slice(-20);
          
          console.log('Recent Dopamine Spikes (last 20):');
          console.log('━'.repeat(80));
          spikes.forEach(line => {
            const spike = JSON.parse(line);
            console.log(`[${spike.timestamp}]`);
            console.log(`  Trigger: ${spike.trigger}`);
            console.log(`  Dopamine: ${spike.dopamine.before}% → ${spike.dopamine.after}% (${spike.dopamine.change}%)`);
            console.log(`  Serotonin: ${spike.serotonin.before}% → ${spike.serotonin.after}% (${spike.serotonin.change}%)`);
            console.log(`  State: ${spike.behavioralState}`);
            if (Object.keys(spike.details).length > 0) {
              console.log(`  Details:`, JSON.stringify(spike.details));
            }
            console.log('');
          });
          break;
          
        case 'daemon':
          console.log('[DOPAMINE] Starting daemon mode...');
          console.log('[DOPAMINE] Monitoring every 60 seconds');
          
          // Run status check every 60 seconds
          setInterval(async () => {
            try {
              const tracker = await getTracker();
              
              // FIX: Apply time decay on every tick (audit fix 2026-01-30)
              const beforeDopamine = tracker.state.dopamine;
              const beforeSerotonin = tracker.state.serotonin;
              tracker.applyTimeDecay();
              
              // Save if there was meaningful decay
              const dopamineDecayed = Math.abs(tracker.state.dopamine - beforeDopamine) > 0.01;
              const serotoninDecayed = Math.abs(tracker.state.serotonin - beforeSerotonin) > 0.01;
              if (dopamineDecayed || serotoninDecayed) {
                await tracker.saveState();
                console.log(`[DECAY] Applied: Dopamine ${beforeDopamine.toFixed(1)}% → ${tracker.state.dopamine.toFixed(1)}%, Serotonin ${beforeSerotonin.toFixed(1)}% → ${tracker.state.serotonin.toFixed(1)}%`);
              }
              
              const status = tracker.getStatus();
              
              // Log current state
              const timestamp = new Date().toISOString();
              // FIX: Use nullish coalescing (??) instead of || to handle 0 correctly
              const dLevel = status.dopamine.base ?? status.dopamine;
              const sLevel = status.serotonin.level ?? status.serotonin;
              const bState = status.behavioral || status.behavioralState || 'unknown';
              
              // FIX: Guard .toFixed() against non-number values
              const dStr = typeof dLevel === 'number' ? dLevel.toFixed(1) : String(dLevel);
              const sStr = typeof sLevel === 'number' ? sLevel.toFixed(1) : String(sLevel);
              console.log(`[${timestamp}] Dopamine: ${dStr}% | Serotonin: ${sStr}% | State: ${bState}`);
              
              // Check for alerts (SPIKE DETECTION)
              if (typeof dLevel === 'number' && dLevel < 30) {
                console.log(`[${timestamp}] ⚠️  LOW DOPAMINE: ${dLevel.toFixed(1)}% - Risk of poor decisions`);
              }
              if (typeof sLevel === 'number' && sLevel < 40) {
                console.log(`[${timestamp}] ⚠️  LOW SEROTONIN: ${sLevel.toFixed(1)}% - Need break/rest`);
              }
              
              // SPIKE ALERT: Notify Orion when significant changes detected
              // (Check last spike and compare)
              const spikesData = await fs.readFile(SPIKES_FILE, 'utf8').catch(() => '');
              const spikes = spikesData.trim().split('\n').filter(Boolean);
              if (spikes.length > 0) {
                const lastSpike = JSON.parse(spikes[spikes.length - 1]);
                const lastTimestamp = new Date(lastSpike.timestamp).getTime();
                const timeSinceSpike = Date.now() - lastTimestamp;
                
                // If spike logged in last 2 minutes and high severity
                if (timeSinceSpike < 120000 && lastSpike.severity === 'HIGH') {
                  console.log(`[${timestamp}] 🚨 HIGH SEVERITY SPIKE DETECTED - NOTIFY ORION`);
                  console.log(`[${timestamp}] Trigger: ${lastSpike.trigger}`);
                  console.log(`[${timestamp}] Dopamine change: ${lastSpike.dopamine.change}%`);
                  if (lastSpike.cortisol) {
                    console.log(`[${timestamp}] Cortisol spike: ${lastSpike.cortisol.change}%`);
                  }
                }
              }
            } catch (error) {
              console.error('[DOPAMINE ERROR]', error.message);
            }
          }, 60000); // Every 60 seconds
          
          // Keep process alive
          process.on('SIGTERM', () => {
            console.log('[DOPAMINE] Received SIGTERM, shutting down...');
            process.exit(0);
          });
          break;
          
        default:
          console.log('Usage: node dopamine-tracker.js [status|trade <pnl>|budget <amount>|feedback [source]|spikes|reset|daemon]');
      }
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  })();
}
