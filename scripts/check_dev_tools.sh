#!/usr/bin/env bash
# check_dev_tools.sh - Verify development tools are installed

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║  canvodpy Development Tools Check                  ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Check uv
echo "Checking uv..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo "  ✅ uv installed: $UV_VERSION"
else
    echo "  ❌ uv NOT installed"
    echo "     Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "     Or: brew install uv"
    EXIT_CODE=1
fi

echo ""

# Check just
echo "Checking just..."
if command -v just &> /dev/null; then
    JUST_VERSION=$(just --version)
    echo "  ✅ just installed: $JUST_VERSION"
else
    echo "  ❌ just NOT installed"
    echo "     Install: curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash"
    echo "     Or: brew install just"
    EXIT_CODE=1
fi

echo ""

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✅ Python installed: $PYTHON_VERSION"
else
    echo "  ⚠️  python3 not found in PATH"
fi

echo ""

# Summary
if [ -z ${EXIT_CODE+x} ]; then
    echo "╔════════════════════════════════════════════════════╗"
    echo "║  ✅ All development tools are installed!          ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
    echo "Next steps:"
    echo "  1. uv sync              # Install Python dependencies"
    echo "  2. just hooks           # Install pre-commit hooks"
    echo "  3. just test            # Run tests"
    echo "  4. just --list          # See all available commands"
    exit 0
else
    echo "╔════════════════════════════════════════════════════╗"
    echo "║  ❌ Missing tools - please install them            ║"
    echo "╚════════════════════════════════════════════════════╝"
    exit 1
fi
