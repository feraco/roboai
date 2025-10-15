# Quick Configuration Reference

## 🚀 Quick Start Commands

```bash
# Premium cloud experience
uv run src/run.py cloud_openai_elevenlabs

# Complete privacy (offline)
uv run src/run.py local_ollama_piper

# Best balance (cloud brain, local audio)
uv run src/run.py hybrid_cloud_llm_local_audio

# Development/testing
uv run src/run.py dev_mock_services
```

## 📊 Configuration Comparison

| Config Name | Type | Quality | Privacy | Cost | Internet Required |
|-------------|------|---------|---------|------|-------------------|
| `cloud_openai_elevenlabs` | Cloud | ⭐⭐⭐⭐⭐ | ⭐⭐ | $$$ | Yes |
| `cloud_gemini_google` | Cloud | ⭐⭐⭐⭐ | ⭐⭐ | $$ | Yes |
| `cloud_openrouter_azure` | Cloud | ⭐⭐⭐⭐⭐ | ⭐⭐ | $$$ | Yes |
| `local_ollama_piper` | Local | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free | No |
| `local_ollama_festival` | Local | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free | No |
| `hybrid_cloud_llm_local_audio` | Hybrid | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$ | Yes |
| `hybrid_local_llm_cloud_audio` | Hybrid | ⭐⭐⭐⭐ | ⭐⭐⭐ | $$ | Yes |
| `hybrid_mixed_cloud` | Hybrid | ⭐⭐⭐⭐⭐ | ⭐⭐ | $$$ | Yes |
| `dev_mock_services` | Dev | ⭐ | ⭐⭐⭐⭐⭐ | Free | No |
| `gpu_optimized_local` | Local | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free | No |

## 🔑 Required API Keys by Config

### Cloud Configs
- **OpenAI + ElevenLabs**: `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`
- **Google Ecosystem**: `GOOGLE_CLOUD_API_KEY`
- **Multi-Provider**: `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `AZURE_SPEECH_KEY`

### Hybrid Configs
- **Cloud LLM + Local Audio**: `OPENAI_API_KEY`
- **Local LLM + Cloud Audio**: `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`
- **Mixed Cloud**: `OPENAI_API_KEY`, `GOOGLE_CLOUD_API_KEY`, `ELEVENLABS_API_KEY`

### Local/Dev Configs
- **All Local Configs**: No API keys required
- **Dev/Mock Configs**: No API keys required

## 🛠️ Prerequisites by Type

### Cloud-Only
- Internet connection
- Valid API keys
- No local model installation needed

### Local-Only
- Ollama installed (`curl -fsSL https://ollama.ai/install.sh | sh`)
- Models pulled (`ollama pull llama3.1:8b`)
- Local TTS/ASR tools installed
- Sufficient RAM (8GB+ recommended)

### Hybrid
- Combination of above based on components
- Internet for cloud components
- Local setup for offline components

### GPU-Optimized
- NVIDIA GPU with CUDA
- 8GB+ VRAM recommended
- GPU-enabled model installations

## 🎯 Use Case Recommendations

| Use Case | Recommended Config | Why |
|----------|-------------------|-----|
| **Production/Business** | `cloud_openai_elevenlabs` | Highest quality, reliable |
| **Privacy-Critical** | `local_ollama_piper` | Complete offline operation |
| **Development** | `dev_mock_services` | No setup, no costs |
| **Balanced Privacy** | `hybrid_cloud_llm_local_audio` | Smart reasoning, private audio |
| **High Performance** | `gpu_optimized_local` | Fast local processing |
| **Cost-Conscious** | `local_ollama_piper` | No ongoing API costs |
| **Multi-Language** | `cloud_gemini_google` | Google's language support |
| **Enterprise** | `cloud_openrouter_azure` | Model flexibility, enterprise TTS |

## 🔧 Quick Setup

### 1. Environment File
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. For Local Configs
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.1:8b
```

### 3. Run Agent
```bash
uv run src/run.py <config_name>
```

## 🚨 Troubleshooting Quick Fixes

| Error | Quick Fix |
|-------|-----------|
| "No such config" | Check config name spelling |
| "API key invalid" | Verify API key in `.env` file |
| "Model not found" | Run `ollama pull <model_name>` |
| "Audio device error" | Normal in headless environments |
| "Connection timeout" | Check internet connection |
| "Out of memory" | Use smaller model or add RAM |

---

*For detailed information, see CONFIG_GUIDE.md*