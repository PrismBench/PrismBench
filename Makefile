.PHONY: help setup setup-system setup-keys start stop status logs clean install-deps check-keys dev-install
.SILENT:

help: ## Show this help message
	echo "PrismBench Development Commands"
	echo "==============================="
	awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup Commands
setup: setup-system setup-dependencies-dev setup-dependencies-container setup-pre-commit setup-keys check-keys
	echo "✅ Setup complete!"
	echo "Run 'make help' to see all available commands"

setup-system: ## Set up system-level configuration (git, docker group, uv)
	echo "🚀 Setting up PrismBench development environment..."
	if [ ! -d ".git/hooks" ]; then \
		mkdir -p .git/hooks; \
		echo "✅ Created git hooks directory"; \
	fi
	if command -v sudo >/dev/null 2>&1; then \
		echo "🐳 Adding user to docker group..."; \
		sudo groupadd -for -g $$(stat -c '%g' /var/run/docker.sock) docker 2>/dev/null || true; \
		sudo usermod -aG docker $$(whoami) 2>/dev/null || true; \
		echo "✅ Added user to docker group"; \
	fi
	uv pip install pre-commit --system
	pre-commit install

setup-dependencies-dev: ## Install dependencies for the development environment
	echo "📦 Installing development dependencies..."
	uv pip install -e ".[dev]" --system
	echo "✅ Installed development dependencies"

setup-dependencies-container: ## Install all dependencies
	echo "📦 Installing container dependencies..."
	sudo uv pip install -r src/services/llm_interface/pyproject.toml --system
	sudo uv pip install -r src/services/environment/pyproject.toml --system
	sudo uv pip install -r src/services/search/pyproject.toml --system
	if [ -f "src/services/gui/package.json" ]; then \
		echo "Installing GUI dependencies..."; \
		cd src/services/gui && npm install; \
	fi
	echo "✅ Installed development dependencies"

setup-pre-commit: ## Install and configure pre-commit hooks
	echo "🪝 Setting up pre-commit hooks..."
	pre-commit install --hook-type pre-commit --hook-type commit-msg
	echo "✅ Pre-commit hooks installed"

setup-keys: ## Create APIs key file from template if it doesn't exist
	if [ ! -f apis.key ]; then \
		echo "📋 Creating apis.key from template..."; \
		cp apis.key.template apis.key; \
		echo "✅ Created apis.key from template"; \
	else \
		echo "✅ apis.key already exists"; \
	fi

check-keys: ## Check if API keys are configured
	if [ ! -f apis.key ]; then \
		echo "❌ Error: apis.key file not found!"; \
		echo "Please make sure apis.key exists and contains your API keys."; \
		exit 1; \
	fi
	if grep -q "your-.*-key-here" apis.key; then \
		echo "⚠️  Warning: It looks like you haven't configured your API keys yet."; \
		echo "Please edit apis.key and replace the placeholder values with real API keys."; \
		echo ""; \
	fi

verify-setup: ## Verify that the development environment is set up correctly
	echo "🔍 Verifying development environment setup..."
	echo "Checking commitizen..."
	cz version || echo "❌ commitizen not found"
	echo "Checking ruff..."
	ruff --version || echo "❌ ruff not found"
	echo "Checking pre-commit..."
	pre-commit --version || echo "❌ pre-commit not found"
	echo "Checking mypy..."
	mypy --version || echo "❌ mypy not found"
	echo "Running pre-commit on all files..."
	pre-commit run --all-files || echo "⚠️  Some pre-commit checks failed"
	echo "✅ Verification complete!"

##@ Service Management
start: check-keys ## Start all services
	echo "🚀 Starting PrismBench services..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench up -d
	echo "✅ Services are starting up!"
	echo ""
	echo "🌐 Access points:"
	echo "   - GUI: http://localhost:3000"
	echo "   - Search API: http://localhost:8002"
	echo "   - LLM Interface: http://localhost:8000"
	echo "   - Environment Service: http://localhost:8001"
dev-start: stop rebuild start ## Start all services with build

stop: ## Stop all services
	echo "🛑 Stopping services..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench down
	echo "✅ Services stopped"

restart: stop rebuild start ## Restart all services

##@ Logs and status
status: ## Show service status
	docker compose -f docker/docker-compose.yaml --project-name prismbench ps
logs: ## Show logs for all services
	docker compose -f docker/docker-compose.yaml --project-name prismbench logs -f
logs-service: ## Show logs for specific service (usage: make logs-service SERVICE=gui)
	docker compose -f docker/docker-compose.yaml --project-name prismbench logs -f $(SERVICE)

##@ Build
build: ## Build all services
	echo "🔨 Building services..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench build
build-base: ## Build only the base image
	echo "🔨 Building base image..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench build base

##@ Rebuild
rebuild: ## Rebuild all services from scratch
	echo "🔨 Rebuilding services from scratch..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench build --no-cache

rebuild-base: ## Rebuild base image from scratch
	echo "🔨 Rebuilding base image from scratch..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench build --no-cache base
rebuild-search: ## Rebuild search service from scratch
	echo "🔨 Rebuilding search service from scratch..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench build --no-cache search
rebuild-llm-interface: ## Rebuild LLM interface service from scratch
	echo "🔨 Rebuilding LLM interface service from scratch..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench build --no-cache llm-interface
rebuild-node-env: ## Rebuild environment service from scratch
	echo "🔨 Rebuilding environment service from scratch..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench build --no-cache node-env
rebuild-gui: ## Rebuild GUI service from scratch
	echo "🔨 Rebuilding GUI service from scratch..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench build --no-cache gui

##@ Cleanup
clean: ## Clean up containers, networks, and volumes
	echo "🧹 Cleaning up..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench down -v --remove-orphans
	docker system prune -f
clean-all: ## Clean up everything including images
	echo "🧹 Deep cleaning..."
	docker compose -f docker/docker-compose.yaml --project-name prismbench down -v --remove-orphans --rmi all
	docker system prune -af

##@ Utilities
shell-gui: ## Open shell in GUI container
	docker compose -f docker/docker-compose.yaml --project-name prismbench exec gui /bin/sh
shell-llm-interface: ## Open shell in LLM interface container
	docker compose -f docker/docker-compose.yaml --project-name prismbench exec llm-interface /bin/bash
shell-node-env: ## Open shell in environment container
	docker compose -f docker/docker-compose.yaml --project-name prismbench exec node-env /bin/bash
shell-search: ## Open shell in search container
	docker compose -f docker/docker-compose.yaml --project-name prismbench exec search /bin/bash
