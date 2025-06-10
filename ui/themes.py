from utils.pathfinder import resource_path


def load_stylesheet(theme="light"):
    """
    Loads and returns the contents of a QSS stylesheet file for the specified theme.

    Args:
        theme (str): The name of the theme to load (default is "light").

    Returns:
        str: The contents of the QSS file as a string if found, otherwise an empty string.
    """
    path = resource_path(f"assets/qss/{theme}.qss")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Stylesheet not found: {path}")
        return ""