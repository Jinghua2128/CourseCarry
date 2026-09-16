[CmdletBinding()]
param(
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"

function Get-Sha256Hex {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    $stream = [System.IO.File]::OpenRead($LiteralPath)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $algorithm.Dispose()
        $stream.Dispose()
    }
}

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$versionFile = Join-Path $projectRoot "coursecarry\version.py"
$versionMatch = Select-String -LiteralPath $versionFile -Pattern '__version__\s*=\s*"([^"]+)"'
if (-not $versionMatch) {
    throw "Could not read the application version from coursecarry\version.py."
}
$applicationVersion = $versionMatch.Matches[0].Groups[1].Value
if (-not $Version) {
    $Version = $applicationVersion
}
if ($Version -notmatch '^\d+\.\d+\.\d+-alpha$') {
    throw "Version must use the form x.y.z-alpha, for example 0.6.3-alpha."
}
if ($Version -ne $applicationVersion) {
    throw "Release version '$Version' does not match application version '$applicationVersion'."
}
$sourceDirectory = Join-Path $projectRoot "dist\CourseCarry"
$releaseDirectory = Join-Path $projectRoot "release"
$archivePath = Join-Path $releaseDirectory "CourseCarry-v$Version-windows-x64.zip"
$checksumPath = "$archivePath.sha256"

if (-not (Test-Path -LiteralPath (Join-Path $sourceDirectory "CourseCarry.exe"))) {
    throw "Missing dist\CourseCarry\CourseCarry.exe. Run build_exe.bat first."
}

& (Join-Path $PSScriptRoot "verify_windows_bundle.ps1")

New-Item -ItemType Directory -Path $releaseDirectory -Force | Out-Null
if (Test-Path -LiteralPath $archivePath) {
    Remove-Item -LiteralPath $archivePath -Force
}
if (Test-Path -LiteralPath $checksumPath) {
    Remove-Item -LiteralPath $checksumPath -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$stagingDirectory = Join-Path $releaseDirectory ".staging-v$Version"
$resolvedReleasePrefix = [System.IO.Path]::GetFullPath($releaseDirectory).TrimEnd('\') + '\'
$resolvedStagingDirectory = [System.IO.Path]::GetFullPath($stagingDirectory)
if (-not $resolvedStagingDirectory.StartsWith($resolvedReleasePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to stage outside the release directory."
}
if (Test-Path -LiteralPath $stagingDirectory) {
    Remove-Item -LiteralPath $stagingDirectory -Recurse -Force
}

try {
    $stagedAppDirectory = Join-Path $stagingDirectory "CourseCarry"
    New-Item -ItemType Directory -Path $stagedAppDirectory -Force | Out-Null
    Copy-Item -Path (Join-Path $sourceDirectory "*") -Destination $stagedAppDirectory -Recurse -Force
    [System.IO.Compression.ZipFile]::CreateFromDirectory($stagingDirectory, $archivePath, [System.IO.Compression.CompressionLevel]::Optimal, $false)
}
finally {
    if (Test-Path -LiteralPath $stagingDirectory) {
        Remove-Item -LiteralPath $stagingDirectory -Recurse -Force
    }
}

$archive = [System.IO.Compression.ZipFile]::OpenRead($archivePath)
try {
    $entryNames = @($archive.Entries | ForEach-Object { $_.FullName.Replace("\", "/") })
    if ($entryNames -notcontains "CourseCarry/CourseCarry.exe") {
        throw "Release archive is missing CourseCarry/CourseCarry.exe."
    }
    $requiredEntries = @(
    "CourseCarry/python311.dll",
        "CourseCarry/PySide6/QtGui.pyd",
        "CourseCarry/qt6gui.dll",
    "CourseCarry/playwright/driver/node.exe",
    "CourseCarry/CourseCarry-Diagnostic.cmd",
    "CourseCarry/CourseCarry-Diagnostic.ps1",
        "CourseCarry/MSVCP140.dll",
        "CourseCarry/MSVCP140_1.dll",
        "CourseCarry/MSVCP140_2.dll",
        "CourseCarry/VCRUNTIME140.dll",
        "CourseCarry/VCRUNTIME140_1.dll"
    )
    foreach ($requiredEntry in $requiredEntries) {
        if ($entryNames -notcontains $requiredEntry) {
            throw "Release archive is missing $requiredEntry."
        }
    }

    $privatePattern = '(?i)(^|/)(chrome-profile|browser-data|archive|downloads|logs|data)(/|$)|(^|/)(config\.json|\.env|cookies?\.json)$|\.(db|db-wal|db-shm|log|part)$'
    $privateEntries = @($entryNames | Where-Object { $_ -match $privatePattern })
    if ($privateEntries.Count -gt 0) {
        throw "Private or runtime data found in release archive:`n$($privateEntries -join "`n")"
    }
}
finally {
    $archive.Dispose()
}

$hash = Get-Sha256Hex -LiteralPath $archivePath
Set-Content -LiteralPath $checksumPath -Value "$hash  $([System.IO.Path]::GetFileName($archivePath))" -Encoding ascii

Write-Output "Created: $archivePath"
Write-Output "SHA256: $hash"
Write-Output "Privacy audit: passed"
