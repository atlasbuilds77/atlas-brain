#!/bin/bash
# Install dependencies for aesthetic perception system

echo "Installing aesthetic perception system dependencies..."

# Install Python packages
pip3 install --quiet torch torchvision pillow transformers 2>&1

echo "✅ Dependencies installed"
echo ""
echo "Installed packages:"
echo "- torch (PyTorch)"
echo "- torchvision (vision utilities)"  
echo "- pillow (image loading)"
echo "- transformers (CLIP model)"
