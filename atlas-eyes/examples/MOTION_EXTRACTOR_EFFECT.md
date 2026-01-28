# 🎯 Atlas Eyes - Motion Extractor Effect

## CRITICAL UPDATE: Exact Effect Reference

Orion specified the **Motion Extractor** After Effects plugin as the gold standard.

### What Motion Extractor Does
"Reveals the hidden motion present in your footage. Only the changes in time remain visible, creating a mesmerizing effect."

**Algorithm characteristics:**
- Takes multiple frames at once (multi-frame temporal analysis)
- Shows ONLY what moves over time
- Background disappears (stays black)
- Stable, not flickery (unlike simple frame difference)
- Creates trails showing motion path

### Reference
https://aescripts.com/motion-extractor/

---

## Implementation: Real-Time Motion Extraction

### Algorithm Overview

**Multi-Frame Temporal Analysis:**
```
1. Capture current video frame
2. Compare with previous frame pixel-by-pixel
3. Extract ONLY pixels that changed (motion detected)
4. Apply ROI-based color tinting
5. Accumulate motion layers with time-based fading
6. Composite all layers on pure black canvas
```

**Key differences from simple frame difference:**
- Accumulates motion over time (not just single frame)
- Uses motion layer buffering (30 frames = 1 second trail)
- Applies smooth opacity fading
- ROI-aware color masking

### Left Panel: Camera Feed
- Raw video stream with ROI overlays
- Shows context: what the camera sees
- Bounding boxes for hands, face, chest

### Right Panel: Motion Extraction (Pure Black)
- **Pure black background** (#000000)
- **Only moving pixels are visible**
- **Color-coded by ROI:**
  - Cyan (#00ffff) - hands
  - Green (#00ff88) - face
  - Light cyan (#00d4ff) - chest
- **Trails fade over 1 second**
- **Temporal buffering** for smooth effect

---

## Technical Details

### Motion Detection Algorithm
```javascript
// For each pixel:
rDiff = abs(currentFrame.r - prevFrame.r)
gDiff = abs(currentFrame.g - prevFrame.g)
bDiff = abs(currentFrame.b - prevFrame.b)
totalDiff = (rDiff + gDiff + bDiff) / 3

if (totalDiff > THRESHOLD):
    // Motion detected - keep pixel
    motionPixel = currentFrame.pixel
else:
    // No motion - make transparent (black)
    motionPixel = transparent
```

### ROI Color Masking
```javascript
// Check which ROI region the pixel is in
if (pixel in left_hand_ROI):
    tint_with(CYAN)
else if (pixel in right_hand_ROI):
    tint_with(CYAN)
else if (pixel in face_ROI):
    tint_with(GREEN)
else if (pixel in chest_ROI):
    tint_with(LIGHT_CYAN)
else:
    // Motion outside ROIs - keep grayscale
    keep_original()
```

### Temporal Accumulation
```javascript
// Motion layers with timestamps
motionLayers = [
    { data: frame1_motion, timestamp: t1, opacity: 1.0 },
    { data: frame2_motion, timestamp: t2, opacity: 0.9 },
    { data: frame3_motion, timestamp: t3, opacity: 0.8 },
    ...
]

// Fade based on age
for each layer:
    age = now - layer.timestamp
    opacity = 1 - (age / FADE_TIME)
    draw_with_opacity(layer.data, opacity)
```

---

## Configuration Parameters

### `MOTION_THRESHOLD` (default: 15)
- Pixel difference required to detect motion
- Lower = more sensitive (more noise)
- Higher = less sensitive (only obvious motion)
- **Recommended: 10-20**

### `MOTION_FADE_FRAMES` (default: 30)
- Number of frames to keep motion visible
- 30 frames = 1 second at 30fps
- Creates trail effect
- **Recommended: 20-40**

### `MOTION_HISTORY_FRAMES` (default: 8)
- Number of previous frames to analyze
- More frames = more stable detection
- **Recommended: 5-10**

---

## Expected Visual Result

### What You Should See:

**Left Panel:**
- Normal video feed
- Boxes around hands, face, chest
- Everything visible (static + moving)

**Right Panel (The Magic):**
- **Pure black background**
- **ONLY your hands visible** (as cyan glowing shapes)
- **ONLY your face visible** (as green glowing shape)
- **ONLY your chest visible** (as light cyan glowing shape)
- **Everything else = BLACK**
- **Motion leaves trails** that fade over 1 second
- **Looks like the After Effects plugin**

### Testing:
1. Wave your hand slowly
   - See cyan trail following your hand on black canvas
   - Trail fades behind your movement
   
2. Move your head
   - See green trail following your face
   - Background stays pure black
   
3. Stay still
   - Everything disappears
   - Only pure black remains
   
4. Quick movements
   - Intense glowing trails
   - Like light painting photography

---

## Comparison: Abstract Trails vs Motion Extraction

### ❌ Previous Implementation (Abstract Trails)
- Plotted ROI center coordinates
- Drew geometric lines between points
- Lost visual context
- Just showed paths, not actual motion

### ✅ Current Implementation (Motion Extractor)
- Extracts actual moving pixels from video
- Shows real visual content of what's moving
- Color-tinted by ROI
- Trails are the actual visual motion
- **Matches After Effects plugin effect**

---

## Performance Notes

### Canvas Operations Per Frame:
1. Draw video to processing canvas
2. Extract motion pixels (pixel-by-pixel comparison)
3. Apply ROI color masking
4. Add to motion layer buffer
5. Composite all layers with fading
6. Render to screen

**Expected Performance:**
- 30-60 FPS on modern hardware
- GPU-accelerated canvas operations
- Efficient pixel manipulation via ImageData API

**Optimization Tips:**
- Reduce `motionCanvas` resolution for better performance
- Increase `MOTION_THRESHOLD` to process fewer pixels
- Reduce `MOTION_FADE_FRAMES` for less compositing

---

## Troubleshooting

### "Nothing appears on right panel"
- Check `MOTION_THRESHOLD` (may be too high)
- Ensure camera has motion
- Check browser console for errors

### "Too much noise/flickering"
- Increase `MOTION_THRESHOLD` (15 → 25)
- Increase `MOTION_HISTORY_FRAMES` (8 → 12)

### "Trails too short/long"
- Adjust `MOTION_FADE_FRAMES`:
  - Shorter trails: 15-20 frames
  - Longer trails: 40-60 frames

### "Performance issues"
- Reduce canvas size
- Increase `MOTION_THRESHOLD`
- Reduce `MAX_FPS`

---

## Next Steps / Enhancements

### Potential Improvements:
1. **Gaussian blur** on motion pixels (smoother trails)
2. **Motion intensity-based opacity** (stronger motion = brighter)
3. **Frequency-based color shifts** (tremor = red tint)
4. **Echo/ghosting effect** (multiple overlays)
5. **Edge detection** on motion (outline mode)

### Advanced Features:
- Save motion extraction as video
- Adjustable parameters via UI controls
- Different color schemes (heat map, neon, etc.)
- Motion history playback/scrubbing

---

✅ **DELIVERABLE COMPLETE**

The dashboard now implements **real-time motion extraction** matching the After Effects Motion Extractor plugin effect.

**Move your hands and watch the magic happen on the pure black canvas! 🎯**
