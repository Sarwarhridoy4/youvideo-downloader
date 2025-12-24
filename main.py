"""
YouVideo Downloader v1.6.2
Simplified & Robust Main Entry Point
- Proper taskbar icon on Windows, Linux (GNOME), macOS
- No external tools (xdotool, PIL)
- Clean, readable, maintainable
"""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

# Your UI modules
from ui.welcome_screen import WelcomeScreen
from ui.main_window import MainWindow
from ui.playlist_window import PlaylistWindow

# Resource helper (works with PyInstaller)
from utils.pathfinder import resource_path


def fix_windows_taskbar():
    """Set Windows taskbar grouping (must be before QApplication)"""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            app_id = "SarwarHossain.YouVideoDownloader.1.6.2"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass  # Non-critical


def create_app() -> QApplication:
    """Create and configure QApplication"""
    # Fix Windows taskbar before app creation
    fix_windows_taskbar()

    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # App metadata
    app.setApplicationName("YouVideo Downloader")
    app.setApplicationDisplayName("YouVideo Downloader")
    app.setOrganizationName("Sarwar Hossain")
    app.setApplicationVersion("2.0.0")

    # Linux: Set desktop file name (helps icon lookup)
    if sys.platform.startswith("linux"):
        app.setDesktopFileName("youvideo-downloader")

    return app


def load_icon() -> QIcon:
    """Load app icon with fallbacks — called AFTER QApplication"""
    icon_paths = [
        resource_path("assets/icons/appicon.png"),
        resource_path("assets/icons/appicon.ico"),
        resource_path("assets/icons/appicon.icns"),
        resource_path("assets/icons/icon.png"),
    ]

    for path in icon_paths:
        if os.path.exists(path):
            icon = QIcon(path)
            if not icon.isNull():
                return icon

    # Final fallback: empty icon (system will show default)
    return QIcon()


def main():
    print("🚀 Starting YouVideo Downloader v1.6.2...")

    # Create app first
    app = create_app()

    # Load icon after app exists
    icon = load_icon()
    app.setWindowIcon(icon)  # Global icon for all windows

    # Create windows
    welcome = WelcomeScreen()
    main_win = MainWindow()
    playlist_win = PlaylistWindow()

    # Apply icon to all windows
    for win in [welcome, main_win, playlist_win]:
        win.setWindowIcon(icon)

    # Window setup
    welcome.setWindowTitle("Welcome — YouVideo Downloader")
    main_win.setWindowTitle("YouVideo Downloader")
    playlist_win.setWindowTitle("YouVideo Downloader - Playlist")

    welcome.resize(720, 520)
    main_win.resize(1000, 680)
    playlist_win.resize(1000, 680)

    # Navigation logic
    def show_main():
        welcome.hide()
        main_win.show()
        main_win.raise_()
        main_win.activateWindow()

    def show_playlist():
        welcome.hide()
        playlist_win.show()
        playlist_win.raise_()
        playlist_win.activateWindow()

    def show_welcome():
        main_win.hide()
        playlist_win.hide()
        welcome.show()
        welcome.raise_()
        welcome.activateWindow()

    # Connect navigation
    welcome.set_callbacks(on_single_video=show_main, on_playlist=show_playlist)
    main_win.set_back_callback(show_welcome)
    playlist_win.set_back_callback(show_welcome)

    # Show welcome screen
    welcome.show()
    welcome.raise_()
    welcome.activateWindow()

    print("✓ App launched successfully!")
    print("\n💡 Tip for Linux (GNOME) taskbar icon:")
    print("   If icon doesn't show immediately:")
    print("   → Press Alt+F2 → type 'r' → Enter (restarts GNOME shell)")
    print("   → Or log out and back in\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()