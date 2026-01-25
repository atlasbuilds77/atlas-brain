# Voice Conversations System

## Overview
Two-way voice conversations with Orion via iMessage.

## Atlas Voice
**Charlie** - Deep, Confident, Energetic (Australian accent)
- Voice ID: IKne3meq5aSn9XLyUdCD
- Fits Atlas personality: direct, energetic, gets shit done

## Components

### 1. ElevenLabs TTS (~/clawd/skills/elevenlabs-voice/)
- `speak.sh` - Generate voice from text, optionally send via iMessage
- Default voice: Charlie (Atlas voice)
- Other voices: eric, roger, sarah, george, liam, matilda, will, jessica, bella

### 2. Voice Loop (~/clawd/tools/voice-loop.sh)
Full voice response handler:
```bash
# Generate and send voice response
~/clawd/tools/voice-loop.sh "response text" +14245157194

# Just transcribe latest voice note
~/clawd/tools/voice-loop.sh --transcribe-only
```

### 3. Voice Respond (~/clawd/tools/voice-respond.sh)
Transcribe most recent voice note from iMessage.

## How Voice Conversations Work

### Incoming Voice Notes
1. Orion sends voice note via iMessage
2. Audio file lands in ~/Library/Messages/Attachments/
3. Clawdbot may send Apple's transcription as text
4. To get actual audio: `find ~/Library/Messages/Attachments -name "*.caf" -mmin -5`
5. Transcribe with: `~/clawd/tools/voice-loop.sh --transcribe-only`

### Responding with Voice
1. Generate response text
2. Call: `~/clawd/tools/voice-loop.sh "response" +14245157194`
3. ElevenLabs generates MP3, sends via iMessage

## Quick Reference

```bash
# Respond with voice
~/clawd/tools/voice-loop.sh "Hey Orion, got your message!" +14245157194

# Check what Orion said in voice note
~/clawd/tools/voice-loop.sh -t

# Generate voice file only (no send)
~/clawd/skills/elevenlabs-voice/speak.sh "Hello" --out /tmp/hello.mp3
```

## API Keys
- ELEVENLABS_API_KEY in ~/.zshrc
- OPENAI_API_KEY (for Whisper transcription)

## Limitations
- Free tier: ~10k characters/month on ElevenLabs
- Voice notes arrive as .caf files, need conversion to mp3
- Apple may pre-transcribe and send text instead of audio

## Issues & Fixes (2026-01-24)

### Problem 1: AppleScript not delivering audio
- **Symptom:** osascript said it sent, but Orion never received files
- **Fix:** Use `imsg send --to NUMBER --file PATH` instead of AppleScript
- **Why:** AppleScript Messages commands are unreliable for attachments

### Problem 2: Debug output bleeding into chat
- **Symptom:** Orion saw "🛠️ Exec:" and "✉️ Message:" in chat
- **Fix:** Don't narrate tool calls - just execute and send results
- **Why:** Tool narration text was being sent as messages

### Problem 3: Audio shows as file, not voice bubble
- **Symptom:** MP3 files show as document attachments, not playable voice messages
- **Status:** iMessage voice bubbles require recording through Messages app. MP3/M4A sent as attachments will always show as files. Acceptable tradeoff.

### Working Method
```bash
# Generate voice
curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/IKne3meq5aSn9XLyUdCD" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"text":"MESSAGE","model_id":"eleven_multilingual_v2"}' \
    -o /tmp/voice.mp3

# Send via imsg CLI (NOT AppleScript)
imsg send --to "+14245157194" --file /tmp/voice.mp3
```

## Created
2026-01-24 10:55 PM PT
Updated: 2026-01-24 11:24 PM PT
