#!/bin/bash

echo "🚀 Setting up PrismBench development environment..."

# Make sure we're in the workspace
cd /workspace

# Set up git hooks directory if needed
if [ ! -d ".git/hooks" ]; then
    mkdir -p .git/hooks
fi

# Add user to docker group
sudo groupadd -for -g $(stat -c '%g' /var/run/docker.sock) docker
sudo usermod -aG docker $(whoami)

# Create apis.key from template if it doesn't exist
if [ ! -f apis.key ]; then
    echo "📋 Creating apis.key from template..."
    cp apis.key.template apis.key
    echo "✅ Created apis.key from template"
else
    echo "✅ apis.key already exists"
fi

# Install Python dependencies for each service
echo "📦 Installing development dependencies..."
if [ -f "src/services/llm_interface/requirements.txt" ]; then
    echo "Installing LLM interface dependencies..."
    pip install -r src/services/llm_interface/requirements.txt
fi

if [ -f "src/services/environment/requirements.txt" ]; then
    echo "Installing environment service dependencies..."
    pip install -r src/services/environment/requirements.txt
fi

if [ -f "src/services/search/requirements.txt" ]; then
    echo "Installing search service dependencies..."
    pip install -r src/services/search/requirements.txt
fi

# Install Node.js dependencies for GUI (but don't wait for it in post-create)
if [ -f "src/services/gui/package.json" ]; then
    echo "Installing GUI dependencies (this may take a moment)..."
    cd src/services/gui
    npm install
    cd /workspace
fi

echo ""
echo "🔑 SETUP REQUIRED:"
echo "1. Edit the 'apis.key' file with your API keys"
echo "2. Get free API keys from:"
echo "   - OpenAI: https://platform.openai.com/api-keys"
echo "   - Anthropic: https://console.anthropic.com/"
echo ""
echo "📦 TO START THE APPLICATION:"
echo "Once you've configured your API keys, run:"
echo "  .devcontainer/start-services.sh"
echo ""
echo "🛠️ GITHUB CODESPACES TIPS:"
echo "- All ports are pre-configured to forward automatically"
echo "- Port 3000 (GUI) will auto-open in your browser when ready"
echo "- Services will auto-reload when you make code changes"
echo "- Check the 'Ports' tab in VS Code to see all forwarded ports"
echo ""

# Function to start tutorial services (can be called separately)
start_services() {
    echo "🚀 Starting PrismBench Tutorial Services..."

    # Check if apis.key exists and has content
    if [ ! -f "apis.key" ]; then
        echo "❌ Error: apis.key file not found!"
        echo "Please make sure apis.key exists and contains your API keys."
        exit 1
    fi

    # Check if APIs key file has been modified from template
    if grep -q "your-.*-key-here" apis.key; then
        echo "⚠️  Warning: It looks like you haven't configured your API keys yet."
        echo "Please edit apis.key and replace the placeholder values with real API keys."
        echo ""
        echo "Continuing anyway (some services may not work without valid keys)..."
        echo ""
    fi

    echo "📦 Starting services with development configuration..."
    docker-compose -f docker-compose.yml -f .devcontainer/docker-compose.tutorial.yml up
}

# If script is called with "start" argument, start services
if [ "$1" = "start" ]; then
    start_services
fi 