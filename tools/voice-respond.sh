#!/bin/bash
# Voice Respond - Transcribe incoming voice note and prepare voice response
# Usage: voice-respond.sh [audio_file]
# If no file provided, finds the most recent voice note

set -e

AUDIO_FILE="$1"
ELEVENLABS_KEY="${ELEVENLABS_API_KEY:-sk_4622e16eec6d4b2aa96bb04d9adf5232328f0f852834573e}"
VOICE_ID="cjVigY5qzO86Huf0OWal"  # Eric

# If no file provided, find most recent
if [[ -z "$AUDIO_FILE" ]]; then
    AUDIO_FILE=$(find ~/Library/Messages/Attachments -type f \( -name "*.caf" -o -name "*.m4a" \) -mmin -5 2>/dev/null | head -1)
fi

if [[ -z "$AUDIO_FILE" ]] || [[ ! -f "$AUDIO_FILE" ]]; then
    echo "No recent voice note found"
    exit 1
fi

echo "🎤 Processing: $AUDIO_FILE"

# Convert to mp3
TEMP_MP3="/tmp/voice_in_$(date +%s).mp3"
ffmpeg -y -i "$AUDIO_FILE" -acodec libmp3lame "$TEMP_MP3" 2>/dev/null

# Transcribe
echo "📝 Transcribing..."
TRANSCRIPT=$(curl -s https://api.openai.com/v1/audio/transcriptions \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -F "file=@$TEMP_MP3" \
    -F "model=whisper-1" | jq -r '.text')

echo "💬 You said: $TRANSCRIPT"

# Clean up
rm -f "$TEMP_MP3"

# Output transcript for further processing
echo "$TRANSCRIPT"
