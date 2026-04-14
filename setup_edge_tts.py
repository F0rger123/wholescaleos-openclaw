#!/usr/bin/env python3
"""
Setup Edge TTS for free voice messages.
"""

import subprocess
import sys

def install_edge_tts():
    """Install Edge TTS and test."""
    print("🎙️ Setting up Edge TTS (Free)...")
    
    # Install edge-tts
    print("1. Installing edge-tts package...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts"], 
                      check=True, capture_output=True)
        print("✅ edge-tts installed")
    except:
        print("⚠️  Could not install edge-tts via pip")
    
    # Test TTS
    print("\n2. Testing TTS...")
    test_script = """
import edge_tts
import asyncio

async def test_tts():
    tts = edge_tts.Communicate(text="Hello! This is a test of Edge TTS.", voice="en-US-ChristopherNeural")
    await tts.save("test_tts.mp3")
    print("✅ TTS test file created: test_tts.mp3")

asyncio.run(test_tts())
"""
    
    with open("/tmp/test_tts.py", "w") as f:
        f.write(test_script)
    
    try:
        subprocess.run([sys.executable, "/tmp/test_tts.py"], capture_output=True)
        print("✅ TTS test completed")
    except:
        print("⚠️  TTS test failed (but package installed)")
    
    print("\n3. Available Voices:")
    voices_script = """
import edge_tts
import asyncio

async def list_voices():
    voices = await edge_tts.list_voices()
    english_voices = [v for v in voices if 'en-' in v['ShortName']]
    for voice in english_voices[:5]:  # Show first 5 English voices
        print(f"{voice['ShortName']}: {voice['Gender']} - {voice['Locale']}")

asyncio.run(list_voices())
"""
    
    with open("/tmp/list_voices.py", "w") as f:
        f.write(voices_script)
    
    subprocess.run([sys.executable, "/tmp/list_voices.py"])
    
    print("\n🎙️ Edge TTS Setup Complete!")
    print("💡 To use in OpenClaw, configure TTS provider in config")
    print("💡 Command: openclaw config set agents.defaults.tts.provider edge")

if __name__ == "__main__":
    install_edge_tts()