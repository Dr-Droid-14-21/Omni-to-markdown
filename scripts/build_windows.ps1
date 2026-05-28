$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

python -m pip install -e .[dev]
python -m pip install mammoth markdownify pymupdf pdfminer.six
python -m PyInstaller --clean --noconfirm packaging/windows/OmniToMarkdown.spec
