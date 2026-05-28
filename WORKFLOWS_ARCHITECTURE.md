# WORKFLOWS_ARCHITECTURE.md

## Purpose

This document describes the system architecture, data flow, MD Stitcher workflow, queue management, and error-handling flow for the Document-to-Markdown Converter + MD Stitcher GUI application.

## Architecture principles

1. GUI must not contain conversion logic.
2. Conversion and stitching must be callable without GUI.
3. All external tools must be wrapped behind engine interfaces.
4. Every job must produce a result object.
5. Errors must be data, not surprise popups only.
6. Source files must never be modified.
7. Temporary outputs must become final outputs only after validation.

## Component diagram

```text
+--------------------------------------------------------------------------------+
|                                   Desktop App                                  |
|                                                                                |
|  +-----------------------------+       +-------------------------------------+ |
|  |           PySide6 UI         |       |          Settings + Profiles        | |
|  |-----------------------------|       |-------------------------------------| |
|  | Main Window                 |<----->| User settings JSON/TOML             | |
|  | Converter Tab               |       | Engine paths                        | |
|  | MD Stitcher Tab             |       | Output preferences                  | |
|  | Settings Dialog             |       | Privacy + diagnostics flags          | |
|  +--------------+--------------+       +------------------+------------------+ |
|                 |                                     |                        |
|                 v                                     v                        |
|  +-----------------------------+       +-------------------------------------+ |
|  |        Job Controller        |<----->|             Logger/Reporter         | |
|  |-----------------------------|       |-------------------------------------| |
|  | Queue state                  |       | Run report                          | |
|  | Worker lifecycle             |       | Per-file report                     | |
|  | Cancel/retry                 |       | User-visible diagnostics             | |
|  +--------------+--------------+       +------------------+------------------+ |
|                 |                                     ^                        |
|                 v                                     |                        |
|  +-----------------------------+       +-------------------------------------+ |
|  |       Conversion Router      |------>|         Conversion Engines          | |
|  |-----------------------------|       |-------------------------------------| |
|  | File type detection          |       | Pandoc Engine                       | |
|  | Engine selection             |       | LibreOffice Engine                  | |
|  | Fallback planning            |       | Mammoth Engine                      | |
|  | Warning generation           |       | PyMuPDF Engine                      | |
|  +--------------+--------------+       | pdfminer.six Engine                 | |
|                 |                      +------------------+------------------+ |
|                 v                                         |                    |
|  +-----------------------------+                          v                    |
|  |     Markdown Normalizer      |<------------------ External Tools           |
|  |-----------------------------|        pandoc / soffice / optional plugins   |
|  | LF line endings              |                                               |
|  | Markdown cleanup             |                                               |
|  | Asset path rewrite           |                                               |
|  +--------------+--------------+                                               |
|                 |                                                              |
|                 v                                                              |
|  +-----------------------------+                                               |
|  |      Output Writer           |                                               |
|  |-----------------------------|                                               |
|  | Temp output                  |                                               |
|  | Validate                     |                                               |
|  | Atomic move                  |                                               |
|  +-----------------------------+                                               |
|                                                                                |
|  +-----------------------------+                                               |
|  |       MD Stitcher Service    |                                               |
|  |-----------------------------|                                               |
|  | Ordered Markdown manifest    |                                               |
|  | Separator insertion          |                                               |
|  | Encoding normalization       |                                               |
|  | Atomic stitched output       |                                               |
|  +-----------------------------+                                               |
+--------------------------------------------------------------------------------+
```

## Primary modules

## UI layer

Responsibilities:

- File selection.
- Drag/drop.
- Queue display.
- User settings.
- Progress display.
- Human-readable errors.
- Dispatch work to controllers.

Non-responsibilities:

- Direct document conversion.
- Parsing Markdown.
- Calling external binaries directly.
- Writing output files directly except via services.

## Job controller

Responsibilities:

- Maintain queue state.
- Create jobs from UI requests.
- Start, pause, cancel, retry jobs.
- Route results back to UI.
- Prevent destructive operations.
- Keep UI responsive via workers/threads.

## Conversion router

Responsibilities:

- Detect input format.
- Select engine route.
- Build fallback plan.
- Validate engine availability.
- Produce preflight warnings.

Example route:

```text
source.doc
  -> LibreOfficeEngine converts to intermediate.docx
  -> PandocEngine converts intermediate.docx to output.md
  -> MarkdownNormalizer cleans output.md
  -> ReportWriter records route
```

## Conversion engines

Each engine is narrow and replaceable.

### Pandoc Engine

- Handles `.docx`, `.odt`, `.html`.
- Invokes Pandoc safely.
- Captures stderr.
- Produces raw Markdown.

### LibreOffice Engine

- Handles `.doc` and fallback conversions.
- Converts legacy formats into safer intermediate formats.
- Uses isolated profiles when possible.
- Applies timeout and crash handling.

### Mammoth Engine

- Handles `.docx` to semantic HTML.
- Good for clean prose.
- Passes HTML to Markdown normalizer.

### PyMuPDF Engine

- Handles PDF extraction.
- Detects image-heavy/scanned pages.
- Produces text/Markdown-like output.

### pdfminer.six Engine

- Fallback for PDF text extraction.
- Can be slower but useful when PyMuPDF output is poor.

## Markdown Normalizer

Responsibilities:

- Normalize line endings.
- Ensure final newline.
- Clean excessive blank lines conservatively.
- Convert HTML fragments to Markdown where required.
- Rewrite asset paths.
- Preserve code blocks.
- Generate warnings for unsupported structures.

## Output Writer

Responsibilities:

- Write to temporary file.
- Validate output exists and has expected encoding.
- Rename/move to final output.
- Prevent overwriting unless user confirms.
- Handle filename conflicts.

## Data flow: conversion pipeline

```text
User adds files
  -> FileDetector scans extension and magic/header
  -> QueueItem created
  -> Router creates ConversionPlan
  -> UI displays engine route and warnings
  -> User clicks Convert
  -> JobController starts worker
  -> Engine converts to temp output
  -> MarkdownNormalizer processes temp output
  -> OutputWriter commits final .md
  -> Reporter records result
  -> UI shows success/warnings/errors
```

## Conversion plan object

Fields:

- `source_path`
- `detected_extension`
- `detected_mime`
- `preferred_engine`
- `fallback_engines`
- `intermediate_format`
- `output_path`
- `warnings`
- `requires_external_tools`
- `estimated_risk_level`

Risk levels:

- Low: normal `.docx`/`.odt`.
- Medium: PDF with extractable text.
- High: old `.doc`, `.odf`, complex PDF.
- Critical: encrypted, corrupt, scanned without OCR.

## MD Stitcher workflow

```text
User opens MD Stitcher tab
  -> User drags .md files into tray or uses menu
  -> Stitcher validates files
  -> UI shows ordered archive-style list
  -> User reorders/removes files
  -> User chooses output path
  -> User clicks Stitch
  -> StitcherService reads files in order
  -> Writes first file content
  -> Inserts separator named after previous file
  -> Writes next file content
  -> Repeats until final file
  -> OutputWriter commits stitched output
  -> UI displays summary
```

## MD Stitcher separator rule

Required exact visible pattern:

```text
===========================PREVIOUS FILE NAME.md=================================
```

Implementation interpretation:

```text
===========================actual_previous_file_name.md=================================
```

The previous file name is the basename only. Directory paths are excluded.

## Stitcher output flow

For input order:

```text
a.md
b.md
c.md
```

The output is:

```text
<content of a.md>

===========================a.md=================================

<content of b.md>

===========================b.md=================================

<content of c.md>
```

## Queue management

## Queue item model

Fields:

- `id`
- `source_path`
- `display_name`
- `detected_type`
- `status`
- `engine_route`
- `output_path`
- `warnings`
- `errors`
- `progress`
- `created_at`
- `updated_at`
- `result`

## Queue operations

- Add files.
- Add folder.
- Remove selected.
- Clear finished.
- Clear all.
- Retry failed.
- Open source location.
- Open output location.
- Export queue report.

## Queue concurrency

Recommended V1:

- Default concurrency: 1.
- Optional concurrency: 2 for documents.
- PDF extraction may run separately if stable.
- LibreOffice conversions should usually run one at a time because headless profile contention can cause unpredictable behavior.

## Error handling flow

```text
Operation starts
  -> Validate inputs
  -> Validate output path
  -> Validate engine availability
  -> Create temp workspace
  -> Run engine with timeout
      -> success: normalize and commit
      -> warning: normalize, commit, mark warning
      -> failure: capture stderr, remove partial, mark failed
      -> timeout: kill process tree, clean temp, mark failed
  -> Write report entry
  -> Update queue status
```

## Error object

Fields:

- `code`
- `severity`
- `title`
- `message`
- `technical_details`
- `suggested_fix`
- `retryable`
- `source_path`
- `engine_name`

Example:

```json
{
  "code": "PDF_NO_TEXT_LAYER",
  "severity": "warning",
  "title": "No extractable text found",
  "message": "This PDF appears to contain scanned pages. Markdown output may be empty.",
  "technical_details": "PyMuPDF extracted 0 text characters across 12 pages.",
  "suggested_fix": "Use an OCR tool first or enable OCR in a future version.",
  "retryable": false
}
```

## Cancellation flow

- User clicks Cancel.
- JobController requests cancellation.
- Worker stops before next file.
- If an external process is running, it is terminated after grace period.
- Temp output is deleted or marked `.cancelled`.
- Source file remains unchanged.
- Queue marks current file cancelled and pending files unchanged.

## Reporting flow

For every run:

```text
run_id/
  conversion-report.json
  conversion-report.md
  logs/
    app.log
  outputs/
    converted files
```

Report should include:

- App version.
- OS.
- Engine versions.
- Source file names.
- Output file names.
- Status per item.
- Warnings/errors.
- Runtime duration.
- Settings profile.

## Data persistence

V1 should persist only:

- User settings.
- Recent output folders.
- Optional recent project/session files.
- App logs.

It should not persist document content.

## Future architecture extension points

- OCR plugin.
- AI cleanup plugin.
- RAG export plugin.
- Watch folder automation.
- CLI binary.
- Split stitched Markdown back into source files.
- Cloud sync integration.
- Conversion quality scoring.
