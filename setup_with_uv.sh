#!/bin/bash
# OM1 Setup Script with UV

set -e  # Exit on any error

echo "🚀 OM1 Local Setup with UV"
echo "=========================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "✅ UV is available"

# Create virtual environment
echo "🐍 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install core dependencies
echo "📚 Installing core dependencies..."
uv pip install -e .

# Ask user what they want to install
echo ""
echo "🎯 Choose your setup:"
echo "1) Cloud services only (requires API keys)"
echo "2) Hybrid (cloud + local fallbacks)"
echo "3) Fully offline (requires Ollama setup)"
echo "4) Development (all dependencies)"

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "☁️ Setting up for cloud services..."
        ;;
    2)
        echo "🔄 Setting up hybrid mode..."
        uv pip install piper-tts
        ;;
    3)
        echo "🏠 Setting up fully offline mode..."
        uv pip install faster-whisper piper-tts
        echo ""
        echo "⚠️  You need to install and setup Ollama separately:"
        echo "   curl -fsSL https://ollama.ai/install.sh | sh"
        echo "   ollama pull llama3"
        echo "   ollama serve"
        ;;
    4)
        echo "🛠️ Installing all dependencies..."
        uv pip install faster-whisper piper-tts
        ;;
    *)
        echo "Invalid choice, installing core only"
        ;;
esac

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your API keys:"
    echo "   nano .env"
    echo ""
    echo "Required API keys:"
    echo "- OpenAI: https://platform.openai.com/api-keys"
    echo "- ElevenLabs: https://elevenlabs.io/ (Profile → API Keys)"
fi

# Run tests
echo ""
echo "🧪 Running setup tests..."
python test_local_setup.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys: nano .env"
echo "2. Test the system: python test_startup.py"
echo "3. Run OM1: python src/run.py start local_agent"
echo ""
echo "For offline mode: python src/run.py start local_offline_agent"