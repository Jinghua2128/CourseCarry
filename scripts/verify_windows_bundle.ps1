[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Get-Sha256Hex {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    $stream = [System.IO.File]::OpenRead($LiteralPath)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace("-", "")
    }
    finally {
        $algorithm.Dispose()
        $stream.Dispose()
    }
}

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$bundleRoot = Join-Path $projectRoot "dist\CourseCarry"
$requiredFiles = @(
    (Join-Path $bundleRoot "CourseCarry.exe"),
    (Join-Path $bundleRoot "python311.dll"),
    (Join-Path $bundleRoot "shiboken6.abi3.dll"),
    (Join-Path $bundleRoot "pyside6.abi3.dll"),
    (Join-Path $bundleRoot "PySide6\QtGui.pyd"),
    (Join-Path $bundleRoot "PySide6\qt-plugins\platforms\qwindows.dll"),
    (Join-Path $bundleRoot "qt6gui.dll"),
    (Join-Path $bundleRoot "playwright\driver\node.exe"),
    (Join-Path $bundleRoot "coursecarry\resources\coursecarry-icon.png"),
    (Join-Path $bundleRoot "CourseCarry-Diagnostic.cmd"),
    (Join-Path $bundleRoot "CourseCarry-Diagnostic.ps1")
)
$runtimeNames = @(
    "MSVCP140.dll",
    "MSVCP140_1.dll",
    "MSVCP140_2.dll",
    "VCRUNTIME140.dll",
    "VCRUNTIME140_1.dll"
)

foreach ($path in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Windows bundle is missing required file: $path"
    }
}

foreach ($name in $runtimeNames) {
    if (-not (Test-Path -LiteralPath (Join-Path $bundleRoot $name) -PathType Leaf)) {
        throw "Windows bundle is missing the application runtime dependency: $name"
    }
}

$hostOperatingSystemDlls = @(
    Get-ChildItem -LiteralPath $bundleRoot -Recurse -File |
        Where-Object { $_.Name -like "api-ms-win-*.dll" -or $_.Name -ieq "ucrtbase.dll" }
)
if ($hostOperatingSystemDlls.Count -gt 0) {
    $relativeNames = $hostOperatingSystemDlls | ForEach-Object {
        $_.FullName.Substring($bundleRoot.Length + 1)
    }
    throw "The bundle contains host operating-system DLLs that can break older supported Windows builds:`n$($relativeNames -join "`n")"
}

$qtGuiPath = Join-Path $bundleRoot "qt6gui.dll"
$qtGuiVersion = (Get-Item -LiteralPath $qtGuiPath).VersionInfo.ProductVersion
if ($qtGuiVersion -notlike "6.5.3*") {
    throw "The bundle has QtGui version '$qtGuiVersion'; expected the Windows-compatible 6.5.3 line."
}
$qtGuiAscii = [System.Text.Encoding]::ASCII.GetString([System.IO.File]::ReadAllBytes($qtGuiPath))
if ($qtGuiAscii.IndexOf("d3d12.dll", [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
    throw "The bundled QtGui directly references d3d12.dll; this reintroduces the affected-laptop compatibility risk."
}

Write-Output "Windows bundle verification: passed"
Write-Output "QtGui compatibility line: $qtGuiVersion"
Write-Output "Direct D3D12 dependency audit: passed"
Write-Output "Application-local C++ runtime: $($runtimeNames -join ', ')"
Write-Output "Host operating-system DLL audit: passed"
