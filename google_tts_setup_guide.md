# Google Text-to-Speech Setup Guide

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
