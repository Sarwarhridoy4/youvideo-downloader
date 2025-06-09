
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
