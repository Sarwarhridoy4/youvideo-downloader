import platform
import subprocess
import shutil
import sys
import os
import tempfile
import urllib.request
import zipfile
from PyQt6.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics
from utils.pathfinder import resource_path


def is_ffmpeg_available():
    return shutil.which("ffmpeg") is not None


def detect_linux_package_manager():
    if shutil.which("apt"):
        return "apt"
    elif shutil.which("dnf"):
        return "dnf"
    elif shutil.which("pacman"):
        return "pacman"
    return None


def install_ffmpeg_linux(log):
    package_manager = detect_linux_package_manager()
    try:
        if package_manager == "apt":
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
        elif package_manager == "dnf":
            subprocess.run(["sudo", "dnf", "install", "-y", "ffmpeg"], check=True)
        elif package_manager == "pacman":
            subprocess.run(["sudo", "pacman", "-Sy", "--noconfirm", "ffmpeg"], check=True)
        else:
            log("Unsupported package manager. Please install FFmpeg manually.")
            return False
        log("✅ FFmpeg installed successfully.")
        return True
    except Exception as e:
        log(f"❌ Linux FFmpeg install failed: {e}")
        return False


def install_ffmpeg_mac(log):
    try:
        subprocess.run(["brew", "install", "ffmpeg"], check=True)
        log("✅ FFmpeg installed successfully.")
        return True
    except Exception as e:
        log(f"❌ macOS FFmpeg install failed: {e}")
        return False


def install_ffmpeg_windows(log):
    if shutil.which("winget"):
        try:
            subprocess.run([
                "winget", "install", "--id", "Gyan.FFmpeg", "-e",
                "--accept-package-agreements", "--accept-source-agreements"
            ], check=True)
            log("✅ FFmpeg installed via winget.")
            return True
        except Exception as e:
            log(f"❌ winget failed: {e}")

    try:
        log("Downloading FFmpeg zip from gyan.dev...")
        zip_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        tmp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(tmp_dir, "ffmpeg.zip")
        urllib.request.urlretrieve(zip_url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)

        for root, _, files in os.walk(tmp_dir):
            if "ffmpeg.exe" in files:
                ffmpeg_exe = os.path.join(root, "ffmpeg.exe")
                shutil.copy(ffmpeg_exe, os.path.join(os.getcwd(), "ffmpeg.exe"))
                log("✅ FFmpeg downloaded and placed in working directory.")
                return True
        log("⚠️ Failed to locate ffmpeg.exe in extracted zip.")
        return False
    except Exception as e:
        log(f"❌ Fallback FFmpeg download failed: {e}")
        return False


def apply_neumorphism_popup_style(widget):
    widget.setStyleSheet("""
    QMessageBox {
        background-color: #0f0f0f;
        color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
        border-radius: 14px;
        border: 1px solid #18191c;
        padding: 20px;
    }

    QLabel {
        color: #ffffff;
        font-size: 14px;
    }

    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23242a, stop:1 #18191c);
        color: #ffffff;
        padding: 12px 24px;
        margin: 8px;
        border: 2px solid #23242a;
        border-radius: 10px;
        font-weight: 500;
        font-size: 16px;
        min-width: 120px;
    }

    QPushButton:hover {
        background-color: #23242a;
        color: #ff5e62;
        border: 2px solid #ff5e62;
    }

    QPushButton:pressed {
        background-color: #18191c;
        color: #ff0000;
        border: 2px solid #ff0000;
    }
    """)


def apply_dynamic_width(msg_box: QMessageBox):
    font = msg_box.font()
    fm = QFontMetrics(font)
    lines = msg_box.text().splitlines()
    max_width = max(fm.horizontalAdvance(line) for line in lines)
    msg_box.setFixedWidth(min(800, max_width + 160))  # 160 for buttons/padding


def prompt_user_install_ffmpeg():
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle("FFmpeg Not Found")
    msg_box.setText("FFmpeg is not installed.\nWould you like to install it now?")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    apply_neumorphism_popup_style(msg_box)
    apply_dynamic_width(msg_box)
    return msg_box.exec() == QMessageBox.StandardButton.Yes


class InstallProgressDialog(QProgressDialog):
    def __init__(self, title="Installing FFmpeg...", parent=None):
        super().__init__("Installing FFmpeg, please wait...", None, 0, 0, parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setCancelButton(None)
        self.setMinimumDuration(0)
        self.setValue(0)
        try:
            qss_path = resource_path("assets/qss/progress.qss")
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass


def ensure_ffmpeg(log_signal=None, parent=None):
    def log(msg):
        if log_signal:
            try:
                log_signal(msg)
            except:
                pass

    if is_ffmpeg_available():
        try:
            output = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
            log("✅ FFmpeg is installed:\n" + output.stdout.splitlines()[0])
            return True
        except Exception as e:
            log(f"⚠️ FFmpeg check failed: {e}")
            return False

    log("❌ FFmpeg not found on this system.")
    if not prompt_user_install_ffmpeg():
        log("User declined installation.")
        return False

    current_platform = platform.system().lower()
    progress_dialog = InstallProgressDialog(parent=parent)
    progress_dialog.setLabelText("Installing FFmpeg, please wait...")
    progress_dialog.show()
    QApplication.processEvents()

    install_success = False
    if current_platform == "windows":
        install_success = install_ffmpeg_windows(log)
    elif current_platform == "linux":
        install_success = install_ffmpeg_linux(log)
    elif current_platform == "darwin":
        install_success = install_ffmpeg_mac(log)

    progress_dialog.close()

    msgbox_parent = parent if parent else QApplication.activeWindow()
    if install_success:
        msg = QMessageBox(msgbox_parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("FFmpeg Installed")
        msg.setText("FFmpeg was installed successfully!\nWould you like to restart the app now?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        apply_neumorphism_popup_style(msg)
        apply_dynamic_width(msg)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            QApplication.quit()
            subprocess.Popen([sys.executable] + sys.argv)
            sys.exit(0)
        return True
    else:
        msg = QMessageBox(msgbox_parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("FFmpeg Installation Failed")
        msg.setText("Automatic installation failed.\nPlease install FFmpeg manually.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        apply_neumorphism_popup_style(msg)
        apply_dynamic_width(msg)
        msg.exec()
        return False
