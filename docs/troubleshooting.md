# Troubleshooting

## Preflight says dependencies are missing

Check the required engines:

- `pandoc` for preferred `.docx`/`.odt` paths.
- `mammoth` or `libreoffice` as fallback `.docx` routes.
- `pymupdf` or `pdfminer` for `.pdf`.
- `libreoffice` for `.doc` and `.odf`.

Actions:

1. Install missing tools/packages.
2. Set explicit binary path in app Settings for Pandoc/LibreOffice if PATH is not configured.
3. Run preflight again.

## Conversion failed for a file

Review:

- Warning/error panel in the Converter tab.
- Generated report files under `<output>/reports/<run_id>/`.

Then retry only failed files using `Retry Failed`.

## LibreOffice timeout

If large `.doc` or `.odf` files time out:

1. Retry with a smaller batch.
2. Ensure LibreOffice is not blocked by first-run dialogs.
3. Verify no antivirus or file-lock process is stalling temporary output.

## PDF produced little or no text

If warnings mention no text layer or image-heavy pages:

- The PDF is likely scanned/image-based.
- Current scope does not include OCR.
- Use OCR externally first, then reconvert the output.

## Stitch failed

Common causes:

- Missing input file.
- Output file path equals one of the input paths.
- Non-markdown input extension.
- UTF-8 decoding issues in input files.

Use the Stitcher warning area and dialog message to identify which file triggered failure.
