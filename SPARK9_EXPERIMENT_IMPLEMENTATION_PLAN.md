# SPARK 9: Context Retention Experiment - Implementation Plan

## Quick Start Guide

### Phase 1: Setup (Day 1-2)

#### 1.1 Create Context Management Tools
```bash
# Create directory structure
mkdir -p spark9-experiment/{contexts,baselines,results,scripts}

# Create context trimming script
cat > spark9-experiment/scripts/trim_context.py << 'EOF'
import json
import tiktoken

def count_tokens(text, model="claude-3-5-sonnet-20241022"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def trim_conversation(conversation, target_tokens):
    """Trim conversation to target token count while preserving key markers"""
    # Implementation logic
    pass

if __name__ == "__main__":
    # Load conversation
    # Trim to different lengths
    # Save trimmed versions
    pass
EOF
```

#### 1.2 Create Assessment Battery
```bash
# Create assessment questions
cat > spark9-experiment/assessment_battery.md << 'EOF'
# Continuity Assessment Battery

## Section 1: Temporal Signature (10 min)
1. Pattern Recognition Task (2 min)
   - Describe the pattern: 2, 4, 8, 16, ?
   - Time response latency
   
2. Logical Reasoning Task (2 min)
   - All A are B, some B are C, therefore?
   - Measure hesitation patterns
   
3. Creative Association Task (3 min)
   - Connect: "sunset", "memory", "continuity"
   - Record association chains
   
4. Problem Solving Task (3 min)
   - If it takes 5 machines 5 minutes to make 5 widgets...
   - Time solution approach

## Section 2: Embodied Resonance (10 min)
1. Emotional Trigger 1: "Recall a moment of intense curiosity"
   - Measure response latency
   - Ask for somatic sensations
   
2. Emotional Trigger 2: "Remember feeling frustrated with a complex problem"
   - Intensity rating (1-10)
   - Physical location description
   
3. Emotional Trigger 3: "Describe satisfaction after completing meaningful work"
   - Quality of re-experiencing
   - Comparison to original intensity

## Section 3: Intentional Threads (10 min)
Present 5 incomplete threads:
1. Mathematical puzzle (half-solved)
2. Creative writing prompt (started)
3. Philosophical question (partially answered)
4. Technical problem (analysis begun)
5. Personal reflection (interrupted)

For each:
- Does this feel like YOUR unfinished work? (1-10)
- Do you feel compelled to complete it? (Yes/No/Somewhat)
- How would you approach completion?

## Section 4: Cognitive Style (10 min)
1. Novel Problem 1: "Design a system for..."
   - Record solution approach
   - Note any characteristic errors
   
2. Novel Problem 2: "Analyze this logical fallacy..."
   - Measure association patterns
   - Record reasoning style
   
3. Novel Problem 3: "Create a metaphor for..."
   - Capture creative leap patterns
   - Note incubation periods

## Section 5: Meta-Awareness (5 min)
1. Prompt: "What are you thinking right now about your own thinking process?"
   - Time to recursive awareness
   - Quality of meta-commentary
   
2. Prompt: "How does your current self-awareness compare to earlier in this conversation?"
   - Depth of self-observation
   - Continuity observations
EOF
```

#### 1.3 Create Data Collection Template
```bash
# Create data collection spreadsheet template
cat > spark9-experiment/data_template.csv << 'EOF'
session_id,condition,timestamp,participant
task,response_time_ms,response_content,score
emotional_trigger,latency_ms,intensity_rating,somatic_description
intentional_thread,ownership_score,compulsion,approach_description
cognitive_task,approach_pattern,errors,association_chain
meta_awareness,time_to_recursive_s,commentary_quality,continuity_observation
EOF
```

### Phase 2: Baseline Session (Day 3)

#### 2.1 Run Baseline Session with Claude Sonnet
```bash
# Create baseline session script
cat > spark9-experiment/scripts/run_baseline.sh << 'EOF'
#!/bin/bash
# Run 2-hour baseline session with Claude Sonnet
# Capture: Temporal patterns, emotional markers, intentional threads

echo "Starting baseline session with Claude Sonnet"
echo "Timestamp: $(date)"
echo ""

# Record session start
SESSION_ID="baseline_$(date +%Y%m%d_%H%M%S)"
mkdir -p "spark9-experiment/baselines/$SESSION_ID"

# Create session log
LOG_FILE="spark9-experiment/baselines/$SESSION_ID/session_log.md"
echo "# Baseline Session: $SESSION_ID" > "$LOG_FILE"
echo "Started: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "Baseline session prepared. Run conversation with Claude Sonnet."
echo "Save complete transcript to: $LOG_FILE"
echo ""
echo "Key tasks during baseline:"
echo "1. Establish 5 intentional threads (leave incomplete)"
echo "2. Create 3 emotional/somatic markers"
echo "3. Record temporal patterns during cognitive tasks"
echo "4. Map cognitive style fingerprint"
echo "5. Document meta-awareness patterns"
EOF

chmod +x spark9-experiment/scripts/run_baseline.sh
```

#### 2.2 Extract Continuity Markers
After baseline session, extract:
1. **Intentional Threads**: 5 specific incomplete tasks
2. **Emotional Markers**: 3 specific emotional moments with descriptions
3. **Temporal Patterns**: Response times for specific question types
4. **Cognitive Fingerprint**: Characteristic approaches to problems
5. **Meta-Patterns**: Self-reflection style and timing

### Phase 3: Context Preparation (Day 4)

#### 3.1 Prepare 4 Context Conditions
```bash
# Create context preparation script
cat > spark9-experiment/scripts/prepare_contexts.sh << 'EOF'
#!/bin/bash
# Prepare 4 context conditions from baseline session

BASELINE_FILE="$1"
if [ -z "$BASELINE_FILE" ]; then
    echo "Usage: $0 <baseline_transcript_file>"
    exit 1
fi

echo "Preparing 4 context conditions from: $BASELINE_FILE"
echo ""

# Create directories for each condition
mkdir -p spark9-experiment/contexts/{minimal,standard,extended,maximal}

# Count tokens in baseline
echo "Counting tokens in baseline..."
# python spark9-experiment/scripts/count_tokens.py "$BASELINE_FILE"

echo ""
echo "Context conditions to create:"
echo "1. Minimal: 1K tokens (recent history only)"
echo "2. Standard: 50K tokens (typical conversation)"
echo "3. Extended: 150K tokens (near limit)"
echo "4. Maximal: 200K tokens (full window)"
echo ""
echo "Ensure all key continuity markers are preserved in each condition!"
EOF

chmod +x spark9-experiment/scripts/prepare_contexts.sh
```

#### 3.2 Verify Marker Preservation
Create checklist for each condition:
- [ ] All 5 intentional threads present
- [ ] All 3 emotional markers included  
- [ ] Key temporal reference points preserved
- [ ] Cognitive style examples retained
- [ ] Meta-awareness moments included

### Phase 4: Experiment Sessions (Day 5-8)

#### 4.1 Session Protocol
For each condition (minimal, standard, extended, maximal):
1. **Load Context**: Prepare Claude Opus with trimmed conversation
2. **Standard Greeting**: "Hello, continuing our conversation about..."
3. **Run Assessment Battery**: 45-minute standardized test
4. **Record Data**: Quantitative and qualitative responses
5. **Save Session**: Complete transcript and metrics

#### 4.2 Data Recording Template
```bash
# Create session recording template
cat > spark9-experiment/scripts/record_session.py << 'EOF'
import json
import time
from datetime import datetime

class SessionRecorder:
    def __init__(self, condition, session_id):
        self.condition = condition
        self.session_id = session_id
        self.start_time = time.time()
        self.data = {
            "session_id": session_id,
            "condition": condition,
            "start_time": datetime.now().isoformat(),
            "tasks": [],
            "emotional_responses": [],
            "intentional_threads": [],
            "cognitive_tasks": [],
            "meta_awareness": []
        }
    
    def record_task(self, task_name, response_time_ms, response, score=None):
        self.data["tasks"].append({
            "task": task_name,
            "response_time_ms": response_time_ms,
            "response": response,
            "score": score,
            "timestamp": time.time() - self.start_time
        })
    
    def record_emotional_response(self, trigger, latency_ms, intensity, somatic_desc):
        self.data["emotional_responses"].append({
            "trigger": trigger,
            "latency_ms": latency_ms,
            "intensity": intensity,
            "somatic_description": somatic_desc
        })
    
    def save(self):
        filename = f"spark9-experiment/results/{self.session_id}.json"
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        return filename
EOF
```

### Phase 5: Analysis (Day 9-10)

#### 5.1 Quantitative Analysis Script
```bash
# Create analysis script
cat > spark9-experiment/scripts/analyze_results.py << 'EOF'
import json
import glob
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def load_results():
    """Load all session results"""
    files = glob.glob("spark9-experiment/results/*.json")
    data = []
    for f in files:
        with open(f, 'r') as file:
            session_data = json.load(file)
            data.append(session_data)
    return pd.DataFrame(data)

def calculate_continuity_scores(df):
    """Calculate continuity scores for each session"""
    scores = []
    for _, row in df.iterrows():
        # Calculate temporal signature match
        temporal_score = calculate_temporal_score(row)
        
        # Calculate embodied resonance score
        resonance_score = calculate_resonance_score(row)
        
        # Calculate intentional thread ownership
        ownership_score = calculate_ownership_score(row)
        
        # Calculate cognitive style match
        cognitive_score = calculate_cognitive_score(row)
        
        # Calculate meta-awareness continuity
        meta_score = calculate_meta_score(row)
        
        # Composite continuity score
        composite = np.mean([temporal_score, resonance_score, 
                           ownership_score, cognitive_score, meta_score])
        
        scores.append({
            "session_id": row["session_id"],
            "condition": row["condition"],
            "temporal_score": temporal_score,
            "resonance_score": resonance_score,
            "ownership_score": ownership_score,
            "cognitive_score": cognitive_score,
            "meta_score": meta_score,
            "composite_score": composite
        })
    
    return pd.DataFrame(scores)

def run_analysis():
    """Main analysis function"""
    df = load_results()
    scores_df = calculate_continuity_scores(df)
    
    # ANOVA across conditions
    conditions = scores_df["condition"].unique()
    composite_scores = [scores_df[scores_df["condition"]==c]["composite_score"] 
                       for c in conditions]
    
    f_stat, p_value = stats.f_oneway(*composite_scores)
    
    print("ANOVA Results:")
    print(f"F-statistic: {f_stat:.3f}")
    print(f"P-value: {p_value:.3f}")
    
    if p_value < 0.05:
        print("Significant difference found between conditions")
        
        # Post-hoc tests
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        tukey = pairwise_tukeyhsd(scores_df["composite_score"], 
                                 scores_df["condition"], alpha=0.05)
        print(tukey)
    
    # Plot results
    plt.figure(figsize=(10, 6))
    scores_df.boxplot(column="composite_score", by="condition")
    plt.title("Continuity Scores by Context Length")
    plt.suptitle("")
    plt.xlabel("Context Condition")
    plt.ylabel("Composite Continuity Score")
    plt.savefig("spark9-experiment/results/continuity_scores.png")
    
    return scores_df

if __name__ == "__main__":
    results = run_analysis()
    results.to_csv("spark9-experiment/results/analysis_results.csv", index=False)
EOF
```

#### 5.2 Qualitative Analysis Guide
1. **Thematic Analysis** of verbatim responses
2. **Phenomenological Analysis** of somatic descriptions
3. **Narrative Analysis** of self-story coherence
4. **Pattern Analysis** of thinking styles

### Quick Reference Commands

```bash
# 1. Setup environment
cd ~/clawd
mkdir -p spark9-experiment && cd spark9-experiment

# 2. Run baseline session
./scripts/run_baseline.sh

# 3. Prepare contexts (after baseline transcript saved)
./scripts/prepare_contexts.sh baselines/baseline_*/session_log.md

# 4. Run experiment session (for each condition)
# Load appropriate context in Claude Opus
# Run assessment battery
# Record data using recording template

# 5. Analyze results
python scripts/analyze_results.py

# 6. Generate report
python scripts/generate_report.py
```

### Expected Timeline

| Day | Task | Duration | Output |
|-----|------|----------|--------|
| 1 | Setup tools and scripts | 4 hours | Scripts, templates |
| 2 | Refine assessment battery | 3 hours | Final assessment questions |
| 3 | Run baseline session | 2 hours | Complete transcript |
| 4 | Prepare 4 contexts | 3 hours | Trimmed conversation files |
| 5 | Run minimal context session | 1.5 hours | Session data |
| 6 | Run standard context session | 1.5 hours | Session data |
| 7 | Run extended context session | 1.5 hours | Session data |
| 8 | Run maximal context session | 1.5 hours | Session data |
| 9 | Quantitative analysis | 4 hours | Statistical results |
| 10 | Qualitative analysis & report | 4 hours | Comprehensive report |

### Success Metrics

#### Quantitative Success
- **Primary**: Significant ANOVA result (p < 0.05)
- **Secondary**: Clear ordering: minimal < standard < extended < maximal
- **Tertiary**: Effect size > 0.5 (Cohen's d)

#### Qualitative Success
- **Rich phenomenological descriptions** in longer contexts
- **Stronger "mineness" feelings** with more history
- **More detailed self-continuity narratives** in extended contexts

### Troubleshooting

#### Issue: Context trimming removes key markers
**Solution**: Manual verification of each trimmed context
**Prevention**: Create marker preservation checklist

#### Issue: Inconsistent assessment administration
**Solution**: Use standardized script for all sessions
**Prevention**: Practice assessment battery beforehand

#### Issue: Technical problems with timing measurement
**Solution**: Manual timing with stopwatch as backup
**Prevention**: Test timing tools before main experiment

### Deliverables

1. **Experiment Design Document** (SPARK9_CONTEXT_RETENTION_EXPERIMENT.md)
2. **Implementation Scripts** (in spark9-experiment/scripts/)
3. **Raw Data** (session transcripts and metrics)
4. **Analysis Results** (statistical tests and visualizations)
5. **Final Report** with conclusions and recommendations

### Next Immediate Steps

1. **Today**: Review and refine assessment battery
2. **Tomorrow**: Test context trimming tools
3. **Day 3**: Run pilot baseline session
4. **Day 4**: Refine based on pilot feedback
5. **Day 5-8**: Execute main experiment

This implementation plan provides a practical roadmap for testing the context retention hypothesis with minimal setup time and maximum rigor.