# SPECS_TECHSTACK.md

## Purpose

This document defines the recommended technical stack for a local-first desktop GUI application that converts `.doc`, `.docx`, `.pdf`, `.odt`, and `.odf` files to Markdown and stitches multiple Markdown files into one ordered output file.

## Product architecture stance

The product should be built as a modular desktop application, not as a monolithic GUI script. The GUI is only the surface. The core conversion, stitching, reporting, logging, and validation logic must run independently so it can be tested through CLI or service-level tests.

## Recommended stack summary

| Layer | Recommendation | Reason |
|---|---|---|
| Language | Python 3.12 or 3.13 | Best fit for document tooling, subprocess orchestration, PySide6 GUI, and fast development. |
| GUI | PySide6 / Qt for Python | Mature desktop widgets, drag/drop, native menus, accessibility potential, cross-platform path. |
| Packaging | PyInstaller first, pyside6-deploy evaluation second | PyInstaller is widely used; pyside6-deploy is Qt-aligned and should be evaluated. |
| DOCX conversion | Pandoc and Mammoth | Pandoc for broad structure; Mammoth for clean semantic HTML from `.docx`. |
| DOC conversion | LibreOffice headless pre-conversion | Old binary `.doc` needs compatibility conversion before Markdown normalization. |
| ODT conversion | Pandoc primary, LibreOffice fallback | ODT is Pandoc-friendly, LibreOffice is good fallback. |
| ODF conversion | LibreOffice guarded route | `.odf` is ambiguous; support must be explicitly validated. |
| PDF extraction | PyMuPDF + pdfminer.six | PyMuPDF for performance and extraction options; pdfminer.six for text analysis fallback. |
| Markdown normalization | custom service + markdownify/html2text where needed | Allows consistent heading, newline, table, and separator behavior. |
| Settings | platformdirs + JSON/TOML | Simple local config without database overhead. |
| Logging | Python logging or structlog/loguru | Structured logs without document body leakage. |
| Models | pydantic or dataclasses | Strong validation for queue items, reports, and settings. |
| Tests | pytest | Standard Python testing. |
| Lint/type | ruff + mypy/pyright | Fast code quality loop. |
| CI | GitHub Actions matrix | Windows-first, Linux, future macOS. |

## Runtime requirements

### Windows 11

Minimum:

- Windows 11 64-bit.
- 8 GB RAM.
- 500 MB app disk space without bundled LibreOffice/Pandoc.
- 2 GB+ if heavy external tools are bundled.
- Python not required for packaged release.
- Optional installed tools: LibreOffice, Pandoc.

Recommended:

- Windows 11 23H2 or newer.
- 16 GB RAM.
- SSD/NVMe.
- LibreOffice current stable.
- Pandoc current stable.

### Linux

Minimum:

- Modern 64-bit Linux distribution.
- glibc-compatible environment for packaged builds.
- Qt runtime compatibility depending on package format.
- LibreOffice and Pandoc available through system package manager or bundled path.

Recommended:

- Ubuntu LTS, Fedora, Debian stable, Arch, or Linux Mint.
- 8 GB RAM minimum, 16 GB preferred.
- Native package build plus AppImage/Flatpak evaluation.

### macOS

Future target:

- macOS current and one previous major release at the time of Q4 2026/Q1 2027 work.
- Apple Silicon required for test.
- Intel optional but preferred if support commitment exists.
- Apple Developer account for signing and notarization.
- DMG distribution.

## External tools

## Pandoc

Role:

- Convert `.docx`, `.odt`, and intermediate HTML into Markdown.
- Generate Markdown with stable structural rules.
- Preserve headings, lists, tables, links, footnotes, and metadata where supported.

Usage strategy:

- Detect `pandoc` binary at startup and from settings.
- Validate with `pandoc --version`.
- Prefer subprocess invocation over binding until stable.
- Use explicit `--from` and `--to` formats.
- Use `--wrap=none` where appropriate.
- Use temporary working directories.
- Capture stderr and exit codes.

Potential command patterns:

```bash
pandoc input.docx --from=docx --to=gfm --wrap=none --output=output.md
pandoc input.odt --from=odt --to=gfm --wrap=none --output=output.md
pandoc input.html --from=html --to=gfm --wrap=none --output=output.md
```

Risks:

- Complex tables may degrade.
- Exact styling is not preserved.
- Some embedded objects will be skipped.
- Requires installation or bundled binary.

## LibreOffice headless

Role:

- Pre-convert `.doc` and problematic ODT/ODF documents.
- Export to `.docx`, `.html`, `.txt`, or another intermediate.
- Provide legacy Office compatibility.

Usage strategy:

- Detect `soffice` or `libreoffice`.
- Use isolated user profile per run where possible.
- Always set timeout.
- Avoid macro execution.
- Run with a controlled temporary output directory.
- Do not run with shell interpolation.

Potential command patterns:

```bash
soffice --headless --convert-to docx --outdir /tmp/out input.doc
soffice --headless --convert-to html --outdir /tmp/out input.doc
soffice --headless --convert-to txt --outdir /tmp/out input.odf
```

Risks:

- Headless conversion can hang.
- Output filenames are controlled by LibreOffice.
- Filter behavior can vary by LibreOffice version.
- Requires write access to user profile.
- Bundling LibreOffice is heavy.

## Mammoth

Role:

- Convert `.docx` to clean semantic HTML.
- Useful when the goal is readable Markdown over layout fidelity.

Pipeline:

```text
docx -> Mammoth HTML -> Markdown normalizer -> .md
```

Strength:

- Clean semantic structure.
- Good for ordinary Word docs.
- Style-map customization.

Limitations:

- Not for old `.doc`.
- Not designed for exact visual reproduction.
- Complex layout and embedded objects may be ignored or simplified.

## PyMuPDF

Role:

- Extract text and layout information from PDF.
- Potentially generate Markdown-oriented output with custom logic.
- Detect image-heavy/scanned PDFs.

Strength:

- Fast.
- Useful for page-level extraction.
- Can inspect images and blocks.

Limitations:

- PDF logical structure may not exist.
- Tables and reading order need heuristics.
- OCR not included as default V1 feature.

## pdfminer.six

Role:

- Text extraction fallback.
- Useful for deeper text layout analysis.
- Handles many PDF internals.

Strength:

- Pure Python.
- Good text extraction tool.
- Supports encrypted PDFs where permitted and many font cases.

Limitations:

- Slower than PyMuPDF in many scenarios.
- Output may still be layout-scrambled.
- Not a semantic Markdown converter.

## Optional evaluation: Microsoft MarkItDown

Role:

- Optional plugin route for converting multiple formats to Markdown for LLM workflows.
- Useful benchmark against custom pipelines.

Caution:

- Use only as optional route until output quality and security posture are validated.
- Sanitize paths and permissions.
- Do not treat as magic perfect converter.

## Markdown normalization rules

The app must normalize output after any conversion engine.

Rules:

- Use UTF-8 output.
- Normalize line endings to LF.
- Trim excessive trailing whitespace.
- Preserve code blocks.
- Avoid rewriting content inside fenced code blocks.
- Ensure document ends with one newline.
- Convert image paths to relative paths if images are extracted.
- Avoid absolute input file paths in Markdown.
- Use safe filename slugs only when creating derived assets.
- Preserve Markdown headings generated by engine.
- Do not invent headings that are not detectable.

## MD Stitcher technical specification

Input:

- Ordered list of Markdown file paths.
- Output file path.
- Separator configuration locked to required format in V1.
- Optional line-ending normalization.

Separator constants:

```python
SEPARATOR_PREFIX = "==========================="
SEPARATOR_SUFFIX = "================================="
```

Separator function:

```text
separator(previous_file_name) = SEPARATOR_PREFIX + previous_file_name + SEPARATOR_SUFFIX
```

Implementation rules:

- Use basename only, not full path.
- Preserve `.md` extension in separator display.
- If input file is `.markdown`, display original basename including `.markdown` unless user chooses normalize-to-md display.
- Insert separator between files only.
- Default: no separator before first file and no separator after final file.
- Ensure blank line before and after separator.
- Do not mutate source files.
- Write to temporary file first, then atomic rename if possible.

## Python package dependencies

Recommended `pyproject.toml` groups:

### Core

- `PySide6`
- `pydantic`
- `platformdirs`
- `charset-normalizer`
- `python-magic` or platform-specific filetype alternative
- `markdownify`
- `beautifulsoup4`
- `pypandoc`
- `mammoth`
- `pymupdf`
- `pdfminer.six`
- `loguru` or `structlog`

### Development

- `pytest`
- `pytest-qt`
- `ruff`
- `mypy` or `pyright`
- `coverage`
- `pre-commit`

### Packaging

- `pyinstaller`
- optional: `nuitka`
- optional: `briefcase`
- optional: `cx_Freeze`

## Proposed repository structure

```text
doc-to-md-stitcher/
  app/
    __init__.py
    main.py
    ui/
      main_window.py
      converter_tab.py
      stitcher_tab.py
      settings_dialog.py
      widgets/
        file_queue_table.py
        drag_drop_list.py
        warning_panel.py
    core/
      models.py
      settings.py
      paths.py
      logging_config.py
      file_detection.py
      temp_manager.py
    conversion/
      base.py
      router.py
      pandoc_engine.py
      libreoffice_engine.py
      mammoth_engine.py
      pdf_pymupdf_engine.py
      pdf_pdfminer_engine.py
      markdown_normalizer.py
      reports.py
    stitcher/
      stitcher_service.py
      separator.py
      manifest.py
    workers/
      conversion_worker.py
      stitch_worker.py
    resources/
      icons/
      styles/
  tests/
    unit/
    integration/
    fixtures/
  docs/
    SPECS_TECHSTACK.md
    WORKFLOWS_ARCHITECTURE.md
    CODING_PIPELINE_CODING_PROGRESS.md
    Agent.md
    GEMINI.md
    PLAN.md
    TODO.md
    ALL-FILES-CHANGELOG.md
  scripts/
    detect_dependencies.py
    build_windows.ps1
    build_linux.sh
    run_tests.ps1
    run_tests.sh
  pyproject.toml
  README.md
  LICENSE
```

## Conversion engine interface

Each engine should implement:

```python
class ConversionEngine:
    name: str
    supported_extensions: set[str]

    def is_available(self) -> EngineAvailability:
        ...

    def can_convert(self, source: Path, context: ConversionContext) -> bool:
        ...

    def convert(self, source: Path, output: Path, context: ConversionContext) -> ConversionResult:
        ...
```

## Conversion result model

Fields:

- `source_path`
- `output_path`
- `engine_name`
- `status`
- `warnings`
- `errors`
- `duration_ms`
- `intermediate_files`
- `metadata`
- `report_path`

## Security requirements

- Never execute macros.
- Never use `shell=True` for converter calls.
- Sanitize file paths displayed in reports if privacy mode is on.
- Use per-run temp directories.
- Delete temp directories by default.
- Keep debug temp files only if user enables diagnostics.
- Timebox external converters.
- Validate outputs before marking success.
- Treat all input documents as untrusted.

## Version strategy

Application version:

```text
0.1.0 CLI prototype
0.2.0 GUI MVP
0.3.0 Windows alpha
0.4.0 Linux beta
1.0.0 Windows/Linux release candidate
1.1.0 macOS collaboration track
```

## Final recommendation

Use **Python + PySide6 + Pandoc/LibreOffice/Mammoth/PyMuPDF/pdfminer.six**. Avoid Tauri/Electron for V1 unless a web UI is strategically required. The conversion problem is already a hydra; do not give it a second head by adding a complex frontend/backend bridge before the engine layer is stable.
