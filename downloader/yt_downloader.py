"""
yt_downloader.py  –  2025‑06‑28 refresh
---------------------------------------
Key goals
• Fetch *just* the playlist slice we need, and do it “flat” (metadata‑only).
• List formats without forcing yt‑dlp to probe every variant/manifest.
"""

from yt_dlp import YoutubeDL
import os

# ───────────────────────── formats ──────────────────────────
def get_formats(url: str) -> list[dict]:
    """
    Return the available formats quickly.

    We use `forcejson + simulate` so yt‑dlp prints the JSON it already has
    after the initial watch‑page request instead of firing extra manifest
    requests for DASH/HLS etc.  The result lists every format id, but it may
    lack *filesize* for some streams – that’s the speed trade‑off.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "simulate": True,          # don’t touch the streams
        "forcejson": True,         # dump raw JSON once and stop
        "no_warnings": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return [
            f for f in info["formats"]
            if f.get("format_id")
            and (f.get("vcodec") != "none" or f.get("acodec") != "none")
            and f["ext"] in ("mp4", "webm", "m4a")
        ]


# ───────────────────────── playlist ─────────────────────────
def get_playlist_videos(url: str, playlist_items: str | None = None) -> list[dict]:
    """
    Fast, sliced playlist listing.

    • `extract_flat="in_playlist"` keeps yt‑dlp from visiting every video page.
    • `playlist_items` (e.g. "1-5" or "7,9,10") lets the caller ask for just
      the items it’s going to show, which can cut large playlists from
      ~seconds → ~hundreds ms.
    """
    ydl_opts = {
        "quiet": True,
        "extract_flat": "in_playlist",   # metadata only
        "skip_download": True,
    }
    if playlist_items:
        ydl_opts["playlist_items"] = playlist_items

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        videos = []
        for entry in info.get("entries", []):
            vid_url = entry.get("url")
            if not vid_url.startswith("http"):
                # yt‑dlp returns bare id in flat mode – build full YouTube URL
                vid_url = f"https://www.youtube.com/watch?v={vid_url}"
            videos.append({"title": entry.get("title", "Untitled"), "url": vid_url})
        return videos


# ─────────────────────── download / merge ───────────────────
def download_and_merge(url, format_code, output_path,
                       progress_hook, log_signal):
    """
    Download *format_code + bestaudio* and mux to MP4 (stream‑copy if possible).
    """
    tmpl = os.path.join(output_path, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": f"{format_code}+bestaudio/best",
        "outtmpl": tmpl,
        "progress_hooks": [progress_hook],
        "quiet": True,
        "merge_output_format": "mp4",
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
        # stream‑copy when compatible – faster, lossless
        "postprocessor_args": ["-c:v", "copy", "-c:a", "aac", "-movflags", "faststart"],
    }

    with YoutubeDL(ydl_opts) as ydl:
        log_signal.emit("Starting download…")
        ydl.download([url])
        log_signal.emit("Download and merge complete.")
