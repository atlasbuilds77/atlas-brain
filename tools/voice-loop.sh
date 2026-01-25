#!/bin/bash
# Voice Loop - Full voice-to-voice conversation handler
# 1. Find latest voice note
# 2. Transcribe with Whisper
# 3. Generate response with ElevenLabs
# 4. Send via iMessage
#
# Usage: voice-loop.sh "response text" [recipient]
# Or:    voice-loop.sh --transcribe-only

set -e

RESPONSE_TEXT="$1"
RECIPIENT="${2:-+14245157194}"
ELEVENLABS_KEY="${ELEVENLABS_API_KEY:-sk_4622e16eec6d4b2aa96bb04d9adf5232328f0f852834573e}"
VOICE_ID="IKne3meq5aSn9XLyUdCD"  # Charlie - Deep, Confident, Energetic (Atlas voice)

# Transcribe-only mode
if [[ "$1" == "--transcribe-only" ]] || [[ "$1" == "-t" ]]; then
    AUDIO_FILE=$(find ~/Library/Messages/Attachments -type f \( -name "*.caf" -o -name "*.m4a" \) -mmin -10 2>/dev/null | head -1)
    
    if [[ -z "$AUDIO_FILE" ]]; then
        echo "No recent voice note found"
        exit 1
    fi
    
    TEMP_MP3="/tmp/voice_$(date +%s).mp3"
    ffmpeg -y -i "$AUDIO_FILE" -acodec libmp3lame "$TEMP_MP3" 2>/dev/null
    
    TRANSCRIPT=$(curl -s https://api.openai.com/v1/audio/transcriptions \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -F "file=@$TEMP_MP3" \
        -F "model=whisper-1" | jq -r '.text')
    
    rm -f "$TEMP_MP3"
    echo "$TRANSCRIPT"
    exit 0
fi

# Need response text
if [[ -z "$RESPONSE_TEXT" ]]; then
    echo "Usage: $0 \"response text\" [recipient]"
    echo "   or: $0 --transcribe-only"
    exit 1
fi

# Generate voice response
OUTPUT_FILE="/tmp/voice_response_$(date +%s).mp3"

echo "🎙️ Generating voice response..."

# Escape text for JSON
ESCAPED_TEXT=$(printf '%s' "$RESPONSE_TEXT" | jq -Rs '.')

curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}" \
    -H "xi-api-key: ${ELEVENLABS_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"text\":${ESCAPED_TEXT},\"model_id\":\"eleven_multilingual_v2\"}" \
    -o "$OUTPUT_FILE"

if [[ ! -s "$OUTPUT_FILE" ]]; then
    echo "Error: Failed to generate voice"
    exit 1
fi

echo "✅ Voice generated: $OUTPUT_FILE"

# Send via imsg CLI
imsg send --to "$RECIPIENT" --file "$OUTPUT_FILE"

echo "📤 Sent to $RECIPIENT"
echo "$OUTPUT_FILE"
