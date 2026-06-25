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

function Get-DefaultRegistryValue {
    param(
        [string]$RegistryPath
    )

    if (-not (Test-Path $RegistryPath)) {
        return $null
    }

    return (Get-Item -LiteralPath $RegistryPath).GetValue("")
}

$registryEntries = foreach ($key in $targetKeys) {
    $commandPath = Join-Path $key "command"
    $keyExists = Test-Path $key
    $commandExists = Test-Path $commandPath
    [pscustomobject]@{
        Key = $key
        Installed = $keyExists -and $commandExists
        Label = Get-DefaultRegistryValue $key
        Command = Get-DefaultRegistryValue $commandPath
    }
}

$missingRegistryKeys = @(
    $registryEntries |
        Where-Object { -not $_.Installed } |
        ForEach-Object { $_.Key }
)
$explorerMenuInstalled = $missingRegistryKeys.Count -eq 0
$sendToShortcutInstalled = Test-Path $sendToShortcut

[pscustomobject]@{
    ExplorerMenuInstalled = $explorerMenuInstalled
    SendToShortcutInstalled = $sendToShortcutInstalled
    Complete = $explorerMenuInstalled -and $sendToShortcutInstalled
    MissingRegistryKeys = $missingRegistryKeys
    SendToShortcut = $sendToShortcut
    RegistryEntries = $registryEntries
} | ConvertTo-Json -Depth 5
