#!/usr/bin/env bash

# Run script for nmgui application
# This script activates the virtual environment and runs the application with the correct PYTHONPATH

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}"
SRC_DIR="${PROJECT_ROOT}/src"

# Activate virtual environment
if [[ -f "${PROJECT_ROOT}/venv/bin/activate" ]]; then
    source "${PROJECT_ROOT}/venv/bin/activate"
else
    echo "Virtual environment not found. Please run:"
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Run the application with correct PYTHONPATH
PYTHONPATH="${SRC_DIR}" python -m nmgui