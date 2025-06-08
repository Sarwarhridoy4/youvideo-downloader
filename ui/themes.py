def load_stylesheet(theme="light"):
    path = f"assets/qss/{theme}.qss"
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""
