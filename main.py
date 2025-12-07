"""
YouVideo Downloader v1.6.2
Main entry point — fully working icons + no warnings on all platforms.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Your UI modules
from ui.welcome_screen import WelcomeScreen
from ui.main_window import MainWindow
from ui.playlist_window import PlaylistWindow

# Your resource path helper (for PyInstaller)
from utils.pathfinder import resource_path


def setup_application() -> QApplication:
    """Create and configure QApplication with best compatibility."""
    app = QApplication(sys.argv)

    app.setApplicationName("YouVideo Downloader")
    app.setApplicationDisplayName("YouVideo Downloader")
    app.setOrganizationName("Sarwar Hossain")
    app.setApplicationVersion("1.6.2")

    # Critical for Linux panel icon
    app.setDesktopFileName("youvideo-downloader")

    # Nice modern style on Windows
    if sys.platform.startswith("win"):
        app.setStyle("Fusion")

    return app


def get_best_icon_path() -> str:
    """Return the best icon path for current platform."""
    base = Path(resource_path("assets/icons"))

    # Platform-specific priority
    if sys.platform.startswith("win"):
        candidates = ["appicon.ico", "appicon.png"]
    elif sys.platform == "darwin":
        candidates = ["appicon.icns", "appicon.png"]
    else:  # Linux
        candidates = ["appicon.png"]

    for name in candidates:
        path = base / name
        if path.exists():
            return str(path)

    # Fallback: any PNG
    pngs = list(base.glob("*.png"))
    return str(pngs[0]) if pngs else ""


def main() -> None:
    app = setup_application()

    # ──────────────────────────────────────────────────────────────
    # Silence harmless xdg-desktop-portal warning on Linux (dev only)
    if getattr(sys, "frozen", False) is False:  # Running from source
        if sys.platform.startswith("linux"):
            import os
            os.environ["QT_QPA_PLATFORMTHEME"] = ""
            os.environ["XDG_DESKTOP_PORTAL_DISABLE"] = "1"
    # ──────────────────────────────────────────────────────────────

    # Load and set icon
    icon_path = get_best_icon_path()
    if icon_path and Path(icon_path).exists():
        print(f"Using app icon: {icon_path}")
        icon = QIcon(icon_path)
    else:
        print("Warning: No icon found in assets/icons/")
        icon = QIcon()

    # Set icon as early as possible
    app.setWindowIcon(icon)

    # Create windows
    welcome = WelcomeScreen()
    main_win = MainWindow()
    playlist_win = PlaylistWindow()

    # Ensure icon appears everywhere (Linux + Windows taskbar grouping)
    welcome.setWindowIcon(icon)
    main_win.setWindowIcon(icon)
    playlist_win.setWindowIcon(icon)

    # Window sizes
    main_win.resize(1000, 680)
    playlist_win.resize(1000, 680)
    welcome.resize(720, 520)
    welcome.setWindowTitle("Welcome — YouVideo Downloader")

    # Navigation callbacks
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

    # Connect UI navigation
    welcome.set_callbacks(on_single_video=show_main, on_playlist=show_playlist)
    main_win.set_back_callback(show_welcome)
    playlist_win.set_back_callback(show_welcome)

    # Start app
    welcome.show()
    welcome.raise_()
    welcome.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()