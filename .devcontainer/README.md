# GitHub Codespaces Guide for PrismBench

## Quick Start in Codespaces

1. **Open in Codespaces**: Click the green "Code" button → "Codespaces" → "Create codespace on [branch]"

2. **Wait for setup**: The devcontainer will automatically install dependencies and prepare your environment

3. **Configure API Keys**:
   ```bash
   # Edit the apis.key file with your actual API keys
   code apis.key
   ```

4. **Start Services**:
   ```bash
   .devcontainer/start-services.sh
   ```

5. **Access the GUI**: Port 3000 will automatically open in your browser when ready

## Port Forwarding

GitHub Codespaces automatically forwards these ports:

| Port | Service | Description | Auto-open |
|------|---------|-------------|-----------|
| 3000 | GUI | Main web interface | ✅ Yes |
| 8000 | LLM Interface | AI service API | ❌ Silent |
| 8001 | Environment | Challenge environment | ❌ Silent |
| 8002 | Search | MCTS search service | ❌ Silent |
| 6379 | Redis | Database | ❌ Silent |

## Accessing Services

### In Codespaces Browser
- The GUI will automatically open at the forwarded 3000 port
- All internal service communication works automatically

### From External Browser
- Go to the "Ports" tab in VS Code
- Click the globe icon next to port 3000 to open the GUI
- Use the forwarded URLs for API access if needed

## Development Workflow

1. **Make code changes** - Services auto-reload with hot reloading enabled
2. **View logs**:
   ```bash
   docker-compose -f .devcontainer/docker-compose.tutorial.yml logs -f [service-name]
   ```
3. **Check service status**:
   ```bash
   docker-compose -f .devcontainer/docker-compose.tutorial.yml ps
   ```
4. **Stop services**:
   ```bash
   docker-compose -f .devcontainer/docker-compose.tutorial.yml down
   ```

## Troubleshooting

### Services not starting?
- Check if `apis.key` is configured properly
- Verify Docker is running: `docker ps`
- Check logs for specific service errors

### Can't access GUI?
- Wait for all services to be healthy (check with `docker-compose ps`)
- Check the "Ports" tab in VS Code - port 3000 should show as forwarded
- Try refreshing the browser tab

### Port forwarding issues?
- Ports are automatically configured in `devcontainer.json`
- GitHub Codespaces may take a moment to forward ports on first startup
- Check the "Ports" tab for status

## Environment Variables

The services are configured with these key environment variables for Codespaces:

- `UVICORN_RELOAD=true` - Enables hot reloading for Python services
- `WATCHPACK_POLLING=true` - Enables file watching for Next.js in containers
- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8002/` - Points GUI to search service

## Security Notes

- API keys are mounted read-only into containers
- Services communicate internally via Docker network
- Only necessary ports are exposed via Codespaces port forwarding 