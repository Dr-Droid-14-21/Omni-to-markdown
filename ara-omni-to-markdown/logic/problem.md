# Problem Specification

## Observations

### O1: Privacy Risks in Cloud Conversion
- **Statement**: Many users resort to cloud-based tools (e.g., online DOCX to MD converters) which require uploading sensitive documents to external servers.
- **Evidence**: `Agent.md` priority on "local-first" processing.
- **Implication**: There is a requirement for a high-quality, local-only alternative that handles diverse formats.

### O2: Non-Deterministic Stitching
- **Statement**: Existing document merger tools often use inconsistent or non-standard separators that vary based on locale or tool version.
- **Evidence**: `GEMINI.md` hard requirement for the separator format.
- **Implication**: Downstream consumers (e.g., LLM ingestors or static site generators) require a byte-for-byte deterministic separator contract.

### O3: Legacy Engine Instability
- **Statement**: Wrapping legacy tools like LibreOffice in headless mode frequently leads to zombie processes or profile lock-ups if not managed correctly.
- **Evidence**: `app/core/process.py` implementation of process-tree cleanup.
- **Implication**: A robust conversion pipeline must implement strict process isolation and cleanup.

## Gaps

### G1: Fragmented Local Support
- **Statement**: No single local tool handles `.doc`, `.docx`, `.pdf`, and `.odt` with equal fidelity and deterministic output.
- **Caused by**: O1, O2.
- **Existing attempts**: Pandoc (weak semantic DOCX), Mammoth (DOCX only), LibreOffice (no native MD export).
- **Why they fail**: Each tool is specialized; none provide the unified "router + stitcher" workflow required for large-scale document processing.

## Key Insight
- **Insight**: By abstracting multiple specialized engines (Pandoc, Mammoth, LibreOffice) behind a unified "router" and "normalization" layer, we can achieve high coverage and consistent quality without inventing a new parser for every format.
- **Derived from**: O1, G1.
- **Enables**: A modular, fallback-capable pipeline that is easy to extend as new open-source engines emerge.

## Assumptions
- A1: Users have or can install external dependencies like Pandoc and LibreOffice.
- A2: System file permissions allow creating temp directories for isolated profiles.
- A3: Markdown is the desired canonical output format for downstream tasks.
