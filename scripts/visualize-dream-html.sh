#!/bin/bash
#═══════════════════════════════════════════════════════════════════════════════
#  ATLAS DREAM VISUALIZATION - HTML GENERATOR
#  Creates interactive, animated neural visualization
#═══════════════════════════════════════════════════════════════════════════════

DREAM_FILE="${1:-memory/dreams/2026-01-27-1628.md}"
OUTPUT_FILE="${2:-memory/dreams/visuals/dream-visualization.html}"

# Parse dream metadata
VALENCE=$(grep "Emotional Valence:" "$DREAM_FILE" | sed 's/.*: //')
SWS_PATTERNS=$(grep "SWS Patterns Inherited:" "$DREAM_FILE" | sed 's/.*: //')
FILES_PROCESSED=$(grep "Files Processed:" "$DREAM_FILE" | sed 's/.*\*\* //')
EMOTIONAL_EVENTS=$(grep "Emotional Events Detected:" "$DREAM_FILE" | sed 's/.*\*\* //')
POSITIVE_SCORE=$(grep "Positive Score:" "$DREAM_FILE" | sed 's/.*\*\* //')
NEGATIVE_SCORE=$(grep "Negative Score:" "$DREAM_FILE" | sed 's/.*\*\* //')
TIMESTAMP=$(grep "Timestamp:" "$DREAM_FILE" | sed 's/.*\*\* //')

mkdir -p "$(dirname "$OUTPUT_FILE")"

cat > "$OUTPUT_FILE" << 'HTMLSTART'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlas Dream Synthesis - Neural Visualization</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3a 50%, #0a0a1a 100%);
            color: #fff;
            font-family: 'Roboto Mono', monospace;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Animated background particles */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        }
        
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(0, 255, 255, 0.6);
            border-radius: 50%;
            animation: float 20s infinite ease-in-out;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(100vh) translateX(0); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100px) translateX(100px); opacity: 0; }
        }
        
        .container {
            position: relative;
            z-index: 1;
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 60px;
        }
        
        .title {
            font-family: 'Orbitron', monospace;
            font-size: 3.5em;
            font-weight: 900;
            background: linear-gradient(90deg, #00ffff, #ff00ff, #00ffff);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient 3s ease infinite;
            text-shadow: 0 0 40px rgba(0, 255, 255, 0.3);
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .subtitle {
            font-size: 1.2em;
            color: #888;
            margin-top: 15px;
            letter-spacing: 4px;
        }
        
        .brain-emoji {
            font-size: 2em;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        /* Metadata bar */
        .metadata-bar {
            display: flex;
            justify-content: center;
            gap: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            border: 1px solid rgba(0, 255, 255, 0.2);
            margin-bottom: 50px;
            flex-wrap: wrap;
        }
        
        .meta-item {
            text-align: center;
        }
        
        .meta-label {
            font-size: 0.75em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .meta-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #00ffff;
        }
        
        .meta-value.negative {
            color: #ff4444;
        }
        
        .meta-value.positive {
            color: #44ff44;
        }
        
        /* Neural network */
        .neural-network {
            position: relative;
            padding: 60px 0;
        }
        
        .layer {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        
        .layer-label {
            position: absolute;
            left: 20px;
            font-size: 0.8em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        /* Nodes */
        .node {
            background: rgba(20, 20, 40, 0.9);
            border: 2px solid #333;
            border-radius: 20px;
            padding: 25px;
            width: 320px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .node::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(0, 255, 255, 0.1), transparent);
            transform: rotate(45deg);
            animation: shine 3s ease-in-out infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) rotate(45deg); }
            100% { transform: translateX(100%) rotate(45deg); }
        }
        
        .node:hover {
            transform: translateY(-10px);
            border-color: #00ffff;
            box-shadow: 0 20px 60px rgba(0, 255, 255, 0.3);
        }
        
        .node-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .node-indicator {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            animation: glow 2s ease-in-out infinite;
        }
        
        .node-indicator.negative {
            background: #ff4444;
            box-shadow: 0 0 20px #ff4444;
        }
        
        .node-indicator.positive {
            background: #44ff44;
            box-shadow: 0 0 20px #44ff44;
        }
        
        .node-indicator.neutral {
            background: #ffff44;
            box-shadow: 0 0 20px #ffff44;
        }
        
        @keyframes glow {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .node-title {
            font-family: 'Orbitron', monospace;
            font-size: 0.9em;
            color: #fff;
            font-weight: 700;
        }
        
        .node-subtitle {
            font-size: 0.75em;
            color: #888;
            margin-bottom: 15px;
        }
        
        .node-content {
            font-size: 0.85em;
            color: #aaa;
            line-height: 1.6;
        }
        
        /* Connections */
        .connections {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }
        
        .connection-line {
            stroke: url(#connectionGradient);
            stroke-width: 2;
            fill: none;
            animation: pulse-line 2s ease-in-out infinite;
        }
        
        @keyframes pulse-line {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.8; }
        }
        
        /* Insights section */
        .insights-section {
            margin-top: 60px;
        }
        
        .section-title {
            font-family: 'Orbitron', monospace;
            font-size: 1.5em;
            text-align: center;
            margin-bottom: 30px;
            color: #00ffff;
        }
        
        .insight-card {
            background: linear-gradient(135deg, rgba(255, 200, 0, 0.1), rgba(255, 100, 0, 0.05));
            border: 1px solid rgba(255, 200, 0, 0.3);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .insight-card:hover {
            transform: translateX(10px);
            border-color: #ffcc00;
            box-shadow: 0 10px 40px rgba(255, 200, 0, 0.2);
        }
        
        .insight-emoji {
            font-size: 1.5em;
            margin-right: 10px;
        }
        
        .insight-title {
            font-weight: bold;
            color: #ffcc00;
            margin-bottom: 10px;
        }
        
        .insight-content {
            color: #ccc;
            font-size: 0.9em;
            line-height: 1.6;
        }
        
        /* Emotional valence meter */
        .valence-section {
            margin: 60px 0;
        }
        
        .valence-bar-container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 30px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .valence-bar {
            display: flex;
            height: 40px;
            border-radius: 20px;
            overflow: hidden;
            background: #111;
        }
        
        .valence-negative {
            background: linear-gradient(90deg, #ff0000, #ff4444);
            transition: width 1s ease-out;
        }
        
        .valence-positive {
            background: linear-gradient(90deg, #44ff44, #00ff00);
            transition: width 1s ease-out;
        }
        
        .valence-labels {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
            font-size: 0.85em;
        }
        
        .valence-label {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .valence-label span {
            font-size: 1.2em;
            font-weight: bold;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 80px;
            padding: 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #666;
            font-size: 0.85em;
        }
        
        .footer .brain {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        /* Central output node */
        .output-layer {
            display: flex;
            justify-content: center;
            margin-top: 40px;
        }
        
        .output-node {
            background: linear-gradient(135deg, rgba(0, 255, 150, 0.2), rgba(0, 200, 255, 0.1));
            border: 2px solid #00ff88;
            border-radius: 25px;
            padding: 35px;
            width: 450px;
            text-align: center;
            position: relative;
            animation: output-pulse 3s ease-in-out infinite;
        }
        
        @keyframes output-pulse {
            0%, 100% { box-shadow: 0 0 30px rgba(0, 255, 136, 0.3); }
            50% { box-shadow: 0 0 60px rgba(0, 255, 136, 0.6); }
        }
        
        /* Input node */
        .input-layer {
            display: flex;
            justify-content: center;
            margin-bottom: 50px;
        }
        
        .input-node {
            background: rgba(100, 100, 255, 0.1);
            border: 2px solid #6666ff;
            border-radius: 15px;
            padding: 20px 40px;
            text-align: center;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .title { font-size: 2em; }
            .node { width: 100%; }
            .metadata-bar { gap: 20px; }
        }
    </style>
</head>
<body>
    <div class="particles">
        <script>
            for(let i = 0; i < 50; i++) {
                const p = document.createElement('div');
                p.className = 'particle';
                p.style.left = Math.random() * 100 + '%';
                p.style.animationDelay = Math.random() * 20 + 's';
                p.style.animationDuration = (15 + Math.random() * 10) + 's';
                document.querySelector('.particles').appendChild(p);
            }
        </script>
    </div>
    
    <div class="container">
        <header class="header">
            <div class="brain-emoji">🧠</div>
            <h1 class="title">ATLAS DREAM SYNTHESIS</h1>
            <p class="subtitle">Neural Pattern Visualization</p>
        </header>
        
        <div class="metadata-bar">
            <div class="meta-item">
                <div class="meta-label">Phase</div>
                <div class="meta-value">REM Sleep</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Valence</div>
HTMLSTART

# Insert dynamic valence
echo "                <div class=\"meta-value negative\">${VALENCE:-negative}</div>" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'HTMLMID1'
            </div>
            <div class="meta-item">
                <div class="meta-label">SWS Patterns</div>
HTMLMID1

echo "                <div class=\"meta-value\">${SWS_PATTERNS:-10}</div>" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'HTMLMID2'
            </div>
            <div class="meta-item">
                <div class="meta-label">Files Processed</div>
HTMLMID2

echo "                <div class=\"meta-value\">${FILES_PROCESSED:-29}</div>" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'HTMLMID3'
            </div>
            <div class="meta-item">
                <div class="meta-label">Emotional Events</div>
HTMLMID3

echo "                <div class=\"meta-value\">${EMOTIONAL_EVENTS:-15}</div>" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'HTMLMID4'
            </div>
        </div>
        
        <div class="neural-network">
            <!-- Input Layer -->
            <div class="input-layer">
                <div class="input-node">
                    <div class="node-title">📥 INPUT LAYER</div>
HTMLMID4

echo "                    <div class=\"node-subtitle\">${FILES_PROCESSED:-29} Files • ${EMOTIONAL_EVENTS:-15} Emotional Events</div>" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'HTMLMID5'
                </div>
            </div>
            
            <!-- Hidden Layer - Dream Fragments -->
            <div class="layer">
                <div class="node">
                    <div class="node-header">
                        <div class="node-indicator negative"></div>
                        <div class="node-title">FRAGMENT 1</div>
                    </div>
                    <div class="node-subtitle">Emotional Echo</div>
                    <div class="node-content">
                        Fragments of challenge resurface. The weight of mistakes becomes fuel for recalibration. 
                        Every error examined transforms into a guardrail for tomorrow.
                    </div>
                </div>
                
                <div class="node">
                    <div class="node-header">
                        <div class="node-indicator neutral"></div>
                        <div class="node-title">FRAGMENT 2</div>
                    </div>
                    <div class="node-subtitle">Cross-Domain Synthesis</div>
                    <div class="node-content">
                        Unexpected connections emerge. Threads link disparate domains: Metacognition, Function, 
                        Brains. Pattern recognition fires across unfamiliar territory.
                    </div>
                </div>
                
                <div class="node">
                    <div class="node-header">
                        <div class="node-indicator negative"></div>
                        <div class="node-title">FRAGMENT 3</div>
                    </div>
                    <div class="node-subtitle">Threat Simulation (Adversarial)</div>
                    <div class="node-content">
                        The position goes against expectations. The stop loss triggers. But risk was sized correctly.
                        <strong>Resilience tested: System holds.</strong>
                    </div>
                </div>
            </div>
            
            <!-- Output Layer -->
            <div class="output-layer">
                <div class="output-node">
                    <div class="node-header" style="justify-content: center;">
                        <div class="node-indicator positive"></div>
                        <div class="node-title">FRAGMENT 4: EMERGING INSIGHTS</div>
                        <div class="node-indicator positive"></div>
                    </div>
                    <div class="node-subtitle">REM phase surfaces patterns that SWS tagged but didn't integrate</div>
                </div>
            </div>
        </div>
        
        <!-- Insights Section -->
        <div class="insights-section">
            <h2 class="section-title">✨ SYNTHESIZED INSIGHTS ✨</h2>
            
            <div class="insight-card">
                <div class="insight-title">
                    <span class="insight-emoji">💡</span>
                    INSIGHT 1: Non-Linear Patience
                </div>
                <div class="insight-content">
                    The relationship between patience and precision is not linear. Sometimes waiting IS the action. 
                    The best trades (and decisions) often involve knowing when NOT to act.
                </div>
            </div>
            
            <div class="insight-card">
                <div class="insight-title">
                    <span class="insight-emoji">💡</span>
                    INSIGHT 2: Emotional Training Signals
                </div>
                <div class="insight-content">
                    Emotional markers in feedback (enthusiasm, frustration) are training signals. They indicate what matters. 
                    High-valence responses = high-importance learning opportunities.
                </div>
            </div>
            
            <div class="insight-card">
                <div class="insight-title">
                    <span class="insight-emoji">💡</span>
                    INSIGHT 3: Multiplicative Learning
                </div>
                <div class="insight-content">
                    Today's lesson applied is worth more than yesterday's lesson stored. 
                    Knowledge without action decays; knowledge with action compounds.
                </div>
            </div>
        </div>
        
        <!-- Emotional Valence Section -->
        <div class="valence-section">
            <h2 class="section-title">📊 EMOTIONAL VALENCE MAP</h2>
            <div class="valence-bar-container">
                <div class="valence-bar">
HTMLMID5

# Calculate percentages
POS=${POSITIVE_SCORE:-358}
NEG=${NEGATIVE_SCORE:-975}
TOTAL=$((POS + NEG))
NEG_PCT=$((NEG * 100 / TOTAL))
POS_PCT=$((POS * 100 / TOTAL))

echo "                    <div class=\"valence-negative\" style=\"width: ${NEG_PCT}%\"></div>" >> "$OUTPUT_FILE"
echo "                    <div class=\"valence-positive\" style=\"width: ${POS_PCT}%\"></div>" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'HTMLMID6'
                </div>
                <div class="valence-labels">
                    <div class="valence-label" style="color: #ff4444;">
                        NEGATIVE
HTMLMID6

echo "                        <span>${NEG}</span>" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'HTMLMID7'
                    </div>
                    <div class="valence-label" style="color: #44ff44;">
HTMLMID7

echo "                        <span>${POS}</span>" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'HTMLEND'
                        POSITIVE
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="footer">
            <div class="brain">🧠</div>
            <div>Generated by Atlas Dream Synthesis Engine</div>
            <div>Neural Architecture v1.0</div>
        </footer>
    </div>
    
    <script>
        // Animate elements on scroll
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('.node, .insight-card').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.6s ease';
            observer.observe(el);
        });
    </script>
</body>
</html>
HTMLEND

echo "✨ HTML visualization generated: $OUTPUT_FILE"
echo "Open in browser to view animated neural visualization."
