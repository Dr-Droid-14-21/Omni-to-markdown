# Omni to Markdown

Omni to Markdown is a Windows 11-first, local desktop app that converts supported document types into Markdown and stitches multiple Markdown files into one ordered output.

## Current scope

- Converter support for `.doc`, `.docx`, `.htm`, `.html`, `.pdf`, `.odt`, `.odf`, `.rtf`, `.txt`.
- Multi-engine routing with fallback:
  - `pandoc`, `mammoth`, `libreoffice` for office formats.
  - local HTML conversion with `pandoc` fallback for `.htm` and `.html`.
  - `pymupdf` primary + `pdfminer` fallback for PDFs.
- Run report generation (`json` + `markdown`) after each conversion batch.
- Batch keyword search across queued `.doc`, `.docx`, `.htm`, `.html`, `.pdf`, `.odt`, `.odf`, `.rtf`, `.txt`, and Markdown files.
- Deterministic Markdown stitcher with exact separator format.
- Stitch tray save/load support for reusable stitch queues.
- Neon-styled Windows GUI with action icons, drag/drop queues, accessibility names, tooltips, startup splash, and UI sounds.
- Markdown image path rewrite helpers for conversion cleanup.
- Threaded GUI execution with cancel/retry for converter and cancel for stitcher.
- Windows Explorer launch-path support plus optional right-click context-menu install scripts.
- Unit + integration test baseline with skip-aware dependency tests and PDF fixture coverage.

## Supported routes

| Source type | Preferred | Fallbacks |
|---|---|---|
| `.docx` | `pandoc` | `mammoth`, `libreoffice` |
| `.odt` | `pandoc` | `libreoffice` |
| `.doc` | `libreoffice` | none |
| `.odf` | `libreoffice` | none |
| `.htm`, `.html` | `html` | `pandoc` |
| `.pdf` | `pymupdf` | `pdfminer` |
| `.rtf` | `libreoffice` | none |
| `.txt` | `text` | none |

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

For release builds, install your Authenticode certificate in `Cert:\CurrentUser\My`, then sign by thumbprint:

```powershell
$env:OMNI_CODE_SIGN_CERT_THUMBPRINT = "YOUR_CERT_THUMBPRINT"
.\scripts\build_windows.ps1 -Sign
```

Validate the packaged app without opening the GUI:

```powershell
.\scripts\validate_windows_build.ps1
```

For stricter release gating where unsigned builds must fail validation:

```powershell
.\scripts\validate_windows_build.ps1 -RequireSignature
```

## Windows Explorer Integration

The app can accept file and folder paths on launch, which enables `Open with` and Explorer context-menu workflows.

You can manage this either from the new converter quick-actions panel inside the app or by running the helper scripts directly.

Register the user-level right-click menu for supported document types and folders:

```powershell
.\scripts\register_windows_context_menu.ps1
```

Remove the context-menu entries:

```powershell
.\scripts\unregister_windows_context_menu.ps1
```

Check current Explorer integration state without changing anything:

```powershell
.\scripts\check_windows_context_menu.ps1
```

Notes:

- The installer writes to `HKCU:\Software\Classes`, not machine-wide registry hives.
- It also creates a user-level `Send to -> Omni to Markdown` shortcut for multi-select handoff.
- By default it uses `dist\OmniToMarkdown\OmniToMarkdown.exe` when available.
- If no packaged app exists yet, it falls back to `.venv\Scripts\python.exe` plus `scripts\launch_omni.py`.
- Unsigned local builds may be blocked by Windows Smart App Control. Public distribution should use Authenticode code signing.

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
