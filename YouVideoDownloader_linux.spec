# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Styles
        ('assets/qss/light.qss', 'assets/qss'),
        ('assets/qss/dark.qss', 'assets/qss'),
        ('assets/qss/welcome.qss', 'assets/qss'),
        
        # Icons & GIFs
        ('assets/icons', 'assets/icons'),               # ← BEST: copy whole folder
        # ('assets/icons/appicon.png', 'assets/icons'), # ← no need anymore
        # ('assets/icons/spinner.gif', 'assets/icons'), # ← included above
        
        # Screenshots (whole folder)
        ('assets/screenshot', 'assets/screenshot'),
        
        # Your Python packages
        ('downloader', 'downloader'),
        ('ui', 'ui'),
        ('utils', 'utils'),                             # ← you probably have this too
    ],
    hiddenimports=[
        # Add these only if you get "ModuleNotFoundError" during build/test
        # 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',  # usually auto-detected
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='YouVideo Downloader',           # Space is OK on Windows/macOS
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                             # Makes exe smaller (install UPX if you want)
    upx_exclude=['vcruntime140.dll'],     # Prevents crashes on some Windows machines
    console=False,                        # ← No black console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/appicon.ico',      # ← Use .ico on Windows (best)
    # For macOS use: icon='assets/icons/appicon.icns'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YouVideoDownloader'
)