---
title: "Omni to Markdown: A Local-First Document-to-Markdown Pipeline"
authors: ["Omni to Markdown Contributors"]
year: 2026
venue: "Self-Published / Open Source"
doi: "N/A"
ara_version: "1.0"
domain: "Software Engineering / Document Processing"
keywords: ["Markdown", "Conversion", "PySide6", "Pandoc", "LibreOffice", "Document Stitching", "Local-First"]
claims_summary:
  - "Stitcher separator format is byte-for-byte deterministic (60 '=' characters with previous filename)."
  - "Multi-engine fallback routing (Pandoc -> Mammoth -> LibreOffice) ensures robustness for complex DOCX/ODT files."
  - "Isolated temp profiles and process-tree termination prevent resource leaks and instability in legacy engine wrappers."
abstract: "Omni to Markdown is a local-first desktop application designed to address the fragmentation and privacy risks of cloud-based document conversion. It implements a multi-engine fallback architecture for converting .doc, .docx, .pdf, .odt, and .odf files into normalized Markdown. The system features a deterministic 'MD Stitcher' with a strictly defined separator contract, ensuring predictable output for large document collections. This artifact documents the logical framework, architecture, and verification strategy for the pipeline."
---

# Omni to Markdown: A Local-First Document-to-Markdown Pipeline

## Overview
Omni to Markdown provides a unified interface for converting various document formats into high-quality Markdown and stitching them together into a single output. It prioritizes data privacy through purely local processing and ensures architectural stability by wrapping multiple conversion engines (Pandoc, Mammoth, LibreOffice, PyMuPDF) with safety-first process management and preflight validation.

## Layer Index

### Cognitive Layer (`/logic`)
| File | Description |
|------|-------------|
| [problem.md](logic/problem.md) | Privacy risks in cloud conversion and non-deterministic stitching |
| [claims.md](logic/claims.md) | 3 falsifiable claims (C01–C03) |
| [concepts.md](logic/concepts.md) | Formal definitions: Separator Contract, Engine Routing, etc. |
| [experiments.md](logic/experiments.md) | Verification plans for separator accuracy and fallback success |
| [solution/architecture.md](logic/solution/architecture.md) | Multi-engine router and background worker architecture |
| [solution/algorithm.md](logic/solution/algorithm.md) | Separator generation and engine selection logic |
| [solution/constraints.md](logic/solution/constraints.md) | Local-only processing and legacy engine limitations |
| [solution/heuristics.md](logic/solution/heuristics.md) | Timeout bounds and temp profile isolation |
| [related_work.md](logic/related_work.md) | Pandoc, Mammoth, and Microsoft MarkItDown |

### Physical Layer (`/src`)
| File | Description | Claims |
|------|-------------|--------|
| [execution/router.py](src/execution/router.py) | Multi-engine fallback routing logic | C02 |
| [execution/separator.py](src/execution/separator.py) | Deterministic separator generation | C01 |
| [environment.md](src/environment.md) | PySide6, Pandoc, and LibreOffice dependencies | - |

### Exploration Graph (`/trace`)
| File | Description |
|------|-------------|
| [exploration_tree.yaml](trace/exploration_tree.yaml) | 8-node research and implementation DAG |

### Evidence (`/evidence`)
| File | Description |
|------|-------------|
| [README.md](evidence/README.md) | Index of conversion quality and separator validation |
