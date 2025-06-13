import platform
import subprocess
import shutil
import sys
import os
import tempfile
import urllib.request
import zipfile
from PySide6.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
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


# --- Terminal detection and runner for Linux ---
def detect_linux_terminal():
    terminals = [
        "gnome-terminal",
        "konsole",
        "xfce4-terminal",
        "xterm",
        "lxterminal",
        "mate-terminal",
        "tilix",
        "alacritty",
    ]
    for term in terminals:
        if shutil.which(term):
            return term
    return None


def run_command_in_linux_terminal(terminal, command, log):
    try:
        if terminal in ["gnome-terminal", "mate-terminal", "tilix"]:
            # Removed exec bash to auto close terminal after done
            subprocess.Popen([terminal, "--", "bash", "-c", command])
        elif terminal == "konsole":
            subprocess.Popen([terminal, "-e", "bash", "-c", command])
        elif terminal in ["xfce4-terminal", "xterm", "lxterminal"]:
            subprocess.Popen([terminal, "-e", f"bash -c '{command}'"])
        elif terminal == "alacritty":
            subprocess.Popen([terminal, "-e", "bash", "-c", command])
        else:
            log(f"⚠️ Unsupported Linux terminal: {terminal}")
            return False
        log(f"🖥️ Running install command in {terminal}...")
        return True
    except Exception as e:
        log(f"❌ Failed to run command in terminal {terminal}: {e}")
        return False


def install_ffmpeg_linux(log):
    package_manager = detect_linux_package_manager()
    if not package_manager:
        log("Unsupported package manager. Please install FFmpeg manually.")
        return False

    install_cmd_map = {
        "apt": "sudo apt update && sudo apt install -y ffmpeg",
        "dnf": "sudo dnf install -y ffmpeg",
        "pacman": "sudo pacman -Sy --noconfirm ffmpeg",
    }
    command = install_cmd_map.get(package_manager)
    if not command:
        log("Unsupported package manager command. Please install FFmpeg manually.")
        return False

    terminal = detect_linux_terminal()
    if terminal:
        # Launch install in terminal for interactive sudo password input
        success = run_command_in_linux_terminal(terminal, command, log)
        if success:
            log("✅ FFmpeg install command launched in terminal. Please complete installation there.")
            return True
        else:
            log("❌ Failed to launch terminal for installation.")
            return False
    else:
        log("⚠️ No terminal emulator found. Attempting silent install (may fail)...")
        try:
            if package_manager == "apt":
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
            elif package_manager == "dnf":
                subprocess.run(["sudo", "dnf", "install", "-y", "ffmpeg"], check=True)
            elif package_manager == "pacman":
                subprocess.run(["sudo", "pacman", "-Sy", "--noconfirm", "ffmpeg"], check=True)
            log("✅ FFmpeg installed successfully.")
            return True
        except Exception as e:
            log(f"❌ Linux FFmpeg install failed: {e}")
            return False


# --- Terminal runner for macOS ---
def run_command_in_macos_terminal(command, log):
    try:
        # AppleScript to open Terminal and run command, then auto-close the window
        # We remove the read/wait command so terminal auto closes after command finishes
        applescript = f'''
        tell application "Terminal"
            activate
            do script "{command}"
        end tell
        '''
        subprocess.Popen(["osascript", "-e", applescript])
        log("🖥️ Running install command in macOS Terminal...")
        return True
    except Exception as e:
        log(f"❌ Failed to run command in macOS Terminal: {e}")
        return False


def install_ffmpeg_mac(log):
    command = "brew install ffmpeg"
    return run_command_in_macos_terminal(command, log)


# --- Terminal runner for Windows ---
def run_command_in_windows_terminal(command, log):
    try:
        # Use powershell to open new window and run the command, close window after done (no -NoExit)
        powershell_path = shutil.which("powershell.exe") or "powershell"
        subprocess.Popen([
            powershell_path,
            "-Command",
            command
        ])
        log("🖥️ Running install command in Windows PowerShell...")
        return True
    except Exception as e:
        log(f"❌ Failed to run command in PowerShell: {e}")
        try:
            # fallback to cmd.exe, window will auto-close after execution (no /k)
            subprocess.Popen([
                "cmd.exe",
                "/c",
                command
            ])
            log("🖥️ Running install command in Windows cmd...")
            return True
        except Exception as e2:
            log(f"❌ Failed to run command in cmd.exe: {e2}")
            return False


def install_ffmpeg_windows(log):
    if shutil.which("winget"):
        command = ('winget install --id Gyan.FFmpeg -e '
                   '--accept-package-agreements --accept-source-agreements')
        success = run_command_in_windows_terminal(command, log)
        if success:
            log("✅ FFmpeg install command launched in Windows terminal via winget.")
            return True
        else:
            log("❌ winget terminal launch failed, falling back to manual download...")

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


# --- UI style and dialog helpers ---

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


# --- Main ensure function ---

def ensure_ffmpeg(log_signal=None, parent=None):
    def log(msg):
        if log_signal:
            try:
                log_signal(msg)
            except Exception:
                pass

    if is_ffmpeg_available():
        try:
            output = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            version_line = output.stdout.splitlines()[0]
            log(f"✅ FFmpeg found: {version_line}")
        except Exception:
            log("✅ FFmpeg found")
        return True

    # Prompt user
    if parent:
        if not prompt_user_install_ffmpeg():
            log("User declined FFmpeg installation.")
            return False
    else:
        print("FFmpeg is not installed. Please install FFmpeg and try again.")
        return False

    system = platform.system()
    log(f"Detected platform: {system}")

    progress_dialog = None
    if parent:
        progress_dialog = InstallProgressDialog(parent=parent)
        progress_dialog.show()

    success = False
    try:
        if system == "Linux":
            success = install_ffmpeg_linux(log)
        elif system == "Darwin":  # macOS
            success = install_ffmpeg_mac(log)
        elif system == "Windows":
            success = install_ffmpeg_windows(log)
        else:
            log("Unsupported OS. Please install FFmpeg manually.")
    finally:
        if progress_dialog:
            progress_dialog.close()

    if not success:
        log("FFmpeg installation failed or was cancelled.")
        if parent:
            QMessageBox.critical(parent, "Error", "FFmpeg installation failed.\nPlease install it manually.")
    else:
        log("FFmpeg installation process completed (check your terminal).")

    return success


# Example usage (for testing, remove or adapt in your app)
# if __name__ == "__main__":
#     def logger(msg):
#         print(msg)

#     app = QApplication([])
#     ensure_ffmpeg(log_signal=logger)
#     app.exec()
