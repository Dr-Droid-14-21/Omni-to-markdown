param(
    [string]$ExecutablePath,
    [switch]$UsePythonLauncher
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$distExe = Join-Path $repoRoot "dist\OmniToMarkdown\OmniToMarkdown.exe"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$launcherScript = Join-Path $repoRoot "scripts\launch_omni.py"
$sendToShortcut = Join-Path ([Environment]::GetFolderPath("SendTo")) "Omni to Markdown.lnk"

function Resolve-LaunchCommand {
    param(
        [string]$ExplicitExecutable,
        [switch]$UsePython
    )

    if ($UsePython) {
        if (-not (Test-Path $pythonExe)) {
            throw "Python launcher requested, but $pythonExe was not found."
        }
        return "`"$pythonExe`" `"$launcherScript`" --convert-now `"%1`""
    }

    if ($ExplicitExecutable) {
        if (-not (Test-Path $ExplicitExecutable)) {
            throw "Executable path not found: $ExplicitExecutable"
        }
        return "`"$ExplicitExecutable`" --convert-now `"%1`""
    }

    if (Test-Path $distExe) {
        return "`"$distExe`" --convert-now `"%1`""
    }

    if (Test-Path $pythonExe) {
        return "`"$pythonExe`" `"$launcherScript`" --convert-now `"%1`""
    }

    throw "No launch target found. Build the Windows app first or pass -ExecutablePath."
}

function Resolve-ShortcutLaunchSpec {
    param(
        [string]$ExplicitExecutable,
        [switch]$UsePython
    )

    if ($UsePython) {
        if (-not (Test-Path $pythonExe)) {
            throw "Python launcher requested, but $pythonExe was not found."
        }
        return [pscustomobject]@{
            TargetPath = $pythonExe
            Arguments = "`"$launcherScript`" --convert-now"
            IconLocation = $pythonExe
        }
    }

    if ($ExplicitExecutable) {
        if (-not (Test-Path $ExplicitExecutable)) {
            throw "Executable path not found: $ExplicitExecutable"
        }
        return [pscustomobject]@{
            TargetPath = $ExplicitExecutable
            Arguments = "--convert-now"
            IconLocation = $ExplicitExecutable
        }
    }

    if (Test-Path $distExe) {
        return [pscustomobject]@{
            TargetPath = $distExe
            Arguments = "--convert-now"
            IconLocation = $distExe
        }
    }

    if (Test-Path $pythonExe) {
        return [pscustomobject]@{
            TargetPath = $pythonExe
            Arguments = "`"$launcherScript`" --convert-now"
            IconLocation = $pythonExe
        }
    }

    throw "No launch target found. Build the Windows app first or pass -ExecutablePath."
}

function Set-OmniVerb {
    param(
        [string]$RegistryPath,
        [string]$CommandText,
        [string]$IconPath
    )

    New-Item -Path $RegistryPath -Force | Out-Null
    Set-Item -Path $RegistryPath -Value "Convert to Markdown with Omni"
    Set-ItemProperty -Path $RegistryPath -Name "Icon" -Value $IconPath

    $commandPath = Join-Path $RegistryPath "command"
    New-Item -Path $commandPath -Force | Out-Null
    Set-Item -Path $commandPath -Value $CommandText
}

function Set-SendToShortcut {
    param(
        [string]$ShortcutPath,
        [string]$TargetPath,
        [string]$Arguments,
        [string]$IconLocation
    )

    $shortcutDir = Split-Path -Parent $ShortcutPath
    New-Item -ItemType Directory -Path $shortcutDir -Force | Out-Null

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($ShortcutPath)
    $shortcut.TargetPath = $TargetPath
    $shortcut.Arguments = $Arguments
    $shortcut.IconLocation = $IconLocation
    $shortcut.Description = "Convert selected files or folders to Markdown with Omni"
    $shortcut.WorkingDirectory = Split-Path -Parent $TargetPath
    $shortcut.Save()
}

$commandText = Resolve-LaunchCommand -ExplicitExecutable $ExecutablePath -UsePython:$UsePythonLauncher
$shortcutSpec = Resolve-ShortcutLaunchSpec -ExplicitExecutable $ExecutablePath -UsePython:$UsePythonLauncher
$iconPath = if ($ExecutablePath) { $ExecutablePath } elseif (Test-Path $distExe) { $distExe } else { $pythonExe }

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
    Set-OmniVerb -RegistryPath $key -CommandText $commandText -IconPath $iconPath
}

Set-SendToShortcut `
    -ShortcutPath $sendToShortcut `
    -TargetPath $shortcutSpec.TargetPath `
    -Arguments $shortcutSpec.Arguments `
    -IconLocation $shortcutSpec.IconLocation

Write-Host "Installed Omni to Markdown Explorer context-menu entries and SendTo shortcut."
