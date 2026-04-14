#!/usr/bin/env python3
"""
Setup Google Text-to-Speech (Free Tier)
"""

import os
import json

def create_setup_guide():
    """Create setup guide for Google TTS."""
    
    guide = """# Google Text-to-Speech Setup Guide

## Step 1: Create Google Cloud Project
1. Go to: https://console.cloud.google.com/
2. Click "Create Project"
3. Name: "OpenClaw-TTS" (or similar)
4. Click "Create"

## Step 2: Enable Text-to-Speech API
1. Go to: https://console.cloud.google.com/apis/library/texttospeech.googleapis.com
2. Click "Enable"

## Step 3: Create Service Account & Credentials
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "Service Account"
3. Name: "openclaw-tts"
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

## Step 4: Create Key
1. Find your service account in the list
2. Click the email address
3. Go to "Keys" tab
4. Click "Add Key" → "Create New Key"
5. Choose "JSON"
6. Click "Create"
7. **SAVE THE DOWNLOADED JSON FILE** as `google-tts-credentials.json`

## Step 5: Install Required Library
```bash
pip install google-cloud-texttospeech
```

## Step 6: Set Environment Variable
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google-tts-credentials.json"
```

## Step 7: Test TTS
```python
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()
synthesis_input = texttospeech.SynthesisInput(text="Hello, this is a test.")

voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-J",
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

with open("output.mp3", "wb") as out:
    out.write(response.audio_content)
```

## Free Tier Limits:
- **1 million characters per month FREE**
- That's about 10+ hours of speech per month!
- After free tier: $4 per 1 million characters

## For OpenClaw Integration:
Save credentials to: `~/.openclaw/google-tts-credentials.json`
"""
    
    return guide

def main():
    print("📝 Creating Google TTS setup guide...")
    guide = create_setup_guide()
    
    # Save guide
    with open('google_tts_setup_guide.md', 'w') as f:
        f.write(guide)
    
    print("✅ Saved setup guide to: google_tts_setup_guide.md")
    print("\n📋 Quick summary:")
    print("1. Create Google Cloud project")
    print("2. Enable Text-to-Speech API")
    print("3. Create service account & download JSON key")
    print("4. Install: pip install google-cloud-texttospeech")
    print("5. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    print("\n🎯 Free: 1 million characters/month (10+ hours of speech)")

if __name__ == "__main__":
    main()