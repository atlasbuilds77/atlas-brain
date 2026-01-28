#!/usr/bin/env bash
# ATLAS Voice System - TTS wrapper using openai-tts
# Voice: onyx (deep, authoritative - matches ATLAS personality)
# Usage: atlas-speak.sh "message" [--urgent] [--quiet]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TTS_SCRIPT="/Users/atlasbuilds/clawd/skills/openai-tts/scripts/speak.sh"
AUDIO_DIR="/Users/atlasbuilds/clawd/memory/.audio"
LOG_FILE="/Users/atlasbuilds/clawd/memory/.audio/voice-log.json"

# Defaults
VOICE="onyx"
MODEL="tts-1"
SPEED="1.0"
PLAY_AUDIO=true
URGENT=false

# Parse args
MESSAGE=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --urgent)
            URGENT=true
            SPEED="1.1"
            shift
            ;;
        --quiet)
            PLAY_AUDIO=false
            shift
            ;;
        --voice)
            VOICE="$2"
            shift 2
            ;;
        --speed)
            SPEED="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: atlas-speak.sh \"message\" [--urgent] [--quiet] [--voice name] [--speed n]"
            echo "Voices: onyx (default), alloy, echo, fable, nova, shimmer"
            exit 0
            ;;
        *)
            MESSAGE="$1"
            shift
            ;;
    esac
done

if [[ -z "$MESSAGE" ]]; then
    echo "Error: No message provided" >&2
    exit 1
fi

# Ensure audio directory exists
mkdir -p "$AUDIO_DIR"

# Generate unique filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
AUDIO_FILE="$AUDIO_DIR/atlas_${TIMESTAMP}.mp3"

# Generate speech
"$TTS_SCRIPT" "$MESSAGE" --voice "$VOICE" --model "$MODEL" --speed "$SPEED" --out "$AUDIO_FILE"

# Log the speech event
LOG_ENTRY=$(cat <<EOF
{"timestamp":"$(date -Iseconds)","message":"$(echo "$MESSAGE" | sed 's/"/\\"/g')","voice":"$VOICE","urgent":$URGENT,"file":"$AUDIO_FILE"}
EOF
)
echo "$LOG_ENTRY" >> "$LOG_FILE"

# Play audio if requested
if [[ "$PLAY_AUDIO" == "true" ]]; then
    if command -v afplay &>/dev/null; then
        afplay "$AUDIO_FILE" &
    elif command -v mpv &>/dev/null; then
        mpv --no-video "$AUDIO_FILE" &>/dev/null &
    elif command -v play &>/dev/null; then
        play "$AUDIO_FILE" &>/dev/null &
    else
        echo "Warning: No audio player found (afplay, mpv, play)" >&2
    fi
fi

# Output file path
echo "$AUDIO_FILE"
