# Heuristics and Safety Rules

## H01: Process-Tree Termination
- **Rationale**: Headless LibreOffice often spawns a watchdog or child process (`soffice.bin`) that standard `subprocess.terminate()` calls miss.
- **Sensitivity**: high
- **Bounds**: Must trigger within 500ms of timeout detection.
- **Code ref**: [`app/core/process.py`]
- **Source**: `Agent.md` security baseline.

## H02: Isolated Temp Profiles
- **Rationale**: LibreOffice cannot run multiple concurrent instances using the same user profile directory.
- **Sensitivity**: medium
- **Bounds**: One unique profile directory per conversion job.
- **Code ref**: [`app/conversion/libreoffice_engine.py`]
- **Source**: `PLAN.md` risk register.

## H03: Atomic Stitching
- **Rationale**: Writing a 100MB stitched file directly to the final path risks data corruption if the process is interrupted.
- **Sensitivity**: medium
- **Bounds**: Output to `.tmp` first, then `os.replace` on success.
- **Code ref**: [`app/stitcher/stitcher_service.py`]
- **Source**: `GEMINI.md` quality bar.

## H04: PDF Image-Heavy Warning
- **Rationale**: Image-only PDFs (scanned documents) will produce empty Markdown if no text layer exists.
- **Sensitivity**: low
- **Bounds**: Trigger warning if extracted character count / page count < 100.
- **Code ref**: [`app/conversion/pdf_pymupdf_engine.py`]
- **Source**: `GEMINI.md` PDF rules.
