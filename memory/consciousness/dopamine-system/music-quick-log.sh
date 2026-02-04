#!/bin/bash
# Quick music logger for Atlas - call when Hunter mentions what's playing
#
# Usage: ./music-quick-log.sh "Song Title" "Artist" [context]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SONG="$1"
ARTIST="${2:-Unknown}"
CONTEXT="${3:-general}"

if [ -z "$SONG" ]; then
  echo "Usage: $0 \"Song Title\" \"Artist\" [context]"
  exit 1
fi

node "$SCRIPT_DIR/music-brain-integration.js" log "$SONG" "$ARTIST" "$CONTEXT"
