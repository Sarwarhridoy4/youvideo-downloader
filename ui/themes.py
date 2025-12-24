import sys
from utils.pathfinder import resource_path


def is_dark_mode() -> bool:
    """
    Detects if the system is currently using a dark theme.
    Supports Windows 10+, macOS 10.14+, and most Linux desktop environments (via Qt palette).

    Returns:
        bool: True if dark mode is active, False if light mode.
    """
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QPalette

        # Create a temporary app if none exists yet
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        palette = app.palette()
        background = palette.color(QPalette.ColorRole.Window).lightness()
        text = palette.color(QPalette.ColorRole.WindowText).lightness()

        # Dark mode: background is dark and text is light
        return background < 128 and text > 128

    except Exception as e:
        print(f"Theme detection fallback due to error: {e}")
        return False  # Default to light if detection fails


def load_stylesheet(theme: str = "auto") -> str:
    """
    Loads and returns the contents of a QSS stylesheet file.

    Args:
        theme (str): 
            - "auto"   : Automatically detect system theme (dark/light) — RECOMMENDED
            - "dark"   : Force dark theme
            - "light"  : Force light theme

    Returns:
        str: The contents of the appropriate QSS file as a string.
             Returns empty string if file not found.
    """
    if theme == "auto":
        theme = "dark" if is_dark_mode() else "light"

    path = resource_path(f"assets/qss/{theme}.qss")
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"✓ Loaded {theme}.qss stylesheet")
            return content
    except FileNotFoundError:
        print(f"✗ Stylesheet not found: {path}")
        # Fallback: try the opposite theme
        fallback_theme = "light" if theme == "dark" else "dark"
        fallback_path = resource_path(f"assets/qss/{fallback_theme}.qss")
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                print(f"⚠ Fallback to {fallback_theme}.qss")
                return f.read()
        except FileNotFoundError:
            print(f"✗ Fallback stylesheet not found: {fallback_path}")
            return ""
    except Exception as e:
        print(f"✗ Error loading stylesheet: {e}")
        return ""