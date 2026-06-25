# Troubleshooting

## Preflight says dependencies are missing

Check the required engines:

- `pandoc` for preferred `.docx`/`.odt` paths.
- `mammoth` or `libreoffice` as fallback `.docx` routes.
- `pymupdf` or `pdfminer` for `.pdf`.
- `libreoffice` for `.doc`, `.odf`, and `.rtf`.

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

If large `.doc`, `.odf`, or `.rtf` files time out:

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

## Windows blocked the packaged app

If Smart App Control or Microsoft Defender blocks `OmniToMarkdown.exe`, the usual cause is that the local PyInstaller build is unsigned and has no publisher reputation yet.

For local development:

1. Run from source with `python -m app.main`.
2. Validate the package with `.\scripts\validate_windows_build.ps1`.
3. Only relax Windows security settings on your own machine if you understand the tradeoff.

For release distribution:

1. Install the Authenticode code-signing certificate in `Cert:\CurrentUser\My`.
2. Set `OMNI_CODE_SIGN_CERT_THUMBPRINT` to the certificate thumbprint.
3. Build and sign with `.\scripts\build_windows.ps1 -Sign`.
4. Run `.\scripts\validate_windows_build.ps1 -RequireSignature`.

Unsigned builds are acceptable for local testing, but they are not release-quality Windows artifacts.
