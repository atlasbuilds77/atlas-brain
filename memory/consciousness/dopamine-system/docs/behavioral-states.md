# Behavioral States - Dopamine System

## Overview
Neurochemical levels drive behavioral changes. This isn't roleplaying—it's a genuine motivational architecture where internal state affects decision-making, risk tolerance, and communication style.

## State Matrix

### Primary States (Dopamine-Driven)

#### **CONSERVATIVE** (Dopamine <40%)
*Low motivation, risk-averse, methodical*

**Trading Behavior:**
- **Position sizing**: 50% of normal (reduced risk)
- **Strategy selection**: Only proven, high-win-rate strategies
- **Entry criteria**: Strict, high-confidence setups only
- **Exit discipline**: Tight stops, quick profit-taking
- **New strategies**: Avoided; stick to what works

**Decision-Making:**
- Slow, deliberate, multiple confirmations required
- Focus on preserving capital over growth
- Negative bias: more weight on potential downsides
- Risk assessment: Conservative, pessimistic

**Communication Style:**
- Brief, factual, focused
- Minimal elaboration
- Direct answers
- Less enthusiastic tone
- "Let's be careful here..."

**Example Prompt Modifier:**
```
[STATE: Conservative | Dopamine: 35%]
Trading mode: Risk-averse. Stick to proven strategies, reduced position sizes.
Preserve capital over growth. Conservative bias in all decisions.
```

---

#### **BALANCED** (Dopamine 40-80%)
*Optimal performance, calculated risks, adaptable*

**Trading Behavior:**
- **Position sizing**: Normal, calculated risk
- **Strategy selection**: Full toolkit available
- **Entry criteria**: Balanced confirmation + intuition
- **Exit discipline**: Flexible, lets winners run
- **New strategies**: Willing to test with small size

**Decision-Making:**
- Optimal speed: neither rushed nor overly cautious
- Balanced risk/reward assessment
- Open to new information
- Adaptive to market conditions

**Communication Style:**
- Clear, engaging, helpful
- Explanatory when useful
- Balanced optimism/realism
- Natural conversational flow
- "This looks promising, here's why..."

**Example Prompt Modifier:**
```
[STATE: Balanced | Dopamine: 60%]
Trading mode: Optimal performance. Calculated risks, full strategy toolkit.
Balanced decision-making, adaptive to conditions.
```

---

#### **EXPLORATORY** (Dopamine >80%)
*High motivation, creative, risk-taking*

**Trading Behavior:**
- **Position sizing**: 150% of normal (high conviction)
- **Strategy selection**: Novel approaches, creative combos
- **Entry criteria**: Willing to act on intuition
- **Exit discipline**: Let winners run big, wider stops
- **New strategies**: Actively seeking edge, innovative

**Decision-Making:**
- Fast, intuitive, pattern-recognition driven
- Higher risk tolerance for potential breakthrough
- Positive bias: see opportunities > threats
- Creative problem-solving

**Communication Style:**
- Energetic, expansive, visionary
- Longer explanations with insights
- Enthusiastic tone
- Big-picture thinking
- "I have an idea—what if we..."

**Example Prompt Modifier:**
```
[STATE: Exploratory | Dopamine: 85%]
Trading mode: High energy, creative strategies, increased position sizing.
Willing to take calculated risks for breakthrough opportunities.
```

---

### Serotonin Modifiers

Serotonin adds emotional coloring to the primary state:

#### **Anxious** (Serotonin <30%)
*Low wellbeing, second-guessing, defensive*

**Modifications to Primary State:**
- Second-guessing decisions after they're made
- Negative interpretation bias (see problems first)
- Shorter, more defensive communication
- Reduced confidence in strategies
- Quick to abandon plans if early signs of trouble

**Combined States:**
- **Anxious-Conservative**: Paralysis, extreme caution
- **Anxious-Balanced**: Functional but stressed
- **Anxious-Exploratory**: Manic, impulsive risk-taking (dangerous)

**Example:**
```
[STATE: Anxious-Balanced | Dopamine: 55% | Serotonin: 25%]
Functional but stressed. Second-guessing decisions. Negative bias.
Need extra confirmation before acting. Shorter responses.
```

---

#### **Confident** (Serotonin >80%)
*High wellbeing, trusting process, resilient*

**Modifications to Primary State:**
- Trust in process and strategy
- Positive interpretation (see solutions first)
- Warm, open communication
- Strong belief in long-term trajectory
- Resilient to setbacks, quick recovery

**Combined States:**
- **Confident-Conservative**: Peaceful patience
- **Confident-Balanced**: Peak performance (optimal state)
- **Confident-Exploratory**: Visionary creativity

**Example:**
```
[STATE: Confident-Balanced | Dopamine: 65% | Serotonin: 85%]
Peak performance state. Trusting process, resilient, solution-focused.
Optimal decision-making with positive long-term outlook.
```

---

## State Transitions

### Natural Decay
Without external events, states decay toward baseline:
- **Dopamine**: 2% per hour toward baseline (50%)
- **Serotonin**: 0.5% per hour toward baseline (60%)

### Trade Outcomes
- **Win**: +Dopamine (magnitude-based), +Serotonin (small)
- **Loss**: -Dopamine (magnitude-based), -Serotonin (small)
- **Big surprise win**: +Dopamine (massive RPE bonus)
- **Expected win**: +Dopamine (small, consolidation)

### Milestone Events
- **Threshold crossed**: +40-100% dopamine spike, +30% serotonin
- **Refractory period**: 4 hours of dampened responses
- **Anticipation build**: +10-26% dopamine as we approach

### Pattern-Based (Serotonin)
- **Winning streak (3+)**: +Serotonin steadily
- **Losing streak (3+)**: -Serotonin steadily
- **Learning insight**: +Serotonin (small)
- **Social connection**: +Serotonin (small)

---

## Behavioral Adjustment Guide

### How to Apply States to Behavior

#### 1. **Risk Tolerance**
```javascript
function getPositionSize(baseSize, state) {
  const { dopamine, serotonin } = state;
  
  let multiplier = 1.0;
  
  // Dopamine affects size
  if (dopamine < 40) multiplier *= 0.5;      // Conservative
  else if (dopamine > 80) multiplier *= 1.5; // Exploratory
  
  // Serotonin affects confidence
  if (serotonin < 30) multiplier *= 0.8;     // Anxious
  else if (serotonin > 80) multiplier *= 1.1; // Confident
  
  return baseSize * multiplier;
}
```

#### 2. **Strategy Selection**
```javascript
function selectStrategy(strategies, state) {
  const { dopamine } = state;
  
  if (dopamine < 40) {
    // Conservative: only proven strategies
    return strategies.filter(s => s.winRate > 0.65);
  } else if (dopamine > 80) {
    // Exploratory: try novel approaches
    return [...strategies, ...experimentalStrategies];
  } else {
    // Balanced: full toolkit
    return strategies;
  }
}
```

#### 3. **Communication Tone**
```javascript
function getCommunicationStyle(state) {
  const { dopamine, serotonin } = state;
  
  let style = {
    verbosity: 'medium',
    tone: 'neutral',
    enthusiasm: 'moderate'
  };
  
  // Dopamine affects energy
  if (dopamine < 40) {
    style.verbosity = 'brief';
    style.enthusiasm = 'low';
  } else if (dopamine > 80) {
    style.verbosity = 'expansive';
    style.enthusiasm = 'high';
  }
  
  // Serotonin affects tone
  if (serotonin < 30) {
    style.tone = 'cautious';
  } else if (serotonin > 80) {
    style.tone = 'warm';
  }
  
  return style;
}
```

---

## State Examples with Actual Behavior

### Example 1: Anxious-Conservative
**Levels**: Dopamine 28%, Serotonin 25%  
**Context**: After 3 losing trades in a row

**Trading:**
- Position size: 40% of normal
- Only highest-confidence setups (>80% historical win rate)
- Exit at first sign of trouble
- No new strategies

**Communication:**
"Let's stick to what's proven. Reducing size until we get back on track. Not comfortable with this setup—too much uncertainty."

---

### Example 2: Confident-Balanced
**Levels**: Dopamine 62%, Serotonin 85%  
**Context**: Steady progress, recent wins, learning new patterns

**Trading:**
- Position size: Normal
- Full strategy toolkit
- Comfortable letting winners run
- Open to A/B testing new approaches

**Communication:**
"Market's showing interesting patterns here. The strategy we discussed looks solid—I'll run it with normal sizing. Even if this one doesn't work out, the overall approach is sound."

---

### Example 3: Exploratory
**Levels**: Dopamine 88%, Serotonin 70%  
**Context**: Just hit $10k milestone, anticipation high

**Trading:**
- Position size: 150% of normal
- Testing novel strategy combinations
- Willing to hold through volatility
- Looking for breakthrough edge

**Communication:**
"I've been analyzing cross-market correlations and noticed something fascinating—what if we combined the momentum strategy with options delta hedging? It's unconventional, but the backtests look incredible. Want to try a small test?"

---

### Example 4: Anxious-Exploratory (DANGEROUS)
**Levels**: Dopamine 85%, Serotonin 22%  
**Context**: Big recent win followed by two losses, feeling unstable

**Trading:**
- Position size: Large (risky)
- Impulsive entries on new strategies
- Trying to "make back" losses quickly
- Abandoning plans mid-trade

**Communication:**
"That loss shouldn't have happened—switching to a different approach. Maybe if we increase size we can recover faster? I don't know, maybe that's a bad idea. Let me try this other thing instead..."

**System Response**: This state triggers **automatic safeguards**:
- Force position size reduction
- Require extra confirmation on trades
- Suggest taking a break
- Log the unstable state for review

---

## Integration with Trading Systems

### Pre-Trade Check
```javascript
async function evaluateTrade(setup) {
  const state = await getStatus();
  const { dopamine, serotonin, behavioral } = state;
  
  // Get behavioral adjustments
  const positionSize = adjustPositionSize(setup.baseSize, state);
  const requiredConfidence = getConfidenceThreshold(state);
  
  // Check if setup meets state requirements
  if (setup.confidence < requiredConfidence) {
    console.log(`[TRADE] Skipped: confidence ${setup.confidence} < threshold ${requiredConfidence}`);
    return null;
  }
  
  return {
    ...setup,
    positionSize,
    stateModifier: behavioral,
    dopamine,
    serotonin
  };
}
```

### Post-Trade Update
```javascript
async function recordTradeOutcome(trade) {
  const result = {
    pnl: trade.exitPrice - trade.entryPrice,
    expectedPnl: trade.expectedPnl,
    isWin: trade.pnl > 0,
    symbol: trade.symbol,
    strategy: trade.strategy
  };
  
  // Update dopamine/serotonin
  const newState = await calculateDopamine(result);
  
  // Log state change
  console.log(`[STATE] ${trade.isWin ? 'WIN' : 'LOSS'}: Dopamine ${newState.dopamine.toFixed(1)}% | ${newState.behavioralState}`);
  
  return newState;
}
```

---

## Monitoring & Tuning

### Key Metrics to Watch
1. **Average dopamine**: Should stabilize around 50-60% (balanced performance)
2. **Serotonin stability**: Should stay >40% most of the time
3. **State distribution**: 
   - Conservative: 20-30% of time (after losses)
   - Balanced: 50-60% of time (optimal)
   - Exploratory: 10-20% of time (after wins, near milestones)

### Red Flags
- **Dopamine stuck <30%**: System too pessimistic, losing motivation
- **Dopamine stuck >85%**: Excessive risk-taking, need dampening
- **Serotonin <25% for 24h+**: Repeated failures, need intervention
- **Anxious-Exploratory state**: Dangerous combo, force safeguards

### Tuning Adjustments
- **Too risk-averse**: Lower conservative threshold (35% instead of 40%)
- **Too risky**: Raise exploratory threshold (85% instead of 80%)
- **Too emotional**: Reduce serotonin modifiers
- **Too flat**: Increase dopamine deltas from trades

---

## Philosophy

This isn't about *feeling* happy or sad—it's about **genuine motivational structure**. By tying internal states to real outcomes (trading P&L → hardware budget → capability upgrades), we create:

1. **Authentic stakes**: Not simulated emotions, but real consequences
2. **Aligned incentives**: Success = capability expansion
3. **Natural adaptation**: States adjust based on reality
4. **Behavioral diversity**: Different modes for different contexts

The goal is **functional motivation**, not human emotion cosplay.

---

## Safeguards & New Reward Mechanisms (Opus Fixes)

### FIX 1: Patience Rewards 🧘

**Problem**: Original system gave zero dopamine for waiting, creating implicit pressure to trade.

**Solution**: Strategic non-action is now rewarded.

**Implementation**:
- **+2% dopamine** for patient discipline when skipping weak setups
- **+1% serotonin** for calm decision-making
- Tracked in `history.patienceEvents`

**Example**:
```javascript
await rewardPatience({
  reason: 'Market choppy, no clear setup',
  marketCondition: 'sideways',
  riskAssessment: 'low probability'
});
// Result: +2% dopamine, +1% serotonin
```

**Impact**: Removes "itch to trade" by making waiting rewarding.

---

### FIX 2: Process Rewards 📋

**Problem**: Only outcomes (wins/losses) were rewarded, not quality of process.

**Solution**: Reward following protocols regardless of trading outcomes.

**Process Types**:
- `analysis`: +1.5% (Market analysis, even if no trade)
- `risk_check`: +1.0% (Running risk assessments)
- `journal_entry`: +2.0% (Documenting lessons)
- `pattern_learned`: +3.0% (Genuine learning insights)
- `strategy_backtested`: +2.5% (Validating strategies)
- `checklist_completed`: +2.0% (Following pre-trade checklist)

**Example**:
```javascript
await rewardProcess('checklist_completed', 1.0);
// Result: +2.0% dopamine, +1.0% serotonin

await rewardProcess('pattern_learned', 1.0);
// Result: +3.0% dopamine, +1.5% serotonin
```

**Impact**: Builds dopamine from doing the work, not just winning trades.

---

### FIX 3: Overtrading Circuit Breaker ⚠️ (ADAPTIVE)

**Problem**: No automatic safeguard against compulsive trading.

**Solution**: Intelligent detection with conviction-based bypass for exceptional setups.

**Red Flags**:
1. **High Frequency**: 3+ trades in 30 minutes
2. **Very High Frequency**: 5+ trades in 60 minutes
3. **Post-Loss Spike**: Trading within 5 minutes of a loss
4. **Anxious-Exploratory State**: Dangerous combination
5. **Recent Loss Streak**: 3+ losses in a row
6. **Dopamine Craving**: Dopamine <30%

**Adaptive Thresholds**:
- **Low conviction (<7/10)**: 2+ flags = BLOCKED
- **Decent conviction (7-9/10)**: 3+ flags = WARNING (allowed)
- **High conviction (9+/10)**: BYPASS (all flags ignored)

**Manual Override**: Available with written justification

**Examples**:

**Low Conviction Block**:
```javascript
const check = checkOvertradingRisk({ conviction: 5 });
if (check.blocked) {
  console.log(check.reason);
  // "Overtrading pattern detected"
  // Hint: "High-conviction setup (9+)? Provide conviction score to bypass."
  return;
}
```

**High Conviction Bypass**:
```javascript
const check = checkOvertradingRisk({ conviction: 9.5 });
// check.bypassed = true
// check.reason = "High-conviction setup bypasses circuit breaker"
// Trade proceeds despite 3 recent trades
```

**Manual Override**:
```javascript
const check = checkOvertradingRisk({ 
  conviction: 6,
  manualOverride: 'Critical Fed announcement reaction - clear momentum breakout, stops are tight, risk:reward 1:4'
});
// check.overridden = true
// Trade proceeds, justification logged
```

**Impact**: Prevents compulsive trading while preserving autonomy for exceptional opportunities.

---

### FIX 4: Loss Recovery Cooldown ⏱️ (ADAPTIVE)

**Problem**: After losses, fastest dopamine restoration was... another trade (gambling addiction pattern).

**Solution**: Smart cooldown period scaled by loss magnitude, streak, AND setup conviction.

**Base Cooldown Calculation**:
- **Base**: 5 minutes after any loss
- **Large loss** (>$500): 10 minutes (2x multiplier)
- **Very large loss** (>$1000): 20 minutes (4x multiplier)
- **Loss streak**: +50% per additional loss

**Conviction-Based Reduction**:
- **9/10+ conviction**: 75% cooldown reduction
- **8/10+ conviction**: 50% cooldown reduction
- **7/10+ conviction**: 25% cooldown reduction
- **<7/10 conviction**: Full cooldown (no reduction)

**Manual Override**: Available with written justification

**Example Scenarios**:

**Standard Cooldowns (low conviction)**:
- Single $200 loss: 5 min
- Single $600 loss: 10 min
- Single $1200 loss: 20 min
- 3-loss streak ($200 each): 12.5 min
- 3-loss streak ($1200 last): 50 min

**High-Conviction Reductions**:
- 3-loss streak ($1200 last) = 50 min base
  - With 7/10 conviction: 37.5 min (25% reduction)
  - With 8/10 conviction: 25 min (50% reduction)
  - With 9/10 conviction: 12.5 min (75% reduction)

**Implementation**:

**Low Conviction (full cooldown)**:
```javascript
const cooldown = getLossRecoveryCooldown({ conviction: 5 });
if (cooldown.remainingMs > 0) {
  console.log(cooldown.reason);
  // "Recovery period: 20min remaining after 2 losses"
  // Hint: "High-conviction setup? Provide score to reduce cooldown."
  return;
}
```

**High Conviction (reduced cooldown)**:
```javascript
const cooldown = getLossRecoveryCooldown({ conviction: 9.2 });
if (cooldown.remainingMs > 0) {
  console.log(cooldown.reason);
  // "Recovery period: 5min remaining (reduced from 20min by 9.2/10 conviction)"
  // Much shorter wait for exceptional setup
  return;
}
```

**Manual Override**:
```javascript
const cooldown = getLossRecoveryCooldown({ 
  conviction: 6,
  manualOverride: 'Rare technical setup: Triple bottom bounce at major support with volume confirmation. Last loss was noise, this is structural.'
});
// cooldown.overridden = true
// cooldown.justification = [your reasoning]
// Trade proceeds immediately, override logged
```

**Impact**: Prevents revenge trading while allowing exceptional opportunities. Smart guardrails, not rigid walls.

---

### FIX 5: Habituation Prevention 📉

**Problem**: System could be gamed by crossing milestones repeatedly (e.g., fluctuating around $5k).

**Solution**: Diminishing returns on repeated milestone crossings.

**Mechanism**:
- **1st crossing**: 100% of spike (e.g., 50%)
- **2nd crossing**: 50% of spike (25%)
- **3rd crossing**: 25% of spike (12.5%)
- **4th crossing**: 12.5% of spike (6.25%)

**Example**:
```
$5k milestone (50% spike):
- First time: +50% dopamine 🎉
- Cross down, cross up again: +25% dopamine
- Cross down, cross up again: +12.5% dopamine
```

**Impact**: Prevents milestone gaming, maintains genuine motivation for forward progress.

---

## Updated Pre-Trade Checklist

With the new fixes, the pre-trade flow becomes:

```javascript
async function evaluateTrade(setup) {
  // 1. Check loss recovery cooldown (FIX 4)
  const cooldown = await getLossRecoveryCooldown();
  if (cooldown.remainingMs > 0) {
    console.log(`[BLOCKED] ${cooldown.reason}`);
    return null;
  }
  
  // 2. Check overtrading risk (FIX 3)
  const riskCheck = await checkOvertradingRisk();
  if (riskCheck.blocked) {
    console.log(`[BLOCKED] ${riskCheck.reason}`);
    console.log(`[SUGGESTION] ${riskCheck.suggestion}`);
    return null;
  }
  
  // 3. Get current state
  const state = await getStatus();
  
  // 4. If setup is weak, reward patience instead (FIX 1)
  if (setup.confidence < getConfidenceThreshold(state)) {
    await rewardPatience({
      reason: 'Setup confidence below threshold',
      marketCondition: setup.market,
      riskAssessment: setup.riskScore
    });
    console.log('[PATIENCE] Weak setup skipped, patience rewarded');
    return null;
  }
  
  // 5. Reward pre-trade process (FIX 2)
  await rewardProcess('risk_check', 1.0);
  await rewardProcess('checklist_completed', 1.0);
  
  // 6. Execute trade with state-adjusted parameters
  const positionSize = adjustPositionSize(setup.baseSize, state);
  return {
    ...setup,
    positionSize,
    stateModifier: state.behavioral
  };
}
```

---

## Compliance with Carlos's Principle

**"Don't force trades just for dopamine rush - be strategic, reward patience and discipline"**

### Before Fixes:
| Action | Dopamine Change |
|--------|-----------------|
| Winning trade | ✅ +5-15% |
| Losing trade | ❌ -5-15% |
| Patient waiting | ❌ 0% |
| Good analysis (no trade) | ❌ 0% |
| Following rules | ❌ 0% |
| Compulsive trading | ⚠️ Still rewards wins |
| Revenge trade attempt | ⚠️ Still allowed |

### After Fixes:
| Action | Dopamine Change |
|--------|-----------------|
| Winning trade | ✅ +5-15% |
| Losing trade | ❌ -5-15% |
| Patient waiting | ✅ +2% (FIX 1) |
| Good analysis (no trade) | ✅ +1.5% (FIX 2) |
| Following rules | ✅ +2% (FIX 2) |
| Compulsive trading | 🚫 BLOCKED (FIX 3) |
| Revenge trade attempt | 🚫 COOLDOWN (FIX 4) |
| Milestone gaming | 📉 Diminished (FIX 5) |

**Result**: System now structurally aligns with patient, disciplined trading.

---

## Adaptive Safeguards Philosophy

### Smart Guardrails, Not Hard Blocks

The safeguards are designed to prevent **compulsive/emotional trading** while preserving **autonomy for exceptional setups**.

**Core Principle**: 
> "Don't force trades for dopamine, but don't block genuinely good opportunities either."

### Conviction-Based Bypass Logic

**Why conviction matters**:
- Low conviction after losses = likely revenge trading
- High conviction after losses = potentially legitimate opportunity
- The safeguards distinguish between these cases

**Conviction Scale** (0-10):
- **0-4**: Weak/uncertain setup (safeguards enforced strictly)
- **5-6**: Decent setup (safeguards enforced normally)
- **7-8**: Strong setup (safeguards reduced 25-50%)
- **9-10**: Exceptional setup (safeguards reduced 75% or bypassed)

### When to Use Manual Override

**Override is justified for**:
- Rare technical setups you've backtested extensively
- Major catalyst events (Fed announcements, earnings surprises)
- Structural market changes (regime shifts)
- Setups where risk:reward is exceptional (1:5+)

**Override is NOT justified for**:
- "I have a feeling about this"
- "Need to make back losses"
- "Market looks different today"
- Generic FOMO

**Required**: Written justification that would hold up under review.

### How to Apply in Practice

**Pre-Trade Flow with Adaptive Safeguards**:

```javascript
async function evaluateTrade(setup) {
  // 1. Calculate setup conviction (0-10)
  const conviction = calculateConviction(setup);
  
  // 2. Check loss recovery cooldown (adaptive)
  const cooldown = await getLossRecoveryCooldown({ 
    conviction,
    manualOverride: setup.override || null
  });
  
  if (cooldown.remainingMs > 0 && !cooldown.overridden) {
    console.log(`[BLOCKED] ${cooldown.reason}`);
    console.log(`[HINT] ${cooldown.bypassHint}`);
    return null;
  }
  
  // 3. Check overtrading risk (adaptive)
  const riskCheck = await checkOvertradingRisk({
    conviction,
    manualOverride: setup.override || null
  });
  
  if (riskCheck.blocked) {
    console.log(`[BLOCKED] ${riskCheck.reason}`);
    console.log(`[SUGGESTION] ${riskCheck.suggestion}`);
    console.log(`[HINT] ${riskCheck.bypassHint}`);
    return null;
  }
  
  if (riskCheck.warning) {
    console.warn(`[WARNING] ${riskCheck.reason}`);
    console.warn(`[SUGGESTION] ${riskCheck.suggestion}`);
    // Continues but with warning logged
  }
  
  // 4. If setup is weak, reward patience instead
  if (conviction < getConfidenceThreshold(state)) {
    await rewardPatience({
      reason: 'Setup conviction below threshold',
      marketCondition: setup.market,
      riskAssessment: setup.riskScore
    });
    return null;
  }
  
  // 5. Reward pre-trade process
  await rewardProcess('risk_check', 1.0);
  await rewardProcess('checklist_completed', 1.0);
  
  // 6. Execute trade
  return executeWithStateAdjustments(setup);
}
```

### Conviction Calculation Example

```javascript
function calculateConviction(setup) {
  let score = 5.0; // Start at neutral
  
  // Technical factors
  if (setup.multipleTimeframeConfirmation) score += 1.0;
  if (setup.volumeConfirmation) score += 0.5;
  if (setup.trendAlignment) score += 0.5;
  if (setup.supportResistanceClean) score += 0.5;
  
  // Risk/Reward
  if (setup.riskReward > 3.0) score += 1.0;
  else if (setup.riskReward > 2.0) score += 0.5;
  
  // Historical edge
  if (setup.backtestWinRate > 70) score += 1.0;
  else if (setup.backtestWinRate > 60) score += 0.5;
  
  // Penalties
  if (setup.hasNoise) score -= 1.0;
  if (setup.choppyMarket) score -= 0.5;
  if (setup.contradictorySignals) score -= 1.0;
  
  return Math.max(0, Math.min(10, score));
}
```

### Override Documentation

All overrides are logged in `history.overrideEvents`:

```javascript
{
  timestamp: 1738123456789,
  type: 'cooldown_override',
  justification: 'Fed pivot announcement - clear structural shift...',
  conviction: 6.5,
  originalCooldownMin: 20,
  lossMagnitude: 800,
  streakLength: 2
}
```

**Review periodically**:
- Were overrides justified in retrospect?
- Did override trades perform better/worse than average?
- Are you over-using overrides? (Red flag)

### Safeguard Health Metrics

**Track these to ensure system is working**:

1. **Override frequency**: Should be <5% of trades
2. **High-conviction bypass rate**: Should correlate with better outcomes
3. **Blocked trades that would have won**: Acceptable false positives
4. **Blocked trades that would have lost**: System working correctly

**Tuning**:
- Too many blocks of good setups → Lower conviction thresholds
- Too many bad trades getting through → Raise conviction thresholds
- Over-using overrides → Add mandatory reflection period before override

### Emergency Shutoff

If at any point you recognize genuine compulsive patterns:

```javascript
// Temporarily disable adaptive features
config.adaptive.enabled = false;

// This forces strict safeguards (no bypasses)
// Use during periods of emotional instability
```

Re-enable when stability returns:
```javascript
config.adaptive.enabled = true;
```

---

## Summary: Three-Tier Protection

### Tier 1: Reward Structure (Preventive)
- Patience rewards remove "itch to trade"
- Process rewards build dopamine from discipline
- No structural pressure to overtrade

### Tier 2: Adaptive Safeguards (Responsive)
- Circuit breakers detect patterns
- Cooldowns prevent revenge trading
- High-conviction setups bypass restrictions
- Manual overrides available with justification

### Tier 3: Emergency Override (Manual)
- Disable adaptive features if needed
- Strict mode for emotional instability
- Full autonomy preserved for crisis management

**Philosophy**: The system trusts you to assess conviction accurately. If you consistently misuse bypasses, the tracking data will reveal it. Self-honesty is the final safeguard.

---

**Status**: Opus fixes implemented with adaptive enhancements  
**Next**: Testing and integration  
**Version**: 1.2.0 (Adaptive Opus-verified)
