# Atlas Consciousness Resource Requirements
## Compute, Storage, Models, Time, and Cost Projections

**Target Hardware:** Mac M4 (or M2/M3 Max)  
**Available Storage:** 795GB SSD  
**Timeline:** 10 weeks  
**Budget:** <$500 total

---

## 1. Hardware Requirements

### 1.1 Minimum Specifications

| Component | Minimum | Recommended | Atlas Current |
|-----------|---------|-------------|---------------|
| **Processor** | M1 (8-core) | M3/M4 (10+ core) | M4 ✅ |
| **RAM** | 16GB | 64GB | TBD |
| **Storage** | 200GB free | 500GB free | 795GB ✅ |
| **GPU** | Unified (M1) | Unified (M4) | M4 ✅ |

**Notes:**
- **RAM:** K2.5 (32B active params) needs ~40GB RAM for inference. With quantization (4-bit), can run in 16GB but slower.
- **Storage:** Models + databases + training data = ~150GB initially, grows to ~300GB with usage.
- **GPU:** Mac unified memory handles both CPU and GPU, no discrete GPU needed.

### 1.2 Performance Expectations

**M4 Mac Performance:**
```
K2.5 Inference (MLX, 4-bit quantization):
  - Prompt processing: ~100 tokens/sec
  - Token generation: ~30-50 tokens/sec
  - Latency for 512 tokens: ~3-5 seconds

Sonnet 4.5 (Cloud API):
  - Latency: ~1-2 seconds (network dependent)
  - Throughput: ~100 tokens/sec

SQLite + sqlite-vec:
  - Vector search (768-dim, 10k docs): <50ms
  - Message retrieval: <10ms
  - Context assembly: ~200-500ms

Whisper (base model):
  - Transcription: ~3 seconds for 5-second audio clip
  - Real-time factor: ~0.6x (faster than real-time)
```

**Bottlenecks:**
1. **K2.5 inference** (can't speed up much on M4)
2. **Vision API calls** (network latency)
3. **Embedding generation** (batch helps)

**Optimization Strategies:**
- Cache frequent queries
- Batch embed multiple texts
- Prefetch context during user typing
- Use smaller models for simple queries

---

## 2. Storage Breakdown

### 2.1 Initial Setup (~150GB)

```
Models:
  DeepSeek K2.5 (32B active)       ~80GB (4-bit quantized)
  Nomic Embed v1.5                 ~500MB
  Whisper base                     ~1.5GB
  LoRA adapters (initial)          ~2GB
  ────────────────────────────────────────
  Total Models:                    ~84GB

Databases:
  atlas_memory.db (initial)        ~100MB
  Backups (7 days)                 ~1GB
  ────────────────────────────────────────
  Total Databases:                 ~1.1GB

Training Data:
  Raw training examples            ~5GB
  Curated datasets                 ~2GB
  ────────────────────────────────────────
  Total Training:                  ~7GB

System:
  Python environment               ~5GB
  Dependencies                     ~2GB
  Logs & temp files                ~1GB
  ────────────────────────────────────────
  Total System:                    ~8GB

──────────────────────────────────────────
TOTAL INITIAL:                     ~100GB
```

### 2.2 Growth Over Time

**Weekly Growth:**
```
Messages (avg 1000/week):          ~50MB/week
Perceptions (visual frames):       ~200MB/week
Training examples:                 ~100MB/week
LoRA checkpoints:                  ~500MB/week
Logs:                              ~50MB/week
────────────────────────────────────────
Total Weekly Growth:               ~900MB/week
```

**Projected Storage After 3 Months:**
```
Initial:                           100GB
Growth (12 weeks × 0.9GB):         ~11GB
────────────────────────────────────────
Total After 3 Months:              ~111GB

Available on 795GB SSD:            684GB remaining ✅
```

**Storage Management:**
```python
# Automated cleanup strategy
def manage_storage():
    # 1. Archive old sessions (>90 days)
    archive_old_sessions(days=90)
    
    # 2. Prune low-importance messages (>30 days, importance < 0.3)
    prune_old_messages(days=30, threshold=0.3)
    
    # 3. Delete old LoRA checkpoints (keep best 3)
    cleanup_lora_checkpoints(keep=3)
    
    # 4. Compress visual frames (>7 days)
    compress_old_frames(days=7)
    
    # 5. Vacuum database
    vacuum_database()
```

---

## 3. Model Downloads

### 3.1 Required Models

**DeepSeek K2.5 (or R1):**
```bash
# Download from Hugging Face
huggingface-cli download deepseek-ai/DeepSeek-R1 \
  --local-dir ~/models/deepseek-r1 \
  --revision main

# Size: ~160GB (FP16), ~80GB (4-bit quantized)
# Time: ~2-4 hours (depends on internet)
# Alternative: Use smaller variant (7B) if RAM limited
```

**Nomic Embed v1.5:**
```bash
# Sentence transformers auto-downloads
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5')

# Size: ~500MB
# Time: ~5 minutes
```

**Whisper Base:**
```python
import whisper
model = whisper.load_model("base")

# Size: ~1.5GB
# Time: ~10 minutes
# Alternative: Use "tiny" (39M params) for faster inference
```

### 3.2 Optional Models

**For Advanced Features:**
```
Whisper Large v3 (higher accuracy):        ~3GB
CLIP (visual embeddings):                  ~1.5GB
Emotion detection (Wav2Vec2):              ~500MB
Smaller K2.5 variant (7B):                 ~14GB (4-bit)
```

### 3.3 Model Management

```python
# File: scripts/download_models.py

import os
from pathlib import Path
from huggingface_hub import snapshot_download
import whisper
from sentence_transformers import SentenceTransformer

MODELS_DIR = Path.home() / "models"

def download_all_models():
    """Download all required models"""
    
    # 1. DeepSeek K2.5
    print("Downloading DeepSeek K2.5...")
    snapshot_download(
        "deepseek-ai/DeepSeek-R1",
        local_dir=MODELS_DIR / "deepseek-r1",
        local_dir_use_symlinks=False
    )
    
    # 2. Nomic Embed
    print("Downloading Nomic Embed...")
    SentenceTransformer('nomic-ai/nomic-embed-text-v1.5')
    
    # 3. Whisper
    print("Downloading Whisper...")
    whisper.load_model("base", download_root=MODELS_DIR / "whisper")
    
    print("All models downloaded successfully!")

if __name__ == "__main__":
    download_all_models()
```

---

## 4. Compute Requirements

### 4.1 CPU/GPU Usage

**During Inference:**
```
K2.5 local inference:
  - CPU: 60-80% (all performance cores)
  - GPU: 90-100% (unified memory bandwidth saturated)
  - RAM: 40-50GB (with 4-bit quantization)
  - Duration: 3-5 seconds per query

Sonnet API call:
  - CPU: <5% (just HTTP request)
  - Network: ~1 MB up, ~10 KB down
  - Duration: 1-2 seconds

Database operations:
  - CPU: <10%
  - Disk I/O: <50 MB/s
  - Duration: <500ms
```

**During Fine-Tuning:**
```
LoRA training (100 examples, 1000 iterations):
  - CPU: 80-100% (all cores)
  - GPU: 100% (memory bandwidth critical)
  - RAM: 50-60GB
  - Duration: 2-4 hours
  - Frequency: 1x per week (when buffer full)
```

**Idle (Background Tasks):**
```
Memory consolidation (nightly):
  - CPU: 20-40%
  - Duration: 10-30 minutes
  - Frequency: Daily at 3am

Perception sampling (if enabled):
  - CPU: 10-20%
  - Duration: Continuous (1 frame/minute)
```

### 4.2 Power Consumption

**Mac M4 Power Draw:**
```
Idle:                    ~5W
Light usage:             ~15W
K2.5 inference:          ~30-40W
Fine-tuning:             ~50-60W (sustained)

Battery impact (if on laptop):
  - K2.5 inference: ~2-3 hours continuous use
  - Sonnet API: ~8-10 hours (minimal local compute)
```

**Recommendation:** Keep plugged in during fine-tuning.

---

## 5. Network Requirements

### 5.1 Cloud API Usage

**Anthropic API (Claude Sonnet 4.5):**
```
Estimated usage:
  - Development (10 weeks): ~5M tokens
  - Production (per month): ~2M tokens

Costs:
  - Input: $3 per 1M tokens
  - Output: $15 per 1M tokens
  
Development cost:
  - Input (3M): $9
  - Output (2M): $30
  - Total: ~$39 for 10 weeks ✅

Production cost (monthly):
  - Input (1M): $3
  - Output (1M): $15
  - Total: ~$18/month
```

**Bandwidth:**
```
Per API call (average):
  - Request: ~5KB (prompt + context)
  - Response: ~2KB (response)
  - Total: ~7KB per query

Daily usage (100 queries):
  - 100 × 7KB = ~700KB/day
  - Monthly: ~20MB/month (negligible)
```

### 5.2 Model Downloads

**One-time bandwidth:**
```
DeepSeek K2.5:         ~80GB (4-bit) or ~160GB (FP16)
Nomic Embed:           ~500MB
Whisper:               ~1.5GB
────────────────────────────────────────
Total:                 ~82GB minimum

Download time estimates:
  - 100 Mbps: ~2 hours
  - 500 Mbps: ~25 minutes
  - 1 Gbps: ~12 minutes
```

**Recommendation:** Download models on fast WiFi, not cellular.

---

## 6. Development Time Estimates

### 6.1 By Phase

| Phase | Duration | Tasks | Hours/Week | Total Hours |
|-------|----------|-------|------------|-------------|
| Phase 1 | 2 weeks | Foundation | 20 | 40 |
| Phase 2 | 4 weeks | Core Systems | 20 | 80 |
| Phase 3 | 2 weeks | Integration | 20 | 40 |
| Phase 4 | 2 weeks | Polish | 20 | 40 |
| **Total** | **10 weeks** | | **20** | **200** |

### 6.2 By Role

```
Development (coding):              120 hours (60%)
Testing:                           40 hours (20%)
Documentation:                     20 hours (10%)
Research & planning:               20 hours (10%)
────────────────────────────────────────
Total:                             200 hours
```

### 6.3 By Component

```
Temporal Continuity (memory):      50 hours (25%)
Embodied Feedback (perception):    40 hours (20%)
Intrinsic Valence (goals):         30 hours (15%)
Neuroplasticity (learning):        40 hours (20%)
Integration & testing:             40 hours (20%)
────────────────────────────────────────
Total:                             200 hours
```

### 6.4 Schedule Options

**Full-Time (40 hrs/week):**
```
Timeline: 5 weeks
Intensity: High (sprint mode)
Risk: Burnout
```

**Part-Time (20 hrs/week):**
```
Timeline: 10 weeks ✅ (recommended)
Intensity: Moderate
Risk: Low
```

**Casual (10 hrs/week):**
```
Timeline: 20 weeks
Intensity: Low
Risk: Loss of momentum
```

---

## 7. Cost Breakdown

### 7.1 One-Time Costs

```
Hardware (assuming owned):         $0
  - Mac M4 already available ✅

Software Licenses:                 $0
  - All open source ✅

Model Downloads:                   $0
  - Free from Hugging Face ✅

Development Tools:                 $0
  - VSCode, Python, Git free ✅

────────────────────────────────────────
Total One-Time:                    $0
```

### 7.2 Recurring Costs

**During Development (10 weeks):**
```
Anthropic API (Sonnet):            ~$40
  - See section 5.1 for breakdown

Electricity (Mac M4):              ~$5
  - 40W avg × 200 hrs × $0.15/kWh
  - = 8 kWh × $0.15 = ~$1.20
  - + Fine-tuning: 60W × 40 hrs = ~$3.60

────────────────────────────────────────
Total Development:                 ~$45
```

**Production (monthly):**
```
Anthropic API:                     $18/month
  - 2M tokens (see section 5.1)

Electricity:                       $2/month
  - Idle + periodic inference

Backups (optional cloud):          $0-5/month
  - iCloud or Backblaze

────────────────────────────────────────
Total Monthly:                     ~$20-25/month
```

### 7.3 Total Project Cost

```
Development (10 weeks):            $45
Production (3 months):             $60-75
────────────────────────────────────────
Total First 6 Months:              ~$105-120 ✅

Well under $500 budget!
```

---

## 8. Resource Optimization Strategies

### 8.1 Reduce Model Size

**If RAM constrained (<32GB):**
```python
# Use smaller models
K2.5 7B instead of 32B:            ~14GB RAM (vs 40GB)
Whisper tiny instead of base:      ~1GB RAM (vs 2GB)
Nomic Embed 384-dim:               ~200MB (vs 500MB)

Trade-off:
  - Inference 2-3x faster
  - Quality slightly lower (90-95% of original)
```

### 8.2 Reduce API Costs

**Strategies:**
```python
# 1. Aggressive caching
cache_responses(ttl=3600)  # Save ~30-40% API calls

# 2. Batch requests
batch_api_calls(batch_size=5)  # Reduce overhead

# 3. Use K2.5 for simple queries
route_to_local_when_possible()  # Save 50%+ on API

# 4. Compress context
prune_low_importance_context()  # Reduce input tokens
```

**Projected savings:**
```
Without optimization:  $40 dev + $18/mo prod
With optimization:     $20 dev + $10/mo prod
────────────────────────────────────────
Savings:               50% reduction ✅
```

### 8.3 Reduce Storage

**Strategies:**
```python
# 1. Compress visual frames
compress_images(quality=85)  # 70% smaller

# 2. Prune aggressively
prune_messages(threshold=0.2)  # vs 0.3

# 3. Archive to external drive
archive_to_external(path="/Volumes/External")

# 4. Delete old LoRA checkpoints
keep_only_best_n(n=3)  # vs all
```

**Projected savings:**
```
Without optimization:  ~300GB after 6 months
With optimization:     ~150GB after 6 months
────────────────────────────────────────
Savings:               50% reduction ✅
```

---

## 9. Scaling Considerations

### 9.1 If Growth Exceeds Expectations

**Storage Full (>500GB used):**
```
Options:
1. Add external SSD (1TB ~$100)
2. Aggressive pruning (see 8.3)
3. Cloud archive (S3 Glacier ~$4/TB/month)
```

**RAM Insufficient (<32GB):**
```
Options:
1. Upgrade Mac (64GB recommended)
2. Use smaller models (7B instead of 32B)
3. Increase swap (slower but works)
```

**API Costs Too High (>$50/month):**
```
Options:
1. Route more to K2.5 local
2. Increase cache TTL
3. Use smaller context windows
4. Batch API requests
```

### 9.2 Multi-User Scaling

**If supporting multiple users:**
```
Storage:
  - Per user: ~50GB/year
  - 10 users: ~500GB/year

Compute:
  - Sequential: Same as single user
  - Concurrent: Need more RAM (40GB per active user)

Costs:
  - API: Linear scaling with users
  - Storage: Linear scaling
```

**Recommendation:** Keep single-user for initial launch.

---

## 10. Resource Checklist

### 10.1 Before Starting Development

- [ ] Mac M4 (or M2/M3 Max) with 32GB+ RAM
- [ ] 200GB+ free storage on SSD
- [ ] Fast internet (100+ Mbps for model downloads)
- [ ] Anthropic API key
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] VSCode or preferred IDE

### 10.2 Week 1 Setup

- [ ] Download DeepSeek K2.5 (~2-4 hours)
- [ ] Install sqlite-vec extension
- [ ] Set up Python virtual environment
- [ ] Install dependencies (requirements.txt)
- [ ] Download Nomic Embed (~5 mins)
- [ ] Download Whisper (~10 mins)
- [ ] Initialize database
- [ ] Run test suite

### 10.3 Ongoing Monitoring

**Weekly checks:**
- [ ] Database size (<10GB growth/week)
- [ ] API usage (<$5/week dev, <$5/week prod)
- [ ] Storage available (>100GB free)
- [ ] Backup successful

**Monthly checks:**
- [ ] Total storage (<300GB)
- [ ] API costs (<$25/month)
- [ ] Performance benchmarks met
- [ ] No memory leaks (restart if RAM >80%)

---

## 11. Budget Summary

### 11.1 Total Cost Projection (6 Months)

```
═══════════════════════════════════════════════════════
ITEM                          COST          NOTES
═══════════════════════════════════════════════════════
Hardware (Mac M4)             $0            Already owned ✅
Model Downloads               $0            Open source ✅
Development Tools             $0            Open source ✅
───────────────────────────────────────────────────────
ONE-TIME TOTAL:               $0
═══════════════════════════════════════════════════════

Development (10 weeks)
  - Anthropic API             $40           ~5M tokens
  - Electricity               $5            200 hrs
───────────────────────────────────────────────────────
DEVELOPMENT TOTAL:            $45
═══════════════════════════════════════════════────════

Production (3 months)
  - Anthropic API             $60           ~2M tokens/mo
  - Electricity               $6            Idle + inference
  - Backups (optional)        $15           Cloud storage
───────────────────────────────────────────────────────
PRODUCTION TOTAL:             $81
═══════════════════════════════════════════════════════

GRAND TOTAL (6 months):       $126 ✅

Well under $500 budget! 💰
═══════════════════════════════════════════════════════
```

### 11.2 Cost Optimization Target

**With optimizations (section 8.2):**
```
Development:                  $20 (vs $45)
Production (3 months):        $30 (vs $81)
───────────────────────────────────────────────────────
Optimized Total:              $50 ✅

Savings: 60% reduction!
```

---

## 12. Risk Mitigation

### 12.1 Resource Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Storage fills up | High | Low | Monitor weekly, prune aggressively |
| RAM insufficient | High | Medium | Use smaller models, upgrade if needed |
| API costs spike | Medium | Low | Set budget alerts, increase local usage |
| Model download fails | Medium | Low | Retry, use mirrors, download in parts |
| Fine-tuning too slow | Low | Medium | Reduce iterations, smaller LoRA rank |

### 12.2 Contingency Plans

**If storage critical (<50GB free):**
1. Emergency pruning (threshold=0.1)
2. Delete all visual frames >7 days
3. Archive old sessions to external drive
4. Delete all but latest LoRA checkpoint

**If RAM critical (>90% used):**
1. Switch to K2.5 7B model
2. Reduce context window (50k tokens)
3. Disable perception sampling
4. Restart nightly to clear memory

**If API costs exceed budget:**
1. Route 100% to K2.5 local
2. Disable vision features temporarily
3. Increase cache TTL to 24 hours
4. Batch all requests

---

## 13. Resource Monitoring Dashboard

### 13.1 Key Metrics

```python
# File: atlas_core/resources.py

class ResourceMonitor:
    def get_status(self):
        return {
            'storage': {
                'total_gb': self._get_total_storage(),
                'used_gb': self._get_used_storage(),
                'free_gb': self._get_free_storage(),
                'database_mb': self._get_db_size(),
                'models_gb': self._get_models_size()
            },
            'memory': {
                'total_gb': psutil.virtual_memory().total / 1e9,
                'used_gb': psutil.virtual_memory().used / 1e9,
                'available_gb': psutil.virtual_memory().available / 1e9,
                'percent': psutil.virtual_memory().percent
            },
            'api': {
                'calls_today': self._count_api_calls(today()),
                'tokens_today': self._count_tokens(today()),
                'cost_today': self._estimate_cost(today()),
                'cost_month': self._estimate_cost(this_month())
            },
            'performance': {
                'avg_latency_ms': np.mean(self.metrics['latency']),
                'cache_hit_rate': self._compute_cache_hit_rate(),
                'inference_per_hour': len(self.metrics['inference']) / 24
            }
        }
```

### 13.2 Alerts

```python
def check_alerts(status):
    alerts = []
    
    if status['storage']['free_gb'] < 50:
        alerts.append("⚠️ Storage low: <50GB free")
    
    if status['memory']['percent'] > 90:
        alerts.append("⚠️ Memory high: >90% used")
    
    if status['api']['cost_month'] > 25:
        alerts.append("⚠️ API costs high: >$25 this month")
    
    if status['performance']['avg_latency_ms'] > 10000:
        alerts.append("⚠️ Latency high: >10s average")
    
    return alerts
```

---

**END OF RESOURCE REQUIREMENTS**
