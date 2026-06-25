$ErrorActionPreference = "Stop"

$sendToShortcut = Join-Path ([Environment]::GetFolderPath("SendTo")) "Omni to Markdown.lnk"

$targetKeys = @(
    "HKCU:\Software\Classes\SystemFileAssociations\.doc\shell\OmniToMarkdown",
    "HKCU:\Software\Classes\SystemFileAssociations\.docx\shell\OmniToMarkdown",
    "HKCU:\Software\Classes\SystemFileAssociations\.htm\shell\OmniToMarkdown",
    "HKCU:\Software\Classes\SystemFileAssociations\.html\shell\OmniToMarkdown",
    "HKCU:\Software\Classes\SystemFileAssociations\.pdf\shell\OmniToMarkdown",
    "HKCU:\Software\Classes\SystemFileAssociations\.odt\shell\OmniToMarkdown",
    "HKCU:\Software\Classes\SystemFileAssociations\.odf\shell\OmniToMarkdown",
    "HKCU:\Software\Classes\SystemFileAssociations\.rtf\shell\OmniToMarkdown",
    "HKCU:\Software\Classes\SystemFileAssociations\.txt\shell\OmniToMarkdown",
    "HKCU:\Software\Classes\Directory\shell\OmniToMarkdown"
)

foreach ($key in $targetKeys) {
    if (Test-Path $key) {
        Remove-Item -LiteralPath $key -Recurse -Force
    }
}

if (Test-Path $sendToShortcut) {
    Remove-Item -LiteralPath $sendToShortcut -Force
}

Write-Host "Removed Omni to Markdown Explorer context-menu entries and SendTo shortcut."
