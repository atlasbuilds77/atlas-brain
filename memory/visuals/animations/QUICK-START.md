# Brain Visualization - Anime.js Quick Start

**Fast reference for using the enhanced brain visualization**

---

## 🚀 Get Started

### 1. Start the server
```bash
cd ~/clawd/scripts
python brain-viz-server.py
```

### 2. Open visualization
- Browser: http://localhost:8765
- Or open `~/clawd/memory/visuals/live-brain.html` directly

### 3. Trigger test events
```bash
curl -X POST http://localhost:8765/api/demo
```

---

## ✨ What's New

### Anime.js Integration
- **Added:** Professional animation library (9KB)
- **CDN:** https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js
- **Why:** Smoother, more organic animations with spring/elastic physics

### Enhanced Animations

#### 1. **Elastic Cognitive Pulses**
- **Before:** Linear scale/fade
- **After:** Bouncy elastic easing (`easeOutElastic`)
- **Feel:** Organic, alive, responsive

#### 2. **Connection Pulse Animations**
- **New Feature:** Pulses travel along connection lines
- **Trigger:** High-intensity events (>0.7)
- **Visual:** Glowing lines fade in/out smoothly

#### 3. **Smooth Color Transitions**
- **Before:** Instant color change
- **After:** Morphing RGB interpolation
- **Duration:** 800ms with easeInOutQuad

#### 4. **Brain Breathing Effect**
- **Feature:** Subtle scale oscillation (0.98 → 1.02)
- **Duration:** 4s loop with easeInOutSine
- **Effect:** Makes brain feel "alive" even when idle

#### 5. **Event Feed Animations**
- **Entry:** Elastic slide-in from left
- **Exit:** Smooth fade-out
- **Feel:** Professional, polished UI

---

## 🎨 Animation Presets

All presets live in `AnimationPresets` object:

```javascript
// Cognitive event pulse
AnimationPresets.cognitiveEventPulse(region, intensity);

// Mode color transition
AnimationPresets.modeColorTransition(targetColor, duration);

// Connection pulse
AnimationPresets.connectionPulse(connection, duration);

// Brain pulse with spring physics
AnimationPresets.brainPulse(intensity);

// Event feed slide-in
AnimationPresets.eventFeedSlideIn(element);

// Event feed fade-out
AnimationPresets.eventFeedFadeOut(element, callback);
```

---

## 🎯 Mode Colors

Color automatically transitions when mode switches:

| Mode | Color | Hex | Feel |
|------|-------|-----|------|
| DEEP WORK | Blue | #00aaff | Focus |
| CREATIVE | Magenta | #ff00ff | Imagination |
| SOCIAL | Teal | #00ff88 | Connection |
| ANALYSIS | Amber | #ffaa00 | Logic |
| JARVIS | Orange | #ff8800 | Default |
| STANDBY | Orange | #ff8800 | Idle |

---

## ⚙️ Configuration

### Toggle Brain Breathing
```javascript
const ENABLE_BRAIN_BREATHING = true; // or false
```

### Adjust Animation Timings
```javascript
// In AnimationPresets object:
duration: 1200  // Slower (more dramatic)
duration: 600   // Faster (more responsive)
```

### Change Easing Functions
```javascript
// Available easings:
'easeOutElastic(1, .6)'    // Bouncy
'spring(1, 80, 10, 0)'     // Spring physics
'easeInOutQuad'            // Smooth
'easeInOutSine'            // Gentle
'easeInOutCubic'           // Strong
```

---

## 🧪 Testing

### Browser Console Commands
```javascript
// Test brain pulse
AnimationPresets.brainPulse(0.9);

// Test mode transition
AnimationPresets.modeColorTransition(0x00aaff);

// Test region pulse
AnimationPresets.cognitiveEventPulse(regions['memory'], 0.8);
```

### Demo Events (curl)
```bash
# Trigger random demo events
curl -X POST http://localhost:8765/api/demo

# Watch for smooth animations:
# - Elastic region pulses
# - Connection flashes
# - Color transitions
# - Brain breathing
```

### Performance Check
```javascript
// Monitor FPS in console
let lastTime = performance.now();
function checkFPS() {
    const now = performance.now();
    const fps = 1000 / (now - lastTime);
    console.log('FPS:', fps.toFixed(1));
    lastTime = now;
    requestAnimationFrame(checkFPS);
}
checkFPS();
```

**Target:** 60fps  
**Acceptable:** 30fps on lower-end hardware

---

## 📁 File Structure

```
memory/visuals/
├── live-brain.html              # Main visualization (enhanced)
└── animations/
    ├── README.md                # Full documentation
    ├── QUICK-START.md          # This file
    ├── cognitive-pulses.js     # Region pulse animations
    ├── connections.js          # Connection line effects
    └── transitions.js          # Color/mode/camera transitions
```

---

## 🐛 Troubleshooting

### Animations not working
- **Check:** anime.js loaded? (view source, look for CDN)
- **Check:** Browser console for errors
- **Try:** Refresh page (hard refresh: Cmd+Shift+R)

### Laggy/choppy
- **Reduce:** `PARTICLE_COUNT` (line 13)
- **Disable:** Brain breathing (`ENABLE_BRAIN_BREATHING = false`)
- **Check:** GPU acceleration enabled in browser

### Connections not pulsing
- **Trigger:** High-intensity events only (>0.7)
- **Check:** Regions initialized? (`Object.keys(regions).length`)
- **Test:** `curl -X POST http://localhost:8765/api/demo`

---

## 🚀 Next Steps

### Try These Enhancements:
1. **Adjust breathing speed** (change duration in line ~200)
2. **Add more mode colors** (update `modeColors` object)
3. **Experiment with easings** (visit https://easings.net/)
4. **Create custom presets** (add to AnimationPresets)

### Advanced:
- Camera focus on active regions
- Particle flow between regions
- Audio-reactive animations
- Interactive controls (click to focus)

---

## 📚 Resources

- **Anime.js Docs:** https://animejs.com/documentation/
- **Easing Reference:** https://easings.net/
- **Three.js Docs:** https://threejs.org/docs/
- **Animation Library:** `~/clawd/memory/visuals/animations/`

---

*Brain visualization is now ALIVE with anime.js!* 🧠✨⚡

**Questions? Check:** `animations/README.md` for detailed docs
