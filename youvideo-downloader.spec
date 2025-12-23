# -*- mode: python ; coding: utf-8 -*-
"""
YouVideo Downloader — PyInstaller Spec v2.2 (Fixed & Optimized)
====================================================================
• onedir mode — perfect for .deb and AppImage packaging
• Consistent output folder: dist/YouVideoDownloader/
• No duplicate bundling (a.binaries/a.datas passed only once)
• Professional icons from create_icon.py
• Optional FFmpeg bundling
• UPX compression
• Clean, minimal, reliable
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys
import shutil
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# PLATFORM DETECTION
# ═══════════════════════════════════════════════════════════════════════════
IS_WINDOWS = sys.platform.startswith("win") or sys.platform == "cygwin"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

print("=" * 80)
print("YouVideo Downloader - PyInstaller Spec v2.2 (onedir)")
print("=" * 80)
print(f"Platform: {sys.platform}")
print(f"Mode: onedir → dist/YouVideoDownloader/")

# ═══════════════════════════════════════════════════════════════════════════
# ICON SELECTION
# ═══════════════════════════════════════════════════════════════════════════
def find_icon():
    icon_dir = Path("assets/icons")
    if not icon_dir.exists():
        print(f"Warning: Icon directory missing: {icon_dir}")
        return None

    if IS_WINDOWS:
        candidates = ["appicon.ico"]
    elif IS_MACOS:
        candidates = ["appicon.icns"]
    else:  # Linux
        candidates = ["icon_512.png", "icon_256.png", "appicon.png"]

    for name in candidates:
        icon_path = icon_dir / name
        if icon_path.exists():
            print(f"Selected icon: {icon_path}")
            return str(icon_path)

    print("Warning: No suitable icon found")
    return None

icon_file = find_icon()

# ═══════════════════════════════════════════════════════════════════════════
# BINARY & OUTPUT DIRECTORY NAMING
# ═══════════════════════════════════════════════════════════════════════════
# Binary name inside the folder
binary_name = "youvideo-downloader" if IS_LINUX else "YouVideo Downloader"

# Output folder name — MUST be "YouVideoDownloader" for your build.sh script
output_dir_name = "YouVideoDownloader"

print(f"Binary name: {binary_name}")
print(f"Output folder: dist/{output_dir_name}")

# ═══════════════════════════════════════════════════════════════════════════
# OPTIONAL FFMPEG BUNDLING
# ═══════════════════════════════════════════════════════════════════════════
def find_ffmpeg():
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"FFmpeg found: {ffmpeg_path} → will be bundled")
        return [(ffmpeg_path, ".")]
    else:
        print("FFmpeg not found → app will download on first run")
        return []

ffmpeg_binaries = find_ffmpeg()

# ═══════════════════════════════════════════════════════════════════════════
# HIDDEN IMPORTS & DATA FILES (Optimized)
# ═══════════════════════════════════════════════════════════════════════════
hidden_imports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtNetwork",
    "yt_dlp",
    "yt_dlp.extractor",
    "yt_dlp.postprocessor",
    "yt_dlp.utils",
    "urllib3",
    "certifi",
    "charset_normalizer",
    "PIL.ImageQt",
]

# Collect necessary data files (assets + project modules)
datas = [
    ("assets/qss", "assets/qss"),
    ("assets/icons", "assets/icons"),
    ("assets/screenshot", "assets/screenshot"),
]

# Add local Python packages if they exist
for module in ["downloader", "ui", "utils"]:
    if Path(module).is_dir():
        datas += collect_data_files(module)

print(f"Data folders bundled: {len(datas)}")
print(f"Hidden imports: {len(hidden_imports)}")

# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=ffmpeg_binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter", "matplotlib", "numpy", "pandas", "scipy",
        "IPython", "notebook", "PyQt5", "PyQt6", "wx"
    ],
    cipher=None,
)

# ═══════════════════════════════════════════════════════════════════════════
# PYZ
# ═══════════════════════════════════════════════════════════════════════════
pyz = PYZ(a.pure)

# ═══════════════════════════════════════════════════════════════════════════
# EXE — DO NOT BUILD STANDALONE (onedir mode)
# ═══════════════════════════════════════════════════════════════════════════
exe = EXE(
    pyz,
    a.scripts,
    [],  # ← Critical: empty exclude list to prevent early EXE creation
    name=binary_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    icon=icon_file,
    disable_windowed_traceback=False,
)

# ═══════════════════════════════════════════════════════════════════════════
# COLLECT — FINAL ONEDIR BUNDLE
# ═══════════════════════════════════════════════════════════════════════════
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=output_dir_name,  # → dist/YouVideoDownloader/
)

# ═══════════════════════════════════════════════════════════════════════════
# macOS APP BUNDLE (uses coll)
# ═══════════════════════════════════════════════════════════════════════════
if IS_MACOS:
    app = BUNDLE(
        coll,
        name="YouVideo Downloader.app",
        icon=icon_file,
        bundle_identifier="com.sarwarhossain.youvideo-downloader",
        version="2.0.0",
        info_plist={
            'CFBundleName': 'YouVideo Downloader',
            'CFBundleDisplayName': 'YouVideo Downloader',
            'CFBundleIdentifier': 'com.sarwarhossain.youvideo-downloader',
            'CFBundleVersion': '2.0.0',
            'CFBundleShortVersionString': '2.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.15.0',
            'NSRequiresAquaSystemAppearance': False,
        },
    )

# ═══════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 80)
print("Spec Ready!")
print("=" * 80)
print(f"Output: dist/{output_dir_name}/")
print(f"Executable: {binary_name}")
print(f"Icon: {icon_file or 'default'}")
print(f"FFmpeg bundled: {'Yes' if ffmpeg_binaries else 'No'}")
print("=" * 80)
print("Run: pyinstaller youvideo-downloader.spec")
print("Your build.sh script will now work perfectly!")
print("=" * 80)