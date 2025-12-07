# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import os

# Collect all files from assets folder recursively
def collect_assets():
    assets_data = []
    assets_path = './assets'
    
    for root, dirs, files in os.walk(assets_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Get the relative directory path from assets
            rel_dir = os.path.relpath(root, '.')
            assets_data.append((file_path, rel_dir))
    
    return assets_data

a = Analysis(
    ['main.py'],
    pathex=['.'],  # Include current directory
    binaries=[],
    datas=[
        # Include entire assets folder recursively
        ('./assets', 'assets'),
        # Include other folders
        ('./downloader/', 'downloader'),
        ('./ui/', 'ui'),
    ],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='YouVideoDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icons/appicon.ico'],  # Optional
    version='version.txt'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YouVideoDownloader'
)