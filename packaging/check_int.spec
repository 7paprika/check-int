# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project_root = Path(SPEC).resolve().parent.parent
src_root = project_root / 'src'
docs_root = project_root / 'docs'

hiddenimports = collect_submodules('check_int')

a = Analysis(
    [str(src_root / 'check_int' / 'main.py')],
    pathex=[str(src_root)],
    binaries=[],
    datas=[
        (str(docs_root), 'docs'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='check-int',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
