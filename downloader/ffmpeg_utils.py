import subprocess
import platform
import shutil
from PyQt6.QtWidgets import QProgressDialog, QApplication, QMessageBox
from PyQt6.QtCore import Qt
import sys

from utils.pathfinder import resource_path


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


class InstallProgressDialog(QProgressDialog):
    def __init__(self, title="Installing FFmpeg...", parent=None):
        super().__init__("Installing FFmpeg, please wait...", None, 0, 0, parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setCancelButton(None)
        self.setMinimumDuration(0)
        self.setValue(0)
        # Load neomorphism style from assets/qss/progress.qss
        qss_path = resource_path("assets/qss/progress.qss")
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load progress.qss: {e}")

def apply_neumorphism_popup_style(widget):
    # Neumorphism style for QMessageBox and popups
    qss = """
    QMessageBox, QDialog {
        background-color: #18191c;
        color: #fff;
        border-radius: 16px;
        border: 2px solid #23242a;
        font-size: 16px;
        font-family: 'Segoe UI', sans-serif;
        padding: 16px;
    }
    QMessageBox QLabel, QDialog QLabel {
        color: #fff;
        font-size: 16px;
    }
    QMessageBox QPushButton, QDialog QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23242a, stop:1 #18191c);
        color: #fff;
        border: 2px solid #23242a;
        border-radius: 10px;
        padding: 8px 28px;
        font-size: 15px;
        font-weight: 500;
        margin: 8px 12px;
    }
    QMessageBox QPushButton:hover, QDialog QPushButton:hover {
        background-color: #23242a;
        color: #ff5e62;
        border: 2px solid #ff5e62;
    }
    QMessageBox QPushButton:pressed, QDialog QPushButton:pressed {
        background-color: #18191c;
        color: #ff0000;
        border: 2px solid #ff0000;
    }
    """
    widget.setStyleSheet(qss)


def ensure_ffmpeg(log_signal=None, parent=None):
    """
    Ensures that FFmpeg is installed and available on the system.

    This function checks if FFmpeg is present in the system's PATH. If not found, it attempts to guide the user through the installation process, providing platform-specific instructions or attempting automated installation using available package managers (winget for Windows, apt for Linux, Homebrew for macOS). If installation is successful or FFmpeg is already present, it verifies the installation by running `ffmpeg -version`.

    Args:
        log_signal (callable, optional): A function to receive log messages (e.g., for UI display). If not provided, logging is suppressed.

    Returns:
        bool: True if FFmpeg is installed and accessible, False otherwise.
    """
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
            return False

        current_platform = platform.system().lower()
        progress_dialog = InstallProgressDialog(parent=parent)
        progress_dialog.setLabelText("Installing FFmpeg, please wait...")
        progress_dialog.show()
        QApplication.processEvents()

        install_success = False
        error_msg = ""
        try:
            if current_platform == "windows":
                result = subprocess.run(
                    ["winget", "--version"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    log("Attempting to install FFmpeg using winget...")
                    progress_dialog.setLabelText("Downloading and installing FFmpeg via winget...")
                    QApplication.processEvents()
                    try:
                        subprocess.run(
                            ["winget", "install", "--id", "Gyan.FFmpeg", "-e", "--accept-package-agreements", "--accept-source-agreements"],
                            check=True
                        )
                        install_success = True
                    except Exception as e:
                        error_msg = f"Failed to install FFmpeg via winget: {e}"
                else:
                    error_msg = "winget is not available on your system."
            elif current_platform == "linux":
                log("Attempting to install FFmpeg using apt...")
                progress_dialog.setLabelText("Downloading and installing FFmpeg via apt...")
                QApplication.processEvents()
                try:
                    subprocess.run(["sudo", "apt", "update"], check=True)
                    subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
                    install_success = True
                except Exception as e:
                    error_msg = f"Failed to install FFmpeg via apt: {e}"
            elif current_platform == "darwin":
                log("Attempting to install FFmpeg using Homebrew...")
                progress_dialog.setLabelText("Downloading and installing FFmpeg via Homebrew...")
                QApplication.processEvents()
                try:
                    subprocess.run(["brew", "install", "ffmpeg"], check=True)
                    install_success = True
                except Exception as e:
                    error_msg = f"Failed to install FFmpeg via Homebrew: {e}"
            else:
                error_msg = "Unsupported platform for automatic installation."
        finally:
            progress_dialog.close()

        # Neumorphism style for popups
        msgbox_parent = parent if parent else QApplication.activeWindow()
        if install_success:
            msg = QMessageBox(msgbox_parent)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("FFmpeg Installed")
            msg.setText("FFmpeg was installed successfully!\n\nWould you like to restart the application now?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            apply_neumorphism_popup_style(msg)
            reply = msg.exec()
            if reply == QMessageBox.StandardButton.Yes:
                QApplication.quit()
                subprocess.Popen([sys.executable] + sys.argv)
                sys.exit(0)
            return False
        else:
            msg = QMessageBox(msgbox_parent)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("FFmpeg Installation Failed")
            msg.setText(f"Automatic installation failed.\n\n{error_msg}\n\nPlease install FFmpeg manually.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            apply_neumorphism_popup_style(msg)
            msg.exec()
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
