#!/usr/bin/env bash

set -euo pipefail

python -m pip install --user pipx
python -m pipx install poetry
echo "HOME=$HOME"
echo "::add-path::$HOME/.local/bin"
ls "$HOME/.local/bin"
