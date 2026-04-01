#!/usr/bin/env bash
set -e  # exit on any error

# Check if pdm is installed
if ! command -v pdm &> /dev/null
then
    echo "PDM not found. Installing via pip..."
    pip install --user pdm
else
    echo "PDM is already installed."
fi

# Add local pip bin to PATH in case --user installs PDM there
export PATH="$HOME/.local/bin:$PATH"

# Install project dependencies
pdm install
