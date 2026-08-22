# -*- mode: python ; coding: utf-8 -*-

analysis = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("politeload/resources/politeload-icon.png", "politeload/resources")],
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
    name="PoliteLoad",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=["politeload/resources/politeload-icon.ico"],
)

collection = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    name="PoliteLoad",
)
