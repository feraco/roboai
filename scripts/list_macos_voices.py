#!/usr/bin/env python3
"""
Utility script to list available macOS voices for AVSpeechSynthesizer.
"""

import platform
import sys
from src.actions.speak.connector.avspeech_tts import AVSpeechTTSConnector


def main():
    """List available macOS voices."""
    if platform.system() != 'Darwin':
        print("❌ This script only works on macOS")
        sys.exit(1)
    
    print("🎤 Available macOS Voices for AVSpeechSynthesizer:")
    print("=" * 60)
    
    voices = AVSpeechTTSConnector.list_available_voices()
    
    if not voices:
        print("❌ No voices found or Swift compilation failed")
        print("\nTroubleshooting:")
        print("1. Make sure Xcode Command Line Tools are installed: xcode-select --install")
        print("2. Test Swift: echo 'print(\"Hello\")' | swift -")
        sys.exit(1)
    
    # Parse and display voices
    english_voices = []
    other_voices = []
    
    for voice in voices:
        if voice.strip():
            if '(en-' in voice or '(en_' in voice:
                english_voices.append(voice)
            else:
                other_voices.append(voice)
    
    print("🇺🇸 English Voices:")
    print("-" * 30)
    for voice in sorted(english_voices):
        print(f"  {voice}")
    
    if other_voices:
        print(f"\n🌍 Other Languages ({len(other_voices)} voices):")
        print("-" * 30)
        for voice in sorted(other_voices[:10]):  # Show first 10
            print(f"  {voice}")
        if len(other_voices) > 10:
            print(f"  ... and {len(other_voices) - 10} more")
    
    print(f"\n📊 Total: {len(voices)} voices available")
    
    # Show recommended voices
    print("\n⭐ Recommended English Voices:")
    print("-" * 30)
    recommended = [
        "com.apple.ttsbundle.Samantha-compact",
        "com.apple.ttsbundle.Alex-compact", 
        "com.apple.ttsbundle.Daniel-compact",
        "com.apple.ttsbundle.Karen-compact",
        "com.apple.ttsbundle.Moira-compact",
        "com.apple.ttsbundle.Tessa-compact"
    ]
    
    for rec in recommended:
        found = any(rec in voice for voice in english_voices)
        status = "✅" if found else "❌"
        print(f"  {status} {rec}")
    
    print("\n💡 To use a voice, update your configuration:")
    print('   "voice_identifier": "com.apple.ttsbundle.Samantha-compact"')


if __name__ == "__main__":
    main()