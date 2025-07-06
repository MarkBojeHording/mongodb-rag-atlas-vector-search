#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip

# Install PyTorch CPU version first
echo "Installing PyTorch CPU version..."
pip install torch==2.7.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Install all other dependencies
echo "Installing all dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p /tmp/cache

# Set environment variables for better performance
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export TRANSFORMERS_CACHE="/tmp/cache"
export HF_HOME="/tmp/cache"

echo "Build completed successfully!"
