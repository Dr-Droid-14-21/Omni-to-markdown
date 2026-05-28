# CODING_PIPELINE_CODING_PROGRESS.md

## Purpose

This file tracks the phased engineering build plan for the Document-to-Markdown Converter + MD Stitcher GUI application. Each phase includes objectives, files to create or modify, acceptance criteria, and estimated complexity.

## Complexity scale

| Score | Meaning |
|---:|---|
| 1 | Tiny task |
| 3 | Small implementation |
| 5 | Moderate feature |
| 7 | Hard feature with integration risk |
| 9 | High-risk subsystem |
| 10 | Research-heavy or release-blocking |

## Phase 0: Repository foundation

### Objectives

- Create repository structure.
- Add Python project configuration.
- Add documentation files.
- Add test/lint baseline.
- Add changelog discipline.

### Files to create/modify

- `pyproject.toml`
- `README.md`
- `.gitignore`
- `.editorconfig`
- `docs/SPECS_TECHSTACK.md`
- `docs/WORKFLOWS_ARCHITECTURE.md`
- `docs/CODING_PIPELINE_CODING_PROGRESS.md`
- `docs/Agent.md`
- `docs/GEMINI.md`
- `docs/PLAN.md`
- `docs/TODO.md`
- `docs/ALL-FILES-CHANGELOG.md`
- `app/__init__.py`
- `tests/__init__.py`

### Acceptance criteria

- `python -m pytest` runs successfully with placeholder tests.
- `ruff check .` runs.
- Project imports without GUI launch.
- Documentation files exist.
- Changelog has initial entry.

### Estimated complexity

**3 / 10**

## Phase 1: Core domain models and settings

### Objectives

- Define data models for files, jobs, conversion plans, results, warnings, and errors.
- Implement settings loader/saver.
- Implement platform-aware app directories.
- Implement logging configuration.

### Files to create/modify

- `app/core/models.py`
- `app/core/settings.py`
- `app/core/paths.py`
- `app/core/logging_config.py`
- `tests/unit/test_models.py`
- `tests/unit/test_settings.py`

### Acceptance criteria

- Models validate required fields.
- Settings load defaults if no config exists.
- Settings save to correct platform config path.
- Logs avoid document body content.
- Unit tests pass.

### Estimated complexity

**4 / 10**

## Phase 2: File detection and queue preflight

### Objectives

- Detect supported file types.
- Validate paths, permissions, extensions, and likely MIME/magic.
- Generate preflight warnings.
- Create conversion plans without converting yet.

### Files to create/modify

- `app/core/file_detection.py`
- `app/conversion/router.py`
- `app/conversion/base.py`
- `tests/unit/test_file_detection.py`
- `tests/unit/test_router.py`

### Acceptance criteria

- `.doc`, `.docx`, `.pdf`, `.odt`, `.odf` recognized.
- Unsupported files rejected with useful error.
- Mislabeled files produce warnings.
- Missing external dependencies produce preflight warnings.
- No source file is modified.

### Estimated complexity

**5 / 10**

## Phase 3: MD Stitcher service

### Objectives

- Implement standalone stitching service.
- Preserve file order.
- Insert exact separator format.
- Handle encoding and newline normalization.
- Write atomically.

### Files to create/modify

- `app/stitcher/separator.py`
- `app/stitcher/manifest.py`
- `app/stitcher/stitcher_service.py`
- `tests/unit/test_separator.py`
- `tests/unit/test_stitcher_service.py`
- `tests/fixtures/markdown/`

### Acceptance criteria

- Three-file stitch produces exact expected separator sequence.
- No trailing separator by default.
- Source files remain unchanged.
- Missing file produces structured error.
- Output file cannot overwrite an input file.
- Duplicate basenames warn but do not fail.
- Encoding errors are reported.

### Estimated complexity

**5 / 10**

## Phase 4: Pandoc engine

### Objectives

- Implement Pandoc availability detection.
- Convert `.docx` and `.odt` to `.md`.
- Capture stderr, exit codes, and durations.
- Normalize output.

### Files to create/modify

- `app/conversion/pandoc_engine.py`
- `app/conversion/markdown_normalizer.py`
- `app/conversion/reports.py`
- `tests/integration/test_pandoc_engine.py`

### Acceptance criteria

- Engine returns unavailable if Pandoc missing.
- `.docx` fixture converts to Markdown.
- `.odt` fixture converts to Markdown.
- Engine failure returns structured error.
- Output is UTF-8 and LF-normalized.

### Estimated complexity

**6 / 10**

## Phase 5: Mammoth engine

### Objectives

- Implement `.docx` to semantic HTML conversion.
- Convert HTML to Markdown.
- Add style-map hooks for headings.
- Compare Mammoth output with Pandoc output.

### Files to create/modify

- `app/conversion/mammoth_engine.py`
- `app/conversion/html_to_markdown.py`
- `tests/integration/test_mammoth_engine.py`

### Acceptance criteria

- Simple `.docx` converts cleanly.
- Heading/list/link fixture passes.
- Embedded unsupported content creates warning.
- Output does not include full HTML wrapper unless intended.

### Estimated complexity

**5 / 10**

## Phase 6: LibreOffice engine

### Objectives

- Detect LibreOffice/soffice.
- Implement `.doc` pre-conversion route.
- Support fallback conversion to HTML/text.
- Use isolated temp profile where possible.
- Add process timeout and cleanup.

### Files to create/modify

- `app/conversion/libreoffice_engine.py`
- `app/core/process.py`
- `tests/integration/test_libreoffice_engine.py`

### Acceptance criteria

- Missing LibreOffice produces actionable error.
- `.doc` fixture converts through intermediate route.
- Timeout kills process tree.
- Temp profile is cleaned.
- Output path is detected even if LibreOffice changes filename capitalization.

### Estimated complexity

**8 / 10**

## Phase 7: PDF engines

### Objectives

- Implement PyMuPDF extraction.
- Implement pdfminer.six fallback.
- Detect likely scanned/image-only PDFs.
- Produce warnings for low-confidence extraction.

### Files to create/modify

- `app/conversion/pdf_pymupdf_engine.py`
- `app/conversion/pdf_pdfminer_engine.py`
- `tests/integration/test_pdf_engines.py`
- `tests/fixtures/pdf/`

### Acceptance criteria

- Text PDF converts to Markdown.
- Empty/scanned PDF creates warning.
- Password-protected PDF creates structured error.
- Multi-page PDF preserves page order.
- Engine reports character count and page count.

### Estimated complexity

**7 / 10**

## Phase 8: GUI shell

### Objectives

- Build PySide6 main window.
- Add Converter and MD Stitcher tabs.
- Add menu bar and app actions.
- Implement drag/drop shell.
- Add stitch tray save/load flow for reusable stitch queues.

### Files to create/modify

- `app/main.py`
- `app/ui/main_window.py`
- `app/ui/converter_tab.py`
- `app/ui/stitcher_tab.py`
- `app/ui/widgets/file_queue_table.py`
- `app/ui/widgets/drag_drop_list.py`
- `app/ui/widgets/warning_panel.py`
- `app/resources/styles/app.qss`

### Acceptance criteria

- App launches.
- User can add/remove files in Converter.
- User can add/reorder/remove Markdown files in Stitcher.
- User can save and load stitch trays.
- UI remains responsive during placeholder jobs.
- Basic accessibility labels exist.

### Estimated complexity

**7 / 10**

## Phase 9: Worker integration

### Objectives

- Connect GUI to conversion services.
- Implement background workers.
- Display progress and status.
- Support cancel/retry.

### Files to create/modify

- `app/workers/conversion_worker.py`
- `app/workers/stitch_worker.py`
- `app/ui/converter_tab.py`
- `app/ui/stitcher_tab.py`
- `app/core/job_controller.py`

### Acceptance criteria

- Batch conversion runs without blocking UI.
- Stitching runs without blocking UI.
- Cancel stops before next job.
- Retry works for failed jobs.
- UI status matches result objects.

### Estimated complexity

**8 / 10**

## Phase 10: Reports and diagnostics

### Objectives

- Implement JSON and Markdown reports.
- Show run summary.
- Add copy diagnostics.
- Add privacy-safe logs.

### Files to create/modify

- `app/conversion/reports.py`
- `app/core/diagnostics.py`
- `app/ui/run_summary_dialog.py`
- `tests/unit/test_reports.py`

### Acceptance criteria

- Report generated for each run.
- Failed jobs include technical detail.
- Report does not include document body content.
- User can open output folder.

### Estimated complexity

**5 / 10**

## Phase 11: Packaging Windows alpha

### Objectives

- Build Windows `.exe`.
- Include icons and resources.
- Detect external dependencies.
- Create installer or portable package.

### Files to create/modify

- `scripts/build_windows.ps1`
- `packaging/windows/`
- `app/resources/icons/`
- `README.md`

### Acceptance criteria

- App runs on clean Windows 11 test machine.
- Missing Pandoc/LibreOffice warnings work.
- Conversion works when dependencies installed.
- No console window appears in GUI release build unless debug mode.

### Estimated complexity

**7 / 10**

## Phase 12: Linux beta

### Objectives

- Validate Linux runtime.
- Package AppImage or deb.
- Test drag/drop and file permissions.
- Document dependency installation.

### Files to create/modify

- `scripts/build_linux.sh`
- `packaging/linux/`
- `README.md`
- `docs/linux-install.md`

### Acceptance criteria

- App launches on target distro.
- Pandoc/LibreOffice detection works.
- File dialogs and drag/drop work.
- Markdown stitcher works identically to Windows.

### Estimated complexity

**7 / 10**

## Phase 13: macOS collaborative track

### Objectives

- Start Q4 2026/Q1 2027 macOS effort.
- Validate PySide6 app bundle.
- Handle signing/notarization path.
- Test Apple Silicon.

### Files to create/modify

- `scripts/build_macos.sh`
- `packaging/macos/`
- `docs/macos-release.md`
- CI macOS workflow

### Acceptance criteria

- App launches as `.app`.
- DMG generated.
- Signed/notarized release path documented.
- Dependency strategy chosen.

### Estimated complexity

**8 / 10**

## Current progress snapshot

| Phase | Status | Notes |
|---|---|---|
| 0 | Completed | Modular scaffold, pyproject, scripts, baseline tests, and initial user/developer docs set are in place. |
| 1 | Completed | Core models/settings/paths/logging implemented and covered by unit tests. |
| 2 | In progress | File detection + dependency preflight added with tests; router now has queue-ready inputs. |
| 3 | Completed | Stitcher separator + service implemented with deterministic tests. |
| 4 | In progress | Pandoc wrapper + normalizer added with unit and optional integration tests; conversion service now supports route fallback selection. |
| 5 | Completed | Mammoth engine + HTML-to-Markdown bridge implemented with fallback and warning coverage tests. |
| 6 | In progress | LibreOffice engine now includes `.doc -> .docx` intermediate routing, process-tree timeout termination, and skip-aware integration coverage; broader fixture corpus remains. |
| 7 | In progress | PyMuPDF + pdfminer engines implemented with unit coverage, fallback routing, and safe PDF fixture integration tests; broader office fixture corpus remains. |
| 8 | In progress | Main window + menu + settings dialog + Converter/Stitcher UI are implemented with neon styling, drag/drop, tray save/load, action icons, accessibility names/tooltips, and offscreen smoke coverage; remaining work is visual QA on real Windows. |
| 9 | In progress | Conversion + stitching now run in workers with cancel support and retry-failed converter path; remaining work is packaging/runtime validation and final UI polish. |
| 10 | In progress | JSON/Markdown conversion report generation with engine metadata added with tests. |
| 11 | In progress | Windows PyInstaller spec and build script are in place; local onedir build succeeded and clean-machine validation remains. |
| 12 | Not started | Linux beta target. |
| 13 | Future | Q4 2026/Q1 2027. |
