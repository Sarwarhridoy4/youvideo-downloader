from __future__ import annotations

from pathlib import Path
from weakref import WeakSet

from utils.pathfinder import resource_path


class ThemeManager:
    _current_theme = "dark"
    _windows: "WeakSet[object]" = WeakSet()
    _is_applying = False

    @classmethod
    def register(cls, window) -> None:
        cls._windows.add(window)
        cls.apply_to(window)

    @classmethod
    def get_current_theme(cls) -> str:
        return cls._current_theme

    @classmethod
    def toggle(cls) -> None:
        if cls._is_applying:
            return
        cls._current_theme = "light" if cls._current_theme == "dark" else "dark"
        cls._apply_all()

    @classmethod
    def set_theme(cls, theme: str) -> None:
        if theme not in ("dark", "light"):
            return
        if cls._is_applying:
            return
        cls._current_theme = theme
        cls._apply_all()

    @classmethod
    def apply_to(cls, window) -> None:
        if hasattr(window, "_apply_theme_from_manager"):
            try:
                window._apply_theme_from_manager(cls._current_theme)
                return
            except Exception:
                # Fall back to stylesheet if custom handler fails.
                pass

        theme_path = cls._get_theme_path()
        try:
            content = Path(theme_path).read_text(encoding="utf-8")
            window.setStyleSheet(content)
        except Exception:
            # Fail silently; UI will still be usable without theme.
            pass

    @classmethod
    def _apply_all(cls) -> None:
        cls._is_applying = True
        try:
            for win in list(cls._windows):
                cls.apply_to(win)
        finally:
            cls._is_applying = False

    @classmethod
    def _get_theme_path(cls) -> str:
        if cls._current_theme == "light":
            return resource_path("assets/qss/light.qss")
        return resource_path("assets/qss/dark.qss")
