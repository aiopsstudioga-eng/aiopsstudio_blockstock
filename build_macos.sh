#!/bin/bash
# Build script for macOS

# Ensure we are in the project root (where the script is)
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

echo "🏗️  Building AIOps Inventory for macOS..."
echo "Project Root: $PROJECT_ROOT"

# Activate virtual environment
source venv/bin/activate

# clean previous builds
rm -rf build dist

# Run PyInstaller
pyinstaller --noconfirm --clean packaging/macos/AIOpsInventory.spec

echo "✅ Build Complete!"
echo "App location: $PROJECT_ROOT/dist/AIOpsInventory.app"
