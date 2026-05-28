#!/usr/bin/env bash
set -euo pipefail

python -m pip install -e .[dev]
python -m pip install pyinstaller
pyinstaller --name OmniToMarkdown app/main.py
