# 🔑 API Keys Setup Guide

## Where to Get API Keys

### 1. OpenAI API Key (Required for cloud ASR + LLM)
**What it's for**: Speech recognition (Whisper) and language model (GPT)
**Where to get it**: https://platform.openai.com/api-keys
**Steps**:
1. Create an OpenAI account
2. Go to API Keys section
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
**Cost**: Pay-per-use (Whisper ~$0.006/minute, GPT-4o-mini ~$0.15/1M tokens)

### 2. ElevenLabs API Key (Required for high-quality TTS)
**What it's for**: Text-to-speech with natural voices
**Where to get it**: https://elevenlabs.io/
**Steps**:
1. Create an ElevenLabs account
2. Go to Profile → API Keys
3. Copy your API key
**Cost**: Free tier: 10,000 characters/month, then pay-per-use

### 3. Google API Key (Optional - alternative ASR)
**What it's for**: Alternative speech recognition
**Where to get it**: https://console.cloud.google.com/
**Steps**:
1. Create Google Cloud project
2. Enable Speech-to-Text API
3. Create credentials → API Key
**Cost**: Free tier: 60 minutes/month, then pay-per-use

## Where to Add API Keys

### Method 1: Environment File (Recommended)
Create a `.env` file in the OM1 project root:

```bash
# Copy the example file
cp env.example .env

# Edit with your actual keys
nano .env
```

Your `.env` file should look like:
```bash
# OpenAI API key for LLM and ASR (Whisper) services
OPENAI_API_KEY=sk-your-actual-openai-key-here

# ElevenLabs API key for TTS services  
ELEVENLABS_API_KEY=your-actual-elevenlabs-key-here

# Optional: Google API key for ASR services
GOOGLE_API_KEY=your-google-api-key-here

# Optional: Ollama base URL (defaults to http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434

# Robot configuration (can use defaults for testing)
ROBOT_IP=127.0.0.1
URID=test_robot_001
```

### Method 2: System Environment Variables
```bash
export OPENAI_API_KEY="sk-your-actual-openai-key-here"
export ELEVENLABS_API_KEY="your-actual-elevenlabs-key-here"
```

### Method 3: Configuration File (Not Recommended for Security)
You can add keys directly to config files, but this is less secure:
```json5
{
  "cortex_llm": {
    "type": "OpenAILLM",
    "config": {
      "api_key": "sk-your-actual-openai-key-here",
      "model": "gpt-4o-mini"
    }
  }
}
```

## 🚀 Testing with UV

UV is a fast Python package manager. Here's how to use it with OM1:

### Install UV
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Setup OM1 with UV

```bash
# Navigate to OM1 directory
cd /workspace/project/OM1

# Create virtual environment with uv
uv venv

# Activate the environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies with uv (much faster than pip)
uv pip install -e .

# Install additional dependencies for local processing
uv pip install faster-whisper piper-tts
```

### Quick Test Commands

```bash
# Test 1: Verify setup without running full system
python test_local_setup.py

# Test 2: Test startup capability
python test_startup.py

# Test 3: Run with cloud services (requires API keys)
python src/run.py start local_agent

# Test 4: Run fully offline (requires Ollama setup)
python src/run.py start local_offline_agent
```

## 🧪 Testing Scenarios

### Scenario 1: Cloud Services Test (Easiest)
**Requirements**: OpenAI + ElevenLabs API keys
```bash
# 1. Set up .env file with API keys
cp env.example .env
# Edit .env with your OpenAI and ElevenLabs keys

# 2. Install with uv
uv pip install -e .

# 3. Test
python src/run.py start local_agent
```

### Scenario 2: Hybrid Test (OpenAI + Local TTS)
**Requirements**: Only OpenAI API key
```bash
# 1. Set up .env with only OpenAI key
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "ROBOT_IP=127.0.0.1" >> .env
echo "URID=test_robot" >> .env

# 2. Install with local TTS support
uv pip install -e .
uv pip install piper-tts

# 3. Use config that falls back to Piper for TTS
python src/run.py start local_agent
```

### Scenario 3: Fully Offline Test (No API Keys)
**Requirements**: Local Ollama installation
```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull a model
ollama pull llama3

# 3. Start Ollama server
ollama serve &

# 4. Install offline dependencies
uv pip install -e .
uv pip install faster-whisper piper-tts

# 5. Set minimal .env
echo "ROBOT_IP=127.0.0.1" > .env
echo "URID=test_robot" >> .env

# 6. Run offline
python src/run.py start local_offline_agent
```

## 💰 Cost Estimates

### Free Tier Options
- **ElevenLabs**: 10,000 characters/month free
- **OpenAI**: $5 free credit for new accounts
- **Google Speech**: 60 minutes/month free
- **Ollama**: Completely free (local processing)
- **Faster-Whisper**: Completely free (local processing)
- **Piper TTS**: Completely free (local processing)

### Typical Usage Costs (Cloud Services)
- **1 hour of conversation**:
  - Whisper ASR: ~$0.36
  - GPT-4o-mini: ~$0.50-2.00 (depending on conversation complexity)
  - ElevenLabs TTS: ~$0.20-0.50
  - **Total**: ~$1-3 per hour

### Cost-Saving Tips
1. **Use local models**: Ollama + Faster-Whisper + Piper = $0 ongoing costs
2. **Hybrid approach**: Use OpenAI for LLM, local for ASR/TTS
3. **Smaller models**: Use `gpt-4o-mini` instead of `gpt-4`
4. **Batch processing**: Process multiple requests together

## 🔧 Troubleshooting

### Common Issues

1. **"API key not found"**
   ```bash
   # Check if .env file exists and has correct format
   cat .env
   
   # Verify environment variables are loaded
   python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
   ```

2. **"Invalid API key"**
   - Double-check the key format (OpenAI keys start with `sk-`)
   - Ensure no extra spaces or quotes
   - Verify the key is active in your provider dashboard

3. **"PortAudio not found"**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install portaudio19-dev
   
   # macOS
   brew install portaudio
   
   # Then reinstall audio packages
   uv pip install sounddevice soundfile
   ```

4. **"Ollama connection failed"**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama if not running
   ollama serve
   ```

## 🎯 Recommended Testing Order

1. **Start Simple**: Test with OpenAI API key only
2. **Add TTS**: Add ElevenLabs key for better speech
3. **Try Offline**: Set up Ollama for local processing
4. **Full Offline**: Add Faster-Whisper and Piper

This progressive approach helps you identify issues step by step!