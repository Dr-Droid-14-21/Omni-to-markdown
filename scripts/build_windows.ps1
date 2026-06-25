param(
    [switch]$SkipValidation,
    [switch]$Sign,
    [switch]$RequireSignature,
    [string]$CertificateThumbprint = $env:OMNI_CODE_SIGN_CERT_THUMBPRINT,
    [string]$TimestampServer = $(if ($env:OMNI_CODE_SIGN_TIMESTAMP_SERVER) { $env:OMNI_CODE_SIGN_TIMESTAMP_SERVER } else { "http://timestamp.digicert.com" })
)

$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

$exePath = Join-Path (Get-Location) "dist\OmniToMarkdown\OmniToMarkdown.exe"
$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
$pythonExe = if (Test-Path $venvPython) { $venvPython } else { "python" }

function Invoke-ProjectPython {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & $pythonExe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE`: $pythonExe $($Arguments -join ' ')"
    }
}

function Invoke-CodeSigning {
    param(
        [string]$TargetPath,
        [string]$Thumbprint,
        [string]$TimestampUrl
    )

    if (-not (Test-Path $TargetPath)) {
        throw "Cannot sign missing executable: $TargetPath"
    }
    if (-not $Thumbprint) {
        throw "Code signing requested, but no certificate thumbprint was provided. Set OMNI_CODE_SIGN_CERT_THUMBPRINT or pass -CertificateThumbprint."
    }

    $normalizedThumbprint = $Thumbprint -replace '\s', ''
    $certificatePath = "Cert:\CurrentUser\My\$normalizedThumbprint"
    if (-not (Test-Path $certificatePath)) {
        throw "Code signing certificate was not found in CurrentUser\My: $normalizedThumbprint"
    }

    $certificate = Get-Item $certificatePath
    $signature = Set-AuthenticodeSignature -FilePath $TargetPath -Certificate $certificate -TimestampServer $TimestampUrl
    if ($signature.Status -ne "Valid") {
        throw "Code signing failed: $($signature.Status) $($signature.StatusMessage)"
    }

    Write-Host "Signed $TargetPath with certificate thumbprint $normalizedThumbprint."
}

Invoke-ProjectPython -Arguments @("-m", "pip", "install", "-e", ".[dev]")
Invoke-ProjectPython -Arguments @(
    "-m",
    "pip",
    "install",
    "mammoth",
    "markdownify",
    "pymupdf",
    "pdfminer.six"
)
Invoke-ProjectPython -Arguments @(
    "-m",
    "PyInstaller",
    "--clean",
    "--noconfirm",
    "packaging/windows/OmniToMarkdown.spec"
)

if ($Sign) {
    Invoke-CodeSigning -TargetPath $exePath -Thumbprint $CertificateThumbprint -TimestampUrl $TimestampServer
}

if (-not $SkipValidation) {
    if ($Sign -or $RequireSignature) {
        & (Join-Path $PSScriptRoot "validate_windows_build.ps1") -ExecutablePath $exePath -RequireSignature
    } else {
        & (Join-Path $PSScriptRoot "validate_windows_build.ps1") -ExecutablePath $exePath
    }
}
