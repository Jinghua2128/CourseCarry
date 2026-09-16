# CourseCarry's PyInstaller build was retired after clean-device Qt runtime
# failures.  Keep this guard so an old command cannot silently create a release
# with the known-bad layout.  Use build_exe.bat, which runs the verified Nuitka
# standalone build in scripts/build_windows.ps1.
raise SystemExit("PyInstaller packaging is retired; run build_exe.bat instead.")
