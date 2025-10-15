#!/usr/bin/env python3
"""
Test script to verify API keys are working correctly.
"""

import os
import sys
import asyncio
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables only")

def test_openai_key():
    """Test OpenAI API key."""
    print("🔑 Testing OpenAI API key...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ OPENAI_API_KEY format invalid (should start with 'sk-')")
        return False
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        
        if "successful" in response.choices[0].message.content.lower():
            print("✅ OpenAI API key is working!")
            return True
        else:
            print("⚠️  OpenAI API responded but with unexpected content")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_elevenlabs_key():
    """Test ElevenLabs API key."""
    print("\n🔑 Testing ElevenLabs API key...")
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in environment")
        return False
    
    try:
        import requests
        
        # Test by getting available voices
        headers = {"xi-api-key": api_key}
        response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
        
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ ElevenLabs API key is working! Found {len(voices.get('voices', []))} voices")
            return True
        elif response.status_code == 401:
            print("❌ ElevenLabs API key is invalid")
            return False
        else:
            print(f"⚠️  ElevenLabs API responded with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ElevenLabs API test failed: {e}")
        return False

def test_google_key():
    """Test Google API key (optional)."""
    print("\n🔑 Testing Google API key (optional)...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not found (this is optional)")
        return True  # Not required, so return True
    
    try:
        import requests
        
        # Test by making a simple request to Speech-to-Text API
        url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"
        
        # Simple test payload
        data = {
            "config": {
                "encoding": "LINEAR16",
                "sampleRateHertz": 16000,
                "languageCode": "en-US"
            },
            "audio": {
                "content": ""  # Empty content for test
            }
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 400:  # Expected for empty audio
            print("✅ Google API key is working!")
            return True
        elif response.status_code == 403:
            print("❌ Google API key is invalid or Speech-to-Text API not enabled")
            return False
        else:
            print(f"⚠️  Google API responded with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Google API test failed: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection (for offline mode)."""
    print("\n🔑 Testing Ollama connection (for offline mode)...")
    
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        import requests
        
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            model_names = [model['name'] for model in models.get('models', [])]
            print(f"✅ Ollama is running! Available models: {', '.join(model_names)}")
            return True
        else:
            print(f"⚠️  Ollama responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Ollama is not running (this is optional for cloud mode)")
        return True  # Not required for cloud mode
    except Exception as e:
        print(f"❌ Ollama connection test failed: {e}")
        return False

def main():
    """Run all API key tests."""
    print("🧪 OM1 API Key Test")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Found .env file")
    else:
        print("⚠️  No .env file found, using system environment variables")
    
    print()
    
    tests = [
        ("OpenAI", test_openai_key),
        ("ElevenLabs", test_elevenlabs_key),
        ("Google", test_google_key),
        ("Ollama", test_ollama_connection)
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_func()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
    
    # Determine what modes are available
    print("\n🎯 Available Modes:")
    
    if results["OpenAI"] and results["ElevenLabs"]:
        print("  ✅ Cloud Mode (local_agent.json5)")
    elif results["OpenAI"]:
        print("  ✅ Hybrid Mode (OpenAI + local TTS)")
    else:
        print("  ❌ Cloud Mode requires OpenAI API key")
    
    if results["Ollama"]:
        print("  ✅ Offline Mode (local_offline_agent.json5)")
    else:
        print("  ⚠️  Offline Mode requires Ollama setup")
    
    print("\n🚀 Next Steps:")
    if results["OpenAI"]:
        print("  python src/run.py start local_agent")
    if results["Ollama"]:
        print("  python src/run.py start local_offline_agent")
    
    if not any(results.values()):
        print("  1. Set up API keys in .env file")
        print("  2. Or install Ollama for offline mode")
        print("  3. Run this test again")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())