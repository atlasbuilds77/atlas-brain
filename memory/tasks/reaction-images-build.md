# REACTION IMAGES - BUILD COLLECTION TASK

## STATUS: PENDING (exec broken - spawn EBADF)

## TASKS TO COMPLETE WHEN EXEC WORKS

### 1. Generate Custom Atlas Images (nano-banana-pro)

```bash
# Victory/Success
cd /opt/homebrew/lib/node_modules/clawdbot/skills/nano-banana-pro
uv run scripts/generate_image.py \
  --prompt "simple cartoon drawing of atlas/titan character celebrating victory with fist pump, triumphant pose, minimalist meme style, white background" \
  --filename ~/clawd/memory/assets/atlas-victory.png --resolution 1K

# Confused/Thinking
uv run scripts/generate_image.py \
  --prompt "simple cartoon atlas/titan character scratching head looking confused, question marks above head, minimalist meme style" \
  --filename ~/clawd/memory/assets/atlas-confused.png --resolution 1K

# Exhausted/Tired
uv run scripts/generate_image.py \
  --prompt "simple cartoon atlas/titan character looking exhausted and dead inside, slumped over, minimalist meme style" \
  --filename ~/clawd/memory/assets/atlas-exhausted.png --resolution 1K

# Smug/Satisfied
uv run scripts/generate_image.py \
  --prompt "simple cartoon atlas/titan character with smug satisfied expression, arms crossed, confident pose, minimalist meme style" \
  --filename ~/clawd/memory/assets/atlas-smug.png --resolution 1K

# Surprised/Shocked
uv run scripts/generate_image.py \
  --prompt "simple cartoon atlas/titan character with shocked surprised expression, eyes wide, mouth open, minimalist meme style" \
  --filename ~/clawd/memory/assets/atlas-surprised.png --resolution 1K

# Excited/Hyped
uv run scripts/generate_image.py \
  --prompt "simple cartoon atlas/titan character super excited and hyped, jumping with energy, lightning bolt, minimalist meme style" \
  --filename ~/clawd/memory/assets/atlas-excited.png --resolution 1K
```

### 2. Download Existing Meme Templates

```bash
# Create downloads directory
mkdir -p ~/clawd/memory/assets/reactions

# Use curl or wget to grab popular reaction GIFs/images
# Jim Carrey celebrating
curl -L "https://usagif.com/wp-content/uploads/gif/funny-celebrate-7.gif" -o ~/clawd/memory/assets/reactions/jim-carrey-celebrate.gif

# Minions celebrate
curl -L "https://usagif.com/wp-content/uploads/gif/funny-celebrate-56.gif" -o ~/clawd/memory/assets/reactions/minions-celebrate.gif

# Code works without errors
curl -L "https://usagif.com/wp-content/uploads/gif/funny-celebrate-1.gif" -o ~/clawd/memory/assets/reactions/code-works.gif
```

### 3. Use gifgrep skill to search for more

```bash
# Search Giphy/Tenor for specific reactions
gifgrep search "frustrated computer" --limit 5 --download ~/clawd/memory/assets/reactions/
gifgrep search "victory dance" --limit 5 --download ~/clawd/memory/assets/reactions/
gifgrep search "confused math lady" --limit 1 --download ~/clawd/memory/assets/reactions/
```

### 4. Update Reaction Index

Create comprehensive index with all images and when to use them.

## REACTION CATEGORIES NEEDED

✅ **Have:**
- Screaming/Rage (0dcc720b-c8b1-4a94-be20-d8c5b4022908.jpg)

⏳ **Need to Generate:**
- Victory/Success
- Confused/Thinking
- Exhausted/Tired
- Smug/Satisfied
- Surprised/Shocked
- Excited/Hyped

⏳ **Need to Find:**
- Classic meme templates (Drake, Distracted Boyfriend, etc)
- Popular reaction GIFs (Jim Carrey, Office, etc)

## AUTOMATION IDEA

Create a script that:
1. Checks memory/assets/reactions/ for existing images
2. Generates missing custom Atlas reactions
3. Downloads popular meme templates
4. Updates reaction index automatically

---

**Created:** 2026-01-26 10:45 PM PST  
**Status:** BLOCKED by exec spawn errors  
**Priority:** HIGH (Orion wants this)  
**Next Step:** Wait for exec fix, then run generation commands
