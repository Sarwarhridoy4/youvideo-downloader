"""Compatibility helpers for yt-dlp version-specific behavior."""

from __future__ import annotations

from typing import Optional, Tuple

ANDROID_SDKLESS_FIX_VERSION: Tuple[int, int, int] = (2026, 1, 31)


def _parse_version(version_str: str) -> Optional[Tuple[int, ...]]:
    parts: list[int] = []
    for part in version_str.split("."):
        digits = ""
        for ch in part:
            if ch.isdigit():
                digits += ch
            else:
                break
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts) if parts else None


def is_android_sdkless_fix_available() -> bool:
    try:
        from yt_dlp.version import __version__ as ytdlp_version
    except Exception:
        return False

    parsed = _parse_version(ytdlp_version)
    if not parsed:
        return False

    return parsed >= ANDROID_SDKLESS_FIX_VERSION


def get_youtube_extractor_args() -> Optional[dict]:
    """Return extractor args needed to avoid 403s on older yt-dlp builds.

    Returns None when the fix is available in yt-dlp, so callers can omit
    extractor_args entirely.
    """
    if is_android_sdkless_fix_available():
        return None

    return {
        "youtube": {
            "player_client": ["default", "-android_sdkless"],
        }
    }
