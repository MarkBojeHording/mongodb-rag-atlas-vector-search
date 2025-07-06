#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip

# Install basic dependencies first
echo "Installing basic dependencies..."
pip install -r requirements.txt

# Install PyTorch CPU version
echo "Installing PyTorch CPU version..."
pip install torch==2.7.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Install minimal ML packages one by one
echo "Installing ML packages..."
pip install --no-deps sentence-transformers
pip install --no-deps transformers
pip install --no-deps langchain
pip install --no-deps langchain-community
pip install --no-deps huggingface-hub

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p /tmp/cache

# Set environment variables for better performance
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export TRANSFORMERS_CACHE="/tmp/cache"
export HF_HOME="/tmp/cache"

echo "Build completed successfully!"
