"""
Optimized Main Window for YouVideo Downloader
----------------------------------------------
Complete and verified implementation with all methods
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QDialog, QComboBox, QProgressBar,
    QTextEdit, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, QFrame
)
from PySide6.QtGui import QAction, QMovie, QIcon, QPixmap
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from typing import Optional, Callable
import os
import sys
import requests
import subprocess
import re
import urllib.request
import logging
from yt_dlp import YoutubeDL

from downloader.yt_downloader import get_formats, get_video_info, get_default_download_path
from downloader.ffmpeg_utils import ensure_ffmpeg
from utils.pathfinder import resource_path
from utils.theme_manager import ThemeManager
from utils.maintenance import start_dependency_update

# Version
def get_latest_version() -> str:
    try:
        resp = requests.get("https://api.github.com/repos/Sarwarhridoy4/youvideo-downloader/releases/latest", timeout=10)
        resp.raise_for_status()
        return resp.json().get("tag_name", "3.0.0").lstrip("v")
    except:
        return "3.0.0"

APP_VERSION = get_latest_version()
GITHUB_RELEASES_URL = "https://api.github.com/repos/Sarwarhridoy4/youvideo-downloader/releases/latest"

# Paths
ICON_PATH = resource_path("assets/icons/appicon.png")
GIF_PATH = resource_path("assets/icons/spinner.gif")


# ─────────────────────── Worker Threads ─────────────────────
class DownloadThread(QThread):
    progress = Signal(int)           # 0–100 for main progress bar
    log = Signal(str)                # Text log messages
    finished = Signal()
    error = Signal(str)

    def __init__(self, url: str, format_code: str | None, output_path: str, is_audio: bool = False):
        super().__init__()
        self.url = url
        self.format_code = format_code
        self.output_path = output_path
        self.is_audio = is_audio

        # Improved regex – more robust matching for FFmpeg progress lines
        self._ffmpeg_pattern = re.compile(
            r'frame=\s*(\d+)\s+'
            r'fps=\s*([\d.]+)\s+'
            r'.*'
            r'time=\s*(\d+:\d+:\d+\.\d+)\s+'
            r'.*'
            r'speed=\s*([\d.]+)x',
            re.IGNORECASE
        )

    def run(self):
        try:
            def progress_hook(d):
                status = d.get("status", "")
                if status == "downloading":
                    downloaded = d.get("downloaded_bytes", 0)
                    total = d.get("total_bytes") or d.get("total_bytes_estimate", 1)
                    percent = min(int((downloaded / total) * 100), 99)  # max 99 until merge
                    self.progress.emit(percent)

                    speed = d.get("speed", 0)
                    eta = d.get("eta", None)

                    speed_str = f"{speed / (1024 * 1024):.2f} MB/s" if speed else "?? MB/s"
                    eta_str = f"{eta // 60:02d}:{eta % 60:02d}" if eta is not None else "??:??"

                    self.log.emit(f"📥 Progress: {percent}% | Speed: {speed_str} | ETA: {eta_str}")

                elif status == "finished":
                    self.log.emit("✓ Downloaded, starting postprocessing...")
                    self.progress.emit(99)  # almost done – waiting for merge

            # ──────────────────────────────── yt-dlp options ────────────────────────────────
            output_template = os.path.join(self.output_path, '%(title)s.%(ext)s')

            ydl_opts = {
                'progress_hooks': [progress_hook],
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'verbose': True,                   # important: needed for FFmpeg output
                'noplaylist': True,
                # Avoid android_sdkless client until yt-dlp is updated; fixes 403 errors.
                'extractor_args': {
                    'youtube': {
                        'player_client': ['default', '-android_sdkless']
                    }
                },
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'postprocessor_args': [
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-movflags', '+faststart'
                ],
                'logger': self._create_ffmpeg_aware_logger(),
            }

            if self.is_audio:
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'merge_output_format': 'mp3',
                })
                self.log.emit("🎵 Starting audio (MP3) download...")
            else:
                if self.format_code:
                    format_str = f"{self.format_code}+bestaudio/best" if "+" not in self.format_code else self.format_code
                else:
                    format_str = "bestvideo+bestaudio/best"
                ydl_opts['format'] = format_str
                self.log.emit(f"🎬 Starting video download (format: {format_str})...")

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.log.emit("✅ Download & post-processing complete!")
            self.progress.emit(100)
            self.finished.emit()

        except Exception as e:
            error_msg = str(e)
            self.log.emit(f"❌ Error: {error_msg}")
            self.error.emit(error_msg)

    def _create_ffmpeg_aware_logger(self):
        class FfmpegAwareLogger(logging.Logger):
            def __init__(self, name, thread):
                super().__init__(name)
                self.thread = thread
                self.setLevel(logging.DEBUG)

            def debug(self, msg, *args, **kwargs):
                if not msg:
                    return

                msg_str = str(msg).strip()

                # ─── Handle FFmpeg real-time progress ───
                if any(k in msg_str.lower() for k in ['frame=', 'fps=', 'time=', 'speed=']):
                    match = self.thread._ffmpeg_pattern.search(msg_str)
                    if match:
                        frame, fps, time_str, speed = match.groups()
                        progress_line = f"🔄 FFmpeg: frame={frame} | fps={fps} | time={time_str} | speed={speed}x"
                        self.thread.log.emit(progress_line)
                        return  # don't log again below

                # ─── Normal debug messages (skip boring ones) ───
                if "Deleting original file" in msg_str:
                    return
                if len(msg_str) > 5:
                    self.thread.log.emit(f"DEBUG: {msg_str[:180]}")

            def info(self, msg, *args, **kwargs):
                msg_str = str(msg).strip()
                if msg_str and "Deleting original file" not in msg_str:
                    self.thread.log.emit(f"ℹ️ {msg_str[:180]}")

            def warning(self, msg, *args, **kwargs):
                msg_str = str(msg).strip()
                if msg_str:
                    self.thread.log.emit(f"⚠️ {msg_str[:180]}")

            def error(self, msg, *args, **kwargs):
                msg_str = str(msg).strip()
                if msg_str:
                    self.thread.log.emit(f"❌ {msg_str[:180]}")

        return FfmpegAwareLogger('yt-dlp-ffmpeg', self)

class FormatLoaderThread(QThread):
    formats_loaded = Signal(list)
    error = Signal(str)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            formats = get_formats(self.url)
            self.formats_loaded.emit(formats)
        except Exception as e:
            self.error.emit(str(e))


class VideoInfoLoaderThread(QThread):
    info_loaded = Signal(dict)
    error = Signal(str)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            info = get_video_info(self.url)
            self.info_loaded.emit(info)
        except Exception as e:
            self.error.emit(str(e))


# ─────────────────────── Dialogs ─────────────────────
class SpinnerDialog(QDialog):
    def __init__(self, message: str = "Loading...", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setModal(True)
        self.setMinimumSize(250, 180)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        self.spinner = QLabel()
        self.movie = QMovie(GIF_PATH)
        self.spinner.setMovie(self.movie)
        self.spinner.setAlignment(Qt.AlignCenter)
        self.movie.start()
        layout.addWidget(self.spinner)
        
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)


class DeveloperInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About YouVideo Downloader")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        ThemeManager.register(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        if os.path.exists(ICON_PATH):
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(ICON_PATH).pixmap(70, 70))
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)
        
        title = QLabel("𝒀𝒐𝒖𝑽𝒊𝒅𝒆𝒐 𝑫𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒆𝒓")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        version = QLabel(f"Version {APP_VERSION}")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        desc = QLabel("A powerful tool for downloading videos from\nYouTube, Facebook, and other platforms.")
        desc.setObjectName("desc")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        close_btn = QPushButton("Close")
        close_btn.setObjectName("close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _apply_theme_from_manager(self, theme: str):
        if theme == "light":
            self.setStyleSheet("""
                QDialog { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f7f7f7, stop:1 #eaeaea); }
                QLabel#title { color: #1f2a33; font-size: 26px; font-weight: bold; }
                QLabel#version { color: #6b7280; font-size: 13px; font-style: italic; }
                QLabel#desc { color: #4b5563; font-size: 13px; }
                QLabel#info { color: #1f2a33; font-size: 14px; }
                QPushButton { background-color: rgba(52, 152, 219, 0.85); color: white; border: none;
                             border-radius: 5px; padding: 10px 20px; font-weight: bold; }
                QPushButton:hover { background-color: rgba(52, 152, 219, 1); }
                QPushButton#close { background-color: rgba(231, 76, 60, 0.85); }
                QPushButton#close:hover { background-color: rgba(231, 76, 60, 1); }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2c3e50, stop:1 #34495e); }
                QLabel#title { color: #ecf0f1; font-size: 26px; font-weight: bold; }
                QLabel#version { color: #95a5a6; font-size: 13px; font-style: italic; }
                QLabel#desc { color: #bdc3c7; font-size: 13px; }
                QLabel#info { color: #ecf0f1; font-size: 14px; }
                QPushButton { background-color: rgba(52, 152, 219, 0.8); color: white; border: none;
                             border-radius: 5px; padding: 10px 20px; font-weight: bold; }
                QPushButton:hover { background-color: rgba(52, 152, 219, 1); }
                QPushButton#close { background-color: rgba(231, 76, 60, 0.8); }
                QPushButton#close:hover { background-color: rgba(231, 76, 60, 1); }
            """)


# ─────────────────────── Main Window ─────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self._back_callback: Optional[Callable] = None
        self.output_path: str = get_default_download_path()
        self.current_theme: str = "dark"
        self.spinner_dialog: Optional[SpinnerDialog] = None
        self.download_thread: Optional[DownloadThread] = None
        self.format_loader: Optional[FormatLoaderThread] = None
        self.video_info_loader: Optional[VideoInfoLoaderThread] = None
        self.dep_update_thread: Optional[QThread] = None
        
        self._setup_window()
        self._setup_ui()
        ThemeManager.register(self)
        self._setup_menu()
        self._check_ffmpeg()
    
    def _setup_window(self):
        self.setWindowTitle("𝒀𝒐𝒖𝑽𝒊𝒅𝒆𝒐 𝑫𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒆𝒓")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setMinimumSize(650, 480)
        self.resize(650, 480)
        self.setWindowFlags(Qt.Window)
    
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        header = QLabel("📥 𝒀𝒐𝒖𝑽𝒊𝒅𝒆𝒐 𝑫𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒆𝒓")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        url_label = QLabel("Video URL:")
        main_layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube, Facebook, or other video URL")
        self.url_input.setMinimumHeight(35)
        self.url_input.textChanged.connect(self._on_url_changed)
        main_layout.addWidget(self.url_input)
        
        thumbnail_layout = QHBoxLayout()
        thumbnail_layout.addWidget(QLabel("Thumbnail:"))
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(120, 68)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setText("No thumbnail")
        thumbnail_layout.addWidget(self.thumbnail_label)
        
        self.load_thumbnail_btn = QPushButton("Load Thumbnail")
        self.load_thumbnail_btn.setMinimumHeight(30)
        self.load_thumbnail_btn.clicked.connect(self._load_thumbnail)
        thumbnail_layout.addWidget(self.load_thumbnail_btn)
        thumbnail_layout.addStretch()
        main_layout.addLayout(thumbnail_layout)
        
        type_frame = QFrame()
        type_frame.setFrameShape(QFrame.StyledPanel)
        type_layout = QHBoxLayout(type_frame)
        type_layout.addWidget(QLabel("Download Type:"))
        
        self.video_radio = QRadioButton("Video (MP4)")
        self.audio_radio = QRadioButton("Audio (MP3)")
        self.video_radio.setChecked(True)
        
        self.type_group = QButtonGroup()
        self.type_group.addButton(self.video_radio)
        self.type_group.addButton(self.audio_radio)
        
        type_layout.addWidget(self.video_radio)
        type_layout.addWidget(self.audio_radio)
        type_layout.addStretch()
        main_layout.addWidget(type_frame)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Quality:"))
        
        self.format_dropdown = QComboBox()
        self.format_dropdown.setMinimumHeight(30)
        self.format_dropdown.currentIndexChanged.connect(self._update_download_state)
        format_layout.addWidget(self.format_dropdown, stretch=1)
        
        self.load_formats_btn = QPushButton("🔄 Load Formats")
        self.load_formats_btn.setMinimumHeight(30)
        self.load_formats_btn.clicked.connect(self._load_formats)
        format_layout.addWidget(self.load_formats_btn)
        main_layout.addLayout(format_layout)
        
        folder_layout = QHBoxLayout()
        self.output_label = QLabel(f"📁 Output: {self.output_path}")
        self.output_label.setWordWrap(True)
        folder_layout.addWidget(self.output_label, stretch=1)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setMinimumHeight(30)
        browse_btn.clicked.connect(self._browse_folder)
        folder_layout.addWidget(browse_btn)
        
        self.open_folder_btn = QPushButton("Open")
        self.open_folder_btn.setMinimumHeight(30)
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        folder_layout.addWidget(self.open_folder_btn)
        main_layout.addLayout(folder_layout)
        
        self.progress = QProgressBar()
        self.progress.setMinimumHeight(20)
        self.progress.setFormat("Ready")
        main_layout.addWidget(self.progress)
        
        main_layout.addWidget(QLabel("Download Log:"))
        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)
        self.log_window.setMaximumHeight(120)
        main_layout.addWidget(self.log_window)
        
        action_layout = QHBoxLayout()
        back_btn = QPushButton("◀ Back")
        back_btn.setMinimumHeight(35)
        back_btn.clicked.connect(self._on_back)
        action_layout.addWidget(back_btn)
        action_layout.addStretch()
        
        self.download_btn = QPushButton("⬇ Download")
        self.download_btn.setMinimumHeight(35)
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self._download)
        self.download_btn.setStyleSheet("""
            QPushButton { font-size: 14px; font-weight: bold; }
            QPushButton:enabled { background-color: #27ae60; }
            QPushButton:enabled:hover { background-color: #229954; }
        """)
        action_layout.addWidget(self.download_btn)
        
        theme_btn = QPushButton("🎨 Theme")
        theme_btn.setMinimumHeight(35)
        theme_btn.clicked.connect(self._switch_theme)
        action_layout.addWidget(theme_btn)
        main_layout.addLayout(action_layout)
        
        self.video_radio.toggled.connect(self._on_type_changed)
        self.audio_radio.toggled.connect(self._on_type_changed)
    
    def _setup_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        info_menu = menubar.addMenu("&Info")
        dev_action = QAction("📋 Developer Info", self)
        dev_action.triggered.connect(self._show_dev_info)
        info_menu.addAction(dev_action)
        
        update_action = QAction("🔄 Check for Updates", self)
        update_action.triggered.connect(self._check_update)
        info_menu.addAction(update_action)

        tools_menu = menubar.addMenu("&Tools")
        deps_action = QAction("🔧 Update Dependencies", self)
        deps_action.triggered.connect(self._update_dependencies)
        tools_menu.addAction(deps_action)
    
    def _check_ffmpeg(self):
        if not ensure_ffmpeg(self.log_window.append, parent=self):
            self._show_error("FFmpeg Missing", "FFmpeg is not installed.\nDownload will be disabled.")
            self.download_btn.setEnabled(False)
            self.load_formats_btn.setEnabled(False)
    
    def set_theme(self, theme: str):
        self._apply_theme_from_manager(theme)
    
    def get_current_theme(self) -> str:
        return ThemeManager.get_current_theme()
    
    def _switch_theme(self):
        if getattr(self, "_theme_switching", False):
            return
        self._theme_switching = True
        sender = self.sender()
        if hasattr(sender, "setEnabled"):
            sender.setEnabled(False)
        ThemeManager.toggle()
        self.current_theme = ThemeManager.get_current_theme()
        self.log_window.append(f"🎨 Switched to {self.current_theme} theme")
        QTimer.singleShot(200, lambda: self._finish_theme_switch(sender))

    def _finish_theme_switch(self, sender):
        self._theme_switching = False
        if hasattr(sender, "setEnabled"):
            sender.setEnabled(True)

    def _apply_theme_from_manager(self, theme: str):
        if theme == "light":
            theme_path = resource_path("assets/qss/light.qss")
        else:
            theme_path = resource_path("assets/qss/dark.qss")

        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
            self.current_theme = theme
        except Exception as e:
            print(f"Error loading theme: {e}")
    
    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path = folder
            self.output_label.setText(f"📁 Output: {folder}")
            self.log_window.append(f"Output folder: {folder}")
            self._update_download_state()
    
    def _open_output_folder(self):
        if not os.path.exists(self.output_path):
            self._show_error("Folder Not Found", "Output folder does not exist.")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.output_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.output_path])
            else:
                subprocess.Popen(["xdg-open", self.output_path])
        except Exception as e:
            self._show_error("Error", f"Could not open folder: {e}")
    
    def _on_url_changed(self):
        self._update_download_state()
    
    def _on_type_changed(self):
        is_audio = self.audio_radio.isChecked()
        self.format_dropdown.setVisible(not is_audio)
        self.load_formats_btn.setVisible(not is_audio)
        self._update_download_state()
    
    def _update_download_state(self):
        url_ok = bool(self.url_input.text().strip())
        folder_ok = bool(self.output_path and os.path.exists(self.output_path))
        
        if self.audio_radio.isChecked():
            ready = url_ok and folder_ok
        else:
            format_ok = bool(self.format_dropdown.currentData())
            ready = url_ok and folder_ok and format_ok
        
        self.download_btn.setEnabled(ready)
    
    def _load_formats(self):
        url = self.url_input.text().strip()
        if not url:
            self._show_error("Missing URL", "Please enter a video URL.")
            return
        
        self.spinner_dialog = SpinnerDialog("Loading formats...", self)
        self.spinner_dialog.show()
        
        self.format_loader = FormatLoaderThread(url)
        self.format_loader.formats_loaded.connect(self._on_formats_loaded)
        self.format_loader.error.connect(self._on_formats_error)
        self.format_loader.start()
    
    def _on_formats_loaded(self, formats: list):
        self.format_dropdown.clear()
        if not formats:
            self.format_dropdown.addItem("No formats available")
        else:
            for f in formats:
                quality = f.get('quality_label', 'Unknown')
                ext = f.get('ext', '')
                stream_type = f.get('stream_type', '')
                filesize = f.get('filesize_mb', 0)
                
                if filesize:
                    label = f"{quality} ({ext}) [{stream_type}] - {filesize}MB"
                else:
                    label = f"{quality} ({ext}) [{stream_type}]"
                
                self.format_dropdown.addItem(label, f['format_id'])
            self.log_window.append(f"✓ Loaded {len(formats)} formats")
        
        if self.spinner_dialog:
            self.spinner_dialog.accept()
            self.spinner_dialog = None
        self._update_download_state()
    
    def _on_formats_error(self, error: str):
        self.format_dropdown.clear()
        self.format_dropdown.addItem(f"Error: {error}")
        self.log_window.append(f"✗ Error loading formats: {error}")
        if self.spinner_dialog:
            self.spinner_dialog.accept()
            self.spinner_dialog = None
        self._show_error("Format Loading Failed", error)
    
    def _load_thumbnail(self):
        url = self.url_input.text().strip()
        if not url:
            self._show_error("Missing URL", "Please enter a video URL.")
            return
        
        self.spinner_dialog = SpinnerDialog("Loading thumbnail...", self)
        self.spinner_dialog.show()
        
        self.video_info_loader = VideoInfoLoaderThread(url)
        self.video_info_loader.info_loaded.connect(self._on_info_loaded)
        self.video_info_loader.error.connect(self._on_info_error)
        self.video_info_loader.start()
    
    def _on_info_loaded(self, info: dict):
        thumbnail_url = info.get("thumbnail_url")
        if thumbnail_url:
            try:
                with urllib.request.urlopen(thumbnail_url) as response:
                    image_data = response.read()
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                scaled_pixmap = pixmap.scaledToWidth(160, Qt.SmoothTransformation)
                self.thumbnail_label.setPixmap(scaled_pixmap)
                self.thumbnail_label.setText("")
                self.log_window.append("✓ Thumbnail loaded")
            except Exception as e:
                self.thumbnail_label.setText("Failed to load")
                self.log_window.append(f"✗ Error loading thumbnail: {str(e)}")
        else:
            self.thumbnail_label.setText("No thumbnail")
            self.log_window.append("No thumbnail available")
        
        if self.spinner_dialog:
            self.spinner_dialog.accept()
            self.spinner_dialog = None
    
    def _on_info_error(self, error: str):
        self.thumbnail_label.setText("Error")
        self.log_window.append(f"✗ Error: {error}")
        if self.spinner_dialog:
            self.spinner_dialog.accept()
            self.spinner_dialog = None
        self._show_error("Thumbnail Loading Failed", error)
    
    def _download(self):
        url = self.url_input.text().strip()
        if not url:
            return
        
        is_audio = self.audio_radio.isChecked()
        format_code = None if is_audio else self.format_dropdown.currentData()
        
        self.progress.setValue(0)
        self.progress.setFormat("Starting...")
        self.download_btn.setEnabled(False)
        self.log_window.clear()
        
        self.download_thread = DownloadThread(url, format_code, self.output_path, is_audio)
        self.download_thread.progress.connect(self._on_progress)
        self.download_thread.finished.connect(self._on_download_finished)
        self.download_thread.error.connect(self._on_download_error)
        self.download_thread.log.connect(self.log_window.append)
        self.download_thread.start()
    
    def _on_progress(self, percent: int):
        self.progress.setValue(percent)
        self.progress.setFormat(f"{percent}%")
    
    def _on_download_finished(self):
        self.progress.setValue(100)
        self.progress.setFormat("✓ Complete")
        self.download_btn.setEnabled(True)
    
    def _on_download_error(self, error: str):
        self.progress.setFormat("✗ Failed")
        self.download_btn.setEnabled(True)
    
    def _show_dev_info(self):
        dialog = DeveloperInfoDialog(self)
        dialog.exec()
    
    def _check_update(self):
        try:
            resp = requests.get(GITHUB_RELEASES_URL, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            latest = data.get("tag_name", "").lstrip("v")
            
            if not latest:
                raise ValueError("No version information")
            
            current = APP_VERSION.lstrip("v")
            
            if latest != current:
                self._show_info("Update Available",
                              f"New version: {latest}\nCurrent: {current}\n\n"
                              f"Visit: https://github.com/Sarwarhridoy4/youvideo-downloader/releases/tag/v{latest}")
            else:
                self._show_info("Up to Date", f"You have the latest version ({current}).")
        except Exception as e:
            self._show_error("Update Check Failed", f"Could not check for updates:\n{str(e)}")

    def _update_dependencies(self):
        if self.dep_update_thread and self.dep_update_thread.isRunning():
            self._show_info("In Progress", "Dependency update is already running.")
            return
        self.dep_update_thread = start_dependency_update(
            parent=self,
            log_func=self.log_window.append,
            on_finished=None
        )

    
    def _show_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)
    
    def _show_info(self, title: str, message: str):
        QMessageBox.information(self, title, message)
    
    def set_back_callback(self, callback: Callable):
        self._back_callback = callback
    
    def _on_back(self):
        if self._back_callback:
            self.hide()
            self._back_callback()
    
    def closeEvent(self, event):
        if self.download_thread and self.download_thread.isRunning():
            reply = QMessageBox.question(
                self, "Download in Progress",
                "A download is in progress. Quit anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
            self.download_thread.terminate()
            self.download_thread.wait()
        
        if self.format_loader and self.format_loader.isRunning():
            self.format_loader.terminate()
            self.format_loader.wait()
        
        if self.video_info_loader and self.video_info_loader.isRunning():
            self.video_info_loader.terminate()
            self.video_info_loader.wait()
        
        event.accept()
