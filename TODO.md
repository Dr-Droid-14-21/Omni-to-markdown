# TODO.md

## Purpose

This is the immediate actionable task list for the Document-to-Markdown Converter + MD Stitcher GUI application.

## Priority 0: Start here

- [x] Create repository root.
- [x] Create `app/`, `tests/`, `docs/`, `scripts/`, and `packaging/` folders.
- [ ] Add all generated documentation files into `docs/`.
- [x] Add `pyproject.toml`.
- [x] Add `.gitignore`.
- [x] Add `.editorconfig`.
- [x] Add initial `README.md`.
- [x] Add initial changelog entry in `ALL-FILES-CHANGELOG.md`.
- [x] Run initial `pytest` placeholder.

## Priority 1: Core safety and models

- [x] Create `app/core/models.py`.
- [x] Define `FileStatus`.
- [x] Define `ConversionWarning`.
- [x] Define `ConversionError`.
- [x] Define `ConversionPlan`.
- [x] Define `ConversionResult`.
- [x] Define `QueueItem`.
- [x] Define `StitchManifest`.
- [x] Add unit tests for model validation.
- [x] Create `app/core/paths.py`.
- [x] Add platform-specific config/cache/temp directories.
- [x] Create `app/core/settings.py`.
- [x] Add default settings.
- [x] Add settings load/save tests.
- [x] Create `app/core/logging_config.py`.
- [x] Ensure logs do not capture document body text.

## Priority 2: MD Stitcher first implementation

- [x] Create `app/stitcher/separator.py`.
- [x] Add exact separator constants.
- [x] Add separator generation tests.
- [x] Create `app/stitcher/stitcher_service.py`.
- [x] Implement ordered file read.
- [x] Implement basename-only separator naming.
- [x] Insert separator between files only.
- [x] Normalize line endings to LF.
- [x] Preserve source content.
- [x] Write to temp output first.
- [x] Prevent output path from matching an input path.
- [x] Add duplicate basename warning.
- [x] Add empty file handling.
- [x] Add encoding error handling.
- [x] Add golden output test.

## Priority 3: File detection and preflight

- [x] Create `app/core/file_detection.py`.
- [x] Detect `.doc`.
- [x] Detect `.docx`.
- [x] Detect `.pdf`.
- [x] Detect `.odt`.
- [x] Detect `.odf`.
- [x] Reject unsupported files.
- [x] Warn on mismatched extension/header.
- [x] Detect cloud placeholder/unavailable file where possible.
- [x] Detect read permission issues.
- [x] Detect output directory write permission.
- [x] Add unit tests.

## Priority 4: Engine availability

- [x] Create `app/conversion/base.py`.
- [x] Define `ConversionEngine` interface.
- [x] Create `app/conversion/router.py`.
- [x] Add engine availability model.
- [x] Detect Pandoc.
- [x] Detect LibreOffice/soffice.
- [x] Detect Python package engines.
- [x] Add settings overrides for binary paths.
- [x] Add preflight dependency warnings.

## Priority 5: Markdown normalizer

- [x] Create `app/conversion/markdown_normalizer.py`.
- [x] Normalize LF line endings.
- [x] Ensure final newline.
- [x] Avoid modifying fenced code blocks.
- [x] Convert HTML fragments to Markdown.
- [x] Add image path rewrite helpers.
- [x] Add table fallback warnings.
- [x] Add unit tests.

## Priority 6: Pandoc conversion

- [x] Create `app/conversion/pandoc_engine.py`.
- [x] Implement `.docx` conversion.
- [x] Implement `.odt` conversion.
- [x] Implement HTML intermediate conversion.
- [x] Capture stderr.
- [x] Handle non-zero exit codes.
- [x] Add timeout.
- [x] Add integration tests skipped if Pandoc unavailable.

## Priority 7: Mammoth conversion

- [x] Create `app/conversion/mammoth_engine.py`.
- [x] Convert `.docx` to HTML.
- [x] Convert HTML to Markdown.
- [x] Add style map option.
- [x] Warn on unsupported embedded content.
- [x] Add tests.

## Priority 8: LibreOffice conversion

- [x] Create `app/conversion/libreoffice_engine.py`.
- [x] Detect `soffice`.
- [x] Convert `.doc` to `.docx`.
- [x] Convert fallback to HTML.
- [x] Convert `.odf` cautiously.
- [x] Use isolated temp profile.
- [x] Add process timeout.
- [x] Kill process tree on timeout.
- [x] Clean temp profile.
- [x] Add integration tests skipped if LibreOffice unavailable.

## Priority 9: PDF conversion

- [x] Create `app/conversion/pdf_pymupdf_engine.py`.
- [x] Extract text by pages.
- [x] Detect image-heavy pages.
- [x] Warn if no text layer.
- [x] Create `app/conversion/pdf_pdfminer_engine.py`.
- [x] Add fallback extraction.
- [x] Add password-protected PDF handling.
- [x] Add tests with safe fixtures.

## Priority 10: Reports

- [x] Create `app/conversion/reports.py`.
- [x] Generate JSON report.
- [x] Generate Markdown report.
- [x] Include engine versions.
- [x] Include warnings/errors.
- [x] Avoid document body text.
- [x] Add tests.

## Priority 11: GUI shell

- [x] Create `app/main.py`.
- [x] Create `app/ui/main_window.py`.
- [x] Add menu bar.
- [x] Add Converter tab.
- [x] Add MD Stitcher tab.
- [x] Add Settings dialog.
- [x] Add status bar.
- [x] Add icons later.
- [x] Add app stylesheet.

## Priority 12: Converter GUI

- [x] Add file queue table.
- [x] Add Add Files action.
- [x] Add Add Folder action.
- [x] Add Remove action.
- [x] Add Clear action.
- [x] Add output folder selector.
- [x] Add Convert button.
- [x] Add Cancel button for active conversion runs.
- [x] Add Retry Failed action for failed queue items.
- [x] Add progress bar.
- [x] Add warning/error panel.
- [x] Connect to preflight scan.

## Priority 13: MD Stitcher GUI

- [x] Add archive-style Markdown tray.
- [x] Add drag/drop.
- [x] Add reorder controls.
- [x] Add remove/clear.
- [x] Add output file selector.
- [x] Add separator preview.
- [x] Add duplicate warning display.
- [x] Connect to StitcherService.
- [x] Add completion summary.

## Priority 14: Workers

- [x] Create `app/workers/conversion_worker.py`.
- [x] Create `app/workers/stitch_worker.py`.
- [x] Ensure UI stays responsive.
- [x] Add cancel behavior.
- [x] Add retry failed behavior.
- [x] Add worker tests where practical.

## Priority 15: Packaging

- [x] Create `scripts/build_windows.ps1`.
- [x] Create Windows PyInstaller spec.
- [ ] Test on clean Windows 11.
- [x] Create `scripts/build_linux.sh`.
- [ ] Evaluate AppImage/deb.
- [x] Document dependency installation.
- [ ] Plan macOS Q4 2026/Q1 2027 track.

## Priority 16: Documentation

- [x] Write `README.md`.
- [x] Write `docs/user-guide.md`.
- [x] Write `docs/troubleshooting.md`.
- [x] Write `docs/developer-setup.md`.
- [x] Write `docs/conversion-quality.md`.
- [x] Update all docs after implementation changes.

## Immediate next three tasks

1. Test the PyInstaller output on this Windows 11 machine, then on a clean Windows 11 machine.
2. Evaluate Linux AppImage/deb packaging options.
3. Plan macOS Q4 2026/Q1 2027 packaging and notarization track.

These are the next unblockers for turning the functional app into a shippable Windows 11 MVP.
