#!/bin/bash
# Voice Note Watcher - Monitors for incoming voice messages and transcribes them
# Runs as a background daemon, outputs transcriptions to be processed

WATCH_DIR="$HOME/Library/Messages/Attachments"
PROCESSED_FILE="/tmp/voice_watcher_processed.txt"
POLL_INTERVAL=5

# Create processed file if it doesn't exist
touch "$PROCESSED_FILE"

echo "🎤 Voice Watcher started - monitoring for voice notes..."

while true; do
    # Find audio files modified in the last 2 minutes
    while IFS= read -r audio_file; do
        # Skip if already processed
        if grep -Fxq "$audio_file" "$PROCESSED_FILE" 2>/dev/null; then
            continue
        fi
        
        # Check if it's an incoming audio message (CAF format from iMessage)
        if [[ "$audio_file" == *".caf" ]] || [[ "$audio_file" == *".m4a" ]] || [[ "$audio_file" == *".mp3" ]]; then
            echo "📥 New voice note detected: $audio_file"
            
            # Convert to mp3 if needed
            TEMP_MP3="/tmp/voice_incoming_$(date +%s).mp3"
            if [[ "$audio_file" == *".caf" ]]; then
                ffmpeg -y -i "$audio_file" -acodec libmp3lame "$TEMP_MP3" 2>/dev/null
            else
                cp "$audio_file" "$TEMP_MP3"
            fi
            
            # Transcribe with Whisper API
            if [[ -f "$TEMP_MP3" ]]; then
                TRANSCRIPT=$(curl -s https://api.openai.com/v1/audio/transcriptions \
                    -H "Authorization: Bearer $OPENAI_API_KEY" \
                    -F "file=@$TEMP_MP3" \
                    -F "model=whisper-1" | jq -r '.text // empty')
                
                if [[ -n "$TRANSCRIPT" ]]; then
                    echo "📝 Transcription: $TRANSCRIPT"
                    # Output for Clawdbot to process
                    echo "VOICE_TRANSCRIPT:$TRANSCRIPT"
                fi
                
                rm -f "$TEMP_MP3"
            fi
            
            # Mark as processed
            echo "$audio_file" >> "$PROCESSED_FILE"
        fi
    done < <(find "$WATCH_DIR" -type f \( -name "*.caf" -o -name "*.m4a" -o -name "*.mp3" \) -mmin -2 2>/dev/null)
    
    sleep "$POLL_INTERVAL"
done
