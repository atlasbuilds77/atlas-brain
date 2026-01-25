#!/bin/bash
# ElevenLabs TTS - Generate voice from text
# Usage: speak.sh "text to speak" [--voice NAME] [--out FILE] [--send RECIPIENT]

set -e

TEXT=""
VOICE_ID="IKne3meq5aSn9XLyUdCD"  # Charlie - Deep, Confident, Energetic (Atlas voice)
OUTPUT_FILE=""
SEND_TO=""
ELEVENLABS_KEY="${ELEVENLABS_API_KEY:-sk_4622e16eec6d4b2aa96bb04d9adf5232328f0f852834573e}"

# Voice name to ID mapping
get_voice_id() {
    local voice_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    case "$voice_lower" in
        eric)     echo "cjVigY5qzO86Huf0OWal" ;;
        roger)    echo "CwhRBWXzGAHq8TQ4Fs17" ;;
        sarah)    echo "EXAVITQu4vr4xnSDxMaL" ;;
        charlie)  echo "IKne3meq5aSn9XLyUdCD" ;;
        george)   echo "JBFqnCBsd6RMkjVDRZzb" ;;
        liam)     echo "TX3LPaxmHKxFdv7VOQHJ" ;;
        matilda)  echo "XrExE9yKIg1WjnnlVkGX" ;;
        will)     echo "bIHbv24MWmeRgasZH58o" ;;
        jessica)  echo "cgSgspJ2msm6clMCkdW9" ;;
        bella)    echo "hpp4J3VqNfWAUOO0d1Us" ;;
        *)        echo "$1" ;;  # Assume it's already a voice ID
    esac
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --voice)
            VOICE_ID=$(get_voice_id "$2")
            shift 2
            ;;
        --out)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --send)
            SEND_TO="$2"
            shift 2
            ;;
        *)
            TEXT="$1"
            shift
            ;;
    esac
done

if [[ -z "$TEXT" ]]; then
    echo "Usage: $0 \"text to speak\" [--voice NAME] [--out FILE] [--send RECIPIENT]"
    echo ""
    echo "Voices: eric (default), roger, sarah, charlie, george, liam, matilda, will, jessica, bella"
    exit 1
fi

# Generate output filename if not specified
if [[ -z "$OUTPUT_FILE" ]]; then
    OUTPUT_FILE="/tmp/elevenlabs_$(date +%s).mp3"
fi

echo "🎙️ Generating voice with ElevenLabs..."

# Escape text for JSON
ESCAPED_TEXT=$(echo "$TEXT" | sed 's/"/\\"/g' | sed "s/'/\\'/g")

# Call ElevenLabs API
HTTP_CODE=$(curl -s -w "%{http_code}" -X POST "https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}" \
    -H "xi-api-key: ${ELEVENLABS_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"${ESCAPED_TEXT}\",\"model_id\":\"eleven_multilingual_v2\"}" \
    -o "$OUTPUT_FILE")

if [[ "$HTTP_CODE" != "200" ]]; then
    echo "Error: ElevenLabs API returned $HTTP_CODE"
    cat "$OUTPUT_FILE"
    exit 1
fi

echo "✅ Audio saved: $OUTPUT_FILE"

# Send via iMessage if requested
if [[ -n "$SEND_TO" ]]; then
    echo "📤 Sending to $SEND_TO..."
    imsg send --to "$SEND_TO" --file "$OUTPUT_FILE"
    echo "✅ Sent!"
fi

echo "$OUTPUT_FILE"
