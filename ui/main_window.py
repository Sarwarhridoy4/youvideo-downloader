"""
Optimized Main Window for YouVideo Downloader
----------------------------------------------
Improvements:
• Cleaner code structure with separated concerns
• Better resource management and caching
• Improved error handling
• Modern UI with better UX
• Performance optimizations
• Type hints throughout
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMenuBar, QMenu, QMessageBox, QDialog, QComboBox, QProgressBar,
    QTextEdit, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, QFrame
)
from PySide6.QtGui import QAction, QMovie, QIcon
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from typing import Optional, Callable
import os
import sys
import requests
import subprocess

from downloader.yt_downloader import get_formats, download_and_merge
from downloader.ffmpeg_utils import ensure_ffmpeg
from utils.pathfinder import resource_path

# Constants
APP_VERSION = "1.0.0"
GITHUB_RELEASES_URL = "https://api.github.com/repos/Sarwarhridoy4/youvideo-downloader/releases/latest"

# Resource paths
ICON_PATH = resource_path("assets/icons/appicon.png")
GIF_PATH = resource_path("assets/icons/spinner.gif")
DARK_QSS_PATH = resource_path("assets/qss/dark.qss")
LIGHT_QSS_PATH = resource_path("assets/qss/light.qss")


# ─────────────────────── Worker Threads ─────────────────────
class DownloadThread(QThread):
    """Thread for handling video/audio downloads."""
    
    progress = Signal(int)
    finished = Signal()
    error = Signal(str)
    log = Signal(str)
    
    def __init__(self, url: str, format_code: Optional[str], output_path: str, is_audio: bool):
        super().__init__()
        self.url = url
        self.format_code = format_code
        self.output_path = output_path
        self.is_audio = is_audio
    
    def run(self):
        """Execute the download."""
        try:
            from yt_dlp import YoutubeDL
            
            def progress_hook(d):
                """Handle download progress updates."""
                if d.get("status") == "downloading":
                    downloaded = d.get("downloaded_bytes", 0)
                    total = d.get("total_bytes") or d.get("total_bytes_estimate", 1)
                    percent = int((downloaded / total) * 100)
                    self.progress.emit(percent)
                    
                    # Calculate speed and ETA
                    speed = d.get("speed", 0)
                    eta = d.get("eta", 0)
                    
                    if speed:
                        speed_mb = speed / (1024 * 1024)
                        self.log.emit(f"Progress: {percent}% | Speed: {speed_mb:.2f} MB/s")
                    else:
                        self.log.emit(f"Progress: {percent}%")
                
                elif d.get("status") == "finished":
                    self.log.emit("Processing and merging...")
            
            output_template = os.path.join(self.output_path, '%(title)s.%(ext)s')
            
            ydl_opts = {
                'progress_hooks': [progress_hook],
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'noplaylist': False,
            }
            
            if self.is_audio:
                # Audio download (MP3)
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'merge_output_format': 'mp3',
                })
                self.log.emit("Starting audio (MP3) download...")
            else:
                # Video download
                ydl_opts['format'] = f"{self.format_code}+bestaudio/best"
                ydl_opts['merge_output_format'] = 'mp4'
                self.log.emit(f"Starting video download (format: {self.format_code})...")
            
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
                self.log.emit("✓ Download complete!")
            
            self.finished.emit()
            
        except Exception as e:
            error_msg = str(e)
            self.log.emit(f"✗ Error: {error_msg}")
            self.error.emit(error_msg)


class FormatLoaderThread(QThread):
    """Thread for loading available video formats."""
    
    formats_loaded = Signal(list)
    error = Signal(str)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    
    def run(self):
        """Fetch formats from the URL."""
        try:
            formats = get_formats(self.url)
            self.formats_loaded.emit(formats)
        except Exception as e:
            self.error.emit(str(e))


# ─────────────────────── Spinner Dialog ─────────────────────
class SpinnerDialog(QDialog):
    """Loading spinner dialog."""
    
    def __init__(self, message: str = "Loading...", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setModal(True)
        self.setFixedSize(250, 180)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Spinner
        self.spinner = QLabel()
        self.movie = QMovie(GIF_PATH)
        self.spinner.setMovie(self.movie)
        self.spinner.setAlignment(Qt.AlignCenter)
        self.movie.start()
        layout.addWidget(self.spinner)
        
        # Message
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
    
    def set_message(self, message: str):
        """Update the loading message."""
        self.label.setText(message)


# ─────────────────────── Developer Info Dialog ─────────────────────
class DeveloperInfoDialog(QDialog):
    """Modern developer information dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About YouVideo Downloader")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        self._apply_stylesheet()
        self._build_ui()
        self._center_on_parent()
    
    def _apply_stylesheet(self):
        """Apply modern styling."""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50,
                    stop:1 #34495e
                );
            }
            QLabel#title { color: #ecf0f1; font-size: 26px; font-weight: bold; }
            QLabel#version { color: #95a5a6; font-size: 13px; font-style: italic; }
            QLabel#desc { color: #bdc3c7; font-size: 13px; }
            QLabel#section { color: #3498db; font-size: 11px; font-weight: bold; }
            QLabel#info { color: #ecf0f1; font-size: 14px; }
            QFrame#card {
                background-color: rgba(44, 62, 80, 0.6);
                border: 1px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton {
                background-color: rgba(52, 152, 219, 0.8);
                color: white; border: none; border-radius: 5px;
                padding: 10px 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(52, 152, 219, 1); }
            QPushButton#close { background-color: rgba(231, 76, 60, 0.8); }
            QPushButton#close:hover { background-color: rgba(231, 76, 60, 1); }
        """)
    
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # App Icon
        if os.path.exists(ICON_PATH):
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(ICON_PATH).pixmap(70, 70))
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)
        
        # Title & Version
        title = QLabel("YouVideo Downloader")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        version = QLabel(f"Version {APP_VERSION}")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # Description
        desc = QLabel("A powerful tool for downloading videos from\nYouTube, Facebook, and other platforms.")
        desc.setObjectName("desc")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # Info Card
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        
        dev_section = QLabel("DEVELOPER")
        dev_section.setObjectName("section")
        card_layout.addWidget(dev_section)
        
        dev_name = QLabel("Sarwar Hossain")
        dev_name.setObjectName("info")
        card_layout.addWidget(dev_name)
        
        github_link = QLabel(
            '<a href="https://github.com/Sarwarhridoy4/youvideo-downloader" '
            'style="color:#3498db;">📦 View on GitHub</a>'
        )
        github_link.setOpenExternalLinks(True)
        github_link.setObjectName("info")
        card_layout.addWidget(github_link)
        
        layout.addWidget(card)
        
        # Social Buttons
        btn_layout = QHBoxLayout()
        portfolio_btn = QPushButton("🌐 Portfolio")
        portfolio_btn.clicked.connect(
            lambda: subprocess.Popen(
                ["start" if sys.platform == "win32" else "open", 
                 "https://sarwar-hossain-vert.vercel.app"], shell=True
            )
        )
        btn_layout.addWidget(portfolio_btn)
        
        github_btn = QPushButton("💻 GitHub")
        github_btn.clicked.connect(
            lambda: subprocess.Popen(
                ["start" if sys.platform == "win32" else "open",
                 "https://github.com/Sarwarhridoy4"], shell=True
            )
        )
        btn_layout.addWidget(github_btn)
        layout.addLayout(btn_layout)
        
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Close Button
        close_btn = QPushButton("Close")
        close_btn.setObjectName("close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _center_on_parent(self):
        """Center dialog on parent window."""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)


# ─────────────────────── Main Window ─────────────────────
class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # State
        self._back_callback: Optional[Callable] = None
        self.output_path: str = os.getcwd()
        self.current_theme: str = "dark"
        self.spinner_dialog: Optional[SpinnerDialog] = None
        self.download_thread: Optional[DownloadThread] = None
        self.format_loader: Optional[FormatLoaderThread] = None
        
        # Setup
        self._setup_window()
        self._setup_ui()
        self._apply_theme(DARK_QSS_PATH)
        self._setup_menu()
        self._check_ffmpeg()
    
    def _setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("YouVideo Downloader")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setMinimumSize(750, 550)
        self.resize(750, 550)
    
    def _setup_ui(self):
        """Build the user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("📥 YouVideo Downloader")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # URL Input
        url_label = QLabel("Video URL:")
        main_layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube, Facebook, or other video URL")
        self.url_input.setMinimumHeight(35)
        self.url_input.textChanged.connect(self._on_url_changed)
        main_layout.addWidget(self.url_input)
        
        # Type Selection (Audio/Video)
        type_frame = QFrame()
        type_frame.setFrameShape(QFrame.StyledPanel)
        type_layout = QHBoxLayout(type_frame)
        
        type_label = QLabel("Download Type:")
        type_layout.addWidget(type_label)
        
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
        
        # Format Selection (for video)
        format_layout = QHBoxLayout()
        format_label = QLabel("Quality:")
        format_layout.addWidget(format_label)
        
        self.format_dropdown = QComboBox()
        self.format_dropdown.setMinimumHeight(35)
        self.format_dropdown.currentIndexChanged.connect(self._update_download_state)
        format_layout.addWidget(self.format_dropdown, stretch=1)
        
        self.load_formats_btn = QPushButton("🔄 Load Formats")
        self.load_formats_btn.setMinimumHeight(35)
        self.load_formats_btn.clicked.connect(self._load_formats)
        format_layout.addWidget(self.load_formats_btn)
        
        main_layout.addLayout(format_layout)
        
        # Output Folder
        folder_layout = QHBoxLayout()
        
        self.output_label = QLabel(f"📁 Output: {self.output_path}")
        self.output_label.setWordWrap(True)
        folder_layout.addWidget(self.output_label, stretch=1)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setMinimumHeight(35)
        browse_btn.clicked.connect(self._browse_folder)
        folder_layout.addWidget(browse_btn)
        
        self.open_folder_btn = QPushButton("Open")
        self.open_folder_btn.setMinimumHeight(35)
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        folder_layout.addWidget(self.open_folder_btn)
        
        main_layout.addLayout(folder_layout)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setMinimumHeight(25)
        self.progress.setFormat("Ready")
        main_layout.addWidget(self.progress)
        
        # Log Window
        log_label = QLabel("Download Log:")
        main_layout.addWidget(log_label)
        
        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)
        self.log_window.setMaximumHeight(150)
        main_layout.addWidget(self.log_window)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        
        back_btn = QPushButton("◀ Back")
        back_btn.setMinimumHeight(40)
        back_btn.clicked.connect(self._on_back)
        action_layout.addWidget(back_btn)
        
        action_layout.addStretch()
        
        self.download_btn = QPushButton("⬇ Download")
        self.download_btn.setMinimumHeight(40)
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self._download)
        self.download_btn.setStyleSheet("""
            QPushButton { font-size: 14px; font-weight: bold; }
            QPushButton:enabled { background-color: #27ae60; }
            QPushButton:enabled:hover { background-color: #229954; }
        """)
        action_layout.addWidget(self.download_btn)
        
        theme_btn = QPushButton("🎨 Theme")
        theme_btn.setMinimumHeight(40)
        theme_btn.clicked.connect(self._switch_theme)
        action_layout.addWidget(theme_btn)
        
        main_layout.addLayout(action_layout)
        
        # Connect signals
        self.video_radio.toggled.connect(self._on_type_changed)
        self.audio_radio.toggled.connect(self._on_type_changed)
    
    def _setup_menu(self):
        """Create application menu."""
        menubar = self.menuBar()
        menubar.setStyleSheet("QMenuBar { font-size: 14px; } QMenu { font-size: 14px; }")
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Info Menu
        info_menu = menubar.addMenu("&Info")
        
        dev_action = QAction("📋 Developer Info", self)
        dev_action.triggered.connect(self._show_dev_info)
        info_menu.addAction(dev_action)
        
        update_action = QAction("🔄 Check for Updates", self)
        update_action.triggered.connect(self._check_update)
        info_menu.addAction(update_action)
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is available."""
        if not ensure_ffmpeg(self.log_window.append, parent=self):
            self._show_error("FFmpeg Missing", 
                           "FFmpeg is not installed or not in PATH.\n"
                           "Download functionality will be disabled.")
            self.download_btn.setEnabled(False)
            self.load_formats_btn.setEnabled(False)
    
    def _apply_theme(self, theme_path: str):
        """Apply QSS theme."""
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading theme: {e}")
    
    def _switch_theme(self):
        """Toggle between dark and light themes."""
        if self.current_theme == "dark":
            self._apply_theme(LIGHT_QSS_PATH)
            self.current_theme = "light"
            self.log_window.append("🎨 Switched to light theme")
        else:
            self._apply_theme(DARK_QSS_PATH)
            self.current_theme = "dark"
            self.log_window.append("🎨 Switched to dark theme")
    
    def _browse_folder(self):
        """Open folder selection dialog."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path = folder
            self.output_label.setText(f"📁 Output: {folder}")
            self.log_window.append(f"Output folder: {folder}")
            self._update_download_state()
    
    def _open_output_folder(self):
        """Open output folder in file manager."""
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
        """Handle URL input changes."""
        self._update_download_state()
    
    def _on_type_changed(self):
        """Handle audio/video type changes."""
        is_audio = self.audio_radio.isChecked()
        self.format_dropdown.setVisible(not is_audio)
        self.load_formats_btn.setVisible(not is_audio)
        self._update_download_state()
    
    def _update_download_state(self):
        """Update download button state."""
        url_ok = bool(self.url_input.text().strip())
        folder_ok = bool(self.output_path and os.path.exists(self.output_path))
        
        if self.audio_radio.isChecked():
            ready = url_ok and folder_ok
        else:
            format_ok = bool(self.format_dropdown.currentData())
            ready = url_ok and folder_ok and format_ok
        
        self.download_btn.setEnabled(ready)
    
    def _load_formats(self):
        """Load available formats for the URL."""
        url = self.url_input.text().strip()
        if not url:
            self._show_error("Missing URL", "Please enter a video URL.")
            return
        
        # Show spinner
        self.spinner_dialog = SpinnerDialog("Loading formats...", self)
        self.spinner_dialog.show()
        
        # Start format loader thread
        self.format_loader = FormatLoaderThread(url)
        self.format_loader.formats_loaded.connect(self._on_formats_loaded)
        self.format_loader.error.connect(self._on_formats_error)
        self.format_loader.start()
    
    def _on_formats_loaded(self, formats: list):
        """Handle loaded formats."""
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
        """Handle format loading error."""
        self.format_dropdown.clear()
        self.format_dropdown.addItem(f"Error: {error}")
        self.log_window.append(f"✗ Error loading formats: {error}")
        
        if self.spinner_dialog:
            self.spinner_dialog.accept()
            self.spinner_dialog = None
        
        self._show_error("Format Loading Failed", error)
    
    def _download(self):
        """Start download."""
        url = self.url_input.text().strip()
        if not url:
            return
        
        is_audio = self.audio_radio.isChecked()
        format_code = None if is_audio else self.format_dropdown.currentData()
        
        # Reset progress
        self.progress.setValue(0)
        self.progress.setFormat("Starting...")
        self.download_btn.setEnabled(False)
        self.log_window.clear()
        
        # Start download thread
        self.download_thread = DownloadThread(url, format_code, self.output_path, is_audio)
        self.download_thread.progress.connect(self._on_progress)
        self.download_thread.finished.connect(self._on_download_finished)
        self.download_thread.error.connect(self._on_download_error)
        self.download_thread.log.connect(self.log_window.append)
        self.download_thread.start()
    
    def _on_progress(self, percent: int):
        """Handle download progress."""
        self.progress.setValue(percent)
        self.progress.setFormat(f"{percent}%")
    
    def _on_download_finished(self):
        """Handle download completion."""
        self.progress.setValue(100)
        self.progress.setFormat("✓ Complete")
        self.download_btn.setEnabled(True)
        
        self._show_info("Download Complete", 
                       f"File saved to:\n{self.output_path}")
    
    def _on_download_error(self, error: str):
        """Handle download error."""
        self.progress.setFormat("✗ Failed")
        self.download_btn.setEnabled(True)
        self._show_error("Download Failed", error)
    
    def _show_dev_info(self):
        """Show developer information dialog."""
        dialog = DeveloperInfoDialog(self)
        dialog.exec()
    
    def _check_update(self):
        """Check for application updates."""
        try:
            resp = requests.get(GITHUB_RELEASES_URL, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            latest = data.get("tag_name", "").lstrip("v")
            
            if not latest:
                raise ValueError("No version information in response")
            
            current = APP_VERSION.lstrip("v")
            
            if latest != current:
                self._show_info("Update Available",
                              f"New version available: {latest}\n"
                              f"Current version: {current}\n\n"
                              f"Visit: https://github.com/Sarwarhridoy4/"
                              f"youvideo-downloader/releases/tag/v{latest}")
            else:
                self._show_info("Up to Date", 
                              f"You have the latest version ({current}).")
        except Exception as e:
            self._show_error("Update Check Failed", 
                           f"Could not check for updates:\n{str(e)}")
    
    def _show_error(self, title: str, message: str):
        """Show error message box."""
        QMessageBox.critical(self, title, message)
    
    def _show_info(self, title: str, message: str):
        """Show information message box."""
        QMessageBox.information(self, title, message)
    
    def set_back_callback(self, callback: Callable):
        """Set callback for back button."""
        self._back_callback = callback
    
    def _on_back(self):
        """Handle back button click."""
        if self._back_callback:
            self.hide()
            self._back_callback()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Clean up threads
        if self.download_thread and self.download_thread.isRunning():
            reply = QMessageBox.question(
                self, "Download in Progress",
                "A download is in progress. Are you sure you want to quit?",
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
        
        event.accept()