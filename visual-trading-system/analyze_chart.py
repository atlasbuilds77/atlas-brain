#!/usr/bin/env python3
"""
Simple Chart Analysis Script
Direct integration example for Atlas

Usage:
  python3 analyze_chart.py /path/to/chart.png
  python3 analyze_chart.py /path/to/chart.png --position LONG --entry 2911
"""

import sys
import json
from pathlib import Path
from ict_patterns import ICT_ANALYSIS_PROMPT, EXIT_CHECK_PROMPT

def analyze_chart(image_path: str, position: str = None, entry: float = None):
    """
    Generate the analysis prompt for a chart image.
    
    In practice, this would be called via Clawdbot's image tool.
    This script outputs the exact prompt to use.
    """
    
    path = Path(image_path)
    if not path.exists():
        print(f"Error: File not found: {image_path}")
        return None
    
    print("=" * 60)
    print("ATLAS EYES - CHART ANALYSIS")
    print("=" * 60)
    print(f"Image: {path.name}")
    
    if position and entry:
        print(f"Position: {position} @ ${entry:,.2f}")
        prompt = EXIT_CHECK_PROMPT.format(
            position_type=position,
            entry_zone=f"${entry:,.2f}"
        )
        print("\n--- EXIT CHECK PROMPT ---")
    else:
        prompt = ICT_ANALYSIS_PROMPT
        print("\n--- FULL ICT ANALYSIS PROMPT ---")
    
    print("=" * 60)
    
    # Output for copy-paste into Clawdbot
    result = {
        "image_path": str(path.absolute()),
        "prompt": prompt,
        "clawdbot_call": f'''
To analyze this chart with Clawdbot, use:

image(
    image="{path.absolute()}",
    prompt="""{prompt}"""
)
'''
    }
    
    print(result["clawdbot_call"])
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_chart.py <image_path> [--position LONG/SHORT] [--entry price]")
        print("\nExamples:")
        print("  python3 analyze_chart.py chart.png")
        print("  python3 analyze_chart.py chart.png --position LONG --entry 2911")
        return
    
    image_path = sys.argv[1]
    position = None
    entry = None
    
    # Parse optional args
    args = sys.argv[2:]
    for i, arg in enumerate(args):
        if arg == "--position" and i + 1 < len(args):
            position = args[i + 1]
        elif arg == "--entry" and i + 1 < len(args):
            try:
                entry = float(args[i + 1])
            except ValueError:
                pass
    
    analyze_chart(image_path, position, entry)

if __name__ == "__main__":
    main()
