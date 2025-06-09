import subprocess
import platform
import shutil
from PyQt6.QtWidgets import QMessageBox


def is_ffmpeg_available():
    return shutil.which("ffmpeg") is not None


def install_ffmpeg_linux(log_signal):
    try:
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
        log_signal.emit("FFmpeg installed successfully.")
        return True
    except Exception as e:
        log_signal.emit(f"Failed to install FFmpeg: {e}")
        return False


def install_ffmpeg_windows(log_signal):
    log_signal.emit("Please install FFmpeg manually from https://ffmpeg.org/download.html and add it to PATH.")
    return False


def install_ffmpeg_mac(log_signal):
    try:
        subprocess.run(["brew", "install", "ffmpeg"], check=True)
        log_signal.emit("FFmpeg installed successfully.")
        return True
    except Exception as e:
        log_signal.emit(f"Failed to install FFmpeg: {e}")
        return False


def prompt_user_install_ffmpeg():
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle("FFmpeg Not Found")
    msg_box.setText("FFmpeg is not installed on your system.\nWould you like to install it automatically?")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    return msg_box.exec() == QMessageBox.StandardButton.Yes


def ensure_ffmpeg(log_signal=None):
    import shutil
    import subprocess

    def log(msg):
        if log_signal:
            try:
                log_signal(msg)  # Call it like a regular function
            except Exception:
                pass  # Optional: log this fallback to console

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        log("❌ FFmpeg not found on this system.")
        current_platform = platform.system().lower()
        if current_platform == "windows":
            log("To install FFmpeg on Windows:\n"
                "Option 1: Download from https://ffmpeg.org/download.html, extract, and add the bin folder to your PATH environment variable.\n"
                "Option 2: If you have winget, run:\n"
                "    winget install Gyan.FFmpeg")
        elif current_platform == "linux":
            log("To install FFmpeg on Linux, run:\n"
                "sudo apt update && sudo apt install -y ffmpeg")
        elif current_platform == "darwin":
            log("To install FFmpeg on macOS, run:\n"
                "brew install ffmpeg")
        else:
            log("Please refer to https://ffmpeg.org/download.html for installation instructions for your platform.")
        return False

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        log("✅ FFmpeg is installed.\n\n" + result.stdout.strip())
        return True
    except Exception as e:
        log(f"⚠️ Error retrieving FFmpeg version info: {e}")
        return False
