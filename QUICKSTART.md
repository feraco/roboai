# 🚀 OM1 Quick Start Guide

Get OM1 running in 5 minutes with UV!

## 📋 Prerequisites

- Python 3.8+
- Microphone and speakers (for voice interaction)
- Internet connection (for cloud services)

## ⚡ Super Quick Setup (Cloud Mode)

```bash
# 1. Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Navigate to OM1 directory
cd OM1

# 3. Run the setup script
./setup_with_uv.sh

# 4. Get your API keys and add them to .env:
#    - OpenAI: https://platform.openai.com/api-keys
#    - ElevenLabs: https://elevenlabs.io/ (Profile → API Keys)

# 5. Edit .env file
nano .env

# 6. Test your API keys
python test_api_keys.py

# 7. Run OM1!
python src/run.py start local_agent
```

## 🔑 API Keys You Need

### Essential (for cloud mode):
1. **OpenAI API Key** - Get from https://platform.openai.com/api-keys
   - Used for: Speech recognition (Whisper) + AI reasoning (GPT)
   - Cost: ~$1-3 per hour of conversation
   - Format: `sk-...`

2. **ElevenLabs API Key** - Get from https://elevenlabs.io/
   - Used for: High-quality text-to-speech
   - Cost: Free tier 10k chars/month, then pay-per-use
   - Format: Regular string

### Optional:
3. **Google API Key** - Alternative speech recognition
4. **Ollama** - For completely offline operation

## 📝 .env File Example

```bash
# Required for cloud mode
OPENAI_API_KEY=sk-your-actual-openai-key-here
ELEVENLABS_API_KEY=your-actual-elevenlabs-key-here

# Optional
GOOGLE_API_KEY=your-google-key-here
OLLAMA_BASE_URL=http://localhost:11434

# Robot settings (can use defaults for testing)
ROBOT_IP=127.0.0.1
URID=my_robot_001
```

## 🧪 Testing Commands

```bash
# Test 1: Verify setup
python test_local_setup.py

# Test 2: Test API keys
python test_api_keys.py

# Test 3: Test startup
python test_startup.py

# Test 4: Run the system
python src/run.py start local_agent
```

## 🎯 Different Modes

### 1. Cloud Mode (Recommended for beginners)
**Requirements**: OpenAI + ElevenLabs API keys
**Command**: `python src/run.py start local_agent`
**Pipeline**: Microphone → OpenAI Whisper → GPT → ElevenLabs → Speaker

### 2. Offline Mode (No API keys needed)
**Requirements**: Ollama installation
**Setup**:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3
ollama serve

# Install offline dependencies
uv pip install faster-whisper piper-tts
```
**Command**: `python src/run.py start local_offline_agent`
**Pipeline**: Microphone → Faster-Whisper → Ollama → Piper → Speaker

### 3. Hybrid Mode
Mix and match services based on your needs and available API keys.

## 🔧 Troubleshooting

### "API key not found"
```bash
# Check your .env file
cat .env

# Verify environment variables
python -c "import os; print('OpenAI:', os.getenv('OPENAI_API_KEY'))"
```

### "PortAudio not found"
```bash
# Ubuntu/Debian
sudo apt-get install portaudio19-dev

# macOS
brew install portaudio

# Reinstall audio packages
uv pip install sounddevice soundfile
```

### "Invalid API key"
- Double-check the key format (OpenAI keys start with `sk-`)
- Ensure no extra spaces or quotes
- Verify the key is active in your provider dashboard

### "Connection refused" (Ollama)
```bash
# Start Ollama server
ollama serve

# Check if it's running
curl http://localhost:11434/api/tags
```

## 💡 Tips

1. **Start with cloud mode** - It's the easiest to set up
2. **Use the test scripts** - They'll help you identify issues quickly
3. **Check the logs** - OM1 provides detailed logging
4. **Try offline mode** - Great for privacy and no ongoing costs

## 🆘 Need Help?

1. Run the test scripts to identify issues
2. Check the logs in the console output
3. Verify your API keys are working with `python test_api_keys.py`
4. Make sure all dependencies are installed

## 🎉 Success!

When everything is working, you should see:
- OM1 starts without errors
- You can speak to the microphone
- The system responds with speech
- Logs show successful API calls

**You're now ready to use OM1 as a local, independent robotics framework!**