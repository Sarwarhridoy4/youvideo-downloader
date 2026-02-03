"""
YouVideo Downloader v3.0.0
Simplified & Robust Main Entry Point with Theme Synchronization
- Proper taskbar icon on Windows, Linux (GNOME), macOS
- Theme synchronization across all windows
- Cross-platform Downloads folder default
- No external tools (xdotool, PIL)
- Clean, readable, maintainable
"""

import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtCore import Qt

# Your UI modules
from ui.welcome_screen import WelcomeScreen
from ui.main_window import MainWindow
from ui.playlist_window import PlaylistWindow

# Resource helper (works with PyInstaller)
from utils.pathfinder import resource_path
from utils.theme_manager import ThemeManager


def fix_windows_taskbar():
    """Set Windows taskbar grouping (must be before QApplication)"""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            app_id = "SarwarHossain.YouVideoDownloader.3.0.0"
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
    app.setApplicationName("𝒀𝒐𝒖𝑽𝒊𝒅𝒆𝒐 𝑫𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒆𝒓")
    app.setApplicationDisplayName("𝒀𝒐𝒖𝑽𝒊𝒅𝒆𝒐 𝑫𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒆𝒓")
    app.setOrganizationName("𝓢𝓪𝓻𝔀𝓪𝓻 𝓗𝓸𝓼𝓼𝓪𝓲𝓷")
    app.setApplicationVersion("3.0.0")

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
    print("🚀 Starting YouVideo Downloader v3.0.0...")

    # Create app first
    app = create_app()

    # Apply initial theme based on system preference
    try:
        scheme = QGuiApplication.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            ThemeManager.set_theme("dark")
        elif scheme == Qt.ColorScheme.Light:
            ThemeManager.set_theme("light")
        else:
            # Unknown: prefer the app's original dark theme
            ThemeManager.set_theme("dark")
    except Exception:
        ThemeManager.set_theme("dark")

    # Load icon after app exists
    icon = load_icon()
    app.setWindowIcon(icon)  # Global icon for all windows

    print("📦 Initializing windows...")
    
    # Create windows
    try:
        welcome = WelcomeScreen()
        print("   ✓ Welcome screen created")
    except Exception as e:
        print(f"   ✗ Failed to create welcome screen: {e}")
        sys.exit(1)
    
    try:
        main_win = MainWindow()
        print("   ✓ Main window created")
    except Exception as e:
        print(f"   ✗ Failed to create main window: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    try:
        playlist_win = PlaylistWindow()
        print("   ✓ Playlist window created")
    except Exception as e:
        print(f"   ✗ Failed to create playlist window: {e}")
        sys.exit(1)

    # Apply icon to all windows
    for win in [welcome, main_win, playlist_win]:
        win.setWindowIcon(icon)

    # Window setup
    welcome.setWindowTitle("Welcome — 𝒀𝒐𝒖𝑽𝒊𝒅𝒆𝒐 𝑫𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒆𝒓")
    main_win.setWindowTitle("𝒀𝒐𝒖𝑽𝒊𝒅𝒆𝒐 𝑫𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒆𝒓")
    playlist_win.setWindowTitle("𝒀𝒐𝒖𝑽𝒊𝒅𝒆𝒐 𝑫𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒆𝒓 – Playlist")

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

    print("\n✅ App launched successfully!")
    print("\n💡 Features:")
    print("   • FFmpeg postprocessing progress tracking")
    print("   • Cross-platform Downloads folder default:")
    print("     - Windows: C:/Users/username/Downloads")
    print("     - Linux:   /home/username/Downloads")
    print("     - Mac:     /Users/username/Downloads")
    print("   • Theme toggle button (🌙/☀️) in welcome screen")
    print("   • Theme syncs across all windows automatically")
    print("   • Fullscreen/maximize enabled on all platforms")
    print("\n💡 Tip for Linux (GNOME) taskbar icon:")
    print("   If icon doesn't show immediately:")
    print("   → Press Alt+F2 → type 'r' → Enter (restarts GNOME shell)")
    print("   → Or log out and back in\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
