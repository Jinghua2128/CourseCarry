# -*- mode: python ; coding: utf-8 -*-

analysis = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("coursecarry/resources/coursecarry-icon.png", "coursecarry/resources")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="CourseCarry",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=["coursecarry/resources/coursecarry-icon.ico"],
)

collection = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    name="CourseCarry",
)
