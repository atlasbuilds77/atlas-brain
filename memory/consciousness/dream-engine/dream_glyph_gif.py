#!/usr/bin/env python3
"""
Dream Glyph GIF Renderer
Generates a looping glyph-field GIF using latest dream PNG as a mask.
"""
import os, glob, math, random, json
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

OUT_DIR = Path(os.path.expanduser('~/Desktop/atlas-dreams'))
MASK_GLOB = str(OUT_DIR / 'dream_*.png')
WIDTH, HEIGHT = 1920, 1080
COLS, ROWS = 120, 68
FRAMES = 24
DURATION_MS = 80  # 12.5 fps

PURPLE = (150, 70, 220)
AMBER = (255, 185, 70)
BLUE = (90, 140, 255)

BINARY_ONLY = True


def lerp(a, b, t):
    return int(a + (b - a) * t)


def mix(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def latest_mask():
    files = sorted(glob.glob(MASK_GLOB))
    if not files:
        return None
    return files[-1]


def latest_dream_title():
    try:
        with open(os.path.expanduser('~/clawd/memory/consciousness/dopamine-system/dream-journal.jsonl'), 'r') as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
        if not lines:
            return 'dream'
        d = json.loads(lines[-1])
        return d.get('title', 'dream') or 'dream'
    except Exception:
        return 'dream'


def slugify(text, max_len=40):
    if not text:
        return 'dream'
    keep = []
    for ch in text.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in [' ', '_', '-']:
            keep.append('-')
    slug = ''.join(keep)
    while '--' in slug:
        slug = slug.replace('--', '-')
    slug = slug.strip('-')
    return slug[:max_len] if slug else 'dream'


def load_font(size=14):
    candidates = [
        '/System/Library/Fonts/Menlo.ttc',
        '/System/Library/Fonts/SFNSMono.ttf',
        '/Library/Fonts/Menlo.ttc'
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main():
    mask_path = latest_mask()
    if mask_path:
        base = Image.open(mask_path).convert('L')
    else:
        base = Image.new('L', (WIDTH, HEIGHT), 0)

    mask = base.resize((COLS, ROWS), resample=Image.BILINEAR)
    font = load_font(14)
    cell_w = WIDTH // COLS
    cell_h = HEIGHT // ROWS

    frames = []
    for f in range(FRAMES):
        img = Image.new('RGB', (WIDTH, HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        phase = f / FRAMES * math.tau

        for y in range(ROWS):
            for x in range(COLS):
                v = mask.getpixel((x, y)) / 255.0
                # shimmer + flicker
                shimmer = 0.15 * math.sin(phase + x * 0.15 + y * 0.1)
                v = max(0.0, min(1.0, v + shimmer + random.uniform(-0.03, 0.03)))

                if v < 0.12:
                    # sparse purple field
                    if random.random() < 0.15:
                        ch = '.' if BINARY_ONLY else random.choice('.,:`')
                        col = mix(PURPLE, BLUE, 0.3)
                    else:
                        continue
                else:
                    ch = '1' if (random.random() < v) else '0' if BINARY_ONLY else random.choice('01abcdef')
                    col = mix(PURPLE, AMBER, v)

                px = x * cell_w + 2
                py = y * cell_h
                draw.text((px, py), ch, fill=col, font=font)

        # glow pass
        glow = img.filter(ImageFilter.GaussianBlur(2))
        img = ImageChops.add(img, glow, scale=1.0, offset=0)
        frames.append(img)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    slug = slugify(latest_dream_title())
    out_path = OUT_DIR / f'dream_glyph_{ts}_{slug}.gif'
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=DURATION_MS, loop=0, disposal=2)
    print(str(out_path))

if __name__ == '__main__':
    main()
