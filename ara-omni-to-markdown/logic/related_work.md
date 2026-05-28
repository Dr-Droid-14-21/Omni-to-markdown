# Related Work and Dependencies

## RW01: Pandoc
- **DOI**: N/A
- **Type**: baseline
- **Delta**:
  - What changed: Omni wraps Pandoc to add deterministic normalization and fallback.
  - Why: Pandoc's native DOCX to MD often produces idiosyncratic formatting that needs cleaning.
- **Claims affected**: C02
- **Adopted elements**: ODT conversion, initial DOCX parsing.

## RW02: Mammoth (Python)
- **DOI**: N/A
- **Type**: baseline
- **Delta**:
  - What changed: Used as a semantic-first fallback for DOCX.
  - Why: Mammoth focuses on semantic HTML, avoiding the "style soup" of Pandoc in some DOCX variants.
- **Claims affected**: C02
- **Adopted elements**: DOCX to HTML logic.

## RW03: Microsoft MarkItDown
- **DOI**: https://github.com/microsoft/markitdown
- **Type**: imports
- **Delta**:
  - What changed: Omni implements a similar multi-engine philosophy but adds a GUI and a strict stitching contract.
  - Why: MarkItDown is a library/CLI; Omni provides a full Windows 11 desktop workflow.
- **Claims affected**: C02
- **Adopted elements**: Idea of engine diversification.
