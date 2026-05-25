#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Detect if we are running in WSL
if grep -qEi "(Microsoft|WSL)" /proc/version 2>/dev/null; then
    VENV_NAME="venv-wsl"
else
    VENV_NAME="venv"
fi

echo "Creating virtual environment ($VENV_NAME)..."
python3 -m venv "$VENV_NAME"

echo "Installing dependencies in editable mode..."
"./$VENV_NAME/bin/pip" install -e .[dev]

echo "Setup complete! You can now run the tool using ./run.sh."
