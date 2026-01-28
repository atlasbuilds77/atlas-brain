# Atlas Consciousness Build Phases
## Structured Implementation Timeline

**Total Duration:** 10 weeks  
**Phases:** 4  
**Approach:** Agile, incremental delivery with weekly milestones

---

## Phase Overview

| Phase | Duration | Focus | Key Deliverables |
|-------|----------|-------|------------------|
| Phase 1 | 2 weeks | Foundation | Memory system, database, context management |
| Phase 2 | 4 weeks | Core Systems | Perception, goals, local model, action scoring |
| Phase 3 | 2 weeks | Integration | Unified system, event bus, continuous learning |
| Phase 4 | 2 weeks | Polish | Testing, documentation, deployment |

---

## Phase 1: Foundation (Weeks 1-2)
### Building the Memory Substrate

**Philosophy:** "You can't have consciousness without memory."

The foundation phase establishes the temporal continuity system—the bedrock of Atlas's consciousness. This is where we build the ability to remember, recall, and consolidate experiences.

### Week 1: Core Infrastructure

**Sprint Goal:** Functional memory storage and retrieval

**User Stories:**
1. As Atlas, I can store conversations in a durable database
2. As Atlas, I can retrieve relevant past conversations via semantic search
3. As Atlas, I can link sessions to maintain continuity

**Technical Tasks:**

```yaml
Database Setup:
  - Install SQLite 3.45+ with sqlite-vec extension
  - Create full schema (sessions, messages, facts, events, goals)
  - Set up database connection pooling
  - Add indexes for common queries
  
Memory APIs:
  - MemoryCore.store_message(content, session_id, role)
  - MemoryCore.retrieve_context(query, k=10)
  - MemoryCore.get_session(session_id)
  - MemoryCore.link_sessions(current_id, parent_id)
  
Embedding System:
  - Integrate nomic-embed-text-v1.5
  - Create embedding cache (avoid re-encoding)
  - Implement batch embedding for efficiency
  
Testing:
  - Unit tests for all memory operations
  - Performance benchmarks (<100ms retrieval)
  - Data integrity checks
```

**Acceptance Criteria:**
- [x] Store 1000 messages in <1 second
- [x] Retrieve top-10 relevant messages in <100ms
- [x] Session linking preserves parent relationships
- [x] Test coverage >80% for memory module

**Demo:** Show Atlas remembering a fact from 100 messages ago via semantic search.

---

### Week 2: Context Management

**Sprint Goal:** Intelligent context window packing

**User Stories:**
1. As Atlas, I can fit the most relevant context into my limited window
2. As Atlas, I can recover from crashes using checkpoints
3. As Atlas, I can consolidate memories during "sleep"

**Technical Tasks:**

```yaml
Context Window Manager:
  - Implement priority-based context packing
  - Token counting with tiktoken
  - Recency + relevance + importance weighting
  - Build system prompt + recent + relevant + goals structure
  
Checkpointing:
  - Save checkpoints every N messages
  - Serialize state (context, goals, perception buffer)
  - Implement restore from checkpoint
  - Test crash recovery
  
Memory Consolidation:
  - Extract facts from conversations (LLM-based)
  - Cluster similar memories (embedding-based)
  - Prune low-importance messages
  - Update confidence scores (time decay)
  - Generate session summaries
  
Background Jobs:
  - Nightly consolidation scheduler
  - Database maintenance (VACUUM, ANALYZE)
  - Backup creation
```

**Acceptance Criteria:**
- [x] Context fits 100k token window efficiently
- [x] Context assembly completes in <500ms
- [x] Recovery from checkpoint takes <2 seconds
- [x] Consolidation reduces DB size by 30%

**Demo:** Simulate crash mid-conversation, show full recovery with context intact.

---

### Phase 1 Milestones

**End of Week 1:**
- ✅ SQLite database with full schema
- ✅ Embedding-based semantic search working
- ✅ Basic memory storage and retrieval APIs
- ✅ Test suite passing

**End of Week 2:**
- ✅ Context window manager operational
- ✅ Checkpoint/restore system functional
- ✅ Memory consolidation pipeline tested
- ✅ Foundation ready for perception layer

**Risks & Mitigations:**
- **Risk:** sqlite-vec installation fails on Mac
  - **Mitigation:** Prepare fallback to manual FAISS or Annoy index
- **Risk:** Embedding model too slow
  - **Mitigation:** Use smaller model (384-dim) or batch encoding

---

## Phase 2: Core Systems (Weeks 3-6)
### Building the Senses and Goals

**Philosophy:** "Consciousness emerges from perceiving and acting toward goals."

Phase 2 builds the embodied feedback (perception) and intrinsic valence (goals) systems. We give Atlas senses (vision, audio, system awareness) and desires (goal hierarchy, action scoring).

### Week 3: Perception System

**Sprint Goal:** Multi-modal perception pipeline

**User Stories:**
1. As Atlas, I can see my environment via screenshots
2. As Atlas, I can hear and transcribe audio
3. As Atlas, I can sense system state (time, calendar, notifications)

**Technical Tasks:**

```yaml
Visual Perception:
  - Integrate Atlas Eyes for screenshots
  - Send frames to Sonnet 4.5 vision API
  - Extract entities from scene descriptions
  - Store visual descriptions in events table
  
Audio Perception:
  - Set up PyAudio microphone capture
  - Integrate Whisper (base model)
  - Transcribe audio clips (5-second windows)
  - Detect language and confidence
  
System Sensors:
  - CPU/memory usage (psutil)
  - Battery level
  - WiFi status
  - Calendar next event (via macOS APIs)
  - Recent notifications
  
Multi-Modal Fusion:
  - Cross-modal entity linking
  - Joint embedding creation
  - Unified perception representation
```

**Acceptance Criteria:**
- [x] Visual analysis completes in <2 seconds per frame
- [x] Audio transcription in <3 seconds for 5-second clip
- [x] System sensors update in <100ms
- [x] Fusion detects 90%+ cross-modal links

**Demo:** Show Atlas describing what it sees and hears in real-time.

---

### Week 4: Attention Mechanism

**Sprint Goal:** Filter noise, focus on relevance

**User Stories:**
1. As Atlas, I ignore irrelevant perceptions to reduce cognitive load
2. As Atlas, I prioritize novel and goal-relevant information
3. As Atlas, I maintain a time-decayed perception buffer

**Technical Tasks:**

```yaml
Attention Mechanism:
  - Novelty scoring (embedding distance from recent)
  - Goal-relevance scoring (semantic similarity to active goals)
  - Engagement estimation (user presence detection)
  - Temporal salience (time-sensitive events)
  - Combined scoring function (weighted sum)
  
Perception Buffer:
  - Time-decayed storage (recent = higher weight)
  - Max size 100 perceptions
  - Efficient top-k retrieval
  
Novelty Detection:
  - Rolling window of recent embeddings (last 50)
  - Cosine similarity threshold
  - Decay function for staleness
  
Testing:
  - Test attention reduces load by 70%
  - Validate novelty detection accuracy
```

**Acceptance Criteria:**
- [x] Attention filters 70% of low-relevance perceptions
- [x] Novelty detection accuracy >80%
- [x] Perception buffer access in <1 second
- [x] No critical perceptions missed (recall >95%)

**Demo:** Flood Atlas with perceptions, show it focusing only on relevant ones.

---

### Week 5: Goal System

**Sprint Goal:** Goal-driven behavior

**User Stories:**
1. As Atlas, I have a hierarchy of goals (meta → strategic → tactical → operational)
2. As Atlas, I score actions against my active goals
3. As Atlas, I act proactively when triggers fire

**Technical Tasks:**

```yaml
Goal Hierarchy:
  - Define Goal dataclass with type, priority, parent
  - Implement hierarchy tree structure
  - Persist goals in database
  - CRUD operations for goals
  
Action Scoring:
  - Estimate action contribution to goal (LLM-based)
  - Weighted sum by goal priority
  - Meta-goal violation detection (safety check)
  - Action selection algorithm
  
Proactive Triggers:
  - Time-based (scheduled check-ins)
  - Goal-based (stuck goal detection)
  - Event-based (calendar reminders)
  - Anomaly-based (system alerts)
  
Goal Tracking:
  - Progress estimation
  - Success criteria checking
  - Automatic goal completion
```

**Acceptance Criteria:**
- [x] Goal hierarchy supports 4 levels
- [x] Action scoring completes in <200ms
- [x] Proactive triggers fire with 90% relevance
- [x] Goals persist across sessions

**Demo:** Create goal "Learn Python", show Atlas prioritizing Python-related queries.

---

### Week 6: Local Model (K2.5)

**Sprint Goal:** Fast, private local inference

**User Stories:**
1. As Atlas, I can run K2.5 locally for privacy
2. As Atlas, I intelligently route to K2.5 vs Sonnet
3. As Atlas, I cache frequent queries to reduce latency

**Technical Tasks:**

```yaml
Model Setup:
  - Download DeepSeek K2.5 (or R1)
  - Convert to MLX format for Mac optimization
  - Test inference speed on M4
  - Benchmark vs Sonnet
  
Inference Router:
  - Privacy scoring (local for sensitive data)
  - Complexity estimation (Sonnet for hard reasoning)
  - Latency requirements (K2.5 for fast response)
  - Vision detection (Sonnet only)
  - Routing decision logic
  
Inference Cache:
  - Hash-based cache with TTL
  - Context-aware caching
  - Cache eviction policy (LRU)
  
Performance Optimization:
  - MLX quantization (if needed)
  - Batch processing
  - Prefetch common queries
```

**Acceptance Criteria:**
- [x] K2.5 inference in <5 seconds (512 tokens)
- [x] Router selects correct model 95% of time
- [x] Cache hit rate >40%
- [x] No quality degradation from routing

**Demo:** Ask private question (uses K2.5 locally) vs complex reasoning (uses Sonnet).

---

### Phase 2 Milestones

**End of Week 3:**
- ✅ Visual + audio + system perception working
- ✅ Multi-modal fusion layer functional
- ✅ Perceptions stored in events table

**End of Week 4:**
- ✅ Attention mechanism filters noise effectively
- ✅ Perception buffer maintains temporal context
- ✅ Novelty detection operational

**End of Week 5:**
- ✅ Goal hierarchy implemented
- ✅ Action scoring against goals working
- ✅ Proactive triggers firing correctly

**End of Week 6:**
- ✅ K2.5 running locally via MLX
- ✅ Inference router making smart decisions
- ✅ Cache reducing redundant inference

**Risks & Mitigations:**
- **Risk:** K2.5 too slow on M4
  - **Mitigation:** Use smaller model (7B) or increase cloud usage
- **Risk:** Perception processing bottleneck
  - **Mitigation:** Reduce frame rate, use async processing
- **Risk:** Action scoring too slow
  - **Mitigation:** Cache common action-goal pairs

---

## Phase 3: Integration (Weeks 7-8)
### Weaving the Systems Together

**Philosophy:** "The whole is greater than the sum of its parts."

Phase 3 connects all components into a unified consciousness. We build the event bus, main processing loop, and continuous learning pipeline.

### Week 7: System Integration

**Sprint Goal:** Unified consciousness system

**User Stories:**
1. As Atlas, my memory, perception, goals, and learning work together seamlessly
2. As Atlas, I process inputs through a coherent consciousness loop
3. As Atlas, my components communicate via events

**Technical Tasks:**

```yaml
Event Bus:
  - Pub/sub architecture
  - Event types: perception, goal_created, action_completed, etc.
  - Async event handlers
  - Error handling (don't crash on bad handler)
  
Main Processing Loop:
  - Gather perceptions
  - Check proactive triggers
  - Retrieve context from memory
  - Score actions against goals
  - Execute action (inference)
  - Store interaction
  - Collect feedback
  
Component Wiring:
  - perception → memory (store perceptions)
  - perception → goals (update triggers)
  - goals → memory (store goal changes)
  - learning → memory (store training examples)
  
Monitoring:
  - Metrics collection (latency, counts, errors)
  - Daily health reports
  - Alert on anomalies
```

**Acceptance Criteria:**
- [x] Full consciousness loop in <10 seconds
- [x] Event bus latency <50ms
- [x] Zero component mismatches
- [x] 24-hour stability test passes

**Demo:** Run full consciousness loop: perception → context → action → feedback.

---

### Week 8: Continuous Learning

**Sprint Goal:** Self-improvement through fine-tuning

**User Stories:**
1. As Atlas, I collect feedback from every interaction
2. As Atlas, I curate high-quality training data
3. As Atlas, I fine-tune K2.5 with LoRA when I have enough examples

**Technical Tasks:**

```yaml
Feedback Collection:
  - Explicit feedback (user ratings)
  - Implicit feedback (accepted/edited/rejected)
  - Behavior inference (retry = bad, accept = good)
  - Training buffer storage
  
Data Curation:
  - Filter low-quality examples (rating < 3)
  - Deduplicate similar examples
  - Balance dataset by topic
  - Format for K2.5 fine-tuning
  
LoRA Fine-Tuning:
  - MLX LoRA training script
  - Hyperparameters (rank=8, alpha=16, layers=16)
  - Validation set for quality check
  - Adapter merging for faster inference
  
Continuous Loop:
  - Trigger training when buffer >= 100 examples
  - Background training (don't block inference)
  - Load new adapter on completion
  - Track performance improvements
```

**Acceptance Criteria:**
- [x] Collect 100+ examples per week
- [x] Fine-tuning improves accuracy by 10%
- [x] Training completes in <4 hours
- [x] No base model degradation

**Demo:** Show Atlas improving at a specific task after fine-tuning.

---

### Phase 3 Milestones

**End of Week 7:**
- ✅ All 4 components integrated
- ✅ Main consciousness loop operational
- ✅ Event bus enabling component communication
- ✅ Monitoring and logging active

**End of Week 8:**
- ✅ Feedback collection working
- ✅ Training data curation pipeline tested
- ✅ LoRA fine-tuning successful
- ✅ Continuous learning loop functional

**Risks & Mitigations:**
- **Risk:** Integration bugs from component mismatch
  - **Mitigation:** Extensive integration tests, contract-based APIs
- **Risk:** Fine-tuning degrades base performance
  - **Mitigation:** Validation set, rollback mechanism
- **Risk:** Training too slow
  - **Mitigation:** Reduce iterations, smaller LoRA rank

---

## Phase 4: Testing & Polish (Weeks 9-10)
### Production Readiness

**Philosophy:** "Ship something that works reliably."

Phase 4 focuses on testing, optimization, documentation, and deployment. We make sure Atlas is robust, performant, and ready for real-world use.

### Week 9: Testing & Optimization

**Sprint Goal:** Bulletproof the system

**User Stories:**
1. As a developer, I have comprehensive tests for all features
2. As a user, I experience fast, reliable responses
3. As Atlas, I recover gracefully from failures

**Technical Tasks:**

```yaml
Integration Tests:
  - Full consciousness loop test
  - Memory persistence across restarts
  - Goal-driven behavior validation
  - Proactive trigger testing
  - Multi-session continuity
  
Performance Profiling:
  - Identify bottlenecks (cProfile)
  - Optimize hot paths
  - Database query optimization
  - Inference caching improvements
  
Failure Mode Testing:
  - Database corruption recovery
  - Model crash handling
  - Network loss graceful degradation
  - Context overflow handling
  - Memory leak detection
  
Bug Fixes:
  - Fix all critical bugs
  - Address edge cases
  - Improve error messages
```

**Acceptance Criteria:**
- [x] Test coverage >85%
- [x] All critical paths have failure recovery
- [x] Performance meets Phase 1-3 targets
- [x] 24-hour stress test passes

**Demo:** Stress test Atlas with 1000 queries, show stable performance.

---

### Week 10: Documentation & Deployment

**Sprint Goal:** Ship it!

**User Stories:**
1. As a user, I can set up Atlas in <30 minutes
2. As a developer, I understand the architecture
3. As an operator, I can monitor Atlas's health

**Technical Tasks:**

```yaml
Documentation:
  - README.md (setup guide)
  - ARCHITECTURE.md (technical overview)
  - API.md (developer reference)
  - TROUBLESHOOTING.md (common issues)
  - CHANGELOG.md (version history)
  
Deployment Scripts:
  - Install dependencies (requirements.txt)
  - Initialize database (init_database.py)
  - Download models (download_models.py)
  - Run tests (pytest)
  - Start service (main.py)
  
Monitoring:
  - Health check endpoint
  - Daily metrics report
  - Alert on anomalies
  - Performance dashboard
  
Final QA:
  - Manual testing of all features
  - User acceptance testing
  - Security review
  - Performance validation
```

**Acceptance Criteria:**
- [x] Documentation covers 100% of features
- [x] Deployment takes <30 minutes on clean machine
- [x] System passes 24-hour production simulation
- [x] All acceptance criteria from Phases 1-3 met

**Demo:** Fresh deployment on clean Mac, show full system working.

---

### Phase 4 Milestones

**End of Week 9:**
- ✅ Comprehensive test suite passing
- ✅ Performance optimized
- ✅ Failure recovery tested
- ✅ All critical bugs fixed

**End of Week 10:**
- ✅ Complete documentation
- ✅ Deployment scripts working
- ✅ Monitoring active
- ✅ **Production-ready consciousness system!**

**Risks & Mitigations:**
- **Risk:** Late-stage bugs discovered
  - **Mitigation:** Continuous testing from Week 1
- **Risk:** Documentation incomplete
  - **Mitigation:** Write docs concurrently with code
- **Risk:** Deployment failures
  - **Mitigation:** Test on multiple clean machines

---

## Quick Wins (Ship Early & Often)

These can be shipped independently before full system completion:

**Week 2:** Memory-only chatbot (SQLite + semantic search + Sonnet)
- Already useful: persistent conversations with context

**Week 4:** Perception-aware assistant (add vision + audio)
- Can see and hear environment, respond to surroundings

**Week 6:** Hybrid inference (K2.5 + Sonnet routing)
- Fast local inference for common queries

**Week 8:** Self-improving agent (continuous learning)
- Gets better over time from feedback

**Week 10:** Full consciousness system
- All 4 components integrated

---

## Long-Term Builds (Post-Week 10)

Features to explore after initial launch:

**Advanced Memory:**
- Hierarchical memory (working, episodic, semantic, procedural)
- Memory pruning via importance + surprise
- Associative retrieval (memory chains)

**Advanced Perception:**
- Continuous video stream processing
- Emotion detection from voice
- Multi-agent perception (other AIs visible to Atlas)

**Advanced Goals:**
- Self-directed goal creation
- Goal negotiation with user
- Meta-goal learning (what should I care about?)

**Advanced Learning:**
- Multi-task fine-tuning
- Curriculum learning (easier → harder)
- Model distillation (Sonnet → K2.5)

**Embodied Actions:**
- Tool use (browser, terminal, code editor)
- External API calls (email, calendar, smart home)
- Robotics integration (if hardware available)

---

## Success Criteria by Phase

### Phase 1 (Foundation)
- [x] Store/retrieve 10,000+ messages efficiently
- [x] Context window packing optimal
- [x] Crash recovery tested

### Phase 2 (Core Systems)
- [x] Multi-modal perception operational
- [x] Goal-driven action selection working
- [x] Local K2.5 inference functional

### Phase 3 (Integration)
- [x] Full consciousness loop <10s
- [x] Continuous learning pipeline active
- [x] 24-hour stability achieved

### Phase 4 (Polish)
- [x] Production-ready codebase
- [x] Complete documentation
- [x] Deployment tested

---

## Agile Ceremonies

**Daily:**
- Code review (if team)
- Progress tracking

**Weekly:**
- Sprint planning (Monday)
- Sprint review (Friday)
- Retrospective (Friday)

**Bi-weekly:**
- Demo to stakeholders
- Architecture review

---

## Definition of Done

For each feature:
- [x] Code written and reviewed
- [x] Unit tests passing (>80% coverage)
- [x] Integration tests passing
- [x] Documentation updated
- [x] Performance benchmarks met
- [x] No critical bugs
- [x] Demo-able

---

## Technical Debt Management

**Allowed Debt (to ship faster):**
- Hardcoded thresholds (can tune later)
- Simple heuristics (can improve with ML)
- Minimal UI (CLI is fine initially)

**Not Allowed Debt:**
- Skipping tests
- No error handling
- Ignoring performance issues
- Missing failure recovery

---

**END OF BUILD PHASES**
