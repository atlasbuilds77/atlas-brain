#!/bin/bash
# Voice Conversation Handler
# Usage: voice-conversation.sh <audio_file> <recipient>
# Transcribes audio, sends to Atlas, generates voice response

set -e

AUDIO_FILE="$1"
RECIPIENT="${2:-+14245157194}"
ELEVENLABS_KEY="${ELEVENLABS_API_KEY:-sk_4622e16eec6d4b2aa96bb04d9adf5232328f0f852834573e}"
VOICE_ID="${ELEVENLABS_VOICE:-cjVigY5qzO86Huf0OWal}"  # Eric - smooth, trustworthy

if [[ -z "$AUDIO_FILE" ]]; then
    echo "Usage: $0 <audio_file> [recipient]"
    exit 1
fi

if [[ ! -f "$AUDIO_FILE" ]]; then
    echo "Error: Audio file not found: $AUDIO_FILE"
    exit 1
fi

echo "🎤 Transcribing audio..."

# Transcribe with Whisper (local or API)
if command -v whisper &> /dev/null; then
    # Local Whisper
    TRANSCRIPT=$(whisper "$AUDIO_FILE" --model tiny --output_format txt --output_dir /tmp 2>/dev/null)
    TRANSCRIPT=$(cat "/tmp/$(basename "${AUDIO_FILE%.*}").txt" 2>/dev/null || echo "")
else
    # OpenAI Whisper API
    TRANSCRIPT=$(curl -s https://api.openai.com/v1/audio/transcriptions \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -F "file=@$AUDIO_FILE" \
        -F "model=whisper-1" | jq -r '.text')
fi

if [[ -z "$TRANSCRIPT" || "$TRANSCRIPT" == "null" ]]; then
    echo "Error: Failed to transcribe audio"
    exit 1
fi

echo "📝 Transcript: $TRANSCRIPT"
echo "$TRANSCRIPT"
