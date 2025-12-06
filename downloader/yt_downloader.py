"""
yt_downloader.py – 2025-12-06 Enhanced Edition
-----------------------------------------------
Improvements:
• Robust error handling with detailed messages
• Dual time display (elapsed + remaining)
• ALL qualities captured (including premium/1080p60/1440p/4K)
• Formats sorted ASCENDING (lowest to highest quality)
• Progress tracking with ETA
"""

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError as YtdlpDownloadError, ExtractorError
import os
import time
from typing import Optional, Callable


class DownloadError(Exception):
    """Custom exception for download errors"""
    pass


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
        "listformats": True,  # Get comprehensive format list
        "no_warnings": True,
        "socket_timeout": 30,
        # Don't skip any formats - get everything
        "youtube_include_dash_manifest": True,
        "youtube_include_hls_manifest": True,
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                raise DownloadError("Could not extract video information")
            
            formats = []
            seen_format_ids = set()
            
            for f in info.get("formats", []):
                format_id = f.get("format_id")
                
                # Skip duplicates
                if not format_id or format_id in seen_format_ids:
                    continue
                
                seen_format_ids.add(format_id)
                
                # Get format details
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
                
                # Skip if neither video nor audio
                if vcodec == "none" and acodec == "none":
                    continue
                
                # Determine stream type
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
                
                # Calculate quality score for sorting
                # Higher resolution, higher fps, higher bitrate = better
                quality_score = (
                    (height * 10000) +      # Height is most important
                    (fps * 100) +            # FPS second
                    (tbr if tbr else vbr)    # Bitrate third
                )
                
                # Build human-readable quality label
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
                
                # Add to formats list
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
                    # Keep original data
                    "_raw": f
                })
            
            # Sort ASCENDING (lowest quality first, highest last)
            formats.sort(key=lambda x: x.get("_quality_score", 0))
            
            return formats
            
    except ExtractorError as e:
        raise DownloadError(f"Failed to extract video info: {str(e)}")
    except Exception as e:
        raise DownloadError(f"Unexpected error fetching formats: {str(e)}")


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
        
        # Get video formats only (we'll merge with best audio)
        video_formats = [
            f for f in formats
            if f["stream_type"] in ("video", "combined")
        ]
        
        if not video_formats:
            return "bestvideo+bestaudio/best"
        
        # Get the LAST item (highest quality due to ascending sort)
        best = video_formats[-1]
        
        # If it's a combined stream, use it directly
        if best["stream_type"] == "combined":
            return best["format_id"]
        
        # Otherwise, merge with best audio
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
        # Create display string
        if f["stream_type"] == "video":
            display_str = f"{f['quality_label']} ({f['vcodec']}) [video only]"
        elif f["stream_type"] == "audio":
            display_str = f"{f['quality_label']} ({f['acodec']})"
        else:  # combined
            display_str = f"{f['quality_label']} ({f['vcodec']}+{f['acodec']})"
        
        # Add filesize if available
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
                if not entry:  # Skip None entries (deleted/private videos)
                    continue
                
                vid_id = entry.get("id") or entry.get("url", "")
                title = entry.get("title") or "Untitled"
                duration = entry.get("duration", 0)
                
                # Build full URL
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
    """Tracks download progress with dual time display"""
    
    def __init__(self):
        self.start_time = time.time()
        self.last_update = 0
    
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


def download_and_merge(
    url: str,
    format_code: str,
    output_path: str,
    progress_hook: Callable,
    log_signal
) -> None:
    """
    Download video with format code + best audio, then merge to MP4.
    
    Args:
        url: Video URL
        format_code: Format ID or "best"
        output_path: Directory to save file
        progress_hook: Callback for progress updates (receives dict)
        log_signal: Signal for logging messages
    
    Raises:
        DownloadError: If download fails
    """
    tracker = ProgressTracker()
    
    def enhanced_progress_hook(d):
        """Enhanced progress hook with dual time display"""
        try:
            status = d.get("status", "")
            
            if status == "downloading":
                downloaded = d.get("downloaded_bytes", 0)
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                speed = d.get("speed", 0) or 0
                
                elapsed = tracker.get_elapsed()
                remaining = tracker.get_remaining(speed, total, downloaded)
                
                # Add timing info to the dict
                d["elapsed_str"] = elapsed
                d["remaining_str"] = remaining
                d["dual_time"] = f"{elapsed} / {remaining}"
                
                # Add percentage
                if total > 0:
                    d["percent"] = (downloaded / total) * 100
                
            elif status == "finished":
                elapsed = tracker.get_elapsed()
                d["elapsed_str"] = elapsed
                d["dual_time"] = f"Completed in {elapsed}"
                d["percent"] = 100
            
            # Call original hook
            progress_hook(d)
            
        except Exception as e:
            log_signal.emit(f"Progress tracking error: {str(e)}")
    
    # Validate output path
    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            raise DownloadError(f"Could not create output directory: {str(e)}")
    
    # Build format string
    if format_code and format_code != "best":
        # If format doesn't have audio, merge with best audio
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
        "quiet": True,
        "no_warnings": False,
        "merge_output_format": "mp4",
        "socket_timeout": 30,
        "retries": 5,
        "fragment_retries": 5,
        "file_access_retries": 3,
        # Enable all manifest types for premium formats
        "youtube_include_dash_manifest": True,
        "youtube_include_hls_manifest": True,
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
        "postprocessor_args": [
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",  # Good audio quality
            "-movflags", "faststart"
        ],
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            log_signal.emit(f"Starting download with format: {format_str}")
            log_signal.emit(f"Saving to: {output_path}")
            
            # Reset tracker
            tracker.start_time = time.time()
            
            # Download
            ydl.download([url])
            
            elapsed = tracker.get_elapsed()
            log_signal.emit(f"✓ Download complete! (Total time: {elapsed})")
            
    except YtdlpDownloadError as e:
        raise DownloadError(f"Download failed: {str(e)}")
    except ExtractorError as e:
        raise DownloadError(f"Extraction failed: {str(e)}")
    except Exception as e:
        raise DownloadError(f"Unexpected error during download: {str(e)}")


# ─────────────────────── batch download ─────────────────────
def download_playlist(
    playlist_url: str,
    output_path: str,
    progress_hook: Callable,
    log_signal,
    max_videos: Optional[int] = None,
    quality: str = "best"
) -> None:
    """
    Download entire playlist with specified quality.
    
    Args:
        playlist_url: Playlist URL
        output_path: Directory to save files
        progress_hook: Progress callback
        log_signal: Logging signal
        max_videos: Optional limit on number of videos
        quality: "best", "worst", or specific format code
    """
    try:
        # Get playlist items
        playlist_items = f"1-{max_videos}" if max_videos else None
        videos = get_playlist_videos(playlist_url, playlist_items)
        
        if not videos:
            raise DownloadError("No videos found in playlist")
        
        log_signal.emit(f"Found {len(videos)} videos in playlist")
        log_signal.emit(f"Quality setting: {quality}\n")
        
        # Download each video
        success_count = 0
        failed_count = 0
        
        for idx, video in enumerate(videos, 1):
            log_signal.emit(f"[{idx}/{len(videos)}] {video['title']}")
            
            try:
                # Determine format code
                if quality == "best":
                    fmt = get_best_format(video['url'])
                elif quality == "worst":
                    formats = get_formats(video['url'])
                    video_fmts = [f for f in formats if f["stream_type"] in ("video", "combined")]
                    fmt = video_fmts[0]["format_id"] if video_fmts else "worst"
                else:
                    fmt = quality
                
                log_signal.emit(f"  Format: {fmt}")
                
                # Download
                download_and_merge(
                    video['url'],
                    fmt,
                    output_path,
                    progress_hook,
                    log_signal
                )
                
                success_count += 1
                
            except Exception as e:
                log_signal.emit(f"  ✗ Failed: {str(e)}\n")
                failed_count += 1
                continue
        
        # Summary
        log_signal.emit(f"\n{'='*50}")
        log_signal.emit(f"Playlist download complete!")
        log_signal.emit(f"✓ Success: {success_count}/{len(videos)}")
        if failed_count > 0:
            log_signal.emit(f"✗ Failed: {failed_count}/{len(videos)}")
        log_signal.emit(f"{'='*50}")
        
    except Exception as e:
        raise DownloadError(f"Playlist download failed: {str(e)}")