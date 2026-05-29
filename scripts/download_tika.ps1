param(
    [string]$Version = "3.2.3"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$targetDir = Join-Path $repoRoot "tools\tika"
$jarName = "tika-app-$Version.jar"
$jarPath = Join-Path $targetDir $jarName
$shaPath = "$jarPath.sha512"
$baseUrl = "https://archive.apache.org/dist/tika/$Version"

New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

Invoke-WebRequest -Uri "$baseUrl/$jarName" -OutFile $jarPath
Invoke-WebRequest -Uri "$baseUrl/$jarName.sha512" -OutFile $shaPath

$expected = (Get-Content $shaPath -Raw).Trim().Split(" ")[0].ToLowerInvariant()
$actual = (Get-FileHash -Algorithm SHA512 $jarPath).Hash.ToLowerInvariant()
if ($actual -ne $expected) {
    Remove-Item -LiteralPath $jarPath -Force
    throw "Apache Tika checksum verification failed."
}

Write-Host "Downloaded and verified $jarPath"
