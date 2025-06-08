import subprocess
import shutil

def is_ffmpeg_available():
    return shutil.which("ffmpeg") is not None
