#!/bin/bash
# Atlas Dream Engine - Quick Render
# Usage: bash render_dream.sh [optional_output_path]
cd "$(dirname "$0")"
python3 dream_renderer.py "$@"
python3 dream_glyph_gif.py
