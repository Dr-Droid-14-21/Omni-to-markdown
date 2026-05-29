# Omni to Markdown

Omni to Markdown is a Windows 11-first, local desktop app that converts supported document types into Markdown and stitches multiple Markdown files into one ordered output.

## Current scope

- Converter support for `.doc`, `.docx`, `.pdf`, `.odt`, `.odf`.
- Multi-engine routing with fallback:
  - `pandoc`, `mammoth`, `libreoffice` for office formats.
  - `pymupdf` primary + `pdfminer` fallback for PDFs.
- Run report generation (`json` + `markdown`) after each conversion batch.
- Batch keyword search across queued `.doc`, `.docx`, `.pdf`, `.odt`, `.odf`, and Markdown files.
- Deterministic Markdown stitcher with exact separator format.
- Stitch tray save/load support for reusable stitch queues.
- Neon-styled Windows GUI with action icons, drag/drop queues, accessibility names, tooltips, startup splash, and UI sounds.
- Markdown image path rewrite helpers for conversion cleanup.
- Threaded GUI execution with cancel/retry for converter and cancel for stitcher.
- Unit + integration test baseline with skip-aware dependency tests and PDF fixture coverage.

## Supported routes

| Source type | Preferred | Fallbacks |
|---|---|---|
| `.docx` | `pandoc` | `mammoth`, `libreoffice` |
| `.odt` | `pandoc` | `libreoffice` |
| `.doc` | `libreoffice` | none |
| `.odf` | `libreoffice` | none |
| `.pdf` | `pymupdf` | `pdfminer` |

## Run locally

```powershell
uv python install 3.12
uv venv .venv --python 3.12
.venv\Scripts\activate
python -m pip install -e .[dev]
python -m pip install pymupdf pdfminer.six
python -m app.main
```

Install optional runtime engines as needed:

```powershell
python -m pip install mammoth markdownify pymupdf pdfminer.six
```

Download the Apache-2.0 Tika CLI jar for keyword search inside Office/OpenDocument/PDF files:

```powershell
.\scripts\download_tika.ps1
```

Tika search also requires Java on `PATH`, or a Java executable path configured in Settings.

If you prefer python.org installs instead of `uv`, install Python 3.12 side-by-side and use:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

External tools on Windows:

- Pandoc: [https://pandoc.org/installing.html](https://pandoc.org/installing.html)
- LibreOffice: [https://www.libreoffice.org/download/download-libreoffice/](https://www.libreoffice.org/download/download-libreoffice/)
- Apache Tika: [https://tika.apache.org/](https://tika.apache.org/)

## Run tests

```powershell
python -m pytest
```

Run lint checks:

```powershell
python -m ruff check .
```

## Build Windows App

```powershell
.\scripts\build_windows.ps1
```

The Windows build uses `packaging/windows/OmniToMarkdown.spec` and writes an onedir build to `dist/OmniToMarkdown/`.

## Architecture

- `app/core`: models, settings, paths, logging setup.
- `app/conversion`: conversion engines, routing, reports, service orchestration.
- `app/stitcher`: separator rules and stitch service.
- `app/ui`: desktop window, converter/stitcher tabs, reusable widgets.
- `app/workers`: threaded worker objects for conversion/stitch actions.
- `tests/unit`: deterministic unit tests.
- `tests/integration`: dependency-aware integration checks.

## Additional docs

- [docs/user-guide.md](docs/user-guide.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [docs/developer-setup.md](docs/developer-setup.md)
- [docs/dependency-installation.md](docs/dependency-installation.md)
- [docs/conversion-quality.md](docs/conversion-quality.md)
- [PLAN.md](PLAN.md)
- [TODO.md](TODO.md)
