#!/bin/bash

echo "🚀 Starting PrismBench Services in GitHub Codespaces..."

# Change to workspace directory
cd /workspace

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

echo "📦 Starting services..."

# Start all services using the tutorial compose file
docker-compose -f .devcontainer/docker-compose.tutorial.yml up -d

echo ""
echo "✅ Services are starting up! This may take a few minutes on first run."
echo ""
echo "🌐 Once ready, you can access:"
echo "   - GUI: Port 3000 (will auto-open in browser)"
echo "   - Search API: Port 8002"
echo "   - LLM Interface: Port 8000"
echo "   - Environment Service: Port 8001"
echo ""
echo "📊 To check service status:"
echo "   docker-compose -f .devcontainer/docker-compose.tutorial.yml ps"
echo ""
echo "📋 To view logs:"
echo "   docker-compose -f .devcontainer/docker-compose.tutorial.yml logs -f [service-name]"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f .devcontainer/docker-compose.tutorial.yml down" 