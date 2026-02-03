from __future__ import annotations

import platform
import shutil

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QMessageBox

from downloader.ffmpeg_utils import (
    get_ffmpeg_version,
    is_ffmpeg_available,
    detect_linux_terminal,
    run_in_linux_terminal,
    run_in_macos_terminal,
    run_in_windows_terminal,
)


class DependencyUpdateThread(QThread):
    log = Signal(str)
    finished = Signal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        ok = False
        try:
            self.log.emit("🔧 Updating system dependencies (FFmpeg + yt-dlp)...")
            ok = self._update_system_dependencies()
        except Exception as e:
            self.log.emit(f"❌ Dependency update failed: {e}")
        self.finished.emit(ok)

    def _update_system_dependencies(self) -> bool:
        system = platform.system()
        managers = self._detect_package_managers()

        if not managers:
            self.log.emit("⚠️ No supported package manager found.")
            return False

        self.log.emit(f"✅ Found package managers: {', '.join(m['name'] for m in managers)}")
        self.log.emit("➡ Will try them in order until one succeeds.")

        for manager in managers:
            name = manager["name"]
            command = manager["command"]
            self.log.emit(f"📦 Trying {name}...")
            if self._run_manager_command(system, name, command):
                self.log.emit(f"✅ {name} succeeded.")
                return True
            self.log.emit(f"⚠️ {name} failed or was cancelled.")

        return False

    def _run_manager_command(self, system: str, name: str, command: str) -> bool:
        try:
            if system == "Linux":
                terminal = detect_linux_terminal()
                if terminal:
                    return run_in_linux_terminal(terminal, command, self.log.emit)
                self.log.emit("⚠️ No terminal emulator found; trying direct execution.")
                return self._run_command_direct(command)
            if system == "Darwin":
                return run_in_macos_terminal(command, self.log.emit)
            if system == "Windows":
                return run_in_windows_terminal(command, self.log.emit)

            self.log.emit(f"⚠️ Unsupported system: {system}")
            return False
        except Exception as e:
            self.log.emit(f"❌ {name} launch failed: {e}")
            return False

    def _run_command_direct(self, command: str) -> bool:
        try:
            self.log.emit(f"▶ {command}")
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if proc.stdout:
                for line in proc.stdout:
                    line = line.strip()
                    if line:
                        self.log.emit(line)
            code = proc.wait()
            if code == 0:
                return True
            self.log.emit(f"⚠️ Command failed with exit code {code}")
            return False
        except Exception as e:
            self.log.emit(f"❌ Direct execution failed: {e}")
            return False

    def _detect_package_managers(self) -> list[dict]:
        system = platform.system()
        managers: list[dict] = []

        if system == "Linux":
            candidates = [
                ("apt", "sudo apt update && sudo apt install -y ffmpeg yt-dlp"),
                ("dnf", "sudo dnf install -y ffmpeg yt-dlp"),
                ("pacman", "sudo pacman -Sy --noconfirm ffmpeg yt-dlp"),
                ("zypper", "sudo zypper refresh && sudo zypper install -y ffmpeg yt-dlp"),
            ]
        elif system == "Darwin":
            candidates = [
                ("brew", "brew update && brew install ffmpeg yt-dlp"),
            ]
        elif system == "Windows":
            candidates = [
                ("winget", "winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements && "
                           "winget install --id yt-dlp.yt-dlp -e --accept-package-agreements --accept-source-agreements"),
                ("choco", "choco install ffmpeg -y && choco install yt-dlp -y"),
            ]
        else:
            candidates = []

        for name, command in candidates:
            if shutil.which(name):
                managers.append({"name": name, "command": command})

        return managers


def start_dependency_update(parent, log_func, on_finished):
    reply = QMessageBox.question(
        parent,
        "Update Dependencies",
        "This will update system dependencies (FFmpeg + yt-dlp) using your OS package manager.\n"
        "It may open a terminal and prompt for permissions.\n\n"
        "Continue?",
        QMessageBox.Yes | QMessageBox.No
    )
    if reply != QMessageBox.Yes:
        return None

    log_func("==== Dependency Update Started ====")
    thread = DependencyUpdateThread()
    thread.log.connect(log_func)
    thread.finished.connect(lambda ok: _finish_dependency_update(log_func, on_finished, ok))
    thread.start()
    return thread


def _finish_dependency_update(log_func, on_finished, ok: bool):
    if ok:
        log_func("✅ Dependencies updated successfully.")
    else:
        log_func("❌ Dependency update failed. Check logs above.")
    log_func("==== Dependency Update Finished ====")

    try:
        if is_ffmpeg_available():
            log_func(f"🎞️ FFmpeg detected (version {get_ffmpeg_version()})")
        else:
            log_func("⚠️ FFmpeg not detected. Use the app to install it.")
    except Exception as e:
        log_func(f"⚠️ Could not check FFmpeg: {e}")

    if on_finished:
        on_finished(ok)
