# Quick Install Instructions for Mac

## Prerequisites
- macOS with Homebrew installed
- Python 3.10+ available

## 1. Install System Dependencies

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required system packages
brew install portaudio
```

## 2. Install UV Package Manager

```bash
# Install UV (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload your shell or run:
source ~/.zshrc  # or ~/.bashrc
```

## 3. Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/feraco/roboai.git
cd roboai

# Switch to the fixed configuration branch
git checkout feature/multiple-agent-configurations

# Create and activate UV environment
uv venv
source .venv/bin/activate

# Install all dependencies
uv sync
```

## 4. Setup Environment Variables

```bash
# Copy and edit environment file
cp .env.example .env  # if .env.example exists, otherwise .env is already there

# Edit .env file with your preferred editor
nano .env

# Make sure these are set for offline operation:
ROBOT_IP=127.0.0.1
URID=local_offline_agent
OLLAMA_BASE_URL=http://localhost:11434
```

## 5. Install and Setup Ollama (for Offline LLM)

```bash
# Install Ollama
brew install ollama

# Start Ollama service
brew services start ollama

# Or start manually in a separate terminal:
ollama serve

# Pull the required model (in another terminal)
ollama pull llama3.1:8b
```

## 6. Run the Offline Agent

```bash
# Make sure you're in the project directory with UV environment activated
cd roboai
source .venv/bin/activate

# Run the offline agent
uv run src/run.py local_offline_agent
```

## Expected Output

The agent should start successfully and show:
- ✅ Faster-Whisper model loading
- ✅ Piper TTS initialization (may show "not available" - that's OK)
- ✅ LLM initialization with function schemas
- ✅ Agent starting with configuration

You may see these expected warnings/errors:
- Audio device errors (normal in headless environment)
- Piper TTS not available (will use mock TTS)

## Troubleshooting

### If you get import errors:
```bash
# Reinstall dependencies
uv sync --reinstall
```

### If Ollama connection fails:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
brew services restart ollama
```

### If audio errors persist:
```bash
# Install additional audio dependencies
brew install sox
```

## Alternative: Cloud-based Agent

If you prefer using cloud APIs instead of local models:

```bash
# Edit .env and add your API keys:
OPENAI_API_KEY=your_actual_openai_key_here
ELEVENLABS_API_KEY=your_actual_elevenlabs_key_here

# Run cloud-based agent
uv run src/run.py local_agent
```

## Quick Commands Summary

```bash
# One-time setup
brew install portaudio ollama
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/feraco/roboai.git
cd roboai && git checkout feature/multiple-agent-configurations
uv venv && source .venv/bin/activate && uv sync

# Start services
brew services start ollama
ollama pull llama3.1:8b

# Run agent
source .venv/bin/activate
uv run src/run.py local_offline_agent
```

That's it! Your offline AI agent should be running locally on your Mac! 🚀