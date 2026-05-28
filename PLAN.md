# PLAN.md

## Purpose

This is the master project plan for the Document-to-Markdown Converter + MD Stitcher GUI application.

## Planning horizon

The plan starts from the current foundation phase and aligns release maturity with Q4 2026 and Q1 2027 milestones, especially for the macOS collaborative effort.

## Project objectives

1. Build a reliable Windows 11-first local desktop GUI.
2. Keep Linux compatibility active from early development.
3. Keep macOS architecture-compatible but schedule polished macOS work for Q4 2026 to Q1 2027.
4. Convert `.doc`, `.docx`, `.pdf`, `.odt`, `.odf` to Markdown.
5. Provide a deterministic MD Stitcher with exact separator behavior.
6. Maintain safe, testable, documented implementation.

## Roles

| Role | Owner | Responsibility |
|---|---|---|
| Product Owner | Project lead | Defines scope, approves UX, prioritizes features. |
| Systems Architect | Engineering lead | Architecture, stack, dependency strategy. |
| Conversion Engineer | Developer/agent | Conversion engines and normalization. |
| GUI Engineer | Developer/agent | PySide6 interface and workers. |
| QA Engineer | Developer/agent | Fixtures, regression tests, edge cases. |
| Packaging Engineer | Developer/agent | Windows/Linux/macOS packaging. |
| Documentation Lead | Developer/agent | User/developer docs and changelog discipline. |
| Gemini Orchestrator | AI conductor | Delegation, review, conflict control. |

## Phase roadmap

## Phase A: Foundation and deterministic core

Target: May to June 2026

Deliverables:

- Repository skeleton.
- Documentation foundation.
- Models and settings.
- File detection.
- MD Stitcher service.
- Stitcher unit tests.

Exit criteria:

- Stitching works from service layer.
- Exact separator behavior is covered by tests.
- Source files remain untouched.
- Changelog process is active.

## Foundation status update (2026-05-23)

Completed in repository:

- Modular scaffold created: `app/`, `tests/`, `docs/`, `scripts/`, `packaging/`.
- Deterministic stitcher core implemented with separator + stitch service.
- Core models/settings/path/logging modules implemented.
- Windows-first PySide6 app shell implemented with Converter + MD Stitcher tabs.
- Converter preflight, dependency checks, conversion execution, and run-report generation wired.
- Mammoth `.docx -> HTML -> Markdown` fallback engine added with warning surfacing.
- Dependency preflight now evaluates alternative routes (`pandoc`, `mammoth`, or `libreoffice`) for `.docx`.
- LibreOffice route now includes `.doc -> .docx -> HTML -> Markdown` with process-tree timeout cleanup and integration coverage.
- PDF baseline engines now include `pymupdf` primary extraction with `pdfminer` fallback routing.
- PDF text extraction is now covered by safe fixture integration tests for both PDF routes.
- Markdown normalization now includes image path rewrite helpers that avoid fenced code blocks.
- Converter thread flow now includes cancel request handling and retry-failed execution path.
- Stitcher tab now runs in a background worker with cancel support and completion reporting.
- Stitcher list UX now supports drag/drop ingestion, separator preview, duplicate-basename warnings, and save/load tray archives for reusable stitch sets.
- Converter, Stitcher, and menu actions now include standard Windows-friendly icons for faster control scanning.
- The Windows GUI now has non-visible accessibility names/tooltips and an offscreen smoke test.
- Windows PyInstaller packaging now has a maintained spec, build script entrypoint, and local onedir build validation.
- Dependency installation is documented for Python packages and external conversion tools.
- First user/developer documentation set is in place (`README`, user guide, troubleshooting, setup, quality notes).
- Unit/integration test baseline active (`pytest`, `ruff`) with skip-aware Pandoc integration coverage.

Tree snapshot is recorded in `docs/PROJECT_TREE.md`.

## Phase B: Conversion engine prototype

Target: June to July 2026

Deliverables:

- Pandoc engine.
- Mammoth engine.
- Markdown normalizer.
- Initial PDF extraction with PyMuPDF.
- Reports model.
- Engine availability detection.

Exit criteria:

- `.docx` converts through at least one route.
- `.odt` converts through Pandoc route.
- Text PDF converts with warnings where needed.
- Missing dependencies are reported clearly.

## Phase C: Legacy and fallback conversion

Target: July to August 2026

Deliverables:

- LibreOffice engine.
- `.doc` route.
- `.odf` guarded route.
- pdfminer.six fallback.
- Timeout and crash handling.
- Expanded test corpus.

Exit criteria:

- `.doc` conversion path works on Windows test machine with LibreOffice installed.
- Encrypted/corrupt files fail safely.
- PDF failures are user-readable.
- Conversion reports are useful.

## Phase D: Windows GUI MVP

Target: August to September 2026

Deliverables:

- PySide6 main window.
- Converter tab.
- MD Stitcher tab.
- Drag/drop.
- Stitch tray save/load archive flow.
- Queue table.
- Settings dialog.
- Background workers.

Exit criteria:

- User can convert files from GUI.
- User can stitch Markdown files from GUI.
- UI does not freeze during work.
- Cancel/retry flows work.
- Output folder actions work.

## Phase E: Windows alpha packaging

Target: September to October 2026

Deliverables:

- Windows portable build.
- Windows installer candidate.
- Dependency detection screen.
- User guide draft.
- Troubleshooting guide.

Exit criteria:

- Runs on clean Windows 11.
- Handles missing Pandoc/LibreOffice gracefully.
- Installer or portable package is testable.
- Basic regression test suite passes.

## Phase F: Linux beta

Target: Q4 2026

Deliverables:

- Linux package strategy.
- AppImage or deb proof.
- Linux dependency guide.
- Linux drag/drop validation.
- Cross-platform path fixes.

Exit criteria:

- Runs on at least one Ubuntu LTS target.
- Runs on one non-Ubuntu distro if feasible.
- Stitcher output identical to Windows.
- Conversion behavior documented per distro limitations.

## Phase G: Windows/Linux release candidate

Target: Q4 2026

Deliverables:

- V1 release candidate.
- Regression corpus.
- Signed Windows build if certificate available.
- Linux package candidate.
- Documentation complete.

Exit criteria:

- No known source-file mutation risk.
- All priority tests pass.
- Critical errors are structured.
- Changelog complete.

## Phase H: macOS collaborative track

Target: Q4 2026 to Q1 2027

Deliverables:

- macOS build investigation.
- `.app` bundle.
- DMG packaging.
- Apple Silicon validation.
- Signing and notarization plan.
- Dependency strategy: Homebrew-detected vs bundled.

Exit criteria:

- App launches on Apple Silicon.
- File dialogs and drag/drop work.
- Converter dependencies are detected.
- Notarized build path is documented or implemented.
- macOS limitations documented honestly.

## Milestone table

| Milestone | Target | Deliverable |
|---|---|---|
| M0 | 2026-05 | Project docs and foundation generated |
| M1 | 2026-06 | Core models + stitcher service |
| M2 | 2026-07 | Conversion prototype |
| M3 | 2026-08 | Legacy and PDF fallback routes |
| M4 | 2026-09 | Windows GUI MVP |
| M5 | 2026-10 | Windows alpha package |
| M6 | Q4 2026 | Linux beta and Windows/Linux RC |
| M7 | Q4 2026 | macOS collaboration starts |
| M8 | Q1 2027 | macOS signed/notarized release candidate if feasible |

## Scope control

Do not add these until V1 is stable:

- OCR.
- Cloud conversion.
- AI summarization.
- RAG database export.
- Real-time folder watcher.
- Markdown editor.
- Obsidian plugin.
- Browser extension.
- Mobile apps.

## Risk register

| Risk | Severity | Mitigation |
|---|---:|---|
| LibreOffice headless hangs | High | Timeouts, isolated profile, single concurrency. |
| PDF extraction quality varies | High | Warnings, fallback engines, no perfection promise. |
| Packaging size grows too large | Medium | Detect external tools instead of bundling initially. |
| macOS signing complexity | High | Schedule collaborative future track. |
| Duplicate filenames in stitcher | Medium | Warn and use basename exactly as required. |
| User expects OCR | Medium | Clear out-of-scope messaging. |
| Source files accidentally modified | Critical | Read-only design, tests, temp output, no in-place operations. |

## Definition of done

The project is release-ready when:

- Converter supports required formats with safe fallbacks.
- MD Stitcher separator behavior is exact and tested.
- GUI is responsive.
- Errors are structured.
- Reports exist.
- Windows package is tested.
- Linux package is validated.
- Docs are complete.
- Changelog allows contributor resume from last line.
