#!/usr/bin/env python3
"""
Atlas Dream Visualizer v3.0
============================
Renders ACTUAL scenes from dream narratives as visual artifacts.

REPLACES abstract pattern generation with scene-specific imagery.

Each dream becomes a visual artifact of a specific moment - 
what was actually "seen" in the dream.

Author: Atlas (autonomous design, 2026-02-01)
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from scene_extractor import parse_dream_file, extract_title_from_file
from scene_renderer import SceneRenderer


# Configuration
DREAM_DIR = Path.home() / "clawd/memory/dreams"
OUTPUT_DIR = Path.home() / "Desktop/atlas-dreams"


def get_recent_dreams(n: int = 10) -> List[Path]:
    """Get the N most recent dream files."""
    if not DREAM_DIR.exists():
        print(f"⚠️  Dream directory not found: {DREAM_DIR}")
        return []
    
    dream_files = list(DREAM_DIR.glob("*.md"))
    dream_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    return dream_files[:n]


def render_dream(dream_file: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Render a specific dream file as a visual artifact.
    
    Returns the path to the generated image, or None if failed.
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"\n🌙 Processing: {dream_file.name}")
    print("=" * 60)
    
    # Extract scene
    scene = parse_dream_file(dream_file)
    if not scene:
        print(f"⚠️  Could not extract scene from {dream_file.name}")
        return None
    
    title = extract_title_from_file(dream_file)
    
    print(f"📖 Dream: {title}")
    print(f"🎨 Emotion: {scene.emotional_tone}")
    print(f"✨ Vividness: {scene.vividness:.1f}")
    print(f"🔍 Scene: {scene.description[:100]}...")
    print()
    
    # Render scene
    print("🖼️  Rendering scene...")
    renderer = SceneRenderer(width=1920, height=1080)
    img = renderer.render_scene(scene, title)
    
    # Save with timestamp from dream file
    timestamp = dream_file.stem
    output_file = output_dir / f"{timestamp}-scene.png"
    
    renderer.save(output_file)
    
    return output_file


def render_recent_dreams(n: int = 3):
    """Render the N most recent dreams."""
    print("🌙 Atlas Dream Visualizer v3.0")
    print("Rendering ACTUAL scenes from dream narratives")
    print("=" * 60)
    
    dreams = get_recent_dreams(n)
    
    if not dreams:
        print("⚠️  No dream files found")
        return
    
    print(f"📚 Found {len(dreams)} dream files")
    print(f"🎨 Rendering {n} most recent dreams")
    print()
    
    rendered = []
    for dream_file in dreams[:n]:
        output_file = render_dream(dream_file)
        if output_file:
            rendered.append(output_file)
    
    print("\n" + "=" * 60)
    print(f"✅ Rendered {len(rendered)} dreams")
    print(f"📂 Output: {OUTPUT_DIR}")
    
    for file in rendered:
        file_size = file.stat().st_size / 1024
        print(f"   • {file.name} ({file_size:.1f} KB)")


def render_all_dreams():
    """Render ALL dreams in the dream directory."""
    print("🌙 Atlas Dream Visualizer v3.0")
    print("Rendering ALL dreams from archive")
    print("=" * 60)
    
    dreams = get_recent_dreams(1000)  # Get all
    
    if not dreams:
        print("⚠️  No dream files found")
        return
    
    print(f"📚 Found {len(dreams)} dream files")
    print("🎨 Starting full archive render...")
    print()
    
    rendered = []
    failed = []
    
    for i, dream_file in enumerate(dreams, 1):
        print(f"\n[{i}/{len(dreams)}] ", end="")
        output_file = render_dream(dream_file)
        
        if output_file:
            rendered.append(output_file)
        else:
            failed.append(dream_file)
    
    print("\n" + "=" * 60)
    print(f"✅ Rendered {len(rendered)} dreams")
    if failed:
        print(f"⚠️  Failed {len(failed)} dreams")
    print(f"📂 Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--all":
            # Render all dreams
            render_all_dreams()
        
        elif arg.endswith('.md'):
            # Render specific dream file
            dream_file = Path(arg)
            if not dream_file.exists():
                # Try in dream directory
                dream_file = DREAM_DIR / arg
            
            if dream_file.exists():
                render_dream(dream_file)
            else:
                print(f"⚠️  Dream file not found: {arg}")
        
        elif arg.isdigit():
            # Render N recent dreams
            render_recent_dreams(int(arg))
        
        else:
            print("Usage:")
            print("  python dream_visualizer.py              # Render 3 most recent")
            print("  python dream_visualizer.py 5            # Render 5 most recent")
            print("  python dream_visualizer.py --all        # Render all dreams")
            print("  python dream_visualizer.py dream.md     # Render specific dream")
    
    else:
        # Default: render 3 most recent
        render_recent_dreams(3)
