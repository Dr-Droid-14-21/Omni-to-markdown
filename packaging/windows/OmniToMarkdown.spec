# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH).parents[1]
APP_ENTRY = ROOT / "app" / "main.py"
APP_RESOURCES = ROOT / "app" / "resources"

datas = [
    (str(APP_RESOURCES), "app/resources"),
]

hiddenimports = [
    "PySide6.QtMultimedia",
    "fitz",
    "mammoth",
    "markdownify",
    "pdfminer.high_level",
]
hiddenimports += collect_submodules("fitz")
hiddenimports += collect_submodules("pdfminer")

a = Analysis(
    [str(APP_ENTRY)],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="OmniToMarkdown",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="OmniToMarkdown",
)
