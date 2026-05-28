# Experiment Plans

## E01: Separator Accuracy Verification
- **Verifies**: C01
- **Setup**:
  - System: Python 3.12+ environment with `pytest`
  - Dataset: Synthetic set of filenames with varying lengths (1 to 50 chars)
- **Procedure**:
  1. Generate separators for each filename using `build_separator`.
  2. Verify string length is exactly 60.
  3. Verify previous filename exists within the string.
  4. Perform a 3-file stitch and check the resulting file for exact byte-sequence matches of the separators.
- **Metrics**: Pass/Fail (Length == 60, Content == deterministic)
- **Expected outcome**:
  - All generated separators will be exactly 60 characters long.
  - Filenames will be correctly positioned.
- **Baselines**: Manual string construction
- **Dependencies**: none

## E02: Fallback Route Success Rate
- **Verifies**: C02
- **Setup**:
  - Hardware: Windows 11 workstation
  - Software: Pandoc 3.x, LibreOffice 24.x, Mammoth (Python)
  - Dataset: 10 complex `.docx` files (with tables, nested lists, and rare fonts)
- **Procedure**:
  1. Attempt conversion of each file using Pandoc only.
  2. Attempt conversion using the full `app/conversion/service.py` sequence (Pandoc -> Mammoth -> LibreOffice).
  3. Compare the number of successfully generated Markdown files.
- **Metrics**: Success count (0-10)
- **Expected outcome**:
  - The multi-engine service will produce more valid Markdown files than any single engine.
- **Baselines**: Single-engine (Pandoc) conversion
- **Dependencies**: E01

## E03: Process Cleanup Integrity
- **Verifies**: C03
- **Setup**:
  - Hardware: Windows 11
  - Software: LibreOffice, `psutil` library
- **Procedure**:
  1. Trigger a LibreOffice conversion with a 1-second timeout on a large file.
  2. Monitor active processes for `soffice.exe` and `soffice.bin`.
  3. After timeout, verify that all related processes are terminated.
- **Metrics**: Zombie process count
- **Expected outcome**:
  - Zero LibreOffice-related processes will remain after a timeout event.
- **Baselines**: Standard `subprocess.run` with `timeout` (which may leave orphaned children)
- **Dependencies**: none
