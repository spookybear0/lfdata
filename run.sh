#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$DIR/src"

# List of potential virtual environment python interpreters
VENV_PATHS=(
    "$DIR/venv-wsl/bin/python"
    "$DIR/.venv/bin/python"
    "$DIR/venv/bin/python"
    "$DIR/venv/Scripts/python"
)

PYTHON_EXE=""
for path in "${VENV_PATHS[@]}"; do
    if [ -f "$path" ]; then
        PYTHON_EXE="$path"
        break
    fi
done

if [ -n "$PYTHON_EXE" ]; then
    "$PYTHON_EXE" -m lfdata "$@"
else
    # Fallback to system python
    if command -v python3 &>/dev/null; then
        python3 -m lfdata "$@"
    else
        python -m lfdata "$@"
    fi
fi
