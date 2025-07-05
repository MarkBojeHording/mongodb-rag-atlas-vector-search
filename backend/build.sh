#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p /tmp/cache

# Set environment variables for better performance
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export TRANSFORMERS_CACHE="/tmp/cache"
export HF_HOME="/tmp/cache"

echo "Build completed successfully!"
