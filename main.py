"""
YouVideo Downloader v2.0.0
Simplified & Robust Main Entry Point with Theme Synchronization
- Proper taskbar icon on Windows, Linux (GNOME), macOS
- Theme synchronization across all windows
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
            app_id = "SarwarHossain.YouVideoDownloader.2.1.0"
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
    app.setApplicationVersion("2.1.0")

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


class ThemeManager:
    """Manages theme synchronization across all windows"""
    
    def __init__(self):
        self.current_theme = "dark"
        self.windows = []
    
    def register_window(self, window):
        """Register a window for theme updates"""
        self.windows.append(window)
    
    def set_theme(self, theme: str):
        """Apply theme to all registered windows"""
        if theme not in ["dark", "light"]:
            return
        
        self.current_theme = theme
        
        # Update theme in all windows
        for window in self.windows:
            if hasattr(window, 'set_theme'):
                window.set_theme(theme)
            elif hasattr(window, '_apply_theme'):
                # For windows with direct theme application
                theme_path = resource_path(f"assets/qss/{theme}.qss")
                if os.path.exists(theme_path):
                    window._apply_theme(theme_path)
                    if hasattr(window, 'current_theme'):
                        window.current_theme = theme
    
    def get_theme(self) -> str:
        """Get current theme"""
        return self.current_theme


def main():
    print("🚀 Starting YouVideo Downloader v2.1.0...")

    # Create app first
    app = create_app()

    # Load icon after app exists
    icon = load_icon()
    app.setWindowIcon(icon)  # Global icon for all windows

    # Create theme manager
    theme_manager = ThemeManager()

    # Create windows
    welcome = WelcomeScreen()
    main_win = MainWindow()
    playlist_win = PlaylistWindow()

    # Apply icon to all windows
    for win in [welcome, main_win, playlist_win]:
        win.setWindowIcon(icon)

    # Register windows with theme manager
    theme_manager.register_window(welcome)
    theme_manager.register_window(main_win)
    theme_manager.register_window(playlist_win)

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

    # Connect theme changes from welcome screen to theme manager
    def on_theme_changed(theme: str):
        """Handle theme change from welcome screen"""
        print(f"🎨 Theme changed to: {theme}")
        theme_manager.set_theme(theme)
    
    welcome.theme_changed.connect(on_theme_changed)

    # Also sync theme changes from main windows back to welcome
    def sync_theme_to_welcome(theme: str):
        """Sync theme from main/playlist windows back to welcome"""
        if welcome.get_current_theme() != theme:
            welcome.set_theme(theme)
    
    # If main_window or playlist_window have theme change signals, connect them
    # (You may need to add similar signals to MainWindow and PlaylistWindow)

    # Show welcome screen
    welcome.show()
    welcome.raise_()
    welcome.activateWindow()

    print("✓ App launched successfully!")
    print("\n💡 Features:")
    print("   • Theme toggle button (🌙/☀️) in top-right of welcome screen")
    print("   • Theme syncs across all windows automatically")
    print("   • Fully rounded UI with compact layout")
    print("\n💡 Tip for Linux (GNOME) taskbar icon:")
    print("   If icon doesn't show immediately:")
    print("   → Press Alt+F2 → type 'r' → Enter (restarts GNOME shell)")
    print("   → Or log out and back in\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()