# -*- mode: python ; coding: utf-8 -*-
# ==============================================================================
# YouVideo Downloader — Ultimate Cross-Platform PyInstaller Spec
# Works perfectly on Linux · Windows · macOS with correct icons everywhere
# Uses your excellent create_icon.py output
# ==============================================================================

import sys
import os

# ────────────────────────────── Platform Detection ──────────────────────────────
IS_WINDOWS = sys.platform.startswith("win") or sys.platform == "cygwin"
IS_MACOS   = sys.platform == "darwin"
IS_LINUX   = sys.platform.startswith("linux")

# ────────────────────────────── Icon Selection ──────────────────────────────
icon_file = None
if IS_WINDOWS:
    icon_file = "assets/icons/appicon.ico"
elif IS_MACOS:
    icon_file = "assets/icons/appicon.icns"
elif IS_LINUX:
    icon_file = "assets/icons/appicon.png"
# Linux: no icon in binary → handled by .desktop file + hicolor theme

# ────────────────────────────── Application Name ──────────────────────────────
binary_name = "youvideo-downloader" if IS_LINUX else "YouVideo Downloader"

# ────────────────────────────── Analysis ──────────────────────────────
a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("assets/qss", "assets/qss"),
        ("assets/icons", "assets/icons"),
        ("assets/screenshot", "assets/screenshot"),
        ("downloader", "downloader"),
        ("ui", "ui"),
        ("utils", "utils"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=None,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=binary_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    icon=icon_file,           # ← Only used on Windows/macOS → safe on Linux
    version="version.txt" if os.path.exists("version.txt") else None,
)

# One-folder bundle (recommended for .deb + portable distribution)
COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="YouVideoDownloader",  # Folder name in dist/
)