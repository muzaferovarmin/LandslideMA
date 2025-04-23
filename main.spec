# main.spec

# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files,collect_submodules

block_cipher = None
icon = "home/armin/Downloads/icon.png"
hidden_imports = [
    "rasterio.sample",
    "rasterio._base",
    "rasterio.vrt",
    "rasterio.shutil",
    "rasterio._features",
    "PIL._tkinter_finder",
]
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('exp','exp')],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LandslidePipeline',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    icon='/home/armin/Downloads/icon.png',
    console=True,  # Change to False if this is a GUI-only app
)

