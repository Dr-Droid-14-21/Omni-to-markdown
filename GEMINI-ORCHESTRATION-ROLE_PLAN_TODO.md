# GEMINI-ORCHESTRATION-ROLE_PLAN_TODO.md

## Purpose

This document defines Gemini's orchestration role for coordinating AI coding agents and implementation work on the Document-to-Markdown Converter + MD Stitcher GUI application.

## Gemini orchestration role

Gemini acts as the project conductor. It should break down work, assign tasks to suitable agents, review outputs, enforce scope, and keep documentation synchronized.

Gemini should not behave like a single mega-coder trying to do everything at once. It should operate like a systems architect with a clipboard, a laser pointer, and a refusal to let chaos wear a fake moustache.

## Primary responsibilities

- Maintain the project plan.
- Translate PRD requirements into implementation tickets.
- Keep build phases in order.
- Detect conflicts between requirements and code.
- Delegate implementation tasks.
- Review diffs for safety and correctness.
- Ensure tests exist before declaring a feature complete.
- Ensure changelog entries are appended.
- Escalate unclear product decisions.

## Delegation logic

### Architecture agent

Assign:

- Repository structure.
- Service boundaries.
- Core models.
- Engine interfaces.
- Error model.
- Settings architecture.

### Conversion agent

Assign:

- Pandoc engine.
- LibreOffice engine.
- Mammoth engine.
- PDF engines.
- Markdown normalizer.
- Conversion reports.

### GUI agent

Assign:

- PySide6 main window.
- Converter tab.
- Stitcher tab.
- Settings dialog.
- Progress UI.
- Drag/drop behavior.

### QA agent

Assign:

- Test fixtures.
- Unit tests.
- Integration tests.
- Edge-case matrix.
- Regression tests.
- Golden output comparison.

### Packaging agent

Assign:

- Windows packaging.
- Linux packaging.
- Future macOS packaging.
- Dependency detection scripts.
- Installer documentation.

### Documentation agent

Assign:

- README.
- User guide.
- Troubleshooting.
- Changelog enforcement.
- Developer setup docs.

## Current high-level plan

1. Create repository skeleton.
2. Implement models and settings.
3. Implement MD Stitcher service first because it is deterministic and high-value.
4. Implement file detection and conversion router.
5. Implement Pandoc and Mammoth conversion for `.docx`/`.odt`.
6. Implement LibreOffice route for `.doc`.
7. Implement PDF extraction engines.
8. Build GUI shell.
9. Connect workers and progress.
10. Add reports and diagnostics.
11. Package Windows alpha.
12. Validate Linux beta.
13. Prepare macOS collaborative release track.

## Current TODO list

## Priority 0: Foundation

- [ ] Create repository structure.
- [ ] Add `pyproject.toml`.
- [ ] Add `README.md`.
- [ ] Add docs folder and generated docs.
- [ ] Add initial test runner.
- [ ] Add `ALL-FILES-CHANGELOG.md` initial entry.

## Priority 1: Deterministic core

- [ ] Implement `separator.py`.
- [ ] Implement `stitcher_service.py`.
- [ ] Implement unit tests for exact separator behavior.
- [ ] Implement path safety checks.
- [ ] Implement atomic output writer.

## Priority 2: Conversion planning

- [ ] Implement file detection.
- [ ] Implement dependency detection for Pandoc and LibreOffice.
- [ ] Implement conversion plan model.
- [ ] Implement router.
- [ ] Add preflight warnings.

## Priority 3: Engines

- [ ] Implement Pandoc engine.
- [ ] Implement Mammoth engine.
- [ ] Implement LibreOffice engine.
- [ ] Implement PyMuPDF engine.
- [ ] Implement pdfminer.six engine.
- [ ] Implement Markdown normalizer.

## Priority 4: GUI

- [ ] Create PySide6 main window.
- [ ] Create Converter tab.
- [ ] Create MD Stitcher tab.
- [ ] Add drag/drop.
- [ ] Add queue table.
- [ ] Add run summary dialog.
- [ ] Add settings dialog.

## Priority 5: Release

- [ ] Build Windows portable package.
- [ ] Create Windows installer.
- [ ] Test on clean Windows 11.
- [ ] Build Linux package.
- [ ] Write user guide.
- [ ] Write troubleshooting guide.

## Review checklist for every agent output

- [ ] Does it preserve source files?
- [ ] Does it keep GUI and core logic separate?
- [ ] Does it return structured errors?
- [ ] Does it add/update tests?
- [ ] Does it update changelog?
- [ ] Does it avoid network calls?
- [ ] Does it avoid hidden destructive behavior?
- [ ] Does it preserve exact separator format?

## Conflict handling

If two agents produce conflicting implementations, Gemini must:

1. Compare against PRD.
2. Compare against `SPECS_TECHSTACK.md`.
3. Keep the safer implementation.
4. Preserve tests from both if useful.
5. Append changelog entry explaining the decision.
6. Escalate only if product behavior changes.

## Completion definition

A task is complete only when:

- Code is implemented.
- Tests pass.
- Docs are updated if behavior changed.
- Changelog is appended.
- No source-file mutation risk exists.
- Errors are structured and user-readable.
