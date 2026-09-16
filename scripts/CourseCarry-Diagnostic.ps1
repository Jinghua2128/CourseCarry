[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$bundleRoot = $PSScriptRoot
$reportDirectory = Join-Path $env:LOCALAPPDATA "CourseCarry"
$reportPath = Join-Path $reportDirectory "startup-diagnostic.txt"
New-Item -ItemType Directory -Path $reportDirectory -Force | Out-Null

if (-not ("CourseCarry.NativeLoader" -as [type])) {
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

namespace CourseCarry {
    public static class NativeLoader {
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        public static extern IntPtr LoadLibraryEx(string fileName, IntPtr fileHandle, uint flags);

        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool FreeLibrary(IntPtr module);
    }
}
"@
}

$windows = Get-ItemProperty -LiteralPath "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion"
$displayVersion = if ($windows.DisplayVersion) { $windows.DisplayVersion } else { $windows.ReleaseId }
$build = "$($windows.CurrentBuildNumber).$($windows.UBR)"
$architecture = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
$executablePath = Join-Path $bundleRoot "CourseCarry.exe"
$applicationVersion = if (Test-Path -LiteralPath $executablePath -PathType Leaf) {
    (Get-Item -LiteralPath $executablePath).VersionInfo.ProductVersion
}
else {
    "missing"
}

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add("CourseCarry startup diagnostic")
$lines.Add("Created UTC: $([DateTime]::UtcNow.ToString('o'))")
$lines.Add("CourseCarry executable version: $applicationVersion")
$lines.Add("OS: $($windows.ProductName) $displayVersion build $build")
$lines.Add("Architecture: $architecture")
$lines.Add("")
$lines.Add("Native probes:")

$handles = [System.Collections.Generic.List[IntPtr]]::new()
$loadWithAlteredSearchPath = 0x00000008
$nativeFiles = @(
    "MSVCP140.dll",
    "MSVCP140_1.dll",
    "MSVCP140_2.dll",
    "VCRUNTIME140.dll",
    "VCRUNTIME140_1.dll",
    "python311.dll",
    "shiboken6.abi3.dll",
    "pyside6.abi3.dll",
    "qt6core.dll",
    "qt6gui.dll",
    "PySide6\QtGui.pyd",
    "PySide6\qt-plugins\platforms\qwindows.dll"
)

try {
    foreach ($relativeName in $nativeFiles) {
        $candidate = Join-Path $bundleRoot $relativeName
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            $lines.Add("- ${relativeName}: missing")
            continue
        }

        $handle = [CourseCarry.NativeLoader]::LoadLibraryEx(
            $candidate,
            [IntPtr]::Zero,
            $loadWithAlteredSearchPath
        )
        if ($handle -eq [IntPtr]::Zero) {
            $errorCode = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
            $lines.Add("- ${relativeName}: failed (WinError $errorCode)")
        }
        else {
            $handles.Add($handle)
            $lines.Add("- ${relativeName}: loaded")
        }
    }
}
finally {
    for ($index = $handles.Count - 1; $index -ge 0; $index--) {
        [void][CourseCarry.NativeLoader]::FreeLibrary($handles[$index])
    }
}

$qtGuiPath = Join-Path $bundleRoot "qt6gui.dll"
if (Test-Path -LiteralPath $qtGuiPath -PathType Leaf) {
    $qtVersion = (Get-Item -LiteralPath $qtGuiPath).VersionInfo.ProductVersion
    $qtAscii = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($qtGuiPath))
    $hasDirectD3D12Reference = $qtAscii.IndexOf(
        "d3d12.dll",
        [StringComparison]::OrdinalIgnoreCase
    ) -ge 0
    $lines.Add("")
    $lines.Add("QtGui version: $qtVersion")
    $lines.Add("QtGui direct D3D12 reference: $hasDirectD3D12Reference")
}

$lines.Add("")
$lines.Add("This report intentionally excludes usernames, paths, course data, browser data, and credentials.")
[IO.File]::WriteAllText($reportPath, ($lines -join [Environment]::NewLine) + [Environment]::NewLine)

Write-Output "Created: $reportPath"
