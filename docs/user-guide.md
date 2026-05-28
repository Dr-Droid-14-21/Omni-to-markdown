# User Guide

## Overview

Omni to Markdown provides two workflows:

1. Convert supported document files into Markdown.
2. Stitch multiple Markdown files into one combined file with deterministic separators.

## Converter workflow

1. Open the `Converter` tab.
2. Click `Add Files` or `Add Folder`.
3. Choose an output folder.
4. Click `Run Preflight`.
5. Click `Convert`.

During conversion:

- `Cancel` requests stop before the next queued file.
- `Retry Failed` reruns only failed files from the last run.

After completion:

- A conversion report is written to `<output>/reports/<run_id>/`.
- Both `conversion-report.json` and `conversion-report.md` are generated.

## Stitcher workflow

1. Open the `Markdown Stitcher` tab.
2. Add markdown files by button or drag/drop from file explorer.
3. Reorder files as needed (buttons or internal drag/drop reorder).
4. Optional: click `Save Tray` to save the current stitch list for reuse.
5. Optional: click `Load Tray` to restore a saved stitch list.
6. Choose output `.md` file.
7. Click `Stitch`.

During stitching:

- `Cancel` requests stop the operation safely.

Stitcher panel features:

- Live separator preview for the selected file.
- Duplicate basename warning display.
- Tray archive save/load (`*.omni-tray.json`) for repeat stitch batches.

## Settings

Use `File -> Settings` from the main window to configure:

- Default output directory.
- Pandoc and LibreOffice binary override paths.
- Conversion behavior defaults.

## Notes

- Source files are read-only in normal workflows.
- Output files are written to new paths and reports are separated under `reports/`.
