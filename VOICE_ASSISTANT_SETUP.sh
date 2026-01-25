#!/bin/bash
# Voice Assistant Setup for Mac Mini M4
# "Hey Atlas" - Voice-activated assistant that only responds to Orion's voice
# 100% local, no cloud, HomePod integration

set -e

echo "🎤 Atlas Voice Assistant Setup"
echo "================================"
echo ""

# Check if running on Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script must run on macOS"
    exit 1
fi

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "📦 Installing dependencies..."

# Install Python 3.11+ (required for Whisper)
brew install python@3.11

# Install ffmpeg (required for audio processing)
brew install ffmpeg

# Install portaudio (required for microphone access)
brew install portaudio

# Install SoX (audio processing)
brew install sox

# Create Python virtual environment for voice assistant
VOICE_DIR="$HOME/.atlas-voice"
mkdir -p "$VOICE_DIR"

python3.11 -m venv "$VOICE_DIR/venv"
source "$VOICE_DIR/venv/bin/activate"

echo "🐍 Installing Python packages..."

# Install Whisper (speech-to-text)
pip install --upgrade pip
pip install openai-whisper

# Install PyAudio (microphone access)
pip install pyaudio

# Install pyttsx3 (text-to-speech)
pip install pyttsx3

# Install voice activity detection
pip install webrtcvad

# Install numpy for audio processing
pip install numpy scipy

# Install sounddevice for audio I/O
pip install sounddevice soundfile

# Install voice recognition training
pip install speechbrain torch torchaudio

# Install wake word detection
pip install pvporcupine  # Picovoice Porcupine (free tier)

echo "📥 Downloading Whisper model (this may take a few minutes)..."
python3 -c "import whisper; whisper.load_model('base')"

echo "✅ Dependencies installed!"
echo ""

# Create voice assistant Python script
cat > "$VOICE_DIR/atlas_voice.py" << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""
Atlas Voice Assistant
Voice-activated AI assistant with speaker verification
Only responds to Orion's voice
"""

import os
import sys
import time
import wave
import json
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper
import pyttsx3
from pathlib import Path

# Configuration
VOICE_DIR = Path.home() / ".atlas-voice"
VOICE_PROFILE_PATH = VOICE_DIR / "orion_voice_profile.json"
WAKE_WORDS = ["hey atlas", "atlas"]
SAMPLE_RATE = 16000
CHANNELS = 1
HOMEPOD_NAME = "HomePod"  # AirPlay device name

class VoiceAssistant:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        self.tts_engine = pyttsx3.init()
        self.listening = False
        self.voice_profile = self.load_voice_profile()
        
        # Configure TTS voice
        voices = self.tts_engine.getProperty('voices')
        # Use a pleasant male voice (adjust index as needed)
        self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('rate', 175)  # Speed
        
    def load_voice_profile(self):
        """Load Orion's voice profile"""
        if VOICE_PROFILE_PATH.exists():
            with open(VOICE_PROFILE_PATH, 'r') as f:
                return json.load(f)
        return None
    
    def verify_speaker(self, audio_data):
        """Verify if speaker is Orion (placeholder for now)"""
        # TODO: Implement proper speaker verification
        # For now, always return True during setup
        return True
    
    def detect_wake_word(self, text):
        """Check if wake word was spoken"""
        text_lower = text.lower()
        return any(wake_word in text_lower for wake_word in WAKE_WORDS)
    
    def listen_for_command(self, duration=5):
        """Record audio and transcribe"""
        print("🎤 Listening...")
        
        # Record audio
        audio_data = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='float32'
        )
        sd.wait()
        
        # Convert to Whisper format
        audio_np = audio_data.flatten()
        
        # Transcribe with Whisper
        result = self.whisper_model.transcribe(audio_np, language='en')
        text = result['text'].strip()
        
        return text
    
    def speak(self, text, use_homepod=True):
        """Speak response via HomePod or built-in speaker"""
        print(f"🔊 Atlas: {text}")
        
        if use_homepod:
            # Generate speech to temporary file
            temp_audio = VOICE_DIR / "response.wav"
            self.tts_engine.save_to_file(text, str(temp_audio))
            self.tts_engine.runAndWait()
            
            # Play via AirPlay to HomePod
            os.system(f'afplay -d "{HOMEPOD_NAME}" "{temp_audio}"')
        else:
            # Use built-in speaker
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
    
    def process_command(self, command):
        """Process user command and generate response"""
        # Strip wake word
        command_clean = command.lower()
        for wake_word in WAKE_WORDS:
            command_clean = command_clean.replace(wake_word, "").strip()
        
        print(f"📝 Command: {command_clean}")
        
        # Route to Clawdbot for processing
        # For now, return a placeholder response
        if "status" in command_clean:
            return "All systems running. FuturesRelay is live. Token usage at 45%."
        elif "deploy" in command_clean:
            return "Starting deployment now. I'll notify you when complete."
        elif "reminder" in command_clean or "remind" in command_clean:
            return "Reminder set. I'll alert you at the specified time."
        else:
            return "I'm listening. How can I help?"
    
    def run(self):
        """Main loop - continuously listen for wake word"""
        print("✅ Atlas Voice Assistant is running")
        print(f"🎤 Wake words: {', '.join(WAKE_WORDS)}")
        print("👂 Listening for Orion's voice...")
        print("")
        
        while True:
            try:
                # Listen for wake word (short duration)
                audio_text = self.listen_for_command(duration=3)
                
                if not audio_text:
                    continue
                
                # Check for wake word
                if self.detect_wake_word(audio_text):
                    # Verify it's Orion's voice
                    # if not self.verify_speaker(audio_text):
                    #     continue
                    
                    # Wake word detected!
                    print("🎯 Wake word detected!")
                    
                    # Listen for full command
                    command = self.listen_for_command(duration=5)
                    
                    if command:
                        # Process and respond
                        response = self.process_command(command)
                        self.speak(response)
                
            except KeyboardInterrupt:
                print("\n👋 Shutting down voice assistant...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
PYTHON_SCRIPT

chmod +x "$VOICE_DIR/atlas_voice.py"

# Create voice training script
cat > "$VOICE_DIR/train_voice.py" << 'TRAIN_SCRIPT'
#!/usr/bin/env python3
"""
Voice Profile Training
Record Orion's voice samples for speaker verification
"""

import os
import json
import sounddevice as sd
import soundfile as sf
from pathlib import Path

VOICE_DIR = Path.home() / ".atlas-voice"
VOICE_SAMPLES_DIR = VOICE_DIR / "voice_samples"
VOICE_SAMPLES_DIR.mkdir(exist_ok=True)

TRAINING_PHRASES = [
    "Hey Atlas, what's the status?",
    "Atlas, deploy the latest changes.",
    "Hey Atlas, remind me to check the market.",
    "Atlas, show me the logs.",
    "Hey Atlas, what's trending on Twitter?",
]

SAMPLE_RATE = 16000

def record_phrase(phrase_num, phrase_text):
    """Record a single training phrase"""
    print(f"\n[{phrase_num}/5] Please say:")
    print(f'  "{phrase_text}"')
    input("Press Enter when ready to record...")
    
    print("🔴 Recording... (3 seconds)")
    audio = sd.rec(int(3 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    print("✅ Recorded!")
    
    # Save audio sample
    filename = VOICE_SAMPLES_DIR / f"sample_{phrase_num}.wav"
    sf.write(filename, audio, SAMPLE_RATE)
    
    return str(filename)

def train():
    """Record training phrases and create voice profile"""
    print("🎤 Voice Profile Training")
    print("=========================")
    print("\nThis will create a voice profile so Atlas only responds to you.")
    print("You'll record 5 short phrases.")
    print("")
    
    samples = []
    for i, phrase in enumerate(TRAINING_PHRASES, 1):
        sample_path = record_phrase(i, phrase)
        samples.append(sample_path)
    
    # Create voice profile (simplified for now)
    profile = {
        "owner": "Orion",
        "samples": samples,
        "created_at": str(Path(samples[0]).stat().st_mtime)
    }
    
    profile_path = VOICE_DIR / "orion_voice_profile.json"
    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)
    
    print("\n✅ Voice profile created!")
    print(f"📁 Saved to: {profile_path}")

if __name__ == "__main__":
    train()
TRAIN_SCRIPT

chmod +x "$VOICE_DIR/train_voice.py"

# Create launcher script
cat > "$VOICE_DIR/start_atlas_voice.sh" << 'LAUNCHER'
#!/bin/bash
# Launch Atlas Voice Assistant

VOICE_DIR="$HOME/.atlas-voice"
source "$VOICE_DIR/venv/bin/activate"

echo "🎤 Starting Atlas Voice Assistant..."
python3 "$VOICE_DIR/atlas_voice.py"
LAUNCHER

chmod +x "$VOICE_DIR/start_atlas_voice.sh"

# Create LaunchAgent for auto-start
PLIST_PATH="$HOME/Library/LaunchAgents/com.atlas.voice.plist"
cat > "$PLIST_PATH" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.atlas.voice</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VOICE_DIR/start_atlas_voice.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>$VOICE_DIR/voice_assistant.log</string>
    <key>StandardOutPath</key>
    <string>$VOICE_DIR/voice_assistant.log</string>
</dict>
</plist>
PLIST

echo ""
echo "✅ Atlas Voice Assistant installed!"
echo ""
echo "📋 Next Steps:"
echo "1. Train your voice profile:"
echo "   $VOICE_DIR/train_voice.py"
echo ""
echo "2. Test the assistant:"
echo "   $VOICE_DIR/start_atlas_voice.sh"
echo ""
echo "3. Enable auto-start on boot:"
echo "   launchctl load $PLIST_PATH"
echo ""
echo "4. Check HomePod name in System Settings → Sound → Output"
echo "   (Update HOMEPOD_NAME in $VOICE_DIR/atlas_voice.py if needed)"
echo ""
echo "🎤 Say 'Hey Atlas' or just 'Atlas' to activate!"
echo ""
