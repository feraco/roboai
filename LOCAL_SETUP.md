# OM1 Local Setup Guide

This guide explains how to run OM1 completely independent of OpenMind's API using local alternatives and user-provided API keys.

## Overview

The refactored OM1 system supports:
- **ASR (Speech Recognition)**: OpenAI Whisper API or Faster-Whisper (local)
- **LLM (Language Model)**: OpenAI GPT or Ollama (local)
- **TTS (Text-to-Speech)**: ElevenLabs API or Piper TTS (local)

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure your API keys:

```bash
cp env.example .env
```

Edit `.env` with your API keys:

```bash
# OpenAI API key for LLM and ASR (Whisper) services
OPENAI_API_KEY=your_openai_api_key_here

# ElevenLabs API key for TTS services
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional: Google API key for ASR services
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Ollama base URL (defaults to http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434
```

### 2. Install Dependencies

```bash
pip install -e .
```

### 3. Choose Your Configuration

#### Option A: Cloud Services (Recommended for best quality)
Uses OpenAI Whisper, OpenAI GPT, and ElevenLabs TTS:

```bash
python src/run.py --config config/local_agent.json5
```

#### Option B: Fully Offline (No internet required after setup)
Uses Faster-Whisper, Ollama, and Piper TTS:

```bash
python src/run.py --config config/local_offline_agent.json5
```

## Detailed Setup

### ASR (Speech Recognition) Options

#### OpenAI Whisper API
- **Pros**: High accuracy, fast, cloud-based
- **Cons**: Requires internet and API key
- **Setup**: Set `OPENAI_API_KEY` in `.env`
- **Config**: `"engine": "openai-whisper"`

#### Faster-Whisper (Local)
- **Pros**: Offline, no API costs, privacy
- **Cons**: Slower, requires local compute
- **Setup**: `pip install faster-whisper`
- **Config**: `"engine": "faster-whisper"`

### LLM (Language Model) Options

#### OpenAI GPT
- **Pros**: High quality responses, fast
- **Cons**: Requires internet and API costs
- **Setup**: Set `OPENAI_API_KEY` in `.env`
- **Config**:
```json5
"cortex_llm": {
  "type": "OpenAILLM",
  "config": {
    "model": "gpt-4o-mini",
    "temperature": 0.7
  }
}
```

#### Ollama (Local)
- **Pros**: Offline, no API costs, privacy
- **Cons**: Requires local setup and compute
- **Setup**:
  1. Install Ollama: https://ollama.ai/
  2. Pull a model: `ollama pull llama3`
  3. Start Ollama: `ollama serve`
- **Config**:
```json5
"cortex_llm": {
  "type": "OllamaLLM",
  "config": {
    "base_url": "http://localhost:11434",
    "model": "llama3"
  }
}
```

### TTS (Text-to-Speech) Options

#### ElevenLabs API
- **Pros**: High quality, natural voices
- **Cons**: Requires internet and API costs
- **Setup**: Set `ELEVENLABS_API_KEY` in `.env`
- **Config**: System automatically uses ElevenLabs if API key is available

#### Piper TTS (Local)
- **Pros**: Offline, no API costs
- **Cons**: Lower quality than ElevenLabs
- **Setup**: `pip install piper-tts`
- **Config**: System automatically falls back to Piper if no ElevenLabs API key

## Configuration Files

### local_agent.json5
Uses cloud services for best quality:
- OpenAI Whisper for ASR
- OpenAI GPT for LLM
- ElevenLabs for TTS (with Piper fallback)

### local_offline_agent.json5
Fully offline configuration:
- Faster-Whisper for ASR
- Ollama for LLM
- Piper for TTS

## Customization

### Creating Your Own Configuration

1. Copy one of the example configs
2. Modify the components you want to change:

```json5
{
  "name": "MyAgent",
  "agent_inputs": [
    {
      "type": "LocalASRInput",
      "config": {
        "engine": "openai-whisper",  // or "faster-whisper"
        "sample_rate": 16000
      }
    }
  ],
  "cortex_llm": {
    "type": "OpenAILLM",  // or "OllamaLLM"
    "config": {
      "model": "gpt-4o-mini",
      "temperature": 0.7
    }
  },
  "agent_actions": [
    {
      "name": "speak",
      "connector": "local_elevenlabs_tts",
      "config": {
        "voice_id": "your_preferred_voice_id"
      }
    }
  ]
}
```

### Voice Configuration

For ElevenLabs, you can customize the voice by setting:
- `voice_id`: ElevenLabs voice ID
- `stability`: Voice stability (0.0-1.0)
- `similarity_boost`: Voice similarity boost (0.0-1.0)

For Piper, you can set:
- `piper_model`: Model name (e.g., "en_US-lessac-medium")

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Make sure `OPENAI_API_KEY` is set in your `.env` file
   - Check that the `.env` file is in the project root

2. **"Ollama connection failed"**
   - Make sure Ollama is running: `ollama serve`
   - Check that the model is installed: `ollama list`
   - Verify the base URL in your config

3. **"Piper TTS not found"**
   - Install Piper: `pip install piper-tts`
   - Or install system package: `apt install piper-tts` (Ubuntu)

4. **"faster-whisper not found"**
   - Install faster-whisper: `pip install faster-whisper`

### Performance Tips

1. **For better ASR accuracy**: Use OpenAI Whisper API
2. **For faster local ASR**: Use smaller Faster-Whisper models ("tiny", "base")
3. **For better LLM responses**: Use OpenAI GPT-4
4. **For faster local LLM**: Use smaller Ollama models (llama3:8b vs llama3:70b)

## Migration from OpenMind API

If you're migrating from the original OpenMind-dependent version:

1. Update your configuration files to remove `"api_key": "openmind_free"`
2. Set up your `.env` file with the new API keys
3. Update any custom plugins to use the new local connectors
4. Test your configuration with the new local setup

## Support

For issues with the local setup:
1. Check the logs for specific error messages
2. Verify all dependencies are installed
3. Test each component individually (ASR, LLM, TTS)
4. Check the example configurations for reference