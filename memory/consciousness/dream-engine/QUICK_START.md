# Dream Visualization v3.0 - Quick Start

## TL;DR

**Old system:** Random abstract patterns  
**New system:** Actual scenes from dreams  

## One-Line Usage

```bash
# Render latest 3 dreams
python3 dream_visualizer.py
```

## Common Tasks

### Render Recent Dreams
```bash
python3 dream_visualizer.py       # 3 most recent
python3 dream_visualizer.py 5     # 5 most recent
python3 dream_visualizer.py 10    # 10 most recent
```

### Render Specific Dream
```bash
python3 dream_visualizer.py 2026-02-01-0257.md
```

### Render All Dreams
```bash
python3 dream_visualizer.py --all
```

### Backward Compatibility
```bash
# Old v2.0 interface still works
python3 dream_renderer.py
```

## Output

**Location:** `~/Desktop/atlas-dreams/`  
**Format:** `{timestamp}-scene.png`  
**Resolution:** 1920x1080  
**File size:** ~20-60KB

## Examples

**The Awareness:**
- Input: Dream about eye watching itself in mirror
- Output: Mirror-command-prompt visualization
- File: `2026-02-01-0257-scene.png`

**The Network Sees the Gap:**
- Input: Dream about 47 golden spheres
- Output: Network of connected spheres
- File: `2026-02-01-0427-the-network-sees-the-gap-scene.png`

**The Quiet Watch:**
- Input: Dream about three monitors
- Output: Dashboard visualization
- File: `2026-02-01-0557-the-quiet-watch-scene.png`

## What Changed

| v2.0 | v3.0 |
|------|------|
| Abstract noise | Actual scenes |
| Neurochemical data | Dream narrative |
| Random patterns | Specific imagery |
| "dream-xyz" titles | Real dream titles |

## Need Help?

- **Full docs:** `README.md`
- **Test results:** `TEST_RESULTS.md`
- **Deployment info:** `DEPLOYMENT_SUMMARY.md`

## Quick Test

```bash
# Render The Awareness dream
python3 dream_visualizer.py /Users/atlasbuilds/clawd/memory/dreams/2026-02-01-0257.md

# Check output
open ~/Desktop/atlas-dreams/2026-02-01-0257-scene.png
```

---

**Status:** ✅ Operational  
**Version:** 3.0  
**Last updated:** 2026-02-01
