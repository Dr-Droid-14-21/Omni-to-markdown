param(
    [string]$ExecutablePath,
    [switch]$RequireSignature
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$defaultExe = Join-Path $repoRoot "dist\OmniToMarkdown\OmniToMarkdown.exe"
$exePath = if ($ExecutablePath) { $ExecutablePath } else { $defaultExe }
$checkScript = Join-Path $repoRoot "scripts\check_windows_context_menu.ps1"
$registerScript = Join-Path $repoRoot "scripts\register_windows_context_menu.ps1"
$unregisterScript = Join-Path $repoRoot "scripts\unregister_windows_context_menu.ps1"
$fileDetectionModule = Join-Path $repoRoot "app\core\file_detection.py"

function Add-Check {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$Name,
        [bool]$Passed,
        [string]$Detail
    )

    $Checks.Add([pscustomobject]@{
        Name = $Name
        Passed = $Passed
        Detail = $Detail
    }) | Out-Null
}

function Test-ScriptSyntax {
    param(
        [string]$ScriptPath
    )

    if (-not (Test-Path $ScriptPath)) {
        return [pscustomobject]@{
            Passed = $false
            Detail = "Script missing: $ScriptPath"
        }
    }

    $tokens = $null
    $errors = $null
    $null = [System.Management.Automation.Language.Parser]::ParseFile(
        $ScriptPath,
        [ref]$tokens,
        [ref]$errors
    )

    if ($errors.Count -gt 0) {
        return [pscustomobject]@{
            Passed = $false
            Detail = ($errors | ForEach-Object { $_.Message }) -join "`n"
        }
    }

    return [pscustomobject]@{
        Passed = $true
        Detail = $ScriptPath
    }
}

function Get-SupportedExtensionsFromPython {
    param(
        [string]$ModulePath
    )

    if (-not (Test-Path $ModulePath)) {
        throw "Supported extension module missing: $ModulePath"
    }

    $content = Get-Content -LiteralPath $ModulePath -Raw
    $match = [regex]::Match($content, 'SUPPORTED_EXTENSIONS\s*=\s*\{(?<body>.*?)\}', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    if (-not $match.Success) {
        throw "Could not find SUPPORTED_EXTENSIONS in $ModulePath"
    }

    $extensions = [regex]::Matches($match.Groups["body"].Value, '"(?<extension>\.[a-z0-9]+)"') |
        ForEach-Object { $_.Groups["extension"].Value } |
        Sort-Object -Unique
    return @($extensions)
}

function Get-ContextMenuExtensionsFromScript {
    param(
        [string]$ScriptPath
    )

    if (-not (Test-Path $ScriptPath)) {
        return @()
    }

    $content = Get-Content -LiteralPath $ScriptPath -Raw
    $extensions = [regex]::Matches($content, 'SystemFileAssociations\\(?<extension>\.[a-z0-9]+)\\shell\\OmniToMarkdown') |
        ForEach-Object { $_.Groups["extension"].Value } |
        Sort-Object -Unique
    return @($extensions)
}

function Test-ContextMenuCoverage {
    param(
        [string]$ScriptPath,
        [string[]]$ExpectedExtensions
    )

    if (-not (Test-Path $ScriptPath)) {
        return [pscustomobject]@{
            Passed = $false
            Detail = "Script missing: $ScriptPath"
        }
    }

    $content = Get-Content -LiteralPath $ScriptPath -Raw
    $actualExtensions = Get-ContextMenuExtensionsFromScript $ScriptPath
    $missing = @($ExpectedExtensions | Where-Object { $_ -notin $actualExtensions })
    $extra = @($actualExtensions | Where-Object { $_ -notin $ExpectedExtensions })
    $hasDirectoryKey = $content -match 'Classes\\Directory\\shell\\OmniToMarkdown'

    if ($missing.Count -gt 0 -or $extra.Count -gt 0 -or -not $hasDirectoryKey) {
        $issues = @()
        if ($missing.Count -gt 0) {
            $issues += "Missing extensions: $($missing -join ', ')"
        }
        if ($extra.Count -gt 0) {
            $issues += "Unexpected extensions: $($extra -join ', ')"
        }
        if (-not $hasDirectoryKey) {
            $issues += "Missing directory context-menu key."
        }
        return [pscustomobject]@{
            Passed = $false
            Detail = $issues -join " "
        }
    }

    return [pscustomobject]@{
        Passed = $true
        Detail = $actualExtensions -join ", "
    }
}

function Test-SendToShortcutSupport {
    param(
        [string]$ScriptPath,
        [switch]$RemoveScript
    )

    if (-not (Test-Path $ScriptPath)) {
        return [pscustomobject]@{
            Passed = $false
            Detail = "Script missing: $ScriptPath"
        }
    }

    $content = Get-Content -LiteralPath $ScriptPath -Raw
    $hasShortcutName = $content -match 'Omni to Markdown\.lnk'
    $hasExpectedAction = if ($RemoveScript) {
        $content -match 'Remove-Item'
    } else {
        $content -match 'CreateShortcut'
    }

    return [pscustomobject]@{
        Passed = $hasShortcutName -and $hasExpectedAction
        Detail = if ($hasShortcutName -and $hasExpectedAction) {
            $ScriptPath
        } else {
            "SendTo shortcut support is incomplete."
        }
    }
}

$checks = [System.Collections.Generic.List[object]]::new()

$exeExists = Test-Path $exePath
Add-Check $checks "Packaged executable exists" $exeExists $exePath

if ($exeExists) {
    $selfCheckHome = Join-Path $repoRoot (".omni-self-check-" + [System.Guid]::NewGuid().ToString("N"))
    $selfCheckReport = Join-Path $selfCheckHome "self-check.json"
    $previousAppHome = $env:OMNI_TO_MARKDOWN_HOME
    $previousSelfCheckReport = $env:OMNI_SELF_CHECK_REPORT
    $env:OMNI_TO_MARKDOWN_HOME = $selfCheckHome
    $env:OMNI_SELF_CHECK_REPORT = $selfCheckReport
    $selfCheckProcess = Start-Process -FilePath $exePath -ArgumentList "--self-check" -Wait -PassThru -WindowStyle Hidden
    $selfCheckExit = $selfCheckProcess.ExitCode
    if ($null -eq $previousAppHome) {
        Remove-Item Env:\OMNI_TO_MARKDOWN_HOME -ErrorAction SilentlyContinue
    } else {
        $env:OMNI_TO_MARKDOWN_HOME = $previousAppHome
    }
    if ($null -eq $previousSelfCheckReport) {
        Remove-Item Env:\OMNI_SELF_CHECK_REPORT -ErrorAction SilentlyContinue
    } else {
        $env:OMNI_SELF_CHECK_REPORT = $previousSelfCheckReport
    }
    $selfCheckDetail = if (Test-Path $selfCheckReport) {
        Get-Content -LiteralPath $selfCheckReport -Raw
    } else {
        "Self-check did not produce a report file."
    }
    Remove-Item -LiteralPath $selfCheckHome -Recurse -Force -ErrorAction SilentlyContinue
    Add-Check $checks "Packaged executable self-check" ($selfCheckExit -eq 0) $selfCheckDetail

    $signature = Get-AuthenticodeSignature -FilePath $exePath
    $signaturePassed = if ($RequireSignature) { $signature.Status -eq "Valid" } else { $true }
    Add-Check $checks "Authenticode signature present" $signaturePassed $signature.Status
} else {
    Add-Check $checks "Packaged executable self-check" $false "Executable missing."
    Add-Check $checks "Authenticode signature present" (-not $RequireSignature) "Executable missing."
}

Add-Check $checks "Register context-menu script exists" (Test-Path $registerScript) $registerScript
Add-Check $checks "Unregister context-menu script exists" (Test-Path $unregisterScript) $unregisterScript
Add-Check $checks "Check context-menu script exists" (Test-Path $checkScript) $checkScript

$checkSyntax = Test-ScriptSyntax $checkScript
$registerSyntax = Test-ScriptSyntax $registerScript
$unregisterSyntax = Test-ScriptSyntax $unregisterScript
Add-Check $checks "Check context-menu script syntax" $checkSyntax.Passed $checkSyntax.Detail
Add-Check $checks "Register context-menu script syntax" $registerSyntax.Passed $registerSyntax.Detail
Add-Check $checks "Unregister context-menu script syntax" $unregisterSyntax.Passed $unregisterSyntax.Detail

$registerSendTo = Test-SendToShortcutSupport $registerScript
$unregisterSendTo = Test-SendToShortcutSupport $unregisterScript -RemoveScript
Add-Check $checks "Register SendTo shortcut support" $registerSendTo.Passed $registerSendTo.Detail
Add-Check $checks "Unregister SendTo shortcut support" $unregisterSendTo.Passed $unregisterSendTo.Detail

try {
    $supportedExtensions = Get-SupportedExtensionsFromPython $fileDetectionModule
    $checkCoverage = Test-ContextMenuCoverage $checkScript $supportedExtensions
    $registerCoverage = Test-ContextMenuCoverage $registerScript $supportedExtensions
    $unregisterCoverage = Test-ContextMenuCoverage $unregisterScript $supportedExtensions
    Add-Check $checks "Check context-menu extension coverage" $checkCoverage.Passed $checkCoverage.Detail
    Add-Check $checks "Register context-menu extension coverage" $registerCoverage.Passed $registerCoverage.Detail
    Add-Check $checks "Unregister context-menu extension coverage" $unregisterCoverage.Passed $unregisterCoverage.Detail
} catch {
    Add-Check $checks "Context-menu extension coverage" $false $_.Exception.Message
}

$failed = @($checks | Where-Object { -not $_.Passed })
$checks | Format-Table -AutoSize

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "Windows build validation found issues:" -ForegroundColor Yellow
    foreach ($item in $failed) {
        Write-Host "- $($item.Name): $($item.Detail)" -ForegroundColor Yellow
    }
    exit 1
}

Write-Host ""
Write-Host "Windows build validation passed." -ForegroundColor Green
