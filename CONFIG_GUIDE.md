# RoboAI Configuration Guide

This guide explains the various agent configurations available in the RoboAI system. Each configuration is designed for different use cases, from fully cloud-based setups to completely offline local deployments.

## Quick Start

1. **Set up your API keys** in the `.env` file (see `.env.example`)
2. **Choose a configuration** from the list below
3. **Run the agent**: `uv run src/run.py <config_name>`

## Configuration Categories

### 🌐 Cloud-Only Configurations
These configurations use cloud services for all AI processing, providing the highest quality but requiring internet connectivity and API keys.

### 🏠 Local-Only Configurations  
These configurations run completely offline using local models, providing privacy and independence but requiring more local resources.

### 🔄 Hybrid Configurations
These configurations mix cloud and local services, balancing quality, privacy, and resource usage.

### 🛠️ Development Configurations
These configurations are designed for testing and development without requiring external services.

---

## Available Configurations

### 1. `cloud_openai_elevenlabs` - Premium Cloud Setup
**Type:** Cloud-Only  
**Best for:** Highest quality interactions, production use

- **LLM:** OpenAI GPT-4 (cloud)
- **ASR:** OpenAI Whisper (cloud) 
- **TTS:** ElevenLabs (cloud)
- **Quality:** ⭐⭐⭐⭐⭐
- **Privacy:** ⭐⭐
- **Cost:** $$$

**Required API Keys:**
- `OPENAI_API_KEY`
- `ELEVENLABS_API_KEY`

**Usage:**
```bash
uv run src/run.py cloud_openai_elevenlabs
```

---

### 2. `cloud_gemini_google` - Google Ecosystem
**Type:** Cloud-Only  
**Best for:** Google services integration

- **LLM:** Google Gemini Pro (cloud)
- **ASR:** Google Speech-to-Text (cloud)
- **TTS:** Google Text-to-Speech (cloud)
- **Quality:** ⭐⭐⭐⭐
- **Privacy:** ⭐⭐
- **Cost:** $$

**Required API Keys:**
- `GOOGLE_CLOUD_API_KEY`

**Usage:**
```bash
uv run src/run.py cloud_gemini_google
```

---

### 3. `cloud_openrouter_azure` - Multi-Provider Cloud
**Type:** Cloud-Only  
**Best for:** Model flexibility, enterprise use

- **LLM:** OpenRouter (Claude/GPT) (cloud)
- **ASR:** OpenAI Whisper (cloud)
- **TTS:** Azure Speech Services (cloud)
- **Quality:** ⭐⭐⭐⭐⭐
- **Privacy:** ⭐⭐
- **Cost:** $$$

**Required API Keys:**
- `OPENROUTER_API_KEY`
- `OPENAI_API_KEY`
- `AZURE_SPEECH_KEY`

**Usage:**
```bash
uv run src/run.py cloud_openrouter_azure
```

---

### 4. `local_ollama_piper` - Complete Privacy
**Type:** Local-Only  
**Best for:** Privacy-focused use, offline environments

- **LLM:** Ollama (local)
- **ASR:** Faster-Whisper (local)
- **TTS:** Piper TTS (local)
- **Quality:** ⭐⭐⭐
- **Privacy:** ⭐⭐⭐⭐⭐
- **Cost:** Free

**Prerequisites:**
- Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
- Pull model: `ollama pull llama3.1:8b`
- Install Piper TTS voices
- Install Faster-Whisper: `pip install faster-whisper`

**Usage:**
```bash
uv run src/run.py local_ollama_piper
```

---

### 5. `local_ollama_festival` - Alternative Local Setup
**Type:** Local-Only  
**Best for:** Alternative offline setup, open-source preference

- **LLM:** Ollama with Mistral (local)
- **ASR:** Vosk (local)
- **TTS:** Festival TTS (local)
- **Quality:** ⭐⭐⭐
- **Privacy:** ⭐⭐⭐⭐⭐
- **Cost:** Free

**Prerequisites:**
- Install Ollama and pull Mistral: `ollama pull mistral:7b`
- Install Vosk models
- Install Festival TTS

**Usage:**
```bash
uv run src/run.py local_ollama_festival
```

---

### 6. `hybrid_cloud_llm_local_audio` - Smart Privacy
**Type:** Hybrid  
**Best for:** High-quality reasoning with audio privacy

- **LLM:** OpenAI GPT-4 (cloud)
- **ASR:** Faster-Whisper (local)
- **TTS:** Piper TTS (local)
- **Quality:** ⭐⭐⭐⭐
- **Privacy:** ⭐⭐⭐⭐
- **Cost:** $$

**Required API Keys:**
- `OPENAI_API_KEY`

**Prerequisites:**
- Install Faster-Whisper and Piper TTS locally

**Usage:**
```bash
uv run src/run.py hybrid_cloud_llm_local_audio
```

---

### 7. `hybrid_local_llm_cloud_audio` - Quality Audio
**Type:** Hybrid  
**Best for:** Private reasoning with professional audio

- **LLM:** Ollama (local)
- **ASR:** OpenAI Whisper (cloud)
- **TTS:** ElevenLabs (cloud)
- **Quality:** ⭐⭐⭐⭐
- **Privacy:** ⭐⭐⭐
- **Cost:** $$

**Required API Keys:**
- `OPENAI_API_KEY`
- `ELEVENLABS_API_KEY`

**Prerequisites:**
- Install Ollama and pull model

**Usage:**
```bash
uv run src/run.py hybrid_local_llm_cloud_audio
```

---

### 8. `hybrid_mixed_cloud` - Best of Each Provider
**Type:** Hybrid  
**Best for:** Optimal quality from specialized providers

- **LLM:** OpenAI GPT-4 (cloud)
- **ASR:** Google Speech-to-Text (cloud)
- **TTS:** ElevenLabs (cloud)
- **Quality:** ⭐⭐⭐⭐⭐
- **Privacy:** ⭐⭐
- **Cost:** $$$

**Required API Keys:**
- `OPENAI_API_KEY`
- `GOOGLE_CLOUD_API_KEY`
- `ELEVENLABS_API_KEY`

**Usage:**
```bash
uv run src/run.py hybrid_mixed_cloud
```

---

### 9. `dev_mock_services` - Development Testing
**Type:** Development  
**Best for:** Testing, development, CI/CD

- **LLM:** Mock responses (local)
- **ASR:** Mock input (local)
- **TTS:** Mock output (local)
- **Quality:** ⭐
- **Privacy:** ⭐⭐⭐⭐⭐
- **Cost:** Free

**No prerequisites required**

**Usage:**
```bash
uv run src/run.py dev_mock_services
```

---

### 10. `gpu_optimized_local` - High-Performance Local
**Type:** Local-Only  
**Best for:** GPU-accelerated local processing

- **LLM:** Ollama with large model (local, GPU)
- **ASR:** Faster-Whisper large (local, GPU)
- **TTS:** High-quality Piper (local)
- **Quality:** ⭐⭐⭐⭐
- **Privacy:** ⭐⭐⭐⭐⭐
- **Cost:** Free

**Prerequisites:**
- NVIDIA GPU with CUDA
- Install Ollama with GPU support
- Pull large model: `ollama pull llama3.1:70b`
- GPU-enabled Faster-Whisper

**Usage:**
```bash
uv run src/run.py gpu_optimized_local
```

---

## Environment Setup

### API Keys (.env file)
Create a `.env` file in the project root with your API keys:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Google Cloud
GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key_here

# Azure
AZURE_SPEECH_KEY=your_azure_speech_key_here

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Robot IP (for hardware integration)
ROBOT_IP=192.168.1.100
```

### Local Model Setup

#### Ollama Installation
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models
ollama pull llama3.1:8b      # Standard model
ollama pull llama3.1:70b     # Large model (requires GPU)
ollama pull mistral:7b       # Alternative model
```

#### Piper TTS Setup
```bash
# Install Piper TTS
pip install piper-tts

# Download voice models (example)
mkdir -p /usr/local/share/piper/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

#### Faster-Whisper Setup
```bash
# Install Faster-Whisper
pip install faster-whisper

# Models are downloaded automatically on first use
```

## Troubleshooting

### Common Issues

1. **Audio device errors**: Normal in headless environments, doesn't affect functionality
2. **API key errors**: Check your `.env` file and API key validity
3. **Model not found**: Ensure Ollama models are pulled correctly
4. **GPU not detected**: Check CUDA installation and GPU compatibility

### Performance Tips

1. **For cloud configs**: Use faster internet connection for better response times
2. **For local configs**: Allocate sufficient RAM (8GB+ recommended)
3. **For GPU configs**: Ensure adequate VRAM (8GB+ for large models)
4. **For hybrid configs**: Balance based on your priorities (privacy vs quality)

## Customization

You can create your own configurations by:

1. Copying an existing config file
2. Modifying the components (LLM, ASR, TTS)
3. Adjusting parameters for your needs
4. Testing with `uv run src/run.py your_config_name`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs for specific error messages
3. Ensure all prerequisites are installed
4. Verify API keys are correctly set

---

*Last updated: October 2024*