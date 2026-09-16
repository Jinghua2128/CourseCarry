[CmdletBinding()]
param(
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$python = if ($PythonPath) { $PythonPath } else { Join-Path $projectRoot ".venv\Scripts\python.exe" }
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Missing Python build environment. Run setup_windows.bat first."
}
$python = (Resolve-Path -LiteralPath $python).Path
$pythonVersion = & $python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($LASTEXITCODE -ne 0 -or $pythonVersion -ne "3.11") {
    throw "The Windows release must be built with Python 3.11; found '$pythonVersion'."
}
$qtVersion = & $python -c "from PySide6.QtCore import qVersion; print(qVersion())"
if ($LASTEXITCODE -ne 0 -or $qtVersion -ne "6.5.3") {
    throw "The Windows release must be built with PySide6/Qt 6.5.3; found '$qtVersion'."
}

$versionFile = Join-Path $projectRoot "coursecarry\version.py"
$versionMatch = Select-String -LiteralPath $versionFile -Pattern '__version__\s*=\s*"(\d+)\.(\d+)\.(\d+)-alpha"'
if (-not $versionMatch) {
    throw "Could not read an alpha application version from coursecarry\version.py."
}
$groups = $versionMatch.Matches[0].Groups
$fileVersion = "$($groups[1].Value).$($groups[2].Value).$($groups[3].Value).0"

$nuitkaRoot = Join-Path $projectRoot "build\nuitka"
$env:NUITKA_CACHE_DIR = Join-Path $projectRoot "build\nuitka-cache"
New-Item -ItemType Directory -Path $nuitkaRoot -Force | Out-Null

$nuitkaArguments = @(
    "-m", "nuitka",
    "--mode=standalone",
    "--enable-plugin=pyside6",
    "--windows-console-mode=disable",
    "--windows-icon-from-ico=coursecarry\resources\coursecarry-icon.ico",
    "--include-data-files=coursecarry\resources\coursecarry-icon.png=coursecarry/resources/coursecarry-icon.png",
    "--include-package=playwright",
    "--include-windows-runtime-dlls=yes",
    "--assume-yes-for-downloads",
    "--output-dir=$nuitkaRoot",
    "--output-filename=CourseCarry.exe",
    "--file-version=$fileVersion",
    "--product-version=$fileVersion",
    "--product-name=CourseCarry",
    "--file-description=CourseCarry student backup utility",
    "--report=$nuitkaRoot\compilation-report.xml",
    "main.py"
)

Push-Location $projectRoot
try {
    & $python @nuitkaArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Nuitka failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

$compiledDirectory = Join-Path $nuitkaRoot "main.dist"
$distParent = Join-Path $projectRoot "dist"
$bundleDirectory = Join-Path $distParent "CourseCarry"
if (-not (Test-Path -LiteralPath (Join-Path $compiledDirectory "CourseCarry.exe") -PathType Leaf)) {
    throw "Nuitka did not create the expected standalone directory."
}

$resolvedProjectPrefix = [System.IO.Path]::GetFullPath($projectRoot).TrimEnd('\') + '\'
$resolvedBundleDirectory = [System.IO.Path]::GetFullPath($bundleDirectory)
if (-not $resolvedBundleDirectory.StartsWith($resolvedProjectPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to replace a bundle outside the project."
}

New-Item -ItemType Directory -Path $distParent -Force | Out-Null
if (Test-Path -LiteralPath $bundleDirectory) {
    Remove-Item -LiteralPath $bundleDirectory -Recurse -Force
}
Copy-Item -LiteralPath $compiledDirectory -Destination $bundleDirectory -Recurse -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "CourseCarry-Diagnostic.cmd") -Destination $bundleDirectory -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "CourseCarry-Diagnostic.ps1") -Destination $bundleDirectory -Force

& (Join-Path $PSScriptRoot "verify_windows_bundle.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Windows bundle verification failed with exit code $LASTEXITCODE."
}

$previousPath = $env:PATH
try {
    $env:PATH = "$env:SystemRoot\System32"
    $selfTestProcess = Start-Process `
        -FilePath (Join-Path $bundleDirectory "CourseCarry.exe") `
        -ArgumentList "--bundle-self-test" `
        -WorkingDirectory $bundleDirectory `
        -WindowStyle Hidden `
        -Wait `
        -PassThru
    if ($selfTestProcess.ExitCode -ne 0) {
        throw "The packaged Qt and Playwright self-test failed with exit code $($selfTestProcess.ExitCode)."
    }
}
finally {
    $env:PATH = $previousPath
}

Write-Output "Build complete: dist\CourseCarry\CourseCarry.exe"
Write-Output "Packaged Qt and Playwright self-test: passed"
Write-Output "Compatibility runtime: Python $pythonVersion with Qt $qtVersion"
