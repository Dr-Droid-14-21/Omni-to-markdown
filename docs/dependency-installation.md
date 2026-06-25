# Dependency Installation

## Python Runtime

Use Python 3.12 for development and Windows packaging.

```powershell
uv python install 3.12
uv venv .venv --python 3.12
.venv\Scripts\activate
python -m pip install -e .[dev]
```

Alternative with python.org:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

## Python Conversion Packages

```powershell
python -m pip install mammoth markdownify pymupdf pdfminer.six
```

These enable:

- `mammoth`: DOCX semantic extraction fallback.
- `markdownify`: local HTML-to-Markdown bridge for `.htm` and `.html`.
- `pymupdf`: primary PDF text extraction.
- `pdfminer.six`: PDF fallback extraction.

## Apache Tika Keyword Search

Used for keyword search inside `.doc`, `.docx`, `.htm`, `.html`, `.odt`, `.odf`, `.pdf`, and `.rtf` files.
HTML conversion itself does not require Tika.
Plain text conversion and search for `.txt` files do not require external tools.
The app uses the Apache-2.0 licensed Tika app jar and runs it through Java.

Install Java 17+ or newer, then download Tika:

```powershell
.\scripts\download_tika.ps1
java -version
```

The script downloads `tools\tika\tika-app-3.2.3.jar` and verifies its SHA-512 checksum.
If Java or Tika live outside the default locations, set their paths in `File -> Settings`.

## Windows External Tools

Install these if you need the full conversion matrix:

- Pandoc: [https://pandoc.org/installing.html](https://pandoc.org/installing.html)
- LibreOffice: [https://www.libreoffice.org/download/download-libreoffice/](https://www.libreoffice.org/download/download-libreoffice/) for `.doc`, `.odf`, and `.rtf` conversion routes.
- Apache Tika: [https://tika.apache.org/](https://tika.apache.org/)

If they are not on `PATH`, set their executable paths in `File -> Settings`.

## Windows Packaging

```powershell
.\scripts\build_windows.ps1
```

The build script uses:

- `packaging/windows/OmniToMarkdown.spec`
- PyInstaller onedir output under `dist/OmniToMarkdown/`
- bundled app resources from `app/resources/`

Pandoc and LibreOffice are detected as external tools; they are not bundled by the current spec.
The Tika jar is included in the Windows onedir build when `tools/tika/tika-app-3.2.3.jar`
exists before packaging.

For release builds, install your Authenticode certificate in `Cert:\CurrentUser\My`
and sign by certificate thumbprint:

```powershell
$env:OMNI_CODE_SIGN_CERT_THUMBPRINT = "YOUR_CERT_THUMBPRINT"
.\scripts\build_windows.ps1 -Sign
```

You can override the timestamp service with `OMNI_CODE_SIGN_TIMESTAMP_SERVER` or
the `-TimestampServer` parameter. The build script intentionally signs from the
Windows certificate store; it does not accept PFX passwords on the command line.

Validate a completed Windows build:

```powershell
.\scripts\validate_windows_build.ps1
```

Require Authenticode signing during validation:

```powershell
.\scripts\validate_windows_build.ps1 -RequireSignature
```

## Linux Development

Install Python dependencies as above, then install external tools with your distro package manager.

Ubuntu/Debian example:

```bash
sudo apt update
sudo apt install pandoc libreoffice
python -m pip install -e .[dev]
python -m pip install mammoth markdownify pymupdf pdfminer.six
```
