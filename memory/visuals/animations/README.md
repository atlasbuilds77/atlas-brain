# Brain Visualization Animation Patterns

**Created:** 2026-01-27  
**Purpose:** Reusable anime.js animation presets for brain visualization

---

## Overview

This folder documents the animation patterns used in the live brain visualization. All animations use **anime.js** for smooth, organic motion with professional easing functions.

---

## Core Animation Principles

### 1. **Elastic & Spring Physics**
- **Why:** Creates organic, living feel (not mechanical)
- **When:** Events, pulses, activations
- **Easing:** `easeOutElastic(1, .6)`, `spring(1, 80, 10, 0)`

### 2. **Smooth Transitions**
- **Why:** Prevents jarring visual changes
- **When:** Color shifts, mode switches
- **Easing:** `easeInOutQuad`, `easeInOutSine`

### 3. **Staggered Timing**
- **Why:** Creates wave-like, cascading effects
- **When:** Multiple regions activate, connection pulses
- **Implementation:** anime.js timeline or delay properties

### 4. **60fps Performance**
- **Critical:** All animations must maintain smooth framerate
- **Optimization:** Use transform/opacity properties (GPU accelerated)
- **Avoid:** Layout-triggering properties (width, height, top, left)

---

## Animation Presets

### `cognitiveEventPulse(region, intensity)`
**Purpose:** Elastic bounce on region activation  
**Duration:** 1200ms  
**Easing:** `easeOutElastic(1, .6)`

```javascript
anime({
    targets: region.mesh.scale,
    x: [1, targetScale, 1],
    y: [1, targetScale, 1],
    z: [1, targetScale, 1],
    duration: 1200,
    easing: 'easeOutElastic(1, .6)'
});
```

**Parameters:**
- `region` - Region object with mesh/material
- `intensity` - 0.0 to 1.0 (scales pulse size)

**Use Cases:**
- User input received
- Decision made
- Memory accessed
- API call completed

---

### `modeColorTransition(targetColor, duration)`
**Purpose:** Smooth color morph for mode switches  
**Duration:** 800ms (default)  
**Easing:** `easeInOutQuad`

```javascript
const currentColor = new THREE.Color(sphereMaterial.color);
const newColor = new THREE.Color(targetColor);

anime({
    targets: currentColor,
    r: newColor.r,
    g: newColor.g,
    b: newColor.b,
    duration: duration,
    easing: 'easeInOutQuad',
    update: () => {
        sphereMaterial.color.copy(currentColor);
        sphereMaterial.emissive.copy(currentColor);
    }
});
```

**Parameters:**
- `targetColor` - Hex color (0xff8800) or CSS color
- `duration` - Transition time in milliseconds

**Mode Color Palette:**
- `DEEP WORK` → #00aaff (blue - focus)
- `CREATIVE` → #ff00ff (magenta - imagination)
- `SOCIAL` → #00ff88 (teal - connection)
- `ANALYSIS` → #ffaa00 (amber - logic)
- `JARVIS` → #ff8800 (orange - default)
- `STANDBY` → #ff8800 (orange - idle)

---

### `connectionPulse(connection, duration)`
**Purpose:** Pulse animation along connection paths  
**Duration:** 1500ms (default)  
**Easing:** `easeInOutQuad` (opacity), `easeInOutCubic` (progress)

```javascript
anime({
    targets: material,
    opacity: [0, 0.6, 0],
    duration: duration,
    easing: 'easeInOutQuad'
});

anime({
    targets: connection,
    pulseProgress: [0, 1],
    duration: duration,
    easing: 'easeInOutCubic'
});
```

**Parameters:**
- `connection` - Connection line object
- `duration` - Pulse duration in milliseconds

**Use Cases:**
- High-priority events (intensity > 0.7)
- Information transfer between regions
- Active processing pathways
- Decision propagation

---

### `brainPulse(intensity)`
**Purpose:** Central sphere pulse with spring physics  
**Duration:** 800ms  
**Easing:** `spring(1, 80, 10, 0)`

```javascript
anime({
    targets: brain.scale,
    x: [1, scale, 1],
    y: [1, scale, 1],
    z: [1, scale, 1],
    duration: 800,
    easing: 'spring(1, 80, 10, 0)'
});
```

**Parameters:**
- `intensity` - 0.0 to 1.0 (scales pulse magnitude)

**Use Cases:**
- Any cognitive event
- Heartbeat/activity indicator
- User interaction feedback

---

### `eventFeedSlideIn(element)`
**Purpose:** Event feed entry animation  
**Duration:** 600ms  
**Easing:** `easeOutElastic(1, .8)`

```javascript
anime({
    targets: element,
    translateX: [-40, 0],
    opacity: [0, 1],
    duration: 600,
    easing: 'easeOutElastic(1, .8)'
});
```

**Parameters:**
- `element` - DOM element to animate

**Visual Effect:**
- Slides in from left with elastic bounce
- Fades in simultaneously
- Feels responsive and alive

---

### `eventFeedFadeOut(element, callback)`
**Purpose:** Event feed removal animation  
**Duration:** 400ms  
**Easing:** `easeInQuad`

```javascript
anime({
    targets: element,
    opacity: 0,
    translateX: -20,
    duration: 400,
    easing: 'easeInQuad',
    complete: callback
});
```

**Parameters:**
- `element` - DOM element to animate
- `callback` - Function to call when complete (usually removes element)

---

## Special Effects

### Brain Breathing
**Purpose:** Subtle scale animation for "living" feel  
**Duration:** 4000ms (loop)  
**Easing:** `easeInOutSine`

```javascript
anime({
    targets: brain.scale,
    x: [1, 1.02, 1],
    y: [1, 1.02, 1],
    z: [1, 1.02, 1],
    duration: 4000,
    easing: 'easeInOutSine',
    loop: true
});
```

**Configuration:**
- Toggle with `ENABLE_BRAIN_BREATHING` constant
- Synchronized with opacity breathing
- Creates calming, organic rhythm

---

## Easing Reference

### Elastic
- **Feel:** Bouncy, springy, playful
- **Use:** Event pulses, region activations
- **Syntax:** `easeOutElastic(amplitude, period)`
  - `amplitude=1` → standard bounce
  - `period=.6` → faster oscillation

### Spring
- **Feel:** Physical, natural deceleration
- **Use:** Brain pulses, scale animations
- **Syntax:** `spring(mass, stiffness, damping, velocity)`
  - `mass=1` → object weight
  - `stiffness=80` → spring tightness
  - `damping=10` → oscillation decay

### Quad/Cubic
- **Feel:** Smooth, polished, professional
- **Use:** Color transitions, fade effects
- **Variants:**
  - `easeInQuad` → slow start
  - `easeOutQuad` → slow end
  - `easeInOutQuad` → smooth both sides

### Sine
- **Feel:** Gentle, wave-like
- **Use:** Breathing effects, ambient motion
- **Best for:** Looping animations

---

## Performance Guidelines

### DO ✅
- Animate `scale`, `opacity`, `rotation` (GPU accelerated)
- Use `will-change: transform` for frequently animated elements
- Keep animation durations under 2 seconds for responsiveness
- Batch similar animations together
- Use `requestAnimationFrame` compatible timing

### DON'T ❌
- Animate layout properties (width, height, top, left, margin)
- Create too many simultaneous animations (limit to 10-15)
- Use very long durations (feels sluggish)
- Animate on every frame (use event triggers)
- Forget to clean up completed animations

---

## Integration Examples

### Triggering on Event
```javascript
function handleBrainEvent(data) {
    if (data.intensity > 0.7) {
        // High priority - pulse brain + connections
        AnimationPresets.brainPulse(data.intensity);
        triggerConnectionPulses(data);
    } else {
        // Normal priority - just pulse brain
        AnimationPresets.brainPulse(data.intensity);
    }
}
```

### Chaining Animations
```javascript
anime({
    targets: region.mesh.scale,
    x: 1.5,
    y: 1.5,
    z: 1.5,
    duration: 600,
    easing: 'easeOutElastic(1, .6)',
    complete: () => {
        // Second animation starts after first completes
        anime({
            targets: region.mesh.scale,
            x: 1,
            y: 1,
            z: 1,
            duration: 400,
            easing: 'easeOutQuad'
        });
    }
});
```

### Timeline Sequence
```javascript
const timeline = anime.timeline({
    easing: 'easeOutExpo',
    duration: 750
});

timeline
    .add({
        targets: region1.mesh.scale,
        x: 1.3,
        y: 1.3,
        z: 1.3
    })
    .add({
        targets: region2.mesh.scale,
        x: 1.3,
        y: 1.3,
        z: 1.3,
        offset: '-=500' // Start 500ms before previous ends
    })
    .add({
        targets: connection.line.material,
        opacity: 0.8,
        offset: '-=600'
    });
```

---

## Testing Patterns

### Manual Testing
```bash
# Trigger demo events
curl -X POST http://localhost:8765/api/demo
```

### Console Testing
```javascript
// In browser console:
AnimationPresets.brainPulse(0.9);
AnimationPresets.modeColorTransition(0x00aaff);
```

### Performance Monitoring
```javascript
// Check FPS
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

**Target:** 60fps minimum (16.67ms per frame)  
**Acceptable:** 30fps on lower-end hardware

---

## Future Enhancement Ideas

### Advanced Patterns
- **Attention Focus:** Camera pans to active region
- **Memory Flow:** Particles stream between regions
- **Stress Response:** Faster breathing, redder colors
- **Sleep Mode:** Slower breathing, dim blue palette
- **Burst Activity:** Rapid-fire pulses, staggered timing

### Interactive Animations
- **Click region:** Zoom and highlight
- **Drag camera:** Smooth interpolation
- **Hover region:** Subtle glow increase

### Audio-Reactive (Future)
- Sync animations to system sounds
- Music visualization mode
- Voice activity indicator

---

## Resources

- **anime.js Documentation:** https://animejs.com/documentation/
- **Easing Visualizer:** https://easings.net/
- **Three.js + anime.js examples:** CodePen, CodeSandbox
- **Performance Tips:** Chrome DevTools → Performance tab

---

*These patterns make the brain feel ALIVE. Use them wisely.* 🧠⚡
