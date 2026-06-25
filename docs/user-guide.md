# User Guide

## Overview

Omni to Markdown provides two workflows:

1. Convert supported document files into Markdown.
2. Stitch multiple Markdown files into one combined file with deterministic separators.

## Converter workflow

1. Open the `Converter` tab.
2. Use the quick-actions panel to review queue count, supported formats, and Explorer menu status.
3. Click `Add Files`, `Add Folder`, or drag supported files/folders into the queue.
4. Choose an output folder.
5. Click `Run Preflight`.
6. Click `Convert`.

During conversion:

- `Cancel` requests stop before the next queued file.
- `Retry Failed` reruns only failed files from the last run.
- Conversion completion plays a short status sound.

After completion:

- A conversion report is written to `<output>/reports/<run_id>/`.
- Both `conversion-report.json` and `conversion-report.md` are generated.

## Batch keyword search

Both main tabs include keyword search for the current batch.

Converter search scans queued `.doc`, `.docx`, `.htm`, `.html`, `.pdf`, `.odt`, `.odf`, and `.rtf` files through
Apache Tika. Plain text and Markdown files are searched directly. Stitcher search scans the current Markdown list directly.

Requirements for converter batch search:

- Java available on `PATH`, or configured in `File -> Settings`.
- `tools/tika/tika-app-3.2.3.jar`, downloaded by `.\scripts\download_tika.ps1`, or a configured Tika jar path.

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
- Stitch completion plays a short status sound.

Stitcher panel features:

- Live separator preview for the selected file.
- Duplicate basename warning display.
- Tray archive save/load (`*.omni-tray.json`) for repeat stitch batches.

## Settings

Use `File -> Settings` from the main window to configure:

- Default output directory.
- Pandoc, LibreOffice, Java, and Apache Tika override paths.
- Conversion behavior defaults.

## Windows Explorer right-click access

You can register a user-level Explorer shortcut for supported document types and folders,
including `.doc`, `.docx`, `.htm`, `.html`, `.pdf`, `.odt`, `.odf`, `.rtf`, and `.txt`.

1. Build the app or prepare the local virtual environment.
2. Run:

```powershell
.\scripts\register_windows_context_menu.ps1
```

3. In Explorer, right-click a supported file or folder.
4. Choose `Convert to Markdown with Omni`.
5. The app opens with that selection queued automatically.

The same installer also creates `Send to -> Omni to Markdown`, which is useful when
you select multiple files and want Windows to pass them to Omni together.

Check the current integration state without changing anything:

```powershell
.\scripts\check_windows_context_menu.ps1
```

Remove the shortcut later with:

```powershell
.\scripts\unregister_windows_context_menu.ps1
```

## Notes

- Source files are read-only in normal workflows.
- Output files are written to new paths and reports are separated under `reports/`.
