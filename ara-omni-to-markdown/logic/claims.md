# Falsifiable Claims

## C01: Byte-for-byte Separator Determinism
- **Statement**: The MD Stitcher produces a separator that is exactly 60 `=` characters long, with the previous filename inserted starting at the 28th character, regardless of system locale.
- **Status**: supported
- **Falsification criteria**: Any stitched output where the separator string is not exactly 60 characters or uses a different character set.
- **Proof**: [E01]
- **Evidence basis**: `app/stitcher/separator.py` unit tests.
- **Interpretation**: This ensures that downstream parsers can rely on a fixed-width, fixed-character boundary.
- **Dependencies**: none
- **Tags**: stitcher, deterministic, contract

## C02: Fallback Routing Reliability
- **Statement**: Using a fallback sequence (Pandoc -> Mammoth -> LibreOffice) for `.docx` files increases the probability of successful conversion compared to using Pandoc alone.
- **Status**: hypothesis
- **Falsification criteria**: A `.docx` file that fails on all three engines but could have been converted by a single-engine tool.
- **Proof**: [E02]
- **Evidence basis**: Conversion service routing logic in `app/conversion/service.py`.
- **Interpretation**: Diversification of engine logic mitigates the impact of engine-specific parsing bugs.
- **Dependencies**: none
- **Tags**: conversion, fallback, robustness

## C03: Process Isolation Integrity
- **Statement**: Terminating the entire process tree (including child processes) on conversion timeout prevents ghost `soffice.bin` instances from consuming system resources.
- **Status**: supported
- **Falsification criteria**: A residual LibreOffice process remaining in the task manager after a timed-out conversion.
- **Proof**: [E03]
- **Evidence basis**: `app/core/process.py` unit tests using `psutil`.
- **Interpretation**: This is critical for long-running batch jobs where a single hang could otherwise starve the system.
- **Dependencies**: none
- **Tags**: safety, process-management, libreoffice
