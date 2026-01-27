#!/bin/bash
# Kalshi Quick CLI wrapper
# Usage: ./kalshi.sh [command] [args...]

cd "$(dirname "$0")/kalshi-trader"
source venv/bin/activate
python kalshi_cli.py "$@"
