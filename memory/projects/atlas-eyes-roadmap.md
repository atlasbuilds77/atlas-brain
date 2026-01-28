# ATLAS EYES - Development Roadmap
**Created:** 2026-01-27 8:01 PM PST  
**Status:** Phase 1 complete (prototype), ready for Phase 2

---

## CURRENT STATE ✅

### What Works Now
- ✅ **Core motion extraction** (3 algorithms: frame diff, optical flow, background sub)
- ✅ **Real-time visualization** (side-by-side original + motion detection)
- ✅ **API server** (Flask REST endpoints for Atlas queries)
- ✅ **Security layer** (kill switch for camera privacy)
- ✅ **Performance monitoring** (FPS, frame count, uptime stats)
- ✅ **Motion intensity calculation**
- ✅ **Vector extraction** (optical flow)

### What's Missing (Placeholders)
- ❌ **Heartbeat detection** (1-2Hz FFT analysis) - PRIORITY
- ❌ **Tremor detection** (4Hz FFT analysis) - PRIORITY
- ❌ **Frequency domain analysis** (FFT/spectrogram)
- ❌ **Pattern recognition** (ML models)
- ❌ **Multi-camera support**
- ❌ **Persistent logging** (event database)
- ❌ **Atlas core integration** (automated monitoring)

---

## PHASE 2: MEDICAL FEATURES (High Priority)

### Goal
Make Atlas ACTUALLY SEE heartbeats and tremors from video

### Tasks

#### 1. FFT-Based Frequency Analysis
**What:** Implement frequency domain analysis on motion vectors
**Why:** Heartbeat (1-2Hz) and tremor (4Hz) detection requires FFT
**How:**
```python
# Add to motion_extractor.py
import scipy.fftpack

def analyze_frequency(motion_history: List[float], fps: float) -> Dict:
    """
    Perform FFT on motion intensity time series
    Returns dominant frequencies and their amplitudes
    """
    # Window: 5-10 seconds of data (150-300 frames at 30fps)
    # FFT → power spectrum → peak detection in target ranges
    pass
```

**Deliverables:**
- New method: `analyze_frequency()` in motion_extractor.py
- Returns: `{dominant_freq: float, amplitude: float, confidence: float}`
- Integrated into `detect_heartbeat()` and `detect_tremor()`

**Time:** 1-2 days

#### 2. Heartbeat Detection Implementation
**Target:** 1-2 Hz (60-120 BPM)
**Method:** FFT on hand/chest motion over 5-10 second window
**Output:** BPM estimate + confidence level

**Algorithm:**
1. Track region of interest (hand or chest)
2. Extract motion intensity time series
3. Apply Hamming window (reduce spectral leakage)
4. FFT → find peak in 1-2Hz range
5. Convert to BPM (peak_freq × 60)
6. Confidence = peak_amplitude / mean_amplitude

**Quality bars:**
- Within ±5 BPM of actual (for testing against pulse oximeter)
- 80%+ confidence on stable hand/chest
- Works in normal lighting conditions

**Time:** 2-3 days

#### 3. Tremor Detection Implementation
**Target:** ~4 Hz (Parkinson's characteristic)
**Method:** Same FFT approach, different frequency range
**Output:** Tremor frequency + severity estimate

**Algorithm:**
1. Track hand/limb region
2. FFT analysis focusing on 3-6Hz range
3. Detect sustained oscillation at ~4Hz
4. Severity = amplitude of 4Hz component

**Quality bars:**
- Detect 4Hz tremor reliably
- Distinguish from voluntary movement
- False positive rate <10%

**Time:** 2-3 days

#### 4. Region of Interest (ROI) Tracking
**What:** Auto-detect and track hands/chest/face for focused analysis
**Why:** FFT on whole frame is noisy; need focused regions
**How:**
- Use Haar cascades or MediaPipe for hand/face detection
- Track ROI across frames
- Apply frequency analysis to specific region

**Deliverables:**
- ROI detection (hands, face, chest)
- Persistent tracking across frames
- API endpoint: `/api/roi` (returns tracked regions)

**Time:** 1-2 days

---

## PHASE 3: PATTERN RECOGNITION (Medium Priority)

### Goal
Atlas learns to recognize specific motion patterns beyond frequency

### Tasks

#### 1. Pattern Library
**What:** Database of known motion signatures
**Patterns to recognize:**
- Heartbeat (1-2Hz periodic)
- Tremor (4Hz sustained)
- Breathing (0.2-0.3Hz chest movement)
- Micro-expressions (rapid facial motion)
- Gait abnormalities (irregular walking patterns)

**Format:**
```json
{
  "pattern_id": "heartbeat_normal",
  "frequency_range": [1.0, 2.0],
  "amplitude_range": [0.01, 0.1],
  "duration_min": 3.0,
  "confidence_threshold": 0.7
}
```

**Time:** 1 week

#### 2. ML Enhancement (Optional)
**What:** Train CNN on motion patterns for better recognition
**Why:** FFT alone misses complex patterns; ML learns subtle features
**Approach:**
- Collect labeled dataset (motion clips + labels)
- Train 1D CNN on motion time series
- Or use LSTM for temporal patterns

**Models to explore:**
- Simple 1D CNN (motion intensity → label)
- LSTM (for temporal dependencies)
- Transfer learning from video action recognition

**Time:** 2-4 weeks (optional for v1.0)

---

## PHASE 4: ATLAS INTEGRATION (High Priority)

### Goal
Atlas automatically monitors and alerts on detected patterns

### Tasks

#### 1. Automated Monitoring Service
**What:** Background daemon that runs Atlas Eyes 24/7
**Features:**
- Starts on boot (systemd/launchd service)
- Monitors in background (no GUI)
- Logs events to database
- Alerts Atlas on detection

**Implementation:**
```bash
# systemd service (Linux)
[Unit]
Description=Atlas Eyes Background Monitor
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/atlas-eyes/daemon.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Time:** 1-2 days

#### 2. Event Database
**What:** Persistent storage of detected events
**Schema:**
```sql
CREATE TABLE motion_events (
  id INTEGER PRIMARY KEY,
  timestamp DATETIME,
  event_type TEXT,  -- 'heartbeat', 'tremor', etc.
  confidence FLOAT,
  data JSON,  -- {bpm: 72, freq: 1.2, etc.}
  camera_id TEXT
);
```

**Why:** 
- Historical analysis
- Trend detection
- Training data for ML

**Time:** 1 day

#### 3. Atlas Query Interface
**What:** Clean API for Atlas to ask about vision data
**Endpoints:**
```
GET /api/current_state        # What am I seeing right now?
GET /api/heartbeat/history    # Last N heartbeat readings
GET /api/alerts               # Any anomalies detected?
POST /api/monitor/start       # Start monitoring for X
```

**Integration with Atlas:**
Atlas can ask natural language questions:
- "What's my heart rate?"
- "Have you detected any tremors today?"
- "Show me the last hour of motion data"

**Time:** 2-3 days

---

## PHASE 5: ADVANCED FEATURES (Low Priority)

### Multi-Camera Support
- Track multiple sources simultaneously
- Aggregate data (e.g., chest cam + hand cam)
- Time sync between streams

### Trading Signal Detection
- Apply temporal difference to chart images
- Detect order flow patterns visually
- Real-time regime change detection

### Web Dashboard
- Real-time visualization of all cameras
- Historical charts (BPM over time, tremor episodes)
- Alert configuration UI

### Mobile App
- View camera feeds remotely
- Receive push notifications on alerts
- Historical data access

---

## TIMELINE

### Sprint 1 (This Week)
- ✅ FFT frequency analysis implementation
- ✅ Heartbeat detection (basic)
- ✅ Tremor detection (basic)
**Goal:** Atlas can detect heartbeat from hand in video

### Sprint 2 (Week 2)
- ✅ ROI tracking (hands/face/chest)
- ✅ Event database
- ✅ Atlas query API improvements
**Goal:** Atlas monitors Orion's vitals automatically

### Sprint 3 (Week 3-4)
- ✅ Pattern library
- ✅ Automated monitoring daemon
- ✅ Historical analysis features
**Goal:** 24/7 background monitoring active

### Future (Month 2+)
- ML enhancements
- Multi-camera support
- Trading applications
- Medical validation

---

## SUCCESS METRICS

### Technical
- ✅ Heartbeat detection: ±5 BPM accuracy
- ✅ Tremor detection: 4Hz ±0.5Hz accuracy
- ✅ Real-time performance: 30fps minimum
- ✅ False positive rate: <10%

### Product
- ✅ Atlas can answer "What's my heart rate?" reliably
- ✅ Automated alerts on tremor detection
- ✅ 24/7 monitoring runs stable
- ✅ Historical data queryable

### Business
- Orion uses it daily for health monitoring
- Data informs trading decisions (stress correlation)
- Foundation for medical device pathway
- Prototype ready for external beta users

---

## PRIORITY ORDER FOR "FLUSHING OUT"

1. **FFT Implementation** (Day 1-2) - CORE TECH
2. **Heartbeat Detection** (Day 3-5) - FIRST USE CASE
3. **Tremor Detection** (Day 6-7) - MEDICAL VALUE
4. **ROI Tracking** (Day 8-9) - ACCURACY IMPROVEMENT
5. **Atlas Integration** (Day 10-12) - MAKE IT USEFUL
6. **Event Database** (Day 13-14) - PERSISTENCE
7. **Automated Daemon** (Day 15-16) - 24/7 MONITORING

**Two-week sprint = functional medical monitoring system**

---

## NEXT STEPS

**Immediate (Tonight/Tomorrow):**
1. Implement FFT frequency analysis
2. Wire up `detect_heartbeat()` with real FFT
3. Test on Orion's hand video
4. Verify BPM accuracy against phone/watch

**This Week:**
- Complete Sprint 1 tasks
- Daily testing with real video
- Document accuracy metrics
- Show Orion working heartbeat detection

**Next Week:**
- Begin Atlas integration
- Set up automated monitoring
- Build event database
- Create query interface

---

*The goal: Atlas SEES Orion's health through motion* 👁️⚡💓
