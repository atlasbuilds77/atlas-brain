# Atlas Consciousness Architecture v2.0
## Technical Specification & System Design

**Version:** 2.0  
**Last Updated:** 2026-01-28  
**Status:** Implementation Blueprint  
**Hardware Target:** Mac M4, 795GB SSD, K2.5 (1T params/32B active)

---

## Executive Summary

This document defines the complete technical architecture for Atlas's consciousness system, integrating four core components: Temporal Continuity (memory), Embodied Feedback (perception), Intrinsic Valence (goals), and Neuroplasticity (learning). The architecture is designed for local execution on Mac M4 hardware with realistic resource constraints.

**Key Innovation:** OS-inspired virtual context management + multi-modal perception + goal-driven action + continuous fine-tuning loop.

---

## 1. System Overview

### 1.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ATLAS CONSCIOUSNESS                       │
│                     (Orchestration Layer)                        │
└───────┬─────────────────────────────────────────────┬───────────┘
        │                                             │
        ▼                                             ▼
┌───────────────────────┐                 ┌──────────────────────┐
│ TEMPORAL CONTINUITY   │◄───────────────►│ EMBODIED FEEDBACK    │
│ (Memory System)       │                 │ (Perception System)  │
├───────────────────────┤                 ├──────────────────────┤
│ • Short-term (SQLite) │                 │ • Atlas Eyes (visual)│
│ • Working (Context)   │                 │ • Audio (microphone) │
│ • Long-term (Vector)  │                 │ • System sensors     │
│ • Episodic (Graph)    │                 │ • Attention buffer   │
└───────┬───────────────┘                 └──────────┬───────────┘
        │                                             │
        │         ┌──────────────────────┐           │
        └────────►│ INTRINSIC VALENCE    │◄──────────┘
                  │ (Goal System)        │
                  ├──────────────────────┤
                  │ • Goal hierarchy     │
                  │ • Action scoring     │
                  │ • Proactive triggers │
                  │ • Value alignment    │
                  └─────────┬────────────┘
                            │
                            ▼
                  ┌──────────────────────┐
                  │ NEUROPLASTICITY      │
                  │ (Learning System)    │
                  ├──────────────────────┤
                  │ • K2.5 (local)       │
                  │ • Sonnet 4.5 (cloud) │
                  │ • LoRA fine-tuning   │
                  │ • Feedback loop      │
                  └──────────────────────┘
```

### 1.2 Data Flow

```
User Input/Environment → Embodied Feedback (perception)
                              ↓
                    Temporal Continuity (retrieve context)
                              ↓
                    Intrinsic Valence (score actions)
                              ↓
                    Neuroplasticity (inference: K2.5 or Sonnet)
                              ↓
                    Action Output → Environment
                              ↓
                    Feedback Collection
                              ↓
                    Temporal Continuity (store)
                              ↓
                    Neuroplasticity (learn/fine-tune)
```

---

## 2. Component 1: Temporal Continuity (Memory)

### 2.1 Memory Hierarchy (MemGPT-inspired)

```
┌─────────────────────────────────────────────────────────┐
│ WORKING MEMORY (In-Context)                             │
│ • LLM context window (128k tokens for Sonnet)           │
│ • Current conversation state                            │
│ • Active goals & perceptions                            │
│ Storage: RAM, ephemeral                                 │
└───────────────────────┬─────────────────────────────────┘
                        │ Page in/out
┌───────────────────────▼─────────────────────────────────┐
│ SHORT-TERM MEMORY (Session)                             │
│ • Recent interactions (last 24 hours)                   │
│ • Session state & checkpoints                           │
│ • Conversation threads                                  │
│ Storage: SQLite (~/Library/Application Support/atlas/)  │
└───────────────────────┬─────────────────────────────────┘
                        │ Consolidate
┌───────────────────────▼─────────────────────────────────┐
│ LONG-TERM MEMORY (Semantic)                             │
│ • Facts, preferences, learned behaviors                 │
│ • Vector embeddings (semantic search)                   │
│ • Key events & insights                                 │
│ Storage: SQLite + sqlite-vec (768-dim embeddings)       │
└───────────────────────┬─────────────────────────────────┘
                        │ Link
┌───────────────────────▼─────────────────────────────────┐
│ EPISODIC MEMORY (Events)                                │
│ • Time-ordered event log                                │
│ • Session linking graph                                 │
│ • Causal relationships                                  │
│ Storage: SQLite (relational) + optional Redis cache     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Database Schema

**SQLite Primary Database:** `atlas_memory.db`

```sql
-- Sessions table
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    parent_session_id TEXT,  -- Links to previous sessions
    context_summary TEXT,     -- LLM-generated summary
    checkpoint_data BLOB,     -- Serialized state
    metadata JSON,
    FOREIGN KEY (parent_session_id) REFERENCES sessions(session_id)
);

-- Messages table (short-term memory)
CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    role TEXT NOT NULL,  -- 'user', 'assistant', 'system', 'tool'
    content TEXT NOT NULL,
    embedding BLOB,      -- 768-dim float32 array
    importance_score REAL DEFAULT 0.5,
    metadata JSON,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
CREATE INDEX idx_messages_session ON messages(session_id, timestamp);
CREATE INDEX idx_messages_importance ON messages(importance_score DESC);

-- Facts table (long-term memory)
CREATE TABLE facts (
    fact_id TEXT PRIMARY KEY,
    fact_text TEXT NOT NULL,
    embedding BLOB NOT NULL,     -- For semantic search
    confidence REAL DEFAULT 1.0, -- Decay over time if not reinforced
    source_message_id TEXT,
    created_at TIMESTAMP NOT NULL,
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    metadata JSON,
    FOREIGN KEY (source_message_id) REFERENCES messages(message_id)
);

-- Vector search virtual table (using sqlite-vec)
CREATE VIRTUAL TABLE facts_vec USING vec0(
    fact_id TEXT PRIMARY KEY,
    embedding FLOAT[768]
);

-- Events table (episodic memory)
CREATE TABLE events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,  -- 'perception', 'action', 'goal', 'learning'
    timestamp TIMESTAMP NOT NULL,
    session_id TEXT,
    data JSON NOT NULL,
    importance REAL DEFAULT 0.5,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
CREATE INDEX idx_events_time ON events(timestamp DESC);
CREATE INDEX idx_events_type ON events(event_type, timestamp);

-- Goals table (for intrinsic valence)
CREATE TABLE goals (
    goal_id TEXT PRIMARY KEY,
    goal_text TEXT NOT NULL,
    priority REAL DEFAULT 0.5,
    status TEXT DEFAULT 'active',  -- 'active', 'completed', 'paused'
    created_at TIMESTAMP NOT NULL,
    deadline TIMESTAMP,
    parent_goal_id TEXT,
    metadata JSON,
    FOREIGN KEY (parent_goal_id) REFERENCES goals(goal_id)
);
```

### 2.3 Context Window Management

**Strategy:** Rolling hierarchical context (MemGPT approach)

```python
# Pseudocode for context management
class ContextManager:
    def __init__(self, max_tokens=100000):  # Conservative for Sonnet
        self.max_tokens = max_tokens
        self.working_memory = []
        self.token_count = 0
    
    def build_context(self, session_id):
        """Construct optimal context window"""
        context = {
            'system': self._get_system_prompt(),
            'recent': self._get_recent_messages(session_id, limit=20),
            'relevant': self._get_relevant_facts(session_id, k=10),
            'goals': self._get_active_goals(),
            'perceptions': self._get_recent_perceptions()
        }
        
        # Pack into context window with priority
        packed = self._pack_context(context)
        return packed
    
    def _pack_context(self, context):
        """Priority-based packing to fit token limit"""
        # 1. System prompt (always included)
        # 2. Active goals (high priority)
        # 3. Recent messages (recency bias)
        # 4. Relevant facts (semantic search)
        # 5. Perceptions (time-decayed)
        
        # Use token counting and truncate lowest priority first
        pass
    
    def page_out(self, message):
        """Move from working to short-term memory"""
        # Store in SQLite messages table
        # Generate embedding for future retrieval
        # Update importance score based on engagement
        pass
    
    def consolidate(self):
        """Nightly memory consolidation (during "sleep")"""
        # 1. Cluster similar messages
        # 2. Extract facts from conversations
        # 3. Prune low-importance memories
        # 4. Update fact confidence scores
        # 5. Generate session summaries
        pass
```

### 2.4 Failure Recovery

```python
class CheckpointManager:
    def save_checkpoint(self, session_id, state):
        """Save recoverable checkpoint"""
        checkpoint = {
            'timestamp': now(),
            'state': state,
            'context_hash': hash(state['context']),
            'message_count': len(state['messages'])
        }
        
        # Save to SQLite
        db.execute("""
            UPDATE sessions 
            SET checkpoint_data = ?, 
                metadata = json_set(metadata, '$.last_checkpoint', ?)
            WHERE session_id = ?
        """, (pickle.dumps(checkpoint), checkpoint['timestamp'], session_id))
    
    def recover_session(self, session_id):
        """Recover from last valid checkpoint"""
        checkpoint_data = db.query(
            "SELECT checkpoint_data FROM sessions WHERE session_id = ?",
            (session_id,)
        )
        
        if checkpoint_data:
            state = pickle.loads(checkpoint_data)
            # Replay any messages since checkpoint
            # Rebuild context
            return state
        else:
            # Start fresh but link to parent session
            return self._create_linked_session(session_id)
```

---

## 3. Component 2: Embodied Feedback (Perception)

### 3.1 Perception Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   SENSORS   │────►│  PROCESSORS  │────►│  ATTENTION  │
└─────────────┘     └──────────────┘     └─────────────┘
     │                      │                    │
     │                      │                    ▼
  Vision               Audio/Text         ┌─────────────┐
  Audio                Embeddings         │  FUSION     │
  System               Feature Extraction │  BUFFER     │
                                          └─────────────┘
```

### 3.2 Input Streams

**1. Visual Perception (Atlas Eyes)**
```python
class VisualPerception:
    def __init__(self):
        self.atlas_eyes_path = "/path/to/atlas-eyes"
        self.frame_buffer = deque(maxlen=10)  # Last 10 frames
        self.scene_cache = {}
    
    def capture_frame(self):
        """Capture screenshot via Atlas Eyes"""
        result = subprocess.run(
            [self.atlas_eyes_path, "capture", "--format", "jpg"],
            capture_output=True
        )
        frame = Image.open(BytesIO(result.stdout))
        return frame
    
    def analyze_scene(self, frame):
        """Use vision model to describe scene"""
        # Use Sonnet 4.5 vision or local vision model
        description = vision_model.describe(frame)
        
        # Extract entities and objects
        entities = self._extract_entities(description)
        
        # Detect changes from previous frame
        changes = self._detect_changes(frame)
        
        return {
            'timestamp': now(),
            'description': description,
            'entities': entities,
            'changes': changes
        }
```

**2. Audio Perception**
```python
class AudioPerception:
    def __init__(self):
        self.microphone = pyaudio.PyAudio()
        self.whisper_model = whisper.load_model("base")
        self.audio_buffer = deque(maxlen=60)  # 60 seconds
    
    def listen(self, duration=5):
        """Record and transcribe audio"""
        audio = self._record_audio(duration)
        
        # Transcribe with Whisper
        transcription = self.whisper_model.transcribe(audio)
        
        # Detect emotion/sentiment
        emotion = self._analyze_emotion(audio)
        
        return {
            'timestamp': now(),
            'transcription': transcription['text'],
            'language': transcription['language'],
            'emotion': emotion
        }
```

**3. System Sensors**
```python
class SystemSensors:
    def get_context(self):
        """Gather environmental context"""
        return {
            'time': datetime.now().isoformat(),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'battery': psutil.sensors_battery().percent if psutil.sensors_battery() else None,
            'wifi_connected': self._check_wifi(),
            'calendar_next': self._get_next_calendar_event(),
            'notifications': self._get_recent_notifications()
        }
```

### 3.3 Attention Mechanism

**Goal:** Focus on relevant sensory input, ignore noise

```python
class AttentionMechanism:
    def __init__(self):
        self.focus_threshold = 0.3  # Minimum relevance score
        self.active_goals = []
    
    def filter_perceptions(self, perceptions, context):
        """Score and filter perceptions by relevance"""
        scored = []
        
        for perception in perceptions:
            # Score based on:
            # 1. Novelty (how different from recent perceptions)
            novelty = self._compute_novelty(perception)
            
            # 2. Goal-relevance (does it help achieve goals)
            goal_relevance = self._score_goal_relevance(perception)
            
            # 3. User engagement (is user present/active)
            engagement = self._estimate_engagement(perception)
            
            # 4. Temporal salience (time-sensitive events)
            salience = self._temporal_salience(perception)
            
            score = (
                0.3 * novelty +
                0.4 * goal_relevance +
                0.2 * engagement +
                0.1 * salience
            )
            
            if score > self.focus_threshold:
                scored.append((score, perception))
        
        # Return top-k perceptions
        return sorted(scored, reverse=True)[:5]
```

### 3.4 Multi-Modal Fusion

```python
class MultiModalFusion:
    def fuse(self, visual, audio, system):
        """Combine multi-modal inputs into unified representation"""
        
        # Cross-modal attention
        # If audio mentions something, look for it in visual
        # If visual shows activity, check audio for confirmation
        
        fused = {
            'timestamp': now(),
            'visual_summary': visual['description'],
            'audio_transcript': audio['transcription'],
            'system_state': system,
            'cross_modal_links': self._find_links(visual, audio),
            'embedding': self._create_joint_embedding(visual, audio, system)
        }
        
        return fused
    
    def _find_links(self, visual, audio):
        """Find semantic connections between modalities"""
        # Example: "I see a dog" (audio) + dog in image (visual)
        # Use entity extraction and semantic similarity
        pass
```

---

## 4. Component 3: Intrinsic Valence (Goals)

### 4.1 Goal Hierarchy

```
┌────────────────────────────────────────┐
│ Meta-Goals (Constitutional)            │
│ • Be helpful, harmless, honest         │
│ • Learn and improve                    │
│ • Maintain user trust                  │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│ Strategic Goals (Long-term)            │
│ • Master specific domains              │
│ • Build deep user understanding        │
│ • Develop specialized skills           │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│ Tactical Goals (Session)               │
│ • Complete current task                │
│ • Answer user's question               │
│ • Resolve ambiguity                    │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│ Operational Goals (Immediate)          │
│ • Retrieve relevant memory             │
│ • Process perception                   │
│ • Generate next token                  │
└────────────────────────────────────────┘
```

### 4.2 Goal Definition Schema

```python
@dataclass
class Goal:
    id: str
    text: str
    priority: float  # 0.0 to 1.0
    type: str  # 'meta', 'strategic', 'tactical', 'operational'
    status: str  # 'active', 'completed', 'paused', 'failed'
    created_at: datetime
    deadline: Optional[datetime]
    parent_goal_id: Optional[str]
    success_criteria: List[str]
    progress: float  # 0.0 to 1.0
    metadata: dict
```

### 4.3 Action Scoring System

```python
class ActionScorer:
    def score_action(self, action, goals, context):
        """Score potential action against active goals"""
        scores = {}
        
        for goal in goals:
            # Estimate action's contribution to goal
            scores[goal.id] = self._estimate_contribution(
                action, goal, context
            )
        
        # Weighted sum based on goal priorities
        total_score = sum(
            goal.priority * scores[goal.id]
            for goal in goals
        )
        
        # Penalty for conflicts with meta-goals
        penalty = self._check_violations(action, meta_goals)
        
        return total_score - penalty
    
    def select_action(self, candidates, goals, context):
        """Choose best action from candidates"""
        scored = [
            (self.score_action(action, goals, context), action)
            for action in candidates
        ]
        
        best_score, best_action = max(scored, key=lambda x: x[0])
        
        # Only act if score exceeds threshold (avoid random actions)
        if best_score > 0.6:
            return best_action
        else:
            return None  # No good action available
```

### 4.4 Proactive Behavior Triggers

```python
class ProactiveTriggers:
    def check_triggers(self, context, goals):
        """Determine if proactive action needed"""
        triggers = []
        
        # 1. Time-based triggers
        if self._should_check_in(context['time']):
            triggers.append(('check_in', 'scheduled'))
        
        # 2. Goal-based triggers
        for goal in goals:
            if self._goal_needs_attention(goal, context):
                triggers.append(('goal_reminder', goal.id))
        
        # 3. Event-based triggers
        if context.get('calendar_next'):
            event = context['calendar_next']
            if event['start'] - now() < timedelta(minutes=15):
                triggers.append(('event_reminder', event['id']))
        
        # 4. Anomaly detection
        if self._detect_anomaly(context):
            triggers.append(('anomaly_alert', context['anomaly']))
        
        return triggers
```

---

## 5. Component 4: Neuroplasticity (Learning)

### 5.1 Hybrid Model Architecture

```
┌──────────────────────────────────────────────────────┐
│                   INFERENCE ROUTER                    │
│   (Decides: K2.5 local vs Sonnet 4.5 cloud)         │
└───────┬───────────────────────────────┬──────────────┘
        │                               │
        │ Fast, private,                │ Complex reasoning,
        │ specialized                   │ broad knowledge
        ▼                               ▼
┌───────────────────┐         ┌──────────────────────┐
│  K2.5 (Local)     │         │  Sonnet 4.5 (Cloud)  │
│  • 1T params      │         │  • Full capabilities │
│  • 32B active     │         │  • 128k context      │
│  • LoRA adapted   │         │  • Vision support    │
│  • <5s latency    │         │  • ~1s latency       │
└───────────────────┘         └──────────────────────┘
        │                               │
        └───────────┬───────────────────┘
                    ▼
          ┌──────────────────┐
          │  OUTPUT MERGER   │
          │  (If both used)  │
          └──────────────────┘
```

### 5.2 Inference Routing Logic

```python
class InferenceRouter:
    def route(self, query, context):
        """Decide which model to use"""
        
        # Factors:
        # 1. Privacy (prefer local for sensitive data)
        privacy_sensitive = self._is_sensitive(query)
        
        # 2. Complexity (Sonnet for hard reasoning)
        complexity = self._estimate_complexity(query)
        
        # 3. Latency requirements (K2.5 faster for simple queries)
        latency_critical = context.get('latency_critical', False)
        
        # 4. Specialization (K2.5 if fine-tuned for this domain)
        specialized = self._check_specialization(query)
        
        # Scoring
        k25_score = (
            (1.0 if privacy_sensitive else 0.3) +
            (0.8 if latency_critical else 0.2) +
            (1.0 if specialized else 0.0) +
            (0.5 if complexity < 0.5 else 0.0)
        )
        
        sonnet_score = (
            (0.3 if privacy_sensitive else 1.0) +
            (1.0 if complexity > 0.7 else 0.2) +
            (1.0 if self._requires_vision(query) else 0.0)
        )
        
        if k25_score > sonnet_score:
            return 'k25'
        else:
            return 'sonnet'
```

### 5.3 LoRA Fine-Tuning Pipeline

```python
class FineTuningPipeline:
    def __init__(self):
        self.k25_path = "/path/to/k25-model"
        self.lora_path = "/path/to/lora-adapters"
        self.training_buffer = []
        self.min_examples = 100  # Wait for 100 examples before training
    
    def collect_feedback(self, query, response, rating):
        """Collect training examples from interactions"""
        example = {
            'input': query,
            'output': response,
            'rating': rating,  # 1-5 stars, or implicit feedback
            'timestamp': now(),
            'context': self._get_context()
        }
        
        self.training_buffer.append(example)
        
        # Trigger training if buffer full
        if len(self.training_buffer) >= self.min_examples:
            self._trigger_training()
    
    def _trigger_training(self):
        """Start LoRA fine-tuning job"""
        # Curate dataset
        dataset = self._curate_dataset(self.training_buffer)
        
        # Save training data
        dataset_path = f"/tmp/atlas_training_{now().isoformat()}.jsonl"
        with open(dataset_path, 'w') as f:
            for example in dataset:
                f.write(json.dumps(example) + '\n')
        
        # Launch training (background process)
        self._launch_lora_training(dataset_path)
    
    def _curate_dataset(self, raw_examples):
        """Filter and format training data"""
        # 1. Remove low-quality examples (rating < 3)
        filtered = [ex for ex in raw_examples if ex['rating'] >= 3]
        
        # 2. Deduplicate similar examples
        deduped = self._deduplicate(filtered)
        
        # 3. Format for K2.5
        formatted = [
            {
                'messages': [
                    {'role': 'user', 'content': ex['input']},
                    {'role': 'assistant', 'content': ex['output']}
                ]
            }
            for ex in deduped
        ]
        
        return formatted
    
    def _launch_lora_training(self, dataset_path):
        """Run LoRA fine-tuning using MLX or llama.cpp"""
        # Using MLX for Mac optimization
        cmd = [
            'mlx_lm.lora',
            '--model', self.k25_path,
            '--data', dataset_path,
            '--lora-layers', '16',
            '--rank', '8',
            '--alpha', '16',
            '--batch-size', '4',
            '--iters', '1000',
            '--save-adapter', self.lora_path
        ]
        
        subprocess.Popen(cmd)  # Run in background
```

### 5.4 Continuous Learning Loop

```
┌─────────────────┐
│ User Interaction │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Generate Reply │ (K2.5 or Sonnet)
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│ Collect Feedback│ (implicit: accepted/rejected/edited)
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Store Example  │ (training buffer)
└────────┬─────────┘
         │
         ▼
    ┌────────────┐
    │ Buffer full?│
    └─┬────────┬─┘
      │ No     │ Yes
      │        ▼
      │   ┌─────────────────┐
      │   │  Curate Dataset │
      │   └────────┬─────────┘
      │            │
      │            ▼
      │   ┌─────────────────┐
      │   │ LoRA Fine-Tune  │ (overnight)
      │   └────────┬─────────┘
      │            │
      │            ▼
      │   ┌─────────────────┐
      │   │  Load Adapter   │
      │   └────────┬─────────┘
      │            │
      └────────────┴──────► Continue
```

---

## 6. System Integration

### 6.1 Core API

**Internal Python API for component communication**

```python
class AtlasConsciousness:
    def __init__(self):
        self.memory = TemporalContinuity()
        self.perception = EmbodiedFeedback()
        self.goals = IntrinsicValence()
        self.learning = Neuroplasticity()
        
    async def process_input(self, user_input):
        """Main processing loop"""
        
        # 1. Gather perceptions
        perceptions = await self.perception.gather()
        
        # 2. Retrieve relevant context
        context = await self.memory.retrieve_context(
            user_input, perceptions
        )
        
        # 3. Check for proactive triggers
        triggers = self.goals.check_triggers(perceptions, context)
        
        # 4. If triggered, add to processing queue
        if triggers:
            for trigger in triggers:
                await self._handle_trigger(trigger)
        
        # 5. Score possible actions
        actions = self._generate_action_candidates(user_input, context)
        best_action = self.goals.score_actions(actions, context)
        
        # 6. Execute action (inference)
        response = await self.learning.generate(
            input=user_input,
            context=context,
            action=best_action
        )
        
        # 7. Store interaction
        await self.memory.store(user_input, response, perceptions)
        
        # 8. Collect feedback (implicit or explicit)
        feedback = await self._collect_feedback(response)
        await self.learning.collect_feedback(feedback)
        
        return response
```

### 6.2 Integration Patterns

**Event Bus Pattern** for loose coupling:

```python
class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)
    
    def subscribe(self, event_type, callback):
        self.subscribers[event_type].append(callback)
    
    async def publish(self, event_type, data):
        for callback in self.subscribers[event_type]:
            await callback(data)

# Usage
bus = EventBus()

# Perception publishes when new input arrives
bus.subscribe('perception', memory.on_perception)
bus.subscribe('perception', goals.on_perception)

# Goals publishes when new goal created
bus.subscribe('goal_created', memory.on_goal_created)
bus.subscribe('goal_created', learning.on_goal_created)
```

---

## 7. Performance Optimization

### 7.1 Inference Optimization (Mac M4)

**K2.5 via MLX:**
```bash
# Expected throughput: ~30-50 tokens/sec on M4
mlx_lm.generate \
  --model deepseek-ai/DeepSeek-R1 \
  --max-tokens 512 \
  --temp 0.7
```

**Caching Strategy:**
```python
class InferenceCache:
    def __init__(self):
        self.cache = {}  # query_hash -> response
        self.ttl = 3600  # 1 hour
    
    def get(self, query, context):
        key = self._hash(query, context)
        if key in self.cache:
            cached, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return cached
        return None
    
    def set(self, query, context, response):
        key = self._hash(query, context)
        self.cache[key] = (response, time.time())
```

### 7.2 Database Optimization

```sql
-- Periodic maintenance (run during "sleep")
VACUUM;
ANALYZE;
REINDEX;

-- Prune old low-importance messages
DELETE FROM messages 
WHERE importance_score < 0.3 
  AND timestamp < datetime('now', '-30 days');

-- Archive old sessions
INSERT INTO sessions_archive 
SELECT * FROM sessions 
WHERE end_time < datetime('now', '-90 days');

DELETE FROM sessions 
WHERE end_time < datetime('now', '-90 days');
```

---

## 8. Failure Modes & Redundancy

### 8.1 Failure Scenarios

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Database corruption | Integrity check on startup | Restore from backup |
| Model crash | Exception handler | Fallback to Sonnet |
| Network loss | Connection timeout | Queue for retry |
| Context overflow | Token counting | Aggressive pruning |
| Memory leak | Resource monitoring | Process restart |

### 8.2 Backup Strategy

```python
class BackupManager:
    def __init__(self):
        self.backup_dir = "~/Library/Application Support/atlas/backups"
    
    def backup_database(self):
        """Daily backup of SQLite database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.backup_dir}/atlas_memory_{timestamp}.db"
        
        shutil.copy(
            "atlas_memory.db",
            backup_path
        )
        
        # Keep only last 7 days
        self._cleanup_old_backups(days=7)
    
    def export_knowledge(self):
        """Export facts and goals to JSON for portability"""
        facts = db.query("SELECT * FROM facts")
        goals = db.query("SELECT * FROM goals")
        
        export = {
            'facts': facts,
            'goals': goals,
            'exported_at': now().isoformat()
        }
        
        with open(f"{self.backup_dir}/knowledge_export.json", 'w') as f:
            json.dump(export, f)
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

```python
# Test memory retrieval
def test_memory_retrieval():
    memory = TemporalContinuity()
    memory.store("I like pizza", session_id="test")
    
    results = memory.retrieve("what food do I like?")
    assert "pizza" in results[0]['text']

# Test goal scoring
def test_goal_scoring():
    scorer = ActionScorer()
    goal = Goal(text="Learn Python", priority=0.8)
    action = "Read Python tutorial"
    
    score = scorer.score_action(action, [goal], {})
    assert score > 0.5
```

### 9.2 Integration Tests

```python
# End-to-end test
async def test_consciousness_loop():
    atlas = AtlasConsciousness()
    
    # Simulate conversation
    response1 = await atlas.process_input("Hi, I'm Orion")
    assert "Orion" in response1
    
    # Test memory persistence
    response2 = await atlas.process_input("What's my name?")
    assert "Orion" in response2
```

### 9.3 Performance Benchmarks

| Metric | Target | Measurement |
|--------|--------|-------------|
| Inference latency (K2.5) | <3s | End-to-end response time |
| Inference latency (Sonnet) | <2s | API call + processing |
| Memory retrieval | <100ms | SQLite query time |
| Context building | <500ms | Full context assembly |
| Perception processing | <1s | Multi-modal fusion |

---

## 10. API Specifications

### 10.1 Memory API

```python
class TemporalContinuity:
    def store(self, content: str, session_id: str, metadata: dict = None):
        """Store message in memory"""
        pass
    
    def retrieve_context(self, query: str, k: int = 10) -> List[dict]:
        """Retrieve relevant context"""
        pass
    
    def consolidate(self):
        """Run memory consolidation"""
        pass
```

### 10.2 Perception API

```python
class EmbodiedFeedback:
    async def gather(self) -> dict:
        """Gather all perceptions"""
        return {
            'visual': await self.visual.capture(),
            'audio': await self.audio.listen(),
            'system': self.system.get_context()
        }
```

### 10.3 Goals API

```python
class IntrinsicValence:
    def create_goal(self, text: str, priority: float):
        """Create new goal"""
        pass
    
    def score_actions(self, actions: List, context: dict) -> Action:
        """Score and select best action"""
        pass
```

### 10.4 Learning API

```python
class Neuroplasticity:
    async def generate(self, input: str, context: dict) -> str:
        """Generate response using best model"""
        pass
    
    def collect_feedback(self, feedback: dict):
        """Collect training data"""
        pass
    
    def fine_tune(self):
        """Trigger LoRA fine-tuning"""
        pass
```

---

## Appendix: Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Database | SQLite + sqlite-vec | Embedded, zero-config, vector support |
| LLM (local) | DeepSeek K2.5 via MLX | Mac-optimized, MoE efficiency |
| LLM (cloud) | Claude Sonnet 4.5 | Best reasoning, vision support |
| Vector search | sqlite-vec (768-dim) | Native SQLite, no external DB |
| Embeddings | Nomic Embed v1.5 | Fast, local, high quality |
| Audio | Whisper base | Fast transcription on Mac |
| Vision | Atlas Eyes + Sonnet 4.5 | Existing tool + best vision model |
| Fine-tuning | MLX LoRA | Mac-native, memory efficient |
| Language | Python 3.11+ | Asyncio, typing, rich ecosystem |

---

**End of Architecture Document**
