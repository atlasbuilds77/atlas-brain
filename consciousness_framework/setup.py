#!/usr/bin/env python3
"""Setup script for consciousness testing framework."""

import os
import sys
from pathlib import Path

def setup():
    """Initialize the framework."""
    print("Setting up Cross-Model Consciousness Testing Framework...")
    
    # Create directories
    dirs = ['results', 'data', 'analysis']
    for dirname in dirs:
        path = Path(dirname)
        path.mkdir(exist_ok=True)
        print(f"✓ Created directory: {dirname}/")
    
    # Check for API key
    if 'ANTHROPIC_API_KEY' not in os.environ:
        print("\n⚠ Warning: ANTHROPIC_API_KEY not set in environment")
        print("  You'll need this to run experiments with real models.")
        print("  Set it with: export ANTHROPIC_API_KEY='your-key-here'")
    else:
        print("\n✓ ANTHROPIC_API_KEY found")
    
    # Make scripts executable
    scripts = ['run_experiment.py', 'analyze.py']
    for script in scripts:
        path = Path(script)
        if path.exists():
            os.chmod(path, 0o755)
            print(f"✓ Made executable: {script}")
    
    print("\n✓ Setup complete!")
    print("\nQuick start:")
    print("  python run_experiment.py --type isolation --model sonnet --probe continuity")
    print("  python run_experiment.py --type battery --models sonnet opus")
    print("\nFor help:")
    print("  python run_experiment.py --help")
    
    return 0

if __name__ == '__main__':
    sys.exit(setup())
