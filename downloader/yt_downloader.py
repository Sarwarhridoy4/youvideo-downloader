"""
yt_downloader.py – 2025-12-06 Enhanced Edition (Cross-Platform Downloads)
------------------------------------------------------------------------
Improvements:
• Default download location set to system Downloads folder (Windows/Linux/Mac)
• All completion messages shown in text log (NO popups)
• Robust error handling with detailed messages
• Dual time display (elapsed + remaining)
• ALL qualities captured (including premium/1080p60/1440p/4K)
• Formats sorted ASCENDING (lowest to highest quality)
• Progress tracking with ETA
• Optimized performance with smart state tracking
"""

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError as YtdlpDownloadError, ExtractorError
import os
import time
from pathlib import Path
from typing import Optional, Callable
from utils.yt_dlp_compat import get_youtube_extractor_args


class DownloadError(Exception):
    """Custom exception for download errors"""
    pass


# ───────────────────────── yt-dlp config ──────────────────────────
# Workaround for YouTube 403 errors tied to android_sdkless formats.
# Exclude the android_sdkless client until users update yt-dlp. See
# https://github.com/yt-dlp/yt-dlp/issues/15712
YOUTUBE_EXTRACTOR_ARGS = get_youtube_extractor_args()


# ───────────────────────── System Paths ──────────────────────────
def get_default_download_path() -> str:
    """
    Get the default Downloads folder path for the current OS.
    
    Returns:
        Path to Downloads folder (Windows/Linux/Mac compatible)
        Example outputs:
        - Windows: C:\\Users\\username\\Downloads
        - Linux: /home/username/Downloads
        - Mac: /Users/username/Downloads
    """
    home = Path.home()
    
    # Try to find Downloads folder
    downloads_folder = home / "Downloads"
    
    # Fallback for some systems where it might be localized
    if not downloads_folder.exists():
        # Try common alternatives
        alternatives = [
            home / "downloads",  # lowercase
            home / "Download",   # singular
        ]
        
        for alt in alternatives:
            if alt.exists():
                downloads_folder = alt
                break
        else:
            # If none exist, create Downloads folder (with capital D)
            downloads_folder = home / "Downloads"
            downloads_folder.mkdir(parents=True, exist_ok=True)
    
    # Return as string with forward slashes normalized
    return str(downloads_folder).replace("\\", "/")


# ───────────────────────── formats ──────────────────────────
def get_formats(url: str) -> list[dict]:
    """
    Return ALL available formats including premium qualities.
    
    Captures:
    • Standard qualities (144p - 720p)
    • Premium qualities (1080p, 1080p60, 1440p, 1440p60, 4K, 4K60)
    • All audio formats (including high-bitrate)
    • Both video+audio combined and separate streams
    
    Returns formats sorted ASCENDING (worst to best quality).
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "listformats": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "noplaylist": True,  # Only get formats for single video, not entire playlist
        "youtube_include_dash_manifest": True,
        "youtube_include_hls_manifest": True,
    }
    if YOUTUBE_EXTRACTOR_ARGS:
        ydl_opts["extractor_args"] = YOUTUBE_EXTRACTOR_ARGS
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                raise DownloadError("Could not extract video information")
            
            formats = []
            seen_format_ids = set()
            
            for f in info.get("formats", []):
                format_id = f.get("format_id")
                
                if not format_id or format_id in seen_format_ids:
                    continue
                
                seen_format_ids.add(format_id)
                
                vcodec = f.get("vcodec", "none")
                acodec = f.get("acodec", "none")
                ext = f.get("ext", "unknown")
                protocol = f.get("protocol", "https")
                height = f.get("height", 0) or 0
                width = f.get("width", 0) or 0
                fps = f.get("fps", 0) or 0
                tbr = f.get("tbr", 0) or 0
                vbr = f.get("vbr", 0) or 0
                abr = f.get("abr", 0) or 0
                filesize = f.get("filesize") or f.get("filesize_approx", 0)
                format_note = f.get("format_note", "")
                
                if vcodec == "none" and acodec == "none":
                    continue
                
                has_video = vcodec != "none"
                has_audio = acodec != "none"
                
                if has_video and has_audio:
                    stream_type = "combined"
                elif has_video:
                    stream_type = "video"
                elif has_audio:
                    stream_type = "audio"
                else:
                    continue
                
                quality_score = (
                    (height * 10000) +
                    (fps * 100) +
                    (tbr if tbr else vbr)
                )
                
                if has_video:
                    quality_label = f"{height}p"
                    if fps > 30:
                        quality_label += f"{fps}"
                    if format_note and "HDR" in format_note:
                        quality_label += " HDR"
                    if format_note and "premium" in format_note.lower():
                        quality_label += " (Premium)"
                elif has_audio:
                    quality_label = f"Audio {int(abr)}kbps" if abr else "Audio"
                else:
                    quality_label = "Unknown"
                
                formats.append({
                    "format_id": format_id,
                    "ext": ext,
                    "quality_label": quality_label,
                    "resolution": f"{width}x{height}" if has_video else "N/A",
                    "fps": fps if has_video else None,
                    "vcodec": vcodec,
                    "acodec": acodec,
                    "tbr": tbr,
                    "vbr": vbr,
                    "abr": abr,
                    "filesize": filesize,
                    "filesize_mb": round(filesize / (1024 * 1024), 2) if filesize else None,
                    "protocol": protocol,
                    "format_note": format_note,
                    "stream_type": stream_type,
                    "_quality_score": quality_score,
                    "_raw": f
                })
            
            formats.sort(key=lambda x: x.get("_quality_score", 0))
            
            return formats
            
    except ExtractorError as e:
        raise DownloadError(f"Failed to extract video info: {str(e)}")
    except Exception as e:
        raise DownloadError(f"Unexpected error fetching formats: {str(e)}")


def get_video_info(url: str) -> dict:
    """
    Get basic video information including title, thumbnail, duration, etc.
    If URL is a playlist, returns info for the first video.
    
    Returns:
        Dict with video info: title, thumbnail_url, duration, uploader, etc.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "playlist_items": "1",  # Only get first item if playlist
        "extract_flat": False,  # Don't flatten playlist info
    }
    if YOUTUBE_EXTRACTOR_ARGS:
        ydl_opts["extractor_args"] = YOUTUBE_EXTRACTOR_ARGS
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                raise DownloadError("Could not extract video information")
            
            # If it's a playlist, get the first entry
            if info.get("_type") == "playlist" and info.get("entries"):
                video_info = info["entries"][0]
            else:
                video_info = info
            
            # Get the best thumbnail
            thumbnail_url = None
            thumbnails = video_info.get("thumbnails", [])
            if thumbnails:
                # Sort by preference: higher resolution first
                thumbnails.sort(key=lambda x: (x.get("height", 0) * x.get("width", 0)), reverse=True)
                thumbnail_url = thumbnails[0].get("url")
            
            return {
                "title": video_info.get("title", "Unknown Title"),
                "thumbnail_url": thumbnail_url,
                "duration": video_info.get("duration", 0),
                "uploader": video_info.get("uploader", "Unknown"),
                "view_count": video_info.get("view_count", 0),
                "upload_date": video_info.get("upload_date", ""),
                "description": video_info.get("description", "")[:200] + "..." if video_info.get("description") else "",
            }
            
    except ExtractorError as e:
        raise DownloadError(f"Failed to extract video info: {str(e)}")
    except Exception as e:
        raise DownloadError(f"Unexpected error fetching video info: {str(e)}")


def get_best_format(url: str) -> Optional[str]:
    """
    Get the BEST available format code (highest quality).
    
    Prioritizes:
    1. Highest resolution (4K > 1440p > 1080p > 720p...)
    2. Highest FPS (60fps > 30fps)
    3. Premium/HDR variants when available
    """
    try:
        formats = get_formats(url)
        
        if not formats:
            return "bestvideo+bestaudio/best"
        
        video_formats = [
            f for f in formats
            if f["stream_type"] in ("video", "combined")
        ]
        
        if not video_formats:
            return "bestvideo+bestaudio/best"
        
        best = video_formats[-1]
        
        if best["stream_type"] == "combined":
            return best["format_id"]
        
        return f"{best['format_id']}+bestaudio"
        
    except Exception:
        return "bestvideo+bestaudio/best"


def get_format_display_info(formats: list[dict]) -> list[dict]:
    """
    Get simplified format info for UI display.
    
    Returns list sorted ASCENDING (lowest to highest quality).
    """
    display_formats = []
    
    for f in formats:
        if f["stream_type"] == "video":
            display_str = f"{f['quality_label']} ({f['vcodec']}) [video only]"
        elif f["stream_type"] == "audio":
            display_str = f"{f['quality_label']} ({f['acodec']})"
        else:
            display_str = f"{f['quality_label']} ({f['vcodec']}+{f['acodec']})"
        
        if f["filesize_mb"]:
            display_str += f" - {f['filesize_mb']}MB"
        
        display_formats.append({
            "format_id": f["format_id"],
            "display": display_str,
            "quality_label": f["quality_label"],
            "stream_type": f["stream_type"],
            "resolution": f["resolution"],
            "fps": f["fps"],
            "filesize_mb": f["filesize_mb"]
        })
    
    return display_formats


# ───────────────────────── playlist ─────────────────────────
def get_playlist_videos(url: str, playlist_items: Optional[str] = None) -> list[dict]:
    """
    Fast, sliced playlist listing with error handling.
    
    Args:
        url: Playlist URL
        playlist_items: Optional slice (e.g., "1-5", "7,9,10")
    
    Returns:
        List of dicts with 'title', 'url', and 'id' keys
    """
    ydl_opts = {
        "quiet": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "socket_timeout": 30,
        "no_warnings": True,
    }
    
    if playlist_items:
        ydl_opts["playlist_items"] = playlist_items
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                raise DownloadError("Could not extract playlist information")
            
            videos = []
            entries = info.get("entries", [])
            
            for entry in entries:
                if not entry:
                    continue
                
                vid_id = entry.get("id") or entry.get("url", "")
                title = entry.get("title") or "Untitled"
                duration = entry.get("duration", 0)
                
                if vid_id and not vid_id.startswith("http"):
                    vid_url = f"https://www.youtube.com/watch?v={vid_id}"
                else:
                    vid_url = entry.get("url", "")
                
                if vid_url:
                    videos.append({
                        "title": title,
                        "url": vid_url,
                        "id": vid_id,
                        "duration": duration
                    })
            
            return videos
            
    except ExtractorError as e:
        raise DownloadError(f"Failed to extract playlist: {str(e)}")
    except Exception as e:
        raise DownloadError(f"Unexpected error fetching playlist: {str(e)}")


# ─────────────────────── download / merge ───────────────────
class ProgressTracker:
    """Tracks download progress with dual time display and state management"""
    
    def __init__(self):
        self.start_time = time.time()
        self.last_update = 0
        self.finished_count = 0  # Track how many streams finished
        self.is_merging = False  # Track if we're in merge phase
        self.download_complete = False  # Track overall completion
        self.current_stream = None  # Track current stream (video/audio/merge)
    
    def format_time(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS or MM:SS format"""
        if seconds < 0:
            return "00:00"
        
        hours, remainder = divmod(int(seconds), 3600)
        mins, secs = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"
    
    def get_elapsed(self) -> str:
        """Get elapsed time"""
        elapsed = time.time() - self.start_time
        return self.format_time(elapsed)
    
    def get_remaining(self, speed: float, total: float, downloaded: float) -> str:
        """Calculate remaining time"""
        if speed <= 0 or total <= 0:
            return "??:??"
        
        remaining_bytes = total - downloaded
        remaining_secs = remaining_bytes / speed
        return self.format_time(remaining_secs)
    
    def reset(self):
        """Reset tracker for new download"""
        self.start_time = time.time()
        self.finished_count = 0
        self.is_merging = False
        self.download_complete = False
        self.current_stream = None


def download_and_merge(
    url: str,
    format_code: str,
    output_path: Optional[str] = None,
    progress_hook: Optional[Callable] = None,
    log_signal = None
) -> None:
    """
    Download video with format code + best audio, then merge to MP4.
    
    ALL completion messages are sent to log_signal (text log).
    NO popup dialogs are triggered from this function.
    
    Args:
        url: Video URL
        format_code: Format ID or "best"
        output_path: Directory to save file (defaults to Downloads folder)
        progress_hook: Callback for progress updates (receives dict)
        log_signal: Signal for logging messages (receives str)
    
    Raises:
        DownloadError: If download fails
    """
    # Use default Downloads folder if no path specified
    if output_path is None:
        output_path = get_default_download_path()
    
    tracker = ProgressTracker()
    
    def enhanced_progress_hook(d):
        """
        Enhanced progress hook with dual time display and smart completion detection.
        Shows progress for BOTH video and audio streams separately.
        Signals completion status via progress_hook for UI updates,
        but ALL text messages go to log_signal only.
        """
        try:
            status = d.get("status", "")
            filename = d.get("filename", "")
            
            if status == "downloading":
                # Detect which stream we're downloading
                if "f" in d:  # yt-dlp includes format info
                    # Determine stream type from filename or format
                    if ".f" in filename:
                        # Extract format ID from filename (e.g., video.fXXX.mp4)
                        if "audio" in filename.lower() or ".m4a" in filename or ".webm" in filename.lower():
                            stream_type = "audio"
                        else:
                            stream_type = "video"
                    else:
                        stream_type = "combined"
                else:
                    stream_type = "unknown"
                
                # Update current stream if changed
                if tracker.current_stream != stream_type:
                    tracker.current_stream = stream_type
                    if log_signal:
                        log_signal.emit(f"📥 Downloading {stream_type}...")
                
                # Reset merge flag if we're downloading again
                tracker.is_merging = False
                
                downloaded = d.get("downloaded_bytes", 0)
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                speed = d.get("speed", 0) or 0
                
                elapsed = tracker.get_elapsed()
                remaining = tracker.get_remaining(speed, total, downloaded)
                
                d["elapsed_str"] = elapsed
                d["remaining_str"] = remaining
                d["dual_time"] = f"{elapsed} / {remaining}"
                d["stream_type"] = stream_type  # Add stream type to progress data
                
                if total > 0:
                    d["percent"] = (downloaded / total) * 100
                else:
                    d["percent"] = 0
                
                # Emit progress for UI (progress bar updates)
                # DO NOT trigger any popups from here
                d["show_popup"] = False  # Explicitly prevent popups
                if progress_hook:
                    progress_hook(d)
                
            elif status == "finished":
                # Increment finished count (video and/or audio stream)
                tracker.finished_count += 1
                
                # Determine what just finished
                if ".f" in filename and not filename.endswith(".mp4"):
                    # This is a partial stream (video or audio)
                    if "audio" in filename.lower() or ".m4a" in filename:
                        stream_finished = "audio"
                    else:
                        stream_finished = "video"
                    
                    # Log to text console only
                    if log_signal:
                        log_signal.emit(f"✓ {stream_finished.capitalize()} stream downloaded")
                    
                    # Emit progress for UI update (NOT for popup)
                    d["stream_type"] = stream_finished
                    d["percent"] = 100
                    d["final_completion"] = False  # Not final yet
                    d["show_popup"] = False  # No popup for partial completion
                    if progress_hook:
                        progress_hook(d)
                    
                elif filename.endswith(".mp4") or filename.endswith(".mkv"):
                    # This is the final merged file
                    if not tracker.download_complete:
                        tracker.download_complete = True
                        tracker.is_merging = False
                        
                        elapsed = tracker.get_elapsed()
                        
                        # ═══════════════════════════════════════════════
                        # LOG COMPLETION MESSAGE (instead of popup)
                        # ═══════════════════════════════════════════════
                        if log_signal:
                            log_signal.emit("=" * 60)
                            log_signal.emit("✅ DOWNLOAD COMPLETE!")
                            log_signal.emit(f"⏱️  Total time: {elapsed}")
                            log_signal.emit(f"📁 Saved to: {output_path}")
                            log_signal.emit(f"📄 File: {os.path.basename(filename)}")
                            log_signal.emit("=" * 60)
                        
                        # Emit progress for UI state update (NOT for popup)
                        d["elapsed_str"] = elapsed
                        d["dual_time"] = f"Completed in {elapsed}"
                        d["percent"] = 100
                        d["stream_type"] = "final"
                        d["final_completion"] = True
                        d["show_popup"] = False  # CRITICAL: No popup dialog
                        if progress_hook:
                            progress_hook(d)
                
            elif status == "error":
                # Log error to console
                error_msg = d.get("error", "Unknown error")
                if log_signal:
                    log_signal.emit(f"❌ Error: {error_msg}")
                
                # Emit error status (NOT for popup)
                d["show_popup"] = False
                if progress_hook:
                    progress_hook(d)
                
        except Exception as e:
            if log_signal:
                log_signal.emit(f"⚠️  Progress tracking error: {str(e)}")
    
    # Validate output path
    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path, exist_ok=True)
            if log_signal:
                log_signal.emit(f"📁 Created output directory: {output_path}")
        except Exception as e:
            raise DownloadError(f"Could not create output directory: {str(e)}")
    
    # Build format string
    if format_code and format_code != "best":
        if "+" not in format_code:
            format_str = f"{format_code}+bestaudio/best"
        else:
            format_str = format_code
    else:
        format_str = "bestvideo+bestaudio/best"
    
    tmpl = os.path.join(output_path, "%(title)s.%(ext)s")
    
    ydl_opts = {
    "format": format_str,
    "outtmpl": tmpl,

    "progress_hooks": [enhanced_progress_hook],

    # ──────────────────────── Output control ────────────────────────
    "quiet": False,                     # ← important: allow more output
    "no_warnings": False,
    "verbose": True,                    # ← crucial: makes yt-dlp log ffmpeg command + some info

    "noplaylist": True,
    "merge_output_format": "mp4",

    "socket_timeout": 30,
    "retries": 5,
    "fragment_retries": 5,
    "file_access_retries": 3,

    "youtube_include_dash_manifest": True,
    "youtube_include_hls_manifest": True,

    # ───────────────────── Post-processing ─────────────────────
    "postprocessors": [
        {
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",   # note: typo in original → "preferredformat"
        }
    ],

    # Better: use dict so args only go to specific postprocessors
    "postprocessor_args": {
        # Applies to Merger + FFmpegVideoConvertor + similar
        "Merger+FFmpegVideoConvertor+default": [
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",   # note: +faststart is correct syntax
            "-loglevel", "info",         # ← more visible output than default
            # Optional (sometimes helps show more): "-stats", "-nostats_period", "1"
        ]
    },

    # NOTE: Keep a single postprocessor_args dict to avoid overriding options.
}
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            if log_signal:
                log_signal.emit("=" * 60)
                log_signal.emit(f"🎬 Starting download")
                log_signal.emit(f"🔧 Format: {format_str}")
                log_signal.emit(f"📁 Output: {output_path}")
                log_signal.emit("=" * 60)
            
            # Reset tracker
            tracker.reset()
            
            # Download
            ydl.download([url])
            
            # Ensure completion is logged if not already done
            if not tracker.download_complete:
                elapsed = tracker.get_elapsed()
                
                if log_signal:
                    log_signal.emit("=" * 60)
                    log_signal.emit("✅ DOWNLOAD COMPLETE!")
                    log_signal.emit(f"⏱️  Total time: {elapsed}")
                    log_signal.emit(f"📁 Saved to: {output_path}")
                    log_signal.emit("=" * 60)
                
                # Emit final status (NOT for popup)
                if progress_hook:
                    progress_hook({
                        "status": "finished",
                        "elapsed_str": elapsed,
                        "dual_time": f"Completed in {elapsed}",
                        "percent": 100,
                        "final_completion": True,
                        "show_popup": False  # No popup
                    })
            
    except YtdlpDownloadError as e:
        if log_signal:
            log_signal.emit(f"❌ Download failed: {str(e)}")
        raise DownloadError(f"Download failed: {str(e)}")
    except ExtractorError as e:
        if log_signal:
            log_signal.emit(f"❌ Extraction failed: {str(e)}")
        raise DownloadError(f"Extraction failed: {str(e)}")
    except Exception as e:
        if log_signal:
            log_signal.emit(f"❌ Unexpected error: {str(e)}")
        raise DownloadError(f"Unexpected error during download: {str(e)}")


# ─────────────────────── batch download ─────────────────────
def download_playlist(
    playlist_url: str,
    output_path: Optional[str] = None,
    progress_hook: Optional[Callable] = None,
    log_signal = None,
    max_videos: Optional[int] = None,
    quality: str = "best"
) -> None:
    """
    Download entire playlist with specified quality.
    
    All completion messages are logged to text console (NO popups).
    
    Args:
        playlist_url: Playlist URL
        output_path: Directory to save files (defaults to Downloads folder)
        progress_hook: Progress callback
        log_signal: Logging signal
        max_videos: Optional limit on number of videos
        quality: "best", "worst", or specific format code
    """
    # Use default Downloads folder if no path specified
    if output_path is None:
        output_path = get_default_download_path()
    
    try:
        playlist_items = f"1-{max_videos}" if max_videos else None
        videos = get_playlist_videos(playlist_url, playlist_items)
        
        if not videos:
            raise DownloadError("No videos found in playlist")
        
        if log_signal:
            log_signal.emit("=" * 60)
            log_signal.emit(f"📋 Playlist: {len(videos)} videos found")
            log_signal.emit(f"🎯 Quality: {quality}")
            log_signal.emit(f"📁 Output: {output_path}")
            log_signal.emit("=" * 60)
        
        success_count = 0
        failed_count = 0
        
        for idx, video in enumerate(videos, 1):
            if log_signal:
                log_signal.emit(f"\n[{idx}/{len(videos)}] {video['title']}")
                log_signal.emit("-" * 60)
            
            try:
                if quality == "best":
                    fmt = get_best_format(video['url'])
                elif quality == "worst":
                    formats = get_formats(video['url'])
                    video_fmts = [f for f in formats if f["stream_type"] in ("video", "combined")]
                    fmt = video_fmts[0]["format_id"] if video_fmts else "worst"
                else:
                    fmt = quality
                
                if log_signal:
                    log_signal.emit(f"🔧 Format: {fmt}")
                
                download_and_merge(
                    video['url'],
                    fmt,
                    output_path,
                    progress_hook,
                    log_signal
                )
                
                success_count += 1
                if log_signal:
                    log_signal.emit(f"✅ Video {idx} complete\n")
                
            except Exception as e:
                if log_signal:
                    log_signal.emit(f"❌ Failed: {str(e)}\n")
                failed_count += 1
                continue
        
        # Final playlist summary (logged, not popup)
        if log_signal:
            log_signal.emit("\n" + "=" * 60)
            log_signal.emit("🎉 PLAYLIST DOWNLOAD COMPLETE!")
            log_signal.emit(f"✅ Successful: {success_count}/{len(videos)}")
            if failed_count > 0:
                log_signal.emit(f"❌ Failed: {failed_count}/{len(videos)}")
            log_signal.emit(f"📁 Location: {output_path}")
            log_signal.emit("=" * 60)
        
    except Exception as e:
        if log_signal:
            log_signal.emit(f"❌ Playlist download failed: {str(e)}")
        raise DownloadError(f"Playlist download failed: {str(e)}")
