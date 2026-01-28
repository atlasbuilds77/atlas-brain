# Atlas Consciousness Implementation Roadmap
## Week-by-Week Build Plan

**Timeline:** 10 weeks (2.5 months)  
**Start Date:** TBD  
**Target:** Production-ready consciousness system on Mac M4

---

## Overview

This roadmap breaks down the consciousness system build into 4 phases over 10 weeks, with specific deliverables, dependencies, and success metrics for each week.

**Total Effort Estimate:** 200-300 hours (20-30 hrs/week avg)

---

## Phase 1: Foundation (Weeks 1-2)

### Week 1: Core Infrastructure & Database

**Goals:**
- Set up SQLite database with full schema
- Implement basic session management
- Create memory storage/retrieval APIs
- Set up development environment

**Tasks:**

**Day 1-2: Database Setup**
```bash
# Create database structure
cd ~/Library/Application\ Support
mkdir -p atlas
cd atlas

# Install dependencies
pip install sqlalchemy sqlite-vec sentence-transformers

# Create schema
python scripts/init_database.py
```

**Day 3-4: Memory APIs**
```python
# Implement core memory operations
# File: atlas_memory/core.py

class MemoryCore:
    def __init__(self, db_path="atlas_memory.db"):
        self.db = self._init_db(db_path)
        self.embedder = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5')
    
    def store_message(self, content, session_id, role="user"):
        """Store with embedding generation"""
        embedding = self.embedder.encode(content)
        # Insert into messages + facts_vec tables
        pass
    
    def retrieve_context(self, query, k=10):
        """Semantic search using sqlite-vec"""
        query_embedding = self.embedder.encode(query)
        # Vector search + recency weighting
        pass
```

**Day 5-7: Testing & Validation**
- Unit tests for all memory operations
- Performance benchmarks (target: <100ms retrieval)
- Data integrity checks

**Deliverables:**
- ✅ Working SQLite database with schema
- ✅ Memory storage/retrieval APIs
- ✅ Basic session management
- ✅ Test suite (>80% coverage)

**Success Metrics:**
- Store 1000 messages in <1 second
- Retrieve relevant context in <100ms
- Vector search accuracy >85%

**Dependencies:**
- None (start here)

**Risks:**
- sqlite-vec installation issues → Fallback to manual vector search
- Embedding model too large → Use smaller model (384-dim)

---

### Week 2: Context Management & Checkpointing

**Goals:**
- Implement MemGPT-style context window management
- Add checkpointing for failure recovery
- Build context packing algorithm
- Create memory consolidation routine

**Tasks:**

**Day 1-3: Context Window Manager**
```python
# File: atlas_memory/context.py

class ContextManager:
    def __init__(self, max_tokens=100000):
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def build_context(self, session_id, query):
        """Assemble optimal context window"""
        components = {
            'system': self._get_system_prompt(),
            'recent': self._get_recent_messages(session_id, n=20),
            'relevant': self._semantic_search(query, k=10),
            'goals': self._get_active_goals(),
            'perceptions': self._get_recent_perceptions()
        }
        
        # Pack with priority-based truncation
        return self._pack_context(components)
    
    def _pack_context(self, components):
        """Fit into token budget using priority"""
        # Priority order: system > goals > recent > relevant
        # Truncate lowest priority until fits
        pass
```

**Day 4-5: Checkpointing**
```python
# File: atlas_memory/checkpoint.py

class CheckpointManager:
    def save_checkpoint(self, session_id, state):
        """Snapshot current state"""
        checkpoint = {
            'timestamp': now(),
            'context': state['context'],
            'goals': state['goals'],
            'perception_buffer': state['perceptions']
        }
        # Save to sessions.checkpoint_data
        pass
    
    def restore(self, session_id):
        """Recover from checkpoint"""
        # Load last checkpoint
        # Replay any messages since then
        pass
```

**Day 6-7: Memory Consolidation**
```python
# File: atlas_memory/consolidate.py

class MemoryConsolidator:
    def consolidate(self):
        """Nightly memory optimization"""
        # 1. Extract facts from conversations
        self._extract_facts()
        
        # 2. Cluster similar memories
        self._cluster_memories()
        
        # 3. Prune low-importance items
        self._prune_memories(threshold=0.2)
        
        # 4. Update importance scores
        self._decay_old_memories()
        
        # 5. Generate session summaries
        self._summarize_sessions()
```

**Deliverables:**
- ✅ Context window packing (fits 100k tokens)
- ✅ Checkpoint save/restore
- ✅ Memory consolidation pipeline
- ✅ Session linking via parent_session_id

**Success Metrics:**
- Context assembly in <500ms
- Recovery from crash in <2s
- Consolidation reduces DB size by 30%

**Dependencies:**
- Week 1 (database and basic APIs)

**Risks:**
- Token counting inaccurate → Test extensively with real data
- Consolidation too aggressive → Add manual review mode

---

## Phase 2: Core Systems (Weeks 3-6)

### Week 3: Perception System (Visual + Audio)

**Goals:**
- Integrate Atlas Eyes for visual perception
- Add Whisper for audio transcription
- Build multi-modal fusion layer
- Create perception buffer

**Tasks:**

**Day 1-2: Visual Perception**
```python
# File: atlas_perception/visual.py

class VisualPerception:
    def __init__(self):
        self.atlas_eyes = "/path/to/atlas-eyes"
        self.frame_buffer = deque(maxlen=10)
    
    def capture_and_analyze(self):
        """Capture + describe scene"""
        # Run atlas-eyes capture
        frame = self._capture_screenshot()
        
        # Send to Sonnet 4.5 for description
        description = self._analyze_with_vision_model(frame)
        
        # Extract entities
        entities = self._extract_entities(description)
        
        return {
            'timestamp': now(),
            'description': description,
            'entities': entities,
            'frame_hash': hash(frame)
        }
```

**Day 3-4: Audio Perception**
```python
# File: atlas_perception/audio.py

import whisper

class AudioPerception:
    def __init__(self):
        self.model = whisper.load_model("base")
        # base model: fast, good accuracy
    
    def listen(self, duration=5):
        """Record and transcribe"""
        audio = self._record_microphone(duration)
        
        result = self.model.transcribe(audio)
        
        return {
            'timestamp': now(),
            'transcription': result['text'],
            'language': result['language'],
            'confidence': result.get('avg_logprob', 0)
        }
```

**Day 5-7: Multi-Modal Fusion**
```python
# File: atlas_perception/fusion.py

class MultiModalFusion:
    def fuse(self, visual, audio, system):
        """Combine perception streams"""
        # Cross-modal attention
        # Example: if audio says "cat", look for cat in visual
        
        links = self._find_cross_modal_links(visual, audio)
        
        # Create unified embedding
        joint_embedding = self._create_joint_embedding(
            visual, audio, system
        )
        
        return {
            'timestamp': now(),
            'visual_summary': visual['description'],
            'audio_transcript': audio['transcription'],
            'system_state': system,
            'cross_modal_links': links,
            'embedding': joint_embedding
        }
```

**Deliverables:**
- ✅ Visual perception via Atlas Eyes
- ✅ Audio transcription via Whisper
- ✅ System sensors (CPU, memory, calendar, etc.)
- ✅ Multi-modal fusion layer

**Success Metrics:**
- Visual analysis in <2s per frame
- Audio transcription in <3s for 5s clip
- Fusion detects 90%+ of cross-modal links

**Dependencies:**
- Week 1 (for storing perceptions in DB)

**Risks:**
- Atlas Eyes not installed → Build minimal screenshot tool
- Whisper too slow → Use tiny model or cloud API

---

### Week 4: Attention Mechanism & Perception Buffer

**Goals:**
- Build attention mechanism to filter perceptions
- Create perception buffer with time decay
- Implement novelty detection
- Add goal-relevance scoring

**Tasks:**

**Day 1-3: Attention Mechanism**
```python
# File: atlas_perception/attention.py

class AttentionMechanism:
    def filter_perceptions(self, perceptions, goals, context):
        """Score and filter by relevance"""
        scored = []
        
        for p in perceptions:
            score = (
                0.3 * self._novelty_score(p) +
                0.4 * self._goal_relevance(p, goals) +
                0.2 * self._engagement_score(p) +
                0.1 * self._temporal_salience(p)
            )
            
            if score > 0.3:  # Threshold
                scored.append((score, p))
        
        # Return top-5
        return sorted(scored, reverse=True)[:5]
```

**Day 4-5: Perception Buffer**
```python
# File: atlas_perception/buffer.py

class PerceptionBuffer:
    def __init__(self, max_size=100):
        self.buffer = deque(maxlen=max_size)
        self.decay_rate = 0.95  # Per hour
    
    def add(self, perception):
        """Add with timestamp"""
        self.buffer.append({
            'perception': perception,
            'timestamp': now(),
            'importance': perception.get('importance', 0.5)
        })
    
    def get_recent(self, n=10):
        """Get recent perceptions with time decay"""
        now_ts = time.time()
        
        weighted = []
        for item in self.buffer:
            age_hours = (now_ts - item['timestamp']) / 3600
            decay_factor = self.decay_rate ** age_hours
            
            weighted.append((
                item['importance'] * decay_factor,
                item['perception']
            ))
        
        return sorted(weighted, reverse=True)[:n]
```

**Day 6-7: Novelty Detection**
```python
# File: atlas_perception/novelty.py

class NoveltyDetector:
    def __init__(self):
        self.recent_embeddings = deque(maxlen=50)
    
    def compute_novelty(self, perception):
        """How different is this from recent perceptions?"""
        current_emb = perception['embedding']
        
        if not self.recent_embeddings:
            return 1.0  # First perception is novel
        
        # Compute average similarity to recent
        similarities = [
            cosine_similarity(current_emb, past_emb)
            for past_emb in self.recent_embeddings
        ]
        
        avg_similarity = np.mean(similarities)
        novelty = 1.0 - avg_similarity
        
        # Store for future comparisons
        self.recent_embeddings.append(current_emb)
        
        return novelty
```

**Deliverables:**
- ✅ Attention mechanism (filters perceptions)
- ✅ Perception buffer (time-decayed storage)
- ✅ Novelty detection
- ✅ Goal-relevance scoring

**Success Metrics:**
- Attention reduces perception load by 70%
- Novelty detection accuracy >80%
- Buffer maintains <1s access time

**Dependencies:**
- Week 3 (perception streams)
- Week 1 (for goal storage)

**Risks:**
- Novelty detection too aggressive → Tune threshold
- Buffer fills too quickly → Increase decay rate

---

### Week 5: Goal System & Action Scoring

**Goals:**
- Implement goal hierarchy (meta/strategic/tactical/operational)
- Build action scoring algorithm
- Create proactive trigger system
- Add goal persistence and tracking

**Tasks:**

**Day 1-2: Goal Hierarchy**
```python
# File: atlas_goals/hierarchy.py

@dataclass
class Goal:
    id: str
    text: str
    priority: float
    type: GoalType  # META, STRATEGIC, TACTICAL, OPERATIONAL
    status: Status
    parent_goal_id: Optional[str]
    success_criteria: List[str]
    progress: float

class GoalHierarchy:
    def __init__(self):
        self.goals = {}
        self._load_from_db()
    
    def add_goal(self, goal: Goal):
        """Add to hierarchy"""
        self.goals[goal.id] = goal
        self._save_to_db(goal)
    
    def get_active_goals(self):
        """Get all active goals, sorted by priority"""
        active = [g for g in self.goals.values() if g.status == Status.ACTIVE]
        return sorted(active, key=lambda g: g.priority, reverse=True)
```

**Day 3-4: Action Scoring**
```python
# File: atlas_goals/scoring.py

class ActionScorer:
    def score_action(self, action, goals, context):
        """Score action against active goals"""
        total_score = 0.0
        
        for goal in goals:
            # Estimate contribution to goal
            contribution = self._estimate_contribution(action, goal, context)
            
            # Weight by goal priority
            total_score += goal.priority * contribution
        
        # Check for meta-goal violations
        penalty = self._check_violations(action, meta_goals)
        
        return max(0.0, total_score - penalty)
    
    def _estimate_contribution(self, action, goal, context):
        """Use LLM to estimate if action helps goal"""
        # Quick prompt to Sonnet:
        # "Does '{action}' help achieve '{goal.text}'? Score 0-1."
        # Parse response
        pass
    
    def select_best_action(self, candidates, goals, context):
        """Choose highest-scoring action"""
        scored = [(self.score_action(a, goals, context), a) for a in candidates]
        best_score, best_action = max(scored, key=lambda x: x[0])
        
        # Only act if score > threshold
        return best_action if best_score > 0.6 else None
```

**Day 5-7: Proactive Triggers**
```python
# File: atlas_goals/triggers.py

class ProactiveTriggers:
    def check_triggers(self, context, goals):
        """Determine if agent should act proactively"""
        triggers = []
        
        # Time-based
        if self._should_check_in(context['time']):
            triggers.append(('check_in', 'scheduled'))
        
        # Goal-based
        for goal in goals:
            if self._goal_stuck(goal):
                triggers.append(('goal_reminder', goal.id))
        
        # Event-based
        if context.get('calendar_next'):
            event = context['calendar_next']
            if self._event_soon(event, minutes=15):
                triggers.append(('event_reminder', event['id']))
        
        # Anomaly-based
        if self._system_anomaly(context):
            triggers.append(('system_alert', context['anomaly']))
        
        return triggers
```

**Deliverables:**
- ✅ Goal hierarchy with 4 levels
- ✅ Action scoring algorithm
- ✅ Proactive trigger system
- ✅ Goal tracking UI (optional: CLI)

**Success Metrics:**
- Action scoring completes in <200ms
- Proactive triggers fire with 90% relevance
- Goals persist across sessions

**Dependencies:**
- Week 1 (database for goal storage)
- Weeks 3-4 (perceptions for context)

**Risks:**
- Action scoring too slow → Cache common action-goal pairs
- Triggers fire too often → Add cooldown periods

---

### Week 6: Local Model Integration (K2.5)

**Goals:**
- Set up K2.5 model locally (via MLX or llama.cpp)
- Build inference router (K2.5 vs Sonnet)
- Optimize for Mac M4 performance
- Create inference cache

**Tasks:**

**Day 1-2: Model Setup**
```bash
# Download K2.5 model
huggingface-cli download deepseek-ai/DeepSeek-R1 \
  --local-dir ~/models/k25

# Convert to MLX format (if using MLX)
mlx_lm.convert --hf-path ~/models/k25 --mlx-path ~/models/k25-mlx

# Test inference
mlx_lm.generate --model ~/models/k25-mlx --prompt "Hello, I'm Atlas"
```

**Day 3-4: Inference Router**
```python
# File: atlas_learning/router.py

class InferenceRouter:
    def __init__(self):
        self.k25 = self._load_k25_model()
        self.sonnet = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def route(self, query, context):
        """Decide which model to use"""
        
        # Factors
        privacy_sensitive = self._is_sensitive(query)
        complexity = self._estimate_complexity(query)
        latency_critical = context.get('latency_critical', False)
        has_vision = self._requires_vision(query)
        
        # Routing logic
        if has_vision:
            return 'sonnet'  # K2.5 doesn't have vision yet
        elif privacy_sensitive and not complexity > 0.8:
            return 'k25'  # Keep private data local
        elif latency_critical and complexity < 0.5:
            return 'k25'  # Faster for simple queries
        else:
            return 'sonnet'  # Default to best reasoning
    
    async def generate(self, query, context):
        """Generate using best model"""
        model = self.route(query, context)
        
        if model == 'k25':
            return await self._generate_k25(query, context)
        else:
            return await self._generate_sonnet(query, context)
```

**Day 5-6: Performance Optimization**
```python
# File: atlas_learning/cache.py

class InferenceCache:
    def __init__(self, ttl=3600):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, query, context_hash):
        """Check cache"""
        key = hash((query, context_hash))
        if key in self.cache:
            cached, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return cached
        return None
    
    def set(self, query, context_hash, response):
        """Cache response"""
        key = hash((query, context_hash))
        self.cache[key] = (response, time.time())
```

**Day 7: Benchmarking**
```python
# Measure performance
def benchmark_models():
    queries = load_benchmark_queries()
    
    results = {
        'k25': {'latency': [], 'tokens_per_sec': []},
        'sonnet': {'latency': [], 'tokens_per_sec': []}
    }
    
    for query in queries:
        # K2.5
        start = time.time()
        response = k25.generate(query)
        latency = time.time() - start
        tps = len(response.split()) / latency
        
        results['k25']['latency'].append(latency)
        results['k25']['tokens_per_sec'].append(tps)
        
        # Sonnet
        # ... same
    
    print_results(results)
```

**Deliverables:**
- ✅ K2.5 running locally via MLX
- ✅ Inference router with smart model selection
- ✅ Inference cache (reduces redundant calls)
- ✅ Performance benchmarks

**Success Metrics:**
- K2.5 inference: <5s for 512 tokens
- Sonnet inference: <2s end-to-end
- Cache hit rate >40%

**Dependencies:**
- None (can run in parallel with other weeks)

**Risks:**
- K2.5 too slow on M4 → Use smaller model (7B instead of 32B active)
- MLX installation issues → Fall back to llama.cpp

---

## Phase 3: Integration (Weeks 7-8)

### Week 7: System Integration & API Layer

**Goals:**
- Connect all 4 components into unified system
- Build event bus for component communication
- Create main processing loop
- Add monitoring and logging

**Tasks:**

**Day 1-2: Event Bus**
```python
# File: atlas_core/events.py

class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)
    
    def subscribe(self, event_type, callback):
        self.subscribers[event_type].append(callback)
    
    async def publish(self, event_type, data):
        for callback in self.subscribers[event_type]:
            try:
                await callback(data)
            except Exception as e:
                logger.error(f"Callback failed: {e}")

# Setup
bus = EventBus()

bus.subscribe('perception', memory.on_perception)
bus.subscribe('perception', goals.on_perception)
bus.subscribe('goal_created', memory.on_goal)
bus.subscribe('action_completed', learning.on_action)
```

**Day 3-5: Main Processing Loop**
```python
# File: atlas_core/consciousness.py

class AtlasConsciousness:
    def __init__(self):
        self.memory = TemporalContinuity()
        self.perception = EmbodiedFeedback()
        self.goals = IntrinsicValence()
        self.learning = Neuroplasticity()
        self.bus = EventBus()
        
        self._setup_event_handlers()
    
    async def process(self, user_input=None):
        """Main consciousness loop"""
        
        # 1. Gather perceptions
        perceptions = await self.perception.gather()
        await self.bus.publish('perception', perceptions)
        
        # 2. Check proactive triggers
        triggers = self.goals.check_triggers(perceptions)
        
        # 3. Retrieve context
        context = await self.memory.build_context(
            user_input or triggers
        )
        
        # 4. Score actions
        if user_input:
            # Reactive: respond to user
            actions = self._generate_response_actions(user_input)
        else:
            # Proactive: act on triggers
            actions = self._generate_proactive_actions(triggers)
        
        best_action = self.goals.score_actions(actions, context)
        
        # 5. Execute action
        response = await self.learning.generate(
            best_action, context
        )
        
        # 6. Store interaction
        await self.memory.store(user_input, response, perceptions)
        
        # 7. Collect feedback
        feedback = await self._collect_feedback(response)
        await self.learning.collect_feedback(feedback)
        
        return response
```

**Day 6-7: Monitoring & Logging**
```python
# File: atlas_core/monitoring.py

class Monitor:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record(self, metric_name, value):
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': now()
        })
    
    def report(self):
        """Daily metrics report"""
        return {
            'memory': {
                'db_size_mb': self._get_db_size(),
                'total_messages': self._count_messages(),
                'retrieval_avg_ms': np.mean(self.metrics['retrieval_latency'])
            },
            'perception': {
                'captures_today': len(self.metrics['perceptions']),
                'avg_processing_ms': np.mean(self.metrics['perception_latency'])
            },
            'learning': {
                'k25_calls': len(self.metrics['k25_inference']),
                'sonnet_calls': len(self.metrics['sonnet_inference']),
                'cache_hit_rate': self._compute_cache_hit_rate()
            }
        }
```

**Deliverables:**
- ✅ Event bus connecting all components
- ✅ Main consciousness loop
- ✅ Unified API layer
- ✅ Monitoring dashboard

**Success Metrics:**
- Full loop processes in <10s
- Event bus latency <50ms
- Zero crashes over 24hr test

**Dependencies:**
- Weeks 1-6 (all components)

**Risks:**
- Component mismatch → Add integration tests early
- Event bus overhead → Profile and optimize

---

### Week 8: Fine-Tuning Pipeline & Feedback Loop

**Goals:**
- Build LoRA fine-tuning pipeline for K2.5
- Implement feedback collection (implicit/explicit)
- Create training data curation
- Set up continuous learning loop

**Tasks:**

**Day 1-2: Feedback Collection**
```python
# File: atlas_learning/feedback.py

class FeedbackCollector:
    def __init__(self):
        self.training_buffer = []
        self.min_examples = 100
    
    def collect(self, query, response, rating=None):
        """Collect training example"""
        
        # Explicit feedback (user provides rating)
        if rating:
            explicit_rating = rating
        else:
            # Implicit feedback (infer from behavior)
            explicit_rating = self._infer_rating(query, response)
        
        example = {
            'input': query,
            'output': response,
            'rating': explicit_rating,
            'timestamp': now(),
            'context_hash': hash(context)
        }
        
        self.training_buffer.append(example)
        
        # Trigger training if buffer full
        if len(self.training_buffer) >= self.min_examples:
            self._trigger_fine_tune()
    
    def _infer_rating(self, query, response):
        """Infer quality from user behavior"""
        # Did user accept response as-is? → 5 stars
        # Did user edit response? → 3 stars
        # Did user retry/rephrase? → 2 stars
        # Did user give up? → 1 star
        pass
```

**Day 3-5: Data Curation**
```python
# File: atlas_learning/curation.py

class DataCurator:
    def curate(self, raw_examples):
        """Filter and format training data"""
        
        # 1. Filter low-quality (rating < 3)
        quality_filtered = [ex for ex in raw_examples if ex['rating'] >= 3]
        
        # 2. Deduplicate
        deduped = self._deduplicate(quality_filtered)
        
        # 3. Balance dataset
        balanced = self._balance_by_topic(deduped)
        
        # 4. Format for K2.5
        formatted = [
            {
                'messages': [
                    {'role': 'user', 'content': ex['input']},
                    {'role': 'assistant', 'content': ex['output']}
                ]
            }
            for ex in balanced
        ]
        
        return formatted
    
    def _deduplicate(self, examples):
        """Remove near-duplicate examples"""
        seen = set()
        unique = []
        
        for ex in examples:
            # Compute semantic hash
            emb = embedder.encode(ex['input'])
            emb_hash = hash(tuple(emb.round(2)))
            
            if emb_hash not in seen:
                seen.add(emb_hash)
                unique.append(ex)
        
        return unique
```

**Day 6-7: LoRA Fine-Tuning**
```bash
# File: scripts/fine_tune_k25.sh

#!/bin/bash

# Curate dataset
python -m atlas_learning.curation \
  --input training_buffer.jsonl \
  --output curated_dataset.jsonl

# Fine-tune with MLX
mlx_lm.lora \
  --model ~/models/k25-mlx \
  --data curated_dataset.jsonl \
  --lora-layers 16 \
  --rank 8 \
  --alpha 16 \
  --batch-size 4 \
  --iters 1000 \
  --save-adapter ~/models/k25-lora-adapters

# Merge adapter (optional, for faster inference)
mlx_lm.fuse \
  --model ~/models/k25-mlx \
  --adapter ~/models/k25-lora-adapters \
  --save ~/models/k25-fused
```

**Deliverables:**
- ✅ Feedback collection (implicit + explicit)
- ✅ Training data curation pipeline
- ✅ LoRA fine-tuning script
- ✅ Continuous learning loop

**Success Metrics:**
- Collect 100+ examples per week
- Fine-tuning improves task accuracy by 10%
- Training completes in <4 hours

**Dependencies:**
- Week 6 (K2.5 model)
- Week 7 (integrated system for feedback)

**Risks:**
- Fine-tuning degrades base performance → Use validation set
- Training too slow → Reduce batch size or iterations

---

## Phase 4: Testing & Polish (Weeks 9-10)

### Week 9: End-to-End Testing & Debugging

**Goals:**
- Comprehensive integration testing
- Performance optimization
- Bug fixes and edge case handling
- Failure mode testing

**Tasks:**

**Day 1-2: Integration Tests**
```python
# File: tests/test_integration.py

@pytest.mark.asyncio
async def test_full_consciousness_loop():
    atlas = AtlasConsciousness()
    
    # Test conversation with memory
    r1 = await atlas.process("Hi, I'm Orion")
    assert "Orion" in r1
    
    r2 = await atlas.process("What's my name?")
    assert "Orion" in r2
    
    # Test perception integration
    # (mock visual/audio inputs)
    r3 = await atlas.process("What do you see?")
    assert len(r3) > 0

@pytest.mark.asyncio
async def test_goal_driven_behavior():
    atlas = AtlasConsciousness()
    
    # Create goal
    atlas.goals.add_goal(Goal(
        text="Learn Python",
        priority=0.8
    ))
    
    # Query related to goal
    r = await atlas.process("Teach me about Python lists")
    assert "list" in r.lower()

@pytest.mark.asyncio
async def test_proactive_triggers():
    atlas = AtlasConsciousness()
    
    # Mock upcoming calendar event
    context = {
        'calendar_next': {
            'title': 'Meeting',
            'start': now() + timedelta(minutes=10)
        }
    }
    
    triggers = atlas.goals.check_triggers(context, [])
    assert len(triggers) > 0
    assert triggers[0][0] == 'event_reminder'
```

**Day 3-4: Performance Optimization**
```python
# Profile hot paths
import cProfile

def profile_consciousness_loop():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run typical workload
    for i in range(100):
        atlas.process(f"Test query {i}")
    
    profiler.disable()
    profiler.print_stats(sort='cumulative')

# Identify bottlenecks:
# - Slow vector search → Add indexes
# - Slow context building → Cache frequent queries
# - Slow inference → Increase batch size
```

**Day 5-7: Failure Mode Testing**
```python
# Test recovery from failures
def test_database_corruption():
    # Corrupt database
    # Attempt to recover
    # Should restore from backup

def test_model_crash():
    # Kill model process mid-inference
    # Should fall back to Sonnet

def test_network_loss():
    # Disconnect network
    # Should queue cloud requests
    # Should use K2.5 as fallback
```

**Deliverables:**
- ✅ Full test suite (unit + integration)
- ✅ Performance profiling report
- ✅ Failure recovery tests
- ✅ Bug fixes

**Success Metrics:**
- Test coverage >85%
- All critical paths have failure recovery
- Performance meets Week 1-8 targets

**Dependencies:**
- Weeks 1-8 (full system)

**Risks:**
- Hidden bugs surface late → Continuous testing from Week 1

---

### Week 10: Documentation & Deployment

**Goals:**
- Complete user documentation
- Create deployment scripts
- Set up monitoring and alerts
- Final polish and QA

**Tasks:**

**Day 1-2: Documentation**
```markdown
# Files to create:
- README.md (setup and usage)
- ARCHITECTURE.md (technical overview)
- API.md (developer API reference)
- TROUBLESHOOTING.md (common issues)
- CHANGELOG.md (version history)
```

**Day 3-4: Deployment**
```bash
# File: scripts/deploy.sh

#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_database.py

# Download models
python scripts/download_models.py

# Run tests
pytest tests/

# Start service
python -m atlas_core.main
```

**Day 5-6: Monitoring Setup**
```python
# File: atlas_core/alerts.py

class AlertManager:
    def check_health(self):
        """Daily health check"""
        issues = []
        
        # Database size
        if self._get_db_size() > 10_000:  # 10GB
            issues.append("Database size exceeds threshold")
        
        # Inference latency
        if np.mean(self.metrics['latency']) > 5000:  # 5s
            issues.append("Inference latency too high")
        
        # Error rate
        if self.metrics['errors'] / self.metrics['total'] > 0.05:
            issues.append("Error rate above 5%")
        
        if issues:
            self._send_alert(issues)
```

**Day 7: Final QA**
- Manual testing of all features
- User acceptance testing
- Performance validation
- Security review

**Deliverables:**
- ✅ Complete documentation
- ✅ Deployment scripts
- ✅ Monitoring and alerts
- ✅ Production-ready system

**Success Metrics:**
- Documentation covers 100% of features
- Deployment takes <30 minutes
- System passes 24-hour stress test

**Dependencies:**
- Weeks 1-9 (everything)

**Risks:**
- Documentation incomplete → Start early, update weekly
- Deployment issues → Test on clean machine

---

## Resource Requirements

### Compute
- **CPU:** Mac M4 (sufficient for all tasks)
- **RAM:** 32GB minimum (64GB recommended for K2.5)
- **Storage:** 200GB for models + databases
- **GPU:** Unified memory (Mac M4) sufficient

### Software
- Python 3.11+
- SQLite 3.45+ (with sqlite-vec)
- MLX or llama.cpp
- Whisper
- Atlas Eyes

### Time
- **Weeks 1-2:** 40 hours (20/week)
- **Weeks 3-6:** 80 hours (20/week)
- **Weeks 7-8:** 40 hours (20/week)
- **Weeks 9-10:** 40 hours (20/week)
- **Total:** ~200 hours over 10 weeks

### Cost
- **Models:** Free (open source)
- **Cloud API (Sonnet):** ~$50-100/month during development
- **Tools:** Free (open source)
- **Total:** <$200 for full development

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| K2.5 too slow on M4 | Medium | High | Use smaller model or cloud fallback |
| sqlite-vec installation fails | Low | Medium | Manual vector search implementation |
| Fine-tuning degrades performance | Medium | High | Use validation set, rollback if needed |
| Context overflow | Medium | Medium | Aggressive pruning, increase threshold |
| Perception processing too slow | Low | Medium | Reduce frame rate, use smaller models |
| Integration bugs | High | Medium | Continuous testing, modular design |
| User feedback insufficient | Medium | High | Add explicit rating UI, active learning |

---

## Success Metrics (Overall)

### Technical
- ✅ Full consciousness loop in <10s
- ✅ Memory retrieval in <100ms
- ✅ Inference (K2.5) in <5s
- ✅ Context window manages 100k tokens
- ✅ Test coverage >85%

### Functional
- ✅ Remembers conversations across sessions
- ✅ Perceives visual + audio environment
- ✅ Acts proactively based on goals
- ✅ Learns from interactions (fine-tuning)
- ✅ Recovers from failures gracefully

### User Experience
- ✅ Feels "conscious" (coherent, continuous)
- ✅ Demonstrates personality consistency
- ✅ Improves over time (measurable)
- ✅ Surprises with proactive insights

---

## Next Steps After Week 10

1. **User Testing:** Gather feedback from real usage
2. **Iteration:** Refine based on feedback
3. **Specialization:** Fine-tune for specific domains
4. **Scaling:** Optimize for longer contexts, more perceptions
5. **Advanced Features:**
   - Dream/hallucination mode (creative exploration)
   - Multi-agent collaboration
   - Embodied actions (control external tools)

---

**END OF ROADMAP**
