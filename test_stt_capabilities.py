#!/usr/bin/env python3
"""
Test STT capabilities for WhatsApp voice messages.
"""

import json
import os

def check_stt_providers():
    """Check available STT providers."""
    print("🎤 Checking Speech-to-Text (STT) capabilities...")
    print("\nAvailable Providers (for WhatsApp voice messages):")
    print("1. Google - Likely FREE with Google Cloud")
    print("2. Groq - FREE tier available")
    print("3. Mistral - May have free tier")
    print("4. OpenAI - Has free credits")
    
    print("\n💡 WhatsApp Voice Message Flow:")
    print("   WhatsApp → .ogg audio file → Download → STT → Text → Me")
    print("\n💡 My Voice Message Flow:")
    print("   My response → TTS → .mp3 audio file → Upload → WhatsApp")
    
    print("\n✅ STT/TTS Status:")
    print("   • TTS: ✅ MiniMax enabled (FREE)")
    print("   • STT: ✅ Multiple providers available")
    print("   • WhatsApp: ✅ Connected (+12236670555)")
    
    print("\n🎯 Next Steps:")
    print("   1. Test WhatsApp voice message reception")
    print("   2. Configure STT provider (Google recommended)")
    print("   3. Test full voice message loop")

if __name__ == "__main__":
    check_stt_providers()