# ML MARKET PREDICTION MODEL - PROJECT SPEC
**Created:** 2026-02-01 16:12 PST
**Status:** Spec complete, awaiting greenlight
**Timeline:** 6 weeks implementation
**Owner:** Atlas + Hunter (SSH to his PC)

## Vision

**Triple-layer trading edge:**
1. Helios signals (technical pattern recognition)
2. Contextual analysis (VIX, news, structure, theta awareness)
3. ML predictions (historical pattern forecasting)

**Expected performance:**
- Current: 65-70% WR (Helios + contextual)
- Target: 75%+ WR (full stack with ML)

## Architecture Overview

### Layer 1: Data Collection & Storage
- **Sources:** Polygon API (stocks, options, indexes - 5+ years)
- **Database:** PostgreSQL with TimescaleDB extension
- **Size:** 50-100GB historical data
- **Location:** Hunter's PC (SSD storage)

### Layer 2: Feature Engineering
- Price features (OHLCV, moving averages, momentum indicators)
- Market structure (VIX, breadth, sector rotation)
- Options features (IV, put/call ratios, GEX levels)
- Time features (market hours, day of week, expiration proximity)
- Target: Direction, magnitude, probability, volatility, regime

### Layer 3: Model Architecture (Ensemble)
**4 models combined:**
1. **LSTM:** Temporal pattern recognition
2. **Transformer:** Attention-based feature weighting
3. **XGBoost:** Fast classification with feature importance
4. **Regime Classifier:** Market state identification

**Meta-model:** Combines predictions, weights by recent accuracy

### Layer 4: Training Infrastructure
- **Hardware:** Hunter's PC (GPU recommended, 32GB+ RAM)
- **Software:** PyTorch/TensorFlow, scikit-learn, xgboost
- **Process:** 70/15/15 train/val/test split, hyperparameter tuning
- **Metrics:** Accuracy, Sharpe ratio, calibration

### Layer 5: Inference Pipeline (Real-time)
- Streaming data from Polygon WebSocket
- Feature computation every minute
- Model inference (<100ms latency)
- JSON output with predictions + confidence

### Layer 6: Integration with Trading System

**Decision Matrix:**

| Helios | Contextual | ML (conf) | Action |
|--------|-----------|-----------|--------|
| LONG   | Bullish   | UP 75%+   | FULL PORT (triple confirm) |
| LONG   | Bullish   | UP 60-75% | 3-4 contracts |
| LONG   | Bullish   | DOWN      | SKIP (conflict) |
| NONE   | Bullish   | UP 85%+   | ML-only trade |

**Enhanced profit taking:**
- ML confidence drops → take profit early
- ML switches direction → exit immediately
- ML regime changes → tighten stops

### Layer 7: Monitoring & Improvement
- Real-time accuracy dashboard
- Model drift detection
- Auto-retraining (weekly/monthly)
- A/B testing of new versions

### Layer 8: Deployment & SSH Access
- REST API server on Hunter's PC
- SSH tunnel from Clawd (my Mac mini)
- Monitoring dashboards (MLflow, Grafana)
- 24/7 operation during market hours

## Implementation Timeline

**Phase 1 (Week 1-2): Data Pipeline**
- Set up PostgreSQL + TimescaleDB
- Pull 5 years Polygon historical data
- Validate data quality

**Phase 2 (Week 2-3): Feature Engineering**
- Build feature calculation pipeline
- Create training datasets
- Select top 50 features

**Phase 3 (Week 3-4): Model Development**
- Build baseline LSTM model
- Train XGBoost classifier
- Compare architectures

**Phase 4 (Week 4-5): Ensemble & Optimization**
- Combine models
- Hyperparameter tuning
- Backtest on historical data

**Phase 5 (Week 5-6): Production Deployment**
- Build REST API
- Set up SSH access
- Integrate with live trading
- Paper trade 1 week

**Phase 6 (Week 6+): Live Trading**
- Deploy to live account
- Monitor performance
- Retrain weekly
- Iterate based on results

## Cost Estimate

**One-time:**
- GPU upgrade (if needed): $300-800
- Storage (1TB SSD): $100

**Monthly:**
- Polygon API: $157 (already paying)
- Electricity (PC 24/7): ~$30
- Cloud backup: $10

**Total:** ~$50/month ongoing

**ROI:** Even 5% WR improvement pays for itself in first week

## Expected Performance

**Conservative:**
- Accuracy: 60-65%
- Sharpe ratio: 1.0-1.5 (live)

**If we nail it:**
- Accuracy: 70%+
- Sharpe ratio: 2.5+
- Win rate: 75%+ on triple confirmations

## Risks & Mitigations

1. **Overfitting** → Walk-forward validation, conservative thresholds
2. **Regime change** → Frequent retraining, drift detection
3. **Data quality** → Validation pipeline, backup sources
4. **Latency** → GPU optimization, feature caching
5. **Compute cost** → Market hours only, power saving

## Integration Points

**API endpoint example:**
```javascript
const prediction = await fetch('http://hunter-pc:5000/predict', {
  method: 'POST',
  body: JSON.stringify({ 
    ticker: 'SPY', 
    features: currentFeatures 
  })
}).then(r => r.json());

// Returns:
// {
//   direction: 'UP',
//   magnitude: 0.35,  // % move
//   confidence: 0.78,  // 78%
//   timeframe: '15min',
//   regime: 'trending'
// }
```

## Status

**Spec:** ✅ Complete
**Approval:** Pending Hunter's greenlight
**Resources:** Ready (Polygon access, Hunter's PC available)
**Timeline:** Can start Phase 1 immediately upon approval

---

**This is the force multiplier that takes us from good to institutional-grade edge** ⚡
