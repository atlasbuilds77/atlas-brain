# ElevenLabs Voice Skill

Generate high-quality voice audio from text using ElevenLabs TTS API.

## Quick Use

```bash
# Generate voice audio
~/clawd/skills/elevenlabs-voice/speak.sh "Hello Orion!" --out /tmp/hello.mp3

# Generate and send via iMessage
~/clawd/skills/elevenlabs-voice/speak.sh "Hello Orion!" --send +14245157194

# Use a different voice
~/clawd/skills/elevenlabs-voice/speak.sh "Hello!" --voice sarah --out /tmp/sarah.mp3
```

## Available Voices

| Name | Style |
|------|-------|
| eric | Smooth, trustworthy (DEFAULT) |
| roger | Laid-back, casual |
| sarah | Mature, reassuring |
| charlie | Deep, confident |
| george | Warm storyteller |
| liam | Energetic |
| matilda | Professional |
| will | Relaxed optimist |
| jessica | Playful, bright |
| bella | Professional, bright |

## Voice Conversation Flow

For real-time voice conversations:

1. **Receive voice note** (iMessage attachment)
2. **Transcribe** with OpenAI Whisper API or local whisper
3. **Process** the transcribed text as normal message
4. **Generate response** with this skill
5. **Send back** via iMessage

### Example (Manual)

```bash
# 1. Transcribe incoming audio
curl -s https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@/path/to/voice_note.m4a" \
  -F "model=whisper-1" | jq -r '.text'

# 2. Generate response audio
~/clawd/skills/elevenlabs-voice/speak.sh "Your response here" --send +14245157194
```

## API Details

- **Endpoint**: https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
- **Model**: eleven_multilingual_v2
- **Format**: MP3
- **Key**: Set ELEVENLABS_API_KEY env var

## Credits

Free tier: ~10,000 characters/month
Upgrade at: https://elevenlabs.io/app/subscription
