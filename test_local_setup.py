#!/usr/bin/env python3
"""
Test script to verify OM1 can run without OpenMind dependencies.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all local components can be imported."""
    print("Testing imports...")
    
    try:
        # Test local ASR input
        from inputs.plugins.local_asr import LocalASRInput
        print("✓ LocalASRInput imported successfully")
    except (ImportError, OSError) as e:
        if "PortAudio" in str(e):
            print("⚠ LocalASRInput requires PortAudio (audio system dependency) - skipping")
        else:
            print(f"✗ Failed to import LocalASRInput: {e}")
            return False
    
    try:
        # Test OpenAI LLM (updated)
        from llm.plugins.openai_llm import OpenAILLM
        print("✓ OpenAILLM imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import OpenAILLM: {e}")
        return False
    
    try:
        # Test Ollama LLM
        from llm.plugins.ollama_llm import OllamaLLM
        print("✓ OllamaLLM imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import OllamaLLM: {e}")
        return False
    
    try:
        # Test local TTS connector
        from actions.speak.connector.local_elevenlabs_tts import LocalElevenLabsTTSConnector
        print("✓ LocalElevenLabsTTSConnector imported successfully")
    except (ImportError, OSError) as e:
        if "PortAudio" in str(e):
            print("⚠ LocalElevenLabsTTSConnector requires PortAudio (audio system dependency) - skipping")
        else:
            print(f"✗ Failed to import LocalElevenLabsTTSConnector: {e}")
            return False
    
    return True

def test_config_loading():
    """Test that configuration files can be loaded."""
    print("\nTesting configuration loading...")
    
    try:
        import json5
        
        # Test local agent config
        config_path = Path(__file__).parent / "config" / "local_agent.json5"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json5.load(f)
            print("✓ local_agent.json5 loaded successfully")
            
            # Check that it doesn't use openmind_free
            if config.get("api_key") != "openmind_free":
                print("✓ Configuration doesn't use openmind_free API key")
            else:
                print("✗ Configuration still uses openmind_free API key")
                return False
        else:
            print("✗ local_agent.json5 not found")
            return False
        
        # Test offline agent config
        offline_config_path = Path(__file__).parent / "config" / "local_offline_agent.json5"
        if offline_config_path.exists():
            with open(offline_config_path, 'r') as f:
                offline_config = json5.load(f)
            print("✓ local_offline_agent.json5 loaded successfully")
        else:
            print("✗ local_offline_agent.json5 not found")
            return False
            
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False
    
    return True

def test_environment_setup():
    """Test environment variable setup."""
    print("\nTesting environment setup...")
    
    env_example_path = Path(__file__).parent / "env.example"
    if env_example_path.exists():
        print("✓ env.example file exists")
        
        # Check that it contains the new environment variables
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        required_vars = [
            "OPENAI_API_KEY",
            "ELEVENLABS_API_KEY",
            "GOOGLE_API_KEY",
            "OLLAMA_BASE_URL"
        ]
        
        for var in required_vars:
            if var in content:
                print(f"✓ {var} found in env.example")
            else:
                print(f"✗ {var} not found in env.example")
                return False
    else:
        print("✗ env.example file not found")
        return False
    
    return True

def test_component_initialization():
    """Test that components can be initialized without OpenMind dependencies."""
    print("\nTesting component initialization...")
    
    # Set dummy environment variables for testing
    os.environ["OPENAI_API_KEY"] = "test_key"
    os.environ["ELEVENLABS_API_KEY"] = "test_key"
    
    try:
        # Test LocalASRInput initialization
        from inputs.plugins.local_asr import LocalASRInput
        from inputs.base import SensorConfig
        
        config = SensorConfig()
        config.engine = "faster-whisper"  # Use offline engine for testing
        
        # This should not fail even without actual API keys for offline mode
        asr = LocalASRInput(config)
        print("✓ LocalASRInput initialized successfully")
        
    except (ImportError, OSError) as e:
        if "PortAudio" in str(e):
            print("⚠ LocalASRInput requires PortAudio (audio system dependency) - skipping")
        else:
            print(f"✗ Failed to initialize LocalASRInput: {e}")
            return False
    
    try:
        # Test LocalElevenLabsTTSConnector initialization
        from actions.speak.connector.local_elevenlabs_tts import LocalElevenLabsTTSConnector
        
        tts = LocalElevenLabsTTSConnector({})
        print("✓ LocalElevenLabsTTSConnector initialized successfully")
        
    except (ImportError, OSError) as e:
        if "PortAudio" in str(e):
            print("⚠ LocalElevenLabsTTSConnector requires PortAudio (audio system dependency) - skipping")
        else:
            print(f"✗ Failed to initialize LocalElevenLabsTTSConnector: {e}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("OM1 Local Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_loading,
        test_environment_setup,
        test_component_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! OM1 is ready to run without OpenMind dependencies.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())