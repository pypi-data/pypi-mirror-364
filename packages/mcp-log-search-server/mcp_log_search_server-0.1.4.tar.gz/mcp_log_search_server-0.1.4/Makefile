.PHONY: all check lint format test install clean help release tag-push

# Default target
all: check lint

# Install dependencies
install:
	uv pip install -e ".[dev]"

# Run basic checks
check:
	@echo "Running basic checks..."
	python -c "import src.mcp_shell_server.server; print('✓ Server module imports successfully')"
	python -m py_compile src/mcp_shell_server/*.py
	@echo "✓ Python syntax check passed"

# Run linting (if ruff is available)
lint:
	@echo "Running linting..."
	@if command -v ruff >/dev/null 2>&1; then \
		echo "Running ruff..."; \
		ruff check src/; \
	else \
		echo "Ruff not installed, skipping lint check"; \
	fi

# Format code (if available)
format:
	@if command -v black >/dev/null 2>&1; then \
		echo "Running black..."; \
		black src/; \
	else \
		echo "Black not installed, skipping format"; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		echo "Running isort..."; \
		isort src/; \
	else \
		echo "Isort not installed, skipping import sort"; \
	fi

# Run basic functionality test
test:
	@echo "Running basic functionality test..."
	python test_simplified_log_search.py

# Create and push a git tag for release
tag-push:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required. Usage: make tag-push VERSION=v1.0.0"; \
		exit 1; \
	fi
	@echo "Creating and pushing tag $(VERSION)..."
	@if git tag -l | grep -q "^$(VERSION)$$"; then \
		echo "Tag $(VERSION) already exists!"; \
		exit 1; \
	fi
	git tag -a $(VERSION) -m "Release $(VERSION)"
	git push origin $(VERSION)
	@echo "✓ Tag $(VERSION) created and pushed successfully"
	@echo "GitHub Action will now build and publish the release"

# Complete release process (check, tag, push)
release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required. Usage: make release VERSION=v1.0.0"; \
		exit 1; \
	fi
	@echo "Starting release process for $(VERSION)..."
	@echo "1. Running checks..."
	@make all
	@echo "2. Checking git status..."
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: Working directory is not clean. Please commit all changes first."; \
		git status --short; \
		exit 1; \
	fi
	@echo "3. Creating and pushing tag..."
	@make tag-push VERSION=$(VERSION)
	@echo "✓ Release $(VERSION) completed successfully!"

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Show help
help:
	@echo "Available targets:"
	@echo "  all        - Run check and lint (default)"
	@echo "  install    - Install dependencies"
	@echo "  check      - Run basic module checks"
	@echo "  lint       - Run code linting"
	@echo "  format     - Format code"
	@echo "  test       - Run basic functionality test"
	@echo "  tag-push   - Create and push git tag (requires VERSION=vX.Y.Z)"
	@echo "  release    - Complete release process: check + tag + push (requires VERSION=vX.Y.Z)"
	@echo "  clean      - Clean build artifacts"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Release example:"
	@echo "  make release VERSION=v1.0.0"
