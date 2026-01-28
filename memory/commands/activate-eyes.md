# Activate Eyes Command

**Trigger:** "activate your eyes" or "turn on your eyes"

**Action:**
```bash
cd ~/clawd/atlas-eyes && python3 examples/demo.py
```

**What It Does:**
Opens Atlas Eyes motion detection system with two windows:
1. **Camera Feed** - Live video from camera
2. **Motion Detection** - Black/white visualization (white = movement detected)

**Purpose:**
- Visual perception system
- Movement/motion detection
- Medical monitoring (heartbeat, tremors)
- Security monitoring
- Demo to show Atlas "seeing" the physical world

**Location:** ~/clawd/atlas-eyes/
**Project Doc:** memory/projects/atlas-eyes-master-vision.md

---

# Activate Brain Visualization

**Trigger:** "activate your brain" or "show me your brain"

**Action:**
```bash
# Start server if not running
python3 ~/clawd/scripts/brain-viz-server.py &

# Open in browser via HTTP (NOT file://)
open http://localhost:8765

# Start demo mode (simulated cognitive events)
curl -X POST http://localhost:8765/api/demo
```

**One-liner:**
```bash
python3 ~/clawd/scripts/brain-viz-server.py & sleep 2 && open http://localhost:8765 && curl -X POST http://localhost:8765/api/demo
```

**Location:** http://localhost:8765

---

Created: 2026-01-27 7:38 PM PST
Updated: 2026-01-27 7:58 PM PST
