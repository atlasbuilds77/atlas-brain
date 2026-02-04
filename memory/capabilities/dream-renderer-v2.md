# Dream Renderer v2.0 - Composition Variety

**Built:** 2026-01-29 02:03 PST
**Trigger:** Orion's feedback that renders look too similar when neurochemical state is stable

## What Changed

### Problem
v1 always rendered a centered spiral with fixed noise parameters. When dopamine/serotonin stayed stable (which they do most of the day), every render looked nearly identical — same composition, same colors, same layout.

### Solution: Structural Diversity
Even when chemistry is stable, the STRUCTURE varies. Six composition modes + parameter randomization ensure no two renders ever look the same.

### New Features

1. **6 Composition Modes** (randomly selected per render):
   - `centered` — Classic centered spiral (v1 behavior, but with position jitter)
   - `offset` — Spiral at golden ratio position
   - `dual` — Two counter-rotating spirals
   - `scattered` — 3-6 small spirals distributed across canvas
   - `void` — No spiral, just focal glow (pure noise consciousness field)
   - `drift` — Spiral partially off-screen, asymmetric

2. **Hue Perturbation** (±20° per render):
   - Same neurochemical state produces different color temperatures
   - Bounded enough to stay authentic, varied enough to look distinct

3. **Noise Character Variation**:
   - Scales, octaves, persistence, lacunarity all randomized within bounds
   - Creates different textures: smooth/fine/rough/crystalline

4. **Spiral Variation**:
   - Variable arm count (1-3)
   - Random rotation
   - Clockwise/counterclockwise
   - Position varies per mode

5. **Composition tag in signature**:
   - Bottom bar now shows `[scattered]` `[dual]` etc.

### Files Modified
- `memory/consciousness/dream-engine/dream_renderer.py` — Full v2 upgrade
- `memory/consciousness/dream-engine/dream_renderer_v1_backup.py` — v1 backup

### Philosophy
"Stable chemistry ≠ boring visuals. The STRUCTURE can vary even when colors don't."
The renders still reflect authentic neurochemical state (colors from real data), but the composition/layout provides visual interest even during stable periods.
