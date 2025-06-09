def load_stylesheet(theme="light"):
    """
    Loads and returns the contents of a QSS stylesheet file for the specified theme.

    Args:
        theme (str): The name of the theme to load (default is "light"). The function looks for a QSS file
            at 'assets/qss/{theme}.qss'.

    Returns:
        str: The contents of the QSS file as a string if found, otherwise an empty string.
    """
    path = f"assets/qss/{theme}.qss"
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""
