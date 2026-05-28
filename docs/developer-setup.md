# Developer Setup

## Requirements

- Python 3.12 (recommended baseline for Windows packaging)
- Windows 11 (primary target), Linux supported during development
- Optional external tools:
  - Pandoc
  - LibreOffice

## Local setup

```powershell
uv python install 3.12
uv venv .venv --python 3.12
.venv\Scripts\activate
python -m pip install -e .[dev]
python -m pip install mammoth markdownify pymupdf pdfminer.six
```

Alternative (python.org launcher path):

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

Run app:

```powershell
python -m app.main
```

## Quality checks

Lint:

```powershell
python -m ruff check .
```

Tests:

```powershell
python -m pytest
```

## Test layout

- `tests/unit`: deterministic local unit tests.
- `tests/integration`: dependency-aware tests that skip when tools are unavailable.

## Project structure highlights

- `app/conversion`: engine implementations + routing + reporting.
- `app/stitcher`: deterministic stitch logic.
- `app/workers`: background worker objects for Qt threads.
- `app/ui`: tab-level UI logic and widgets.

## Notes for contributors

- Keep source-document operations read-only.
- Prefer writing outputs atomically or via temp-file replacement.
- Update `TODO.md`, `PLAN.md`, `CODING_PIPELINE_CODING_PROGRESS.md`, and `ALL-FILES-CHANGELOG.md` alongside implementation changes.
