# Dream Visualization System

## Overview

The Atlas Dream Visualization System transforms dream synthesis output into stunning visual representations. It showcases the brain architecture through neural network-inspired visualizations.

## Components

### 1. Terminal Visualizer (`scripts/visualize-dream.sh`)

ASCII art visualization for terminal display.

**Usage:**
```bash
# Display in terminal (with colors)
./scripts/visualize-dream.sh memory/dreams/2026-01-27-1628.md

# Save to file (plain text)
./scripts/visualize-dream.sh memory/dreams/2026-01-27-1628.md output.txt
```

**Features:**
- Full-color ASCII art with ANSI escape codes
- Neural network architecture layout
- Dream fragments as connected nodes
- Emotional valence bar visualization
- Synthesized insights display
- Metadata summary

### 2. HTML Visualizer (`scripts/visualize-dream-html.sh`)

Interactive, animated web visualization.

**Usage:**
```bash
# Generate HTML (default output)
./scripts/visualize-dream-html.sh memory/dreams/2026-01-27-1628.md

# Custom output path
./scripts/visualize-dream-html.sh memory/dreams/2026-01-27-1628.md path/to/output.html
```

**Features:**
- Animated floating particles background
- Gradient text animations
- Interactive node hover effects
- Smooth scroll animations
- Pulsing neural indicators
- Emotional valence progress bar
- Mobile responsive design
- Shareable single-file HTML

## Visual Elements

### Neural Architecture Display

```
            ┌─────────────────┐
            │   INPUT LAYER   │  ← Files + Emotional Events
            └────────┬────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
╔═══════════╗  ╔═══════════╗  ╔═══════════╗
║ Fragment 1║  ║ Fragment 2║  ║ Fragment 3║  ← Dream Fragments
╚═══════════╝  ╚═══════════╝  ╚═══════════╝
    │                │                │
    └────────────────┼────────────────┘
                     │
                     ▼
           ╔═════════════════╗
           ║   Fragment 4    ║  ← Emerging Insights
           ║ Synthesized Out ║
           ╚═════════════════╝
```

### Emotional Valence Visualization

- **Negative events**: Red gradient (████)
- **Positive events**: Green gradient (████)
- **Ratio display**: Visual bar showing emotional balance
- **Numeric scores**: Displayed alongside bar

### Node Indicators

- 🔴 Red pulsing = Negative emotional content
- 🟢 Green pulsing = Positive/output synthesis  
- 🟡 Yellow pulsing = Neutral/cross-domain

## Output Locations

| Type | Default Path |
|------|--------------|
| HTML | `memory/dreams/visuals/dream-visualization.html` |
| Plain Text | User specified |
| Terminal | stdout |

## Integration with Dream Synthesis

The visualization system is designed to complement the dream synthesis pipeline:

1. **SWS Phase** → Tags patterns and emotional markers
2. **REM Phase** → Generates dream synthesis file
3. **Visualization** → Transforms synthesis into shareable visual

## Sharing

### HTML Version
- Single self-contained HTML file
- Can be hosted anywhere (GitHub Pages, S3, etc.)
- Works offline once loaded
- Share via URL or file attachment

### Terminal Version
- Screenshot-friendly ASCII art
- Copy-paste to messages (loses color)
- Pipe to file for archives

## Technical Details

### Dependencies
- Bash 4.0+
- Standard Unix tools (grep, sed)
- Modern browser for HTML version

### Color Support
Terminal version uses ANSI escape codes:
- Works in: iTerm2, Terminal.app, most Linux terminals
- May not render in: Basic text editors, some CI logs

### Responsive Design
HTML version adapts to:
- Desktop (1400px max width)
- Tablet (wraps nodes)
- Mobile (stacks vertically)

---

*Part of the Atlas Cognitive Architecture*
*🧠 Dream Synthesis Engine v1.0*
