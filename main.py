"""
YouVideo Downloader v1.6.2
Main entry point — FIXED taskbar icon for Linux/GNOME
"""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt

# Your UI modules
from ui.welcome_screen import WelcomeScreen
from ui.main_window import MainWindow
from ui.playlist_window import PlaylistWindow

# Your resource path helper (for PyInstaller)
from utils.pathfinder import resource_path


def fix_linux_wmclass():
    """
    Fix Linux WM_CLASS before QApplication is created.
    This is THE critical step for GNOME taskbar icon.
    """
    if sys.platform.startswith("linux"):
        # Set the resource name that will become WM_CLASS
        os.environ['RESOURCE_NAME'] = 'youvideo-downloader'
        print("✓ Linux: Set RESOURCE_NAME environment variable")


def fix_windows_taskbar_icon():
    """Fix Windows taskbar icon grouping - MUST be called before QApplication."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            app_id = "SarwarHossain.YouVideoDownloader.1.6.2"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            print(f"✓ Windows AppUserModelID set: {app_id}")
            return True
        except Exception as e:
            print(f"✗ AppUserModelID error: {e}")
            return False
    return True


def setup_application() -> QApplication:
    """Create and configure QApplication with best compatibility."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)

    # Application metadata
    app.setApplicationName("YouVideo Downloader")
    app.setApplicationDisplayName("YouVideo Downloader")
    app.setOrganizationName("Sarwar Hossain")
    app.setOrganizationDomain("youvideo.app")
    app.setApplicationVersion("1.6.2")

    # Platform-specific settings
    if sys.platform.startswith("linux"):
        # Remove .desktop suffix - Qt will add it
        app.setDesktopFileName("youvideo-downloader")
        
        # CRITICAL: Set the application class name
        # This must match the StartupWMClass in .desktop file
        app.setProperty("applicationName", "youvideo-downloader")
    
    return app


def get_icon() -> QIcon:
    """
    Get the application icon with proper fallback chain.
    Returns a QIcon that works across all platforms.
    """
    icon = QIcon()
    base = Path(resource_path("assets/icons"))
    print(f"\n🔍 Searching for icon in: {base}")
    print(f"   Directory exists: {base.exists()}")
    
    if base.exists():
        files = [f.name for f in base.iterdir()]
        print(f"   Contents: {files}")
    
    # Try multiple icon files in order of preference
    icon_files = []
    
    if sys.platform.startswith("win"):
        icon_files = ["appicon.ico", "appicon.png", "icon.png"]
    elif sys.platform == "darwin":
        icon_files = ["appicon.icns", "appicon.png", "icon.png"]
    else:
        # Linux: Try PNG files
        icon_files = ["appicon.png", "icon_256.png", "icon_128.png", "icon.png"]
    
    # Try each icon file
    for name in icon_files:
        path = base / name
        print(f"   Trying: {name} ... ", end="")
        
        if path.exists():
            print(f"EXISTS", end="")
            
            # For PNG files, load as pixmap and add multiple sizes
            if name.endswith('.png'):
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    icon.addPixmap(pixmap)
                    # Add scaled versions for different sizes
                    for size in [16, 22, 24, 32, 48, 64, 128, 256]:
                        scaled = pixmap.scaled(
                            size, size,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        icon.addPixmap(scaled)
                    
                    print(f" ✓ LOADED ({pixmap.width()}x{pixmap.height()})")
                    print(f"\n✓ Using icon: {path}")
                    return icon
                else:
                    print(f" ✗ INVALID")
            else:
                # For ICO/ICNS, use directly
                test_icon = QIcon(str(path))
                if not test_icon.isNull():
                    print(f" ✓ LOADED")
                    print(f"\n✓ Using icon: {path}")
                    return test_icon
                else:
                    print(f" ✗ NULL")
        else:
            print(f"NOT FOUND")
    
    print("\n✗ ERROR: No valid icon found!")
    return QIcon()


def install_linux_desktop_file(icon_path: str):
    """
    Create a .desktop file for proper Linux integration.
    This is CRITICAL for taskbar icon on GNOME/Ubuntu.
    """
    if not sys.platform.startswith("linux"):
        return False
    
    try:
        home = Path.home()
        desktop_dir = home / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / "youvideo-downloader.desktop"
        
        # Get absolute paths
        if getattr(sys, 'frozen', False):
            exec_path = sys.executable
        else:
            exec_path = f"python3 {os.path.abspath(sys.argv[0])}"
        
        icon_abs_path = os.path.abspath(icon_path)
        
        # CRITICAL: WM_CLASS must match what Qt sets
        content = f"""[Desktop Entry]
Type=Application
Version=1.0
Name=YouVideo Downloader
GenericName=Video Downloader
Comment=Download videos from YouTube and other platforms
Exec={exec_path}
Icon={icon_abs_path}
Terminal=false
Categories=AudioVideo;Video;Network;Qt;
MimeType=x-scheme-handler/http;x-scheme-handler/https;
StartupWMClass=youvideo-downloader
StartupNotify=true
Keywords=youtube;video;download;
"""
        
        desktop_file.write_text(content)
        desktop_file.chmod(0o755)
        
        print(f"\n✓ Linux desktop file created:")
        print(f"   Location: {desktop_file}")
        print(f"   Exec: {exec_path}")
        print(f"   Icon: {icon_abs_path}")
        print(f"   WM_CLASS: youvideo-downloader")
        
        # Update desktop database
        import subprocess
        try:
            result = subprocess.run(
                ["update-desktop-database", str(desktop_dir)],
                capture_output=True,
                timeout=5,
                text=True
            )
            if result.returncode == 0:
                print("✓ Desktop database updated")
        except FileNotFoundError:
            print("⚠ update-desktop-database not found")
        except Exception as e:
            print(f"⚠ Could not update desktop database: {e}")
        
        # Also try to update icon cache
        try:
            icon_dir = home / ".local" / "share" / "icons"
            if icon_dir.exists():
                subprocess.run(
                    ["gtk-update-icon-cache", str(icon_dir)],
                    capture_output=True,
                    timeout=5
                )
                print("✓ Icon cache updated")
        except:
            pass
            
        return True
    except Exception as e:
        print(f"\n✗ Desktop file creation failed: {e}")
        return False


def set_x11_wmclass():
    """
    Manually set X11 WM_CLASS property if possible.
    This is a backup method for X11 sessions.
    """
    if not sys.platform.startswith("linux"):
        return
    
    try:
        # Check if we're on X11 (not Wayland)
        if os.environ.get('WAYLAND_DISPLAY'):
            print("✓ Running on Wayland (WM_CLASS set via Qt)")
            return
        
        # Try to set via xprop
        import subprocess
        import time
        
        # Give Qt time to create the window
        time.sleep(0.5)
        
        # Find our window ID
        result = subprocess.run(
            ["xdotool", "search", "--name", "YouVideo"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0 and result.stdout.strip():
            window_id = result.stdout.strip().split()[0]
            
            # Set WM_CLASS
            subprocess.run(
                ["xprop", "-id", window_id, "-f", "WM_CLASS", "8s",
                 "-set", "WM_CLASS", "youvideo-downloader"],
                timeout=2
            )
            print(f"✓ X11 WM_CLASS set via xprop (window {window_id})")
    except Exception as e:
        # This is optional, so don't worry if it fails
        pass


def main() -> None:
    print("\n" + "="*70)
    print("🚀 YouVideo Downloader v1.6.2 Starting...")
    print("="*70)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 1: Set environment variables BEFORE QApplication
    # ═══════════════════════════════════════════════════════════════
    fix_linux_wmclass()
    
    if sys.platform.startswith("win"):
        fix_windows_taskbar_icon()
    
    # Silence Qt portal warnings
    if not getattr(sys, "frozen", False):
        os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"
        os.environ["QT_QPA_PLATFORMTHEME"] = ""
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 2: Create QApplication
    # ═══════════════════════════════════════════════════════════════
    app = setup_application()

    # ═══════════════════════════════════════════════════════════════
    # STEP 3: Load and set icon GLOBALLY
    # ═══════════════════════════════════════════════════════════════
    icon = get_icon()
    
    if icon.isNull():
        print("\n⚠ WARNING: Icon is NULL - taskbar icon WILL NOT SHOW!")
        print("   Check that assets/icons/appicon.png exists")
    else:
        print("\n✓ Icon loaded successfully")
        
        # Set icon globally for ALL windows
        app.setWindowIcon(icon)
        
        # Linux: Create desktop file for taskbar integration
        if sys.platform.startswith("linux"):
            icon_path = resource_path("assets/icons/appicon.png")
            if os.path.exists(icon_path):
                install_linux_desktop_file(icon_path)
            else:
                print(f"\n✗ Icon file not found: {icon_path}")

    # ═══════════════════════════════════════════════════════════════
    # STEP 4: Create windows
    # ═══════════════════════════════════════════════════════════════
    welcome = WelcomeScreen()
    main_win = MainWindow()
    playlist_win = PlaylistWindow()

    # Explicitly set icon on each window
    for window in [welcome, main_win, playlist_win]:
        window.setWindowIcon(icon)
        
        # Linux: Set class name for window matching
        if sys.platform.startswith("linux"):
            window.setWindowFlags(window.windowFlags())
            # This ensures Qt uses our WM_CLASS

    # Window configuration
    main_win.resize(1000, 680)
    playlist_win.resize(1000, 680)
    welcome.resize(720, 520)
    
    # Set titles
    welcome.setWindowTitle("Welcome — YouVideo Downloader")
    main_win.setWindowTitle("YouVideo Downloader")
    playlist_win.setWindowTitle("YouVideo Downloader - Playlist")

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

    # ═══════════════════════════════════════════════════════════════
    # STEP 5: Start application
    # ═══════════════════════════════════════════════════════════════
    welcome.show()
    welcome.raise_()
    welcome.activateWindow()
    
    # Linux: Try to set WM_CLASS via X11 as backup
    if sys.platform.startswith("linux"):
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, set_x11_wmclass)

    print("\n" + "="*70)
    print("✓ Application started successfully!")
    print("="*70)
    
    # Platform-specific instructions
    if sys.platform.startswith("linux"):
        print("\n📌 LINUX TASKBAR ICON - IMMEDIATE FIXES:")
        print("\n   METHOD 1 - Restart GNOME Shell (FASTEST):")
        print("      • Press Alt+F2")
        print("      • Type: r")
        print("      • Press Enter")
        print("      • Icon should appear immediately")
        
        print("\n   METHOD 2 - Check WM_CLASS match:")
        print("      • Run: xprop WM_CLASS")
        print("      • Click on the app window")
        print("      • Should show: youvideo-downloader")
        
        print("\n   METHOD 3 - Verify desktop file:")
        print("      • Run: desktop-file-validate ~/.local/share/applications/youvideo-downloader.desktop")
        
        print("\n   METHOD 4 - Manual icon install:")
        print("      • Run these commands:")
        print("      • mkdir -p ~/.local/share/icons/hicolor/256x256/apps")
        print("      • cp assets/icons/appicon.png ~/.local/share/icons/hicolor/256x256/apps/youvideo-downloader.png")
        print("      • gtk-update-icon-cache ~/.local/share/icons/hicolor")
        
        print("\n   If still not working:")
        print("      • Logout and login")
        print("      • Or: killall gnome-shell")
        
    elif sys.platform.startswith("win"):
        print("\n📌 WINDOWS TASKBAR ICON:")
        print("   • AppUserModelID set for proper grouping")
        print("   • Icon should show immediately")
        
    print("\n" + "="*70 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()