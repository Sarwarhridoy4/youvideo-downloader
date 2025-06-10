import os
import sys

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for development and PyInstaller bundle.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)