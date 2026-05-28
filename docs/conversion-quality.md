# Conversion Quality Notes

## Quality principles

- Prefer deterministic outputs over hidden heuristics.
- Preserve safety: never mutate source files.
- Surface uncertainty with warnings rather than silently masking it.

## Engine behavior summary

## Office documents

- `.docx`: preferred `pandoc`, fallback `mammoth`, then `libreoffice`.
- `.odt`: preferred `pandoc`, fallback `libreoffice`.
- `.doc` and `.odf`: handled via `libreoffice`.

Known limitations:

- Complex tables may flatten.
- Embedded objects/charts can lose fidelity.
- Some style semantics depend on engine capabilities.

## PDFs

- Primary: `pymupdf` page text extraction.
- Fallback: `pdfminer` plain extraction.

Warnings are emitted for:

- Missing text layer.
- Image-heavy pages.

Known limitations:

- Scanned PDFs require OCR (out of current scope).
- Layout-heavy PDFs may lose column structure.

## Stitcher output

- File order is deterministic from UI order.
- Separator format is exact and stable.
- Duplicate basenames are warned, not blocked.

## Validation strategy

- Unit tests cover engine error paths, fallback routing, and output normalization.
- Integration tests are skip-aware and run when dependencies are available.
- Run reports capture status/error/warning metadata without including full document body text.
