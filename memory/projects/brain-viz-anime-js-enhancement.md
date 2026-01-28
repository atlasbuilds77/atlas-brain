# Brain Visualization - Anime.js Enhancement Ideas

**Created:** 2026-01-27 7:58 PM PST  
**Context:** Orion suggested using anime.js for brain animations instead of pure Three.js

---

## WHY ANIME.JS

**Current:** Three.js handles everything (geometry, animations, particles)  
**Better:** anime.js for smooth animation timelines + Three.js for 3D rendering

**Advantages:**
- Easing functions (elastic, bounce, spring physics)
- Timeline control (sequence events perfectly)
- Smoother transitions between states
- Less code for complex animations
- Better performance on lower-end hardware

---

## ANIMATION IDEAS

### 1. Cognitive Event Pulses
**Current:** Particles spawn and fade
**With anime.js:**
- Elastic bounce on region activation
- Spring-based ripple effects
- Stagger animations (wave patterns)
- Smooth intensity transitions

### 2. Connection Strengthening
**Current:** Static lines between regions
**With anime.js:**
- Pulse animation along connection paths
- Color transitions based on activity
- Width morphing (thicker = stronger connection)
- Glow effects on high-priority events

### 3. Mode Switches
**Current:** Color changes
**With anime.js:**
- Smooth color transitions (not instant)
- Camera zoom/rotation to highlight active region
- Background fade effects
- UI element morphing

### 4. Brain Breathing
**Idea:** Entire brain subtly expands/contracts like breathing
- Slow sine wave scale (0.98 → 1.02)
- Synchronized with "thought cycles"
- Creates organic living feel

### 5. Attention Focus
**When important event fires:**
- Camera smoothly pans to region
- Region scales up (1.0 → 1.2)
- Other regions dim/desaturate
- Returns to overview after event

### 6. Memory Consolidation
**Visual for sleep/memory processing:**
- Particles flow from active regions to memory region
- Trail effects (like neurons firing)
- Accumulation visualization
- Burst release when consolidated

---

## TECHNICAL IMPLEMENTATION

### Integration Pattern
```javascript
// Current: Three.js only
region.scale.set(1.2, 1.2, 1.2);

// With anime.js
anime({
  targets: region.scale,
  x: 1.2,
  y: 1.2,
  z: 1.2,
  duration: 500,
  easing: 'easeOutElastic(1, .8)'
});
```

### Performance Considerations
- anime.js is lightweight (9KB gzipped)
- Works alongside Three.js (no conflicts)
- RequestAnimationFrame compatible
- Can animate Three.js properties directly

### File Structure
```
memory/visuals/
├── live-brain.html           # Main visualization
├── live-brain-anime.html     # Enhanced version with anime.js
├── animations/
│   ├── cognitive-pulses.js   # Reusable animation presets
│   ├── connections.js
│   └── transitions.js
```

---

## PRIORITY ENHANCEMENTS

### Phase 1 (Quick Wins)
1. **Event pulses** - Elastic bounce instead of linear fade
2. **Connection glow** - Pulse along paths on high-priority events
3. **Mode transitions** - Smooth color morphing

### Phase 2 (Polish)
4. **Camera movements** - Smooth pan to active regions
5. **Brain breathing** - Subtle scale animation
6. **Particle trails** - Flow effects for memory/decisions

### Phase 3 (Advanced)
7. **Timeline sequences** - Choreograph complex events
8. **State transitions** - Smooth between different brain "modes"
9. **Interactive controls** - User can trigger/scrub animations

---

## REFERENCES

- **anime.js:** https://animejs.com/
- **Three.js + anime.js examples:** Search CodePen/GitHub
- **Performance tips:** Use will-change, transform properties
- **Easing visualizer:** https://easings.net/

---

## NEXT STEPS

1. **Test integration** - Add anime.js to live-brain.html
2. **Prototype one animation** - Event pulse with elastic easing
3. **Measure performance** - Compare before/after FPS
4. **Build animation library** - Reusable presets for different events
5. **Document patterns** - Best practices for brain animations

---

*anime.js = the secret sauce for making the brain feel ALIVE* ⚡🧠
