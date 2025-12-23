"""
YouVideo Downloader v1.6.2
Main entry point — FIXED taskbar icon for Linux/GNOME (Enhanced)
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


ICON_PATH = resource_path("assets/icons/appicon.png")

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


def get_icon() -> QIcon:
    """
    Get the application icon with proper fallback chain.
    Returns a QIcon that works across all platforms.
    MUST be called AFTER QApplication is created!
    """
    icon = QIcon()
    base = Path(resource_path("assets/icons"))
    print(f"\n🔍 Searching for icon in: {base}")
    print(f"   Directory exists: {base.exists()}")
    
    if base.exists():
        files = [f.name for f in base.iterdir()]
        print(f"   Contents: {files[:5]}...")  # Show first 5 only
    
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
                    print(f"✓ Using icon: {path}")
                    return icon
                else:
                    print(f" ✗ INVALID")
            else:
                # For ICO/ICNS, use directly
                test_icon = QIcon(str(path))
                if not test_icon.isNull():
                    print(f" ✓ LOADED")
                    print(f"✓ Using icon: {path}")
                    return test_icon
                else:
                    print(f" ✗ NULL")
        else:
            print(f"NOT FOUND")
    
    print("✗ ERROR: No valid icon found!")
    return QIcon()


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
        print("✓ Linux desktop integration configured")
    
    return app


def install_linux_desktop_file(icon_path: str):
    """
    Create a .desktop file for proper Linux integration.
    This is CRITICAL for taskbar icon on GNOME/Ubuntu.
    """
    if not sys.platform.startswith("linux"):
        return False
    
    try:
        home = Path.home()
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: Install icon to standard system location
        # ═══════════════════════════════════════════════════════════
        icon_dir = home / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps"
        icon_dir.mkdir(parents=True, exist_ok=True)
        
        icon_dest = icon_dir / "youvideo-downloader.png"
        
        # Copy icon if source exists
        if os.path.exists(icon_path):
            import shutil
            shutil.copy2(icon_path, icon_dest)
            icon_dest.chmod(0o644)
            print(f"✓ Icon installed to: {icon_dest}")
            
            # Also install to other common sizes
            for size in [16, 22, 24, 32, 48, 64, 128]:
                size_dir = home / ".local" / "share" / "icons" / "hicolor" / f"{size}x{size}" / "apps"
                size_dir.mkdir(parents=True, exist_ok=True)
                size_dest = size_dir / "youvideo-downloader.png"
                
                # Create scaled version
                try:
                    from PIL import Image
                    img = Image.open(icon_path)
                    img_resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    img_resized.save(str(size_dest))
                except ImportError:
                    # If PIL not available, just copy the main icon
                    shutil.copy2(icon_path, size_dest)
                except Exception as e:
                    print(f"⚠ Could not create {size}x{size} icon: {e}")
            
            print(f"✓ Multiple icon sizes installed")
        else:
            print(f"⚠ Source icon not found: {icon_path}")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: Create desktop file
        # ═══════════════════════════════════════════════════════════
        desktop_dir = home / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / "youvideo-downloader.desktop"
        
        # Get absolute paths
        if getattr(sys, 'frozen', False):
            exec_path = sys.executable
        else:
            exec_path = f"python3 {os.path.abspath(sys.argv[0])}"
        
        # IMPORTANT: Use icon name (without path) for system integration
        # This allows the system to find the icon in standard locations
        content = f"""[Desktop Entry]
Type=Application
Version=1.0
Name=YouVideo Downloader
GenericName=Video Downloader
Comment=Download videos from YouTube and other platforms
Exec={exec_path}
Icon=youvideo-downloader
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
        print(f"   Icon: youvideo-downloader (system)")
        print(f"   WM_CLASS: youvideo-downloader")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 3: Update system caches
        # ═══════════════════════════════════════════════════════════
        import subprocess
        
        # Update desktop database
        try:
            result = subprocess.run(
                ["update-desktop-database", str(desktop_dir)],
                capture_output=True,
                timeout=5,
                text=True
            )
            if result.returncode == 0:
                print("✓ Desktop database updated")
            else:
                print(f"⚠ Desktop database update warning: {result.stderr.strip()}")
        except FileNotFoundError:
            print("⚠ update-desktop-database not found (optional)")
        except Exception as e:
            print(f"⚠ Could not update desktop database: {e}")
        
        # Update icon cache
        try:
            icon_base = home / ".local" / "share" / "icons" / "hicolor"
            result = subprocess.run(
                ["gtk-update-icon-cache", "-f", "-t", str(icon_base)],
                capture_output=True,
                timeout=5,
                text=True
            )
            if result.returncode == 0:
                print("✓ Icon cache updated")
            else:
                print(f"⚠ Icon cache update warning: {result.stderr.strip()}")
        except FileNotFoundError:
            print("⚠ gtk-update-icon-cache not found (optional)")
        except Exception as e:
            print(f"⚠ Could not update icon cache: {e}")
            
        return True
    except Exception as e:
        print(f"\n✗ Desktop file creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def set_window_properties(window, icon):
    """
    Set all necessary properties for proper taskbar integration.
    This ensures consistent behavior across all windows.
    """
    # Set icon
    window.setWindowIcon(icon)
    
    if sys.platform.startswith("linux"):
        # Force WM_CLASS to be consistent
        window.setProperty("_q_xcb_wm_class", b"youvideo-downloader")
        
        # Set window class hint
        try:
            # This helps X11 window managers match the window
            flags = window.windowFlags()
            window.setWindowFlags(flags)
        except:
            pass


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
        
        if not os.environ.get('DISPLAY'):
            print("⚠ No X11 display detected")
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
    except FileNotFoundError:
        # xdotool or xprop not installed - that's fine
        pass
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
    # STEP 2: Create QApplication FIRST
    # ═══════════════════════════════════════════════════════════════
    app = setup_application()

    # ═══════════════════════════════════════════════════════════════
    # STEP 3: Load icon AFTER QApplication exists
    # ═══════════════════════════════════════════════════════════════
    icon = get_icon()
    
    if icon.isNull():
        print("\n⚠ WARNING: Icon is NULL - taskbar icon WILL NOT SHOW!")
        print("   Check that assets/icons/appicon.png exists")
    else:
        print("\n✓ Icon loaded successfully")
        # Set icon globally for ALL windows
        app.setWindowIcon(icon)

    # ═══════════════════════════════════════════════════════════════
    # STEP 4: Linux - Install desktop file and system icon
    # ═══════════════════════════════════════════════════════════════
    if sys.platform.startswith("linux") and not icon.isNull():
        icon_path = resource_path("assets/icons/appicon.png")
        if os.path.exists(icon_path):
            install_linux_desktop_file(icon_path)
        else:
            print(f"\n✗ Icon file not found: {icon_path}")

    # ═══════════════════════════════════════════════════════════════
    # STEP 5: Create windows and set properties
    # ═══════════════════════════════════════════════════════════════
    welcome = WelcomeScreen()
    main_win = MainWindow()
    playlist_win = PlaylistWindow()

    # Set icon and properties on each window
    for window in [welcome, main_win, playlist_win]:
        set_window_properties(window, icon)

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
    # STEP 6: Start application
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
        print("\n📌 LINUX TASKBAR ICON - TROUBLESHOOTING:")
        print("\n   🔄 QUICKEST FIX - Restart GNOME Shell:")
        print("      • Press Alt+F2")
        print("      • Type: r")
        print("      • Press Enter")
        print("      • Icon should appear immediately")
        
        print("\n   🔍 VERIFY SETUP:")
        print("      1. Check WM_CLASS:")
        print("         xprop WM_CLASS")
        print("         (click window, should show: youvideo-downloader)")
        
        print("\n      2. Check desktop file:")
        print("         desktop-file-validate ~/.local/share/applications/youvideo-downloader.desktop")
        
        print("\n      3. Check icon installation:")
        print("         ls -la ~/.local/share/icons/hicolor/*/apps/youvideo-downloader.png")
        
        print("\n   🔧 MANUAL REFRESH (if needed):")
        print("      gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor")
        print("      update-desktop-database ~/.local/share/applications")
        
        print("\n   ⚠️  If STILL not working:")
        print("      • Logout and login again")
        print("      • Or: killall gnome-shell")
        
    elif sys.platform.startswith("win"):
        print("\n📌 WINDOWS TASKBAR ICON:")
        print("   ✓ AppUserModelID set for proper grouping")
        print("   ✓ Icon should show immediately")
        
    print("\n" + "="*70 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()