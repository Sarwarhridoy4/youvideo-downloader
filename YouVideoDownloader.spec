# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=['.'],  # Include current directory
    binaries=[],
    datas=[
        ('./assets/qss/light.qss', 'assets/qss'),
        ('./assets/qss/dark.qss', 'assets/qss'),
        ('./assets/qss/welcome.qss', 'assets/qss'),
        ('./assets/icons/appicon.png', 'assets/icons'),
        ('./assets/icons/spinner.gif', 'assets/icons'),
        ('./assets/screenshot/', 'assets/screenshot'),
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
