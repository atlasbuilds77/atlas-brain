# 🎯 Testing the Motion Extractor Effect

## Quick Start

### 1. Start the Atlas Eyes Server
```bash
cd ~/clawd/atlas-eyes/examples
python motion_trails_api.py
```

Expected output:
```
🚀 Atlas Eyes Motion Trails API Server
📡 Server: http://localhost:5001
🎥 Video feed: http://localhost:5001/video_feed
✅ Server started
```

### 2. Open the Dashboard
```bash
open motion_trails_dashboard.html
```

Or navigate to: `file:///Users/atlasbuilds/clawd/atlas-eyes/examples/motion_trails_dashboard.html`

### 3. Test the Effect

#### LEFT PANEL (Camera Feed)
- Should show live video from your camera
- Colored boxes around detected regions:
  - **Cyan boxes** = hands
  - **Green box** = face
  - **Light cyan box** = chest

#### RIGHT PANEL (Motion Extractor - The Magic!)
- Should be **pure black** when nothing moves
- When you move:
  - **Wave your hand** → See cyan glowing shape following your hand
  - **Move your head** → See green glowing shape following your face
  - **Move your torso** → See light cyan glowing chest motion
  - **Stay still** → Everything fades to black

---

## What You Should See

### Static (No Movement)
```
LEFT PANEL:          RIGHT PANEL:
┌────────────┐      ┌────────────┐
│            │      │            │
│  You       │      │   PURE     │
│  sitting   │      │   BLACK    │
│  still     │      │            │
│            │      │            │
└────────────┘      └────────────┘
```

### Moving Hand
```
LEFT PANEL:          RIGHT PANEL:
┌────────────┐      ┌────────────┐
│            │      │            │
│  [Hand]──→ │      │   ╱╲       │  ← CYAN TRAIL
│            │      │  ╱  ╲      │    (only hand visible)
│            │      │ ╱    ╲     │
│            │      │       ↓    │
└────────────┘      └────────────┘
```

### Multiple Movements
```
LEFT PANEL:          RIGHT PANEL:
┌────────────┐      ┌────────────┐
│  [Face]    │      │   ●~~~     │  ← GREEN (face)
│            │      │            │
│ [Hand] [Hand]     │  ◐~~~ ~~◐  │  ← CYAN (hands)
│            │      │            │
│  [Chest]   │      │    ▓▓▓     │  ← LIGHT CYAN (chest)
└────────────┘      └────────────┘
      ↑                    ↑
  All visible        Only moving parts
   (normal)           on BLACK canvas
```

---

## Demo Movements

### Test 1: Hand Wave
1. Start with hands still
2. Slowly wave one hand left to right
3. **Expected:** Cyan trail follows hand on black canvas
4. Stop moving
5. **Expected:** Trail fades out over 1 second

### Test 2: Face Movement
1. Keep body still
2. Turn your head slowly left to right
3. **Expected:** Green trail follows face movement
4. Stop moving
5. **Expected:** Face trail fades to black

### Test 3: Full Body Dance
1. Move hands, head, and torso
2. **Expected:** Multi-colored glowing trails:
   - Cyan hands
   - Green face
   - Light cyan chest
3. Stop
4. **Expected:** All trails fade to pure black

### Test 4: Quick vs Slow
1. Move hand SLOWLY
   - **Expected:** Faint, smooth trail
2. Move hand QUICKLY
   - **Expected:** Bright, intense glowing trail
3. **Observation:** Motion intensity affects brightness

---

## Troubleshooting

### ❌ Right panel stays pure black (no motion showing)
**Possible causes:**
- `MOTION_THRESHOLD` too high
- Camera not detecting changes
- No ROIs detected

**Fix:**
1. Open browser console (F12)
2. Check for errors
3. Lower threshold: Change `MOTION_THRESHOLD: 15` → `10`
4. Move more dramatically

### ❌ Too much noise/flickering
**Cause:** Threshold too low or camera noise

**Fix:**
1. Increase `MOTION_THRESHOLD: 15` → `25`
2. Ensure good lighting
3. Use higher quality camera

### ❌ Trails too short
**Cause:** Fade time too short

**Fix:**
Change `MOTION_FADE_FRAMES: 30` → `60` (2 seconds)

### ❌ Trails too long
**Cause:** Fade time too long

**Fix:**
Change `MOTION_FADE_FRAMES: 30` → `15` (0.5 seconds)

### ❌ Left panel shows video, right panel black (no motion detected)
**Cause:** ROI detection might be off

**Check:**
1. Are ROI boxes visible on left panel?
2. Are you moving within the boxes?
3. Try moving more dramatically

---

## Performance Check

### Check FPS
Look at header status bar:
- **Target:** 30-60 FPS
- **Good:** 25+ FPS
- **Poor:** <20 FPS

### If Performance Poor:
1. Close other browser tabs
2. Reduce `MAX_FPS: 60` → `30`
3. Increase `MOTION_THRESHOLD` (fewer pixels to process)

---

## Visual Comparison

### This is NOT what you should see:
❌ Simple trails (just lines)
❌ Geometric paths
❌ Abstract coordinates
❌ Everything visible

### This IS what you should see:
✅ Actual visual content of moving parts
✅ Glowing colored shapes (hands, face, chest)
✅ Trails that are the REAL motion
✅ Everything else = pure black
✅ **Looks like After Effects Motion Extractor plugin**

---

## Recording the Effect

### To capture the motion extraction:
1. Screen record the dashboard
2. Focus on RIGHT PANEL (motion extraction canvas)
3. Perform movements
4. Result: Video of pure motion on black canvas

**Example movements to record:**
- Hand choreography
- Face expressions
- Dance movements
- Gesture sequences

---

## Next: Share with Orion

Once working, capture a video showing:
1. Split screen (left = normal, right = motion extraction)
2. Demonstrate effect with hand movements
3. Show color coding (cyan hands, green face)
4. Show trails fading on black canvas

**This should match the Motion Extractor plugin aesthetic! 🎯**

---

✅ Ready to test? Run the commands above and start moving!
