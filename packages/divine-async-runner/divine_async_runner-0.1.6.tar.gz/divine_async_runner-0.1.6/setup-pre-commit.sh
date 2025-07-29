#!/bin/bash

# Setup pre-commit hooks for divine-async-runner

set -e

echo "Setting up pre-commit hooks for divine-async-runner..."

# Check if UV is available
if ! command -v uv &> /dev/null; then
    echo "❌ UV is required but not installed."
    echo "Please install UV first: https://python-uv.org/docs/#installation"
    exit 1
fi

# Install development dependencies
echo "Installing development dependencies..."
uv install --with dev

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
uv run pre-commit install

# Generate secrets baseline if it doesn't exist
if [ ! -f .secrets.baseline ]; then
    echo "Generating secrets baseline..."
    uv run detect-secrets scan --baseline .secrets.baseline
fi

echo "✅ Pre-commit hooks installed successfully!"
echo "Run 'uv run pre-commit run --all-files' to test all hooks."