#!/bin/bash

# Publish script for gh-safeapprove

set -e

echo "🚀 Publishing gh-safeapprove to PyPI"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in the project root directory"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v

# Check code quality
echo "🔍 Checking code quality..."
black --check src/ tests/
ruff check src/ tests/
mypy src/

# Build package
echo "📦 Building package..."
python -m build

# Check the built package
echo "🔍 Checking built package..."
twine check dist/*

echo "✅ Package built successfully!"
echo ""
echo "To upload to TestPyPI (for testing):"
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "To upload to PyPI:"
echo "  twine upload dist/*"
echo ""
echo "To create a GitHub release:"
echo "  gh release create v0.1.0 --generate-notes" 