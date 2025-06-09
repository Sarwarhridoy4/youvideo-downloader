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
                log_signal(msg)
            except Exception:
                pass

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        log("❌ FFmpeg not found on this system.")
        if not prompt_user_install_ffmpeg():
            current_platform = platform.system().lower()
            if current_platform == "windows":
                log("Please install FFmpeg manually:\n"
                    "Download from https://ffmpeg.org/download.html, extract, and add the bin folder to your PATH environment variable.")
            elif current_platform == "linux":
                log("Please install FFmpeg manually with:\n"
                    "sudo apt update && sudo apt install -y ffmpeg")
            elif current_platform == "darwin":
                log("Please install FFmpeg manually with:\n"
                    "brew install ffmpeg")
            else:
                log("Please refer to https://ffmpeg.org/download.html for installation instructions for your platform.")
            return False

        current_platform = platform.system().lower()
        if current_platform == "windows":
            try:
                result = subprocess.run(
                    ["winget", "--version"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    log("Attempting to install FFmpeg using winget...")
                    try:
                        subprocess.run(
                            ["winget", "install", "--id", "Gyan.FFmpeg", "-e", "--accept-package-agreements", "--accept-source-agreements"],
                            check=True
                        )
                        log("FFmpeg installed successfully via winget. Please restart the application if needed.")
                        return True
                    except Exception as e:
                        log(f"Failed to install FFmpeg via winget: {e}")
                        return False
                else:
                    log("winget is not available on your system.\n"
                        "Please install winget from https://github.com/microsoft/winget-cli/releases or install FFmpeg manually:\n"
                        "Download from https://ffmpeg.org/download.html, extract, and add the bin folder to your PATH environment variable.")
                    return False
            except FileNotFoundError:
                log("winget is not found on your system.\n"
                    "Please install winget from https://github.com/microsoft/winget-cli/releases or install FFmpeg manually:\n"
                    "Download from https://ffmpeg.org/download.html, extract, and add the bin folder to your PATH environment variable.")
                return False
        elif current_platform == "linux":
            log("Attempting to install FFmpeg using apt...")
            try:
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
                log("FFmpeg installed successfully via apt.")
                return True
            except Exception as e:
                log(f"Failed to install FFmpeg via apt: {e}\n"
                    "You may need to install it manually with:\n"
                    "sudo apt update && sudo apt install -y ffmpeg")
                return False
        elif current_platform == "darwin":
            log("Attempting to install FFmpeg using Homebrew...")
            try:
                subprocess.run(["brew", "install", "ffmpeg"], check=True)
                log("FFmpeg installed successfully via Homebrew.")
                return True
            except Exception as e:
                log(f"Failed to install FFmpeg via Homebrew: {e}\n"
                    "You may need to install it manually with:\n"
                    "brew install ffmpeg")
                return False
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
