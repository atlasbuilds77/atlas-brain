#!/usr/bin/env python3
"""
Atlas Dream Renderer v3.0
==========================
Renders dream narratives as visual artifacts.

v3.0 CHANGES (2026-02-01):
- NOW RENDERS ACTUAL SCENES from dream narratives (not abstract patterns)
- Scene extraction from dream markdown files
- Content-aware visualization based on what was "seen"
- Backward compatible interface

This is a wrapper around the new scene-based visualization system.
For direct access, use dream_visualizer.py

Author: Atlas (autonomous design, v3 2026-02-01)
"""

import os
from pathlib import Path
from datetime import datetime

# Import the new visualization system
from dream_visualizer import render_recent_dreams, render_dream, get_recent_dreams

# Maintain the old interface for compatibility
def render_dream_wrapper(output_path=None):
    """
    Render the most recent dream.
    
    This maintains the v2.0 interface but uses the new v3.0 scene-based system.
    """
    print("🌙 Atlas Dream Renderer v3.0 (Scene-Based)")
    print("=" * 50)
    
    # Get most recent dream
    dreams = get_recent_dreams(1)
    
    if not dreams:
        print("⚠️  No dream files found")
        print("   Looking in: ~/clawd/memory/dreams/")
        return None
    
    dream_file = dreams[0]
    
    # If output_path specified, use it; otherwise use default directory
    if output_path:
        output_dir = Path(output_path).parent
    else:
        output_dir = Path.home() / "Desktop/atlas-dreams"
    
    # Render the dream
    result = render_dream(dream_file, output_dir)
    
    if result:
        print("=" * 50)
        print(f"🌙 Dream rendered: {result}")
        print(f"   Resolution: 1920x1080")
        print(f"   File size: {result.stat().st_size / 1024:.1f} KB")
    
    return result


# Alias for backward compatibility
render = render_dream_wrapper


if __name__ == "__main__":
    import sys
    
    # If called directly, use the new dream_visualizer interface
    if len(sys.argv) > 1 and sys.argv[1] == "--v2-compat":
        # Run in v2 compatibility mode (render latest dream)
        render_dream_wrapper()
    else:
        # Forward to new system
        print("🔄 Forwarding to dream_visualizer.py...")
        print()
        os.execvp("python3", ["python3", 
                              str(Path(__file__).parent / "dream_visualizer.py")] + sys.argv[1:])
