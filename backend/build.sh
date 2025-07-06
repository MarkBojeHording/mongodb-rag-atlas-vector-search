#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip

# Install PyTorch CPU version first
echo "Installing PyTorch CPU version..."
pip install torch==2.7.1+cpu torchvision==0.22.1+cpu torchaudio==2.7.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Install ML packages with pre-compiled wheels
echo "Installing ML packages with pre-compiled wheels..."
pip install --only-binary=all sentence-transformers==2.5.1 transformers==4.40.0 langchain==0.2.0 langchain-community==0.2.0 huggingface-hub==0.22.2 einops==0.8.1

# Install other dependencies
echo "Installing other dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p /tmp/cache

# Set environment variables for better performance
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export TRANSFORMERS_CACHE="/tmp/cache"
export HF_HOME="/tmp/cache"

echo "Build completed successfully!"
