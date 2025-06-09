
from yt_dlp import YoutubeDL
import os
from PyQt6.QtWidgets import QMessageBox

def get_formats(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = [
            f for f in info['formats']
            if f.get('format_id') and (
                f.get('vcodec') != 'none' or f.get('acodec') != 'none'
            ) and f['ext'] in ('mp4', 'webm', 'm4a')
        ]
        return formats

def download_and_merge(url, format_code, output_path, progress_hook, log_signal):
    """
    Downloads a video from the given URL using the specified format code, merges the video and audio streams into an MP4 file, and saves it to the specified output path.

    Args:
        url (str): The URL of the video to download.
        format_code (str): The format code specifying the desired video quality/format.
        output_path (str): The directory where the downloaded file will be saved.
        progress_hook (callable): A callback function to handle progress updates during download.
        log_signal (QObject): An object with an 'emit' method for logging messages (typically a Qt signal).

    Raises:
        Any exceptions raised by YoutubeDL during the download or merging process.

    Notes:
        - The function uses youtube-dl (or a compatible fork) for downloading and merging.
        - The output file will be in MP4 format, with video and audio streams merged.
        - Progress and status messages are emitted via the provided log_signal.
    """

    output_file_template = os.path.join(output_path, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': f"{format_code}+bestaudio/best",
        'outtmpl': output_file_template,
        'progress_hooks': [progress_hook],
        'quiet': True,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'postprocessor_args': [
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental'
        ],
    }

    with YoutubeDL(ydl_opts) as ydl:
        log_signal.emit("Starting download...")
        ydl.download([url])
        log_signal.emit("Download and merge complete.")
