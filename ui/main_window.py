# ui/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMenuBar, QMenu, QMessageBox, QDialog,QComboBox,QProgressBar,QTextEdit,
    QRadioButton, QButtonGroup
)
from PySide6.QtGui import QAction

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QMovie, QIcon
from downloader.yt_downloader import get_formats, download_and_merge
import os
import sys
from downloader.ffmpeg_utils import ensure_ffmpeg
from PySide6.QtWidgets import QApplication
from utils.pathfinder import resource_path
import requests
import subprocess

APP_VERSION = "1.0.0"
GITHUB_RELEASES_URL = "https://api.github.com/repos/Sarwarhridoy4/youvideo-downloader/releases/latest"

icon_path = resource_path("assets/icons/appicon.png")
gif_path = resource_path("assets/icons/spinner.gif")
qss_path = resource_path("assets/qss/dark.qss")

class DownloadThread(QThread):
    progress = Signal(int)
    finished = Signal()
    error = Signal(str)
    log = Signal(str)

    def __init__(self, url, format_code, output_path, is_audio):
        super().__init__()
        self.url = url
        self.format_code = format_code
        self.output_path = output_path
        self.is_audio = is_audio

    def run(self):
        try:
            from yt_dlp import YoutubeDL

            def hook(d):
                if d.get("status") == "downloading":
                    downloaded = d.get("downloaded_bytes") or 0
                    total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
                    percent = downloaded / total * 100
                    self.progress.emit(int(percent))
                    self.log.emit(f"Downloading: {percent:.2f}%")

            output_file_template = os.path.join(self.output_path, '%(title)s.%(ext)s')
            ydl_opts = {
                'progress_hooks': [hook],
                'outtmpl': output_file_template,
                'quiet': True,
                'noplaylist': False,  # Allow playlist download
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
            else:
                # Use selected format for video
                ydl_opts['format'] = f"{self.format_code}+bestaudio/best"

            with YoutubeDL(ydl_opts) as ydl:
                self.log.emit("Starting download...")
                ydl.download([self.url])
                self.log.emit("Download and merge complete.")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class FormatLoaderThread(QThread):
    formats_loaded = Signal(list)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            formats = get_formats(self.url)
            self.formats_loaded.emit(formats)
        except Exception as e:
            self.error.emit(str(e))


class SpinnerDialog(QDialog):
    def __init__(self, message="Loading..."):
        super().__init__()
        self.setWindowTitle("Please wait")
        self.setWindowIcon(QIcon(icon_path))
        self.setModal(True)
        self.setFixedSize(200, 150)

        layout = QVBoxLayout(self)

        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.spinner = QLabel(self)
        movie = QMovie(gif_path)
        self.spinner.setMovie(movie)
        movie.start()
        layout.addWidget(self.spinner)

"""
    Main application window for the YouVideo Downloader GUI.
    This class provides the main interface for downloading YouTube videos, allowing users to:
    - Enter a YouTube URL.
    - Load available video/audio formats for the given URL.
    - Select an output folder for downloads.
    - Switch between dark and light themes.
    - View download progress and logs.
    - Handle errors and display informational messages.
    Key Features:
    - Checks for FFmpeg availability on startup and disables download functionality if missing.
    - Uses a spinner dialog while loading formats.
    - Supports threaded downloads with real-time progress updates.
    - Displays logs and download completion information.
    Attributes:
        url_input (QLineEdit): Input field for the YouTube URL.
        format_dropdown (QComboBox): Dropdown to select video/audio format.
        output_label (QLabel): Displays the selected output folder.
        progress (QProgressBar): Shows download progress.
        log_window (QTextEdit): Displays logs and messages.
        load_formats_btn (QPushButton): Button to load available formats.
        download_btn (QPushButton): Button to start the download.
        output_path (str): Path to the selected output folder.
        current_theme (str): Current theme ("dark" or "light").
        spinner_dialog (SpinnerDialog or None): Dialog shown during format loading.
    Methods:
        setup_ui(): Initializes and arranges UI widgets.
        browse_folder(): Opens a dialog to select the output folder.
        switch_theme(): Switches between dark and light themes.
        apply_theme(theme_path): Applies a QSS stylesheet from the given path.
        load_formats(): Loads available formats for the entered URL.
        _fetch_formats(url): Fetches and populates the format dropdown.
        show_error(title, message): Displays an error message box.
        show_info(title, message): Displays an informational message box.
        download_finished(): Handles actions after download completion.
        update_progress(percent): Updates the progress bar and logs.
        download(): Starts the download process in a separate thread.
    """

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._back_callback = None
        self.setWindowTitle("YouVideo Downloader")
        self.setWindowIcon(QIcon(icon_path))
        QApplication.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(700, 500)

        self.resize(700, 500)
        self.setup_ui()

        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load dark.qss: {e}")

        # Add this line to show the menubar
        self._setup_menu()

        if not ensure_ffmpeg(self.log_window.append, parent=self):
            self.show_error("FFmpeg Missing", "FFmpeg is not installed or not in PATH.")
            self.download_btn.setEnabled(False)
            self.load_formats_btn.setEnabled(False)

    def set_back_callback(self, callback):
        self._back_callback = callback

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL or Playlist")
        layout.addWidget(self.url_input)

        # --- Audio/Video selection ---
        self.video_radio = QRadioButton("Video")
        self.audio_radio = QRadioButton("Audio (MP3)")
        self.video_radio.setChecked(True)
        self.type_group = QButtonGroup()
        self.type_group.addButton(self.video_radio)
        self.type_group.addButton(self.audio_radio)
        type_layout = QHBoxLayout()
        type_layout.addWidget(self.video_radio)
        type_layout.addWidget(self.audio_radio)
        layout.addLayout(type_layout)

        self.format_dropdown = QComboBox()
        self.format_dropdown.setMinimumWidth(400)
        layout.addWidget(self.format_dropdown)

        self.output_label = QLabel("Output folder: Not selected")
        layout.addWidget(self.output_label)

        browse_btn = QPushButton("Select Output Folder")
        browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(browse_btn)

        self.progress = QProgressBar()
        self.progress.setFormat("0%")
        layout.addWidget(self.progress)

        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)
        layout.addWidget(self.log_window)

        hlayout = QHBoxLayout()

        # Add Back button
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self._on_back)
        hlayout.addWidget(back_btn)

        self.load_formats_btn = QPushButton("Load Formats")
        self.load_formats_btn.clicked.connect(self.load_formats)
        hlayout.addWidget(self.load_formats_btn)

        self.download_btn = QPushButton("Download")
        self.download_btn.setEnabled(False)           # ← start disabled
        self.download_btn.clicked.connect(self.download)
        hlayout.addWidget(self.download_btn)

        theme_btn = QPushButton("Switch Theme")
        theme_btn.clicked.connect(self.switch_theme)
        hlayout.addWidget(theme_btn)

        layout.addLayout(hlayout)
        central.setLayout(layout)

        self.output_path = os.getcwd()
        self.current_theme = "dark"
        self.spinner_dialog = None

        self.audio_radio.toggled.connect(lambda checked: self.format_dropdown.setVisible(not checked))
        self.video_radio.toggled.connect(self.update_download_button_state)
        self.audio_radio.toggled.connect(self.update_download_button_state)

        self.format_dropdown.currentIndexChanged.connect(
        self.update_download_button_state
        
)
        # Output folder section
        self.open_folder_btn = QPushButton("Open Output Folder")
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        self.open_folder_btn.setEnabled(False)
        layout.addWidget(self.open_folder_btn)

    def update_download_button_state(self):
        url_ok = bool(self.url_input.text().strip())
        folder_ok = bool(self.output_path)
        format_ok = bool(self.format_dropdown.currentData())

        self.open_folder_btn.setEnabled(folder_ok)

        if self.audio_radio.isChecked():
            ready = url_ok and folder_ok
        else:
            ready = url_ok and folder_ok and format_ok
        self.download_btn.setEnabled(ready)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path = folder
            self.output_label.setText(f"Output folder: {folder}")
            self.update_download_button_state()  # Update button state after selecting folder
            self.log_window.append(f"Output folder set to: {folder}")
            
    def switch_theme(self):
        if self.current_theme == "dark":
            self.apply_theme(resource_path("assets/qss/light.qss"))
            self.current_theme = "light"
        else:
            self.apply_theme(resource_path("assets/qss/dark.qss"))
            self.current_theme = "dark"

    def apply_theme(self, theme_path):
        try:
            with open(theme_path, "r") as f:
                style = f.read()
                self.setStyleSheet(style)
        except Exception as e:
            self.show_error("Error loading theme", str(e))

    def load_formats(self):
        url = self.url_input.text()
        if not url:
            self.show_error("Missing URL", "Please enter a YouTube URL.")
            return
        try:
            self.spinner_dialog = SpinnerDialog("Loading formats...")
            movie = QMovie(gif_path)
            self.spinner_dialog.spinner.setMovie(movie)
            movie.start()
            self.spinner_dialog.show()
            QTimer.singleShot(100, lambda: self._fetch_formats(url))
        except Exception as e:
            self.show_error("Error", str(e))

    def _fetch_formats(self, url):
        try:
            formats = get_formats(url)
            self.format_dropdown.clear()
            for f in formats:
                label = f"{f['format_id']} - {f['ext']} - {f.get('format_note', '')} - {f.get('resolution', '') or f.get('abr', '')}"
                self.format_dropdown.addItem(label, f['format_id'])
        except Exception as e:
            self.format_dropdown.clear()
            self.format_dropdown.addItem(f"Error: {e}")
        finally:
            if self.spinner_dialog:
                self.spinner_dialog.accept()
                self.spinner_dialog = None

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_info(self, title, message):
        QMessageBox.information(self, title, message)

    def download_finished(self):
        self.progress.setValue(100)
        self.progress.setFormat("100%")
        self.download_btn.setEnabled(True)
        url = self.url_input.text()
        if not url:
            return

        try:
            from yt_dlp import YoutubeDL
            with YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "video")
                ext = "mp4"
                final_path = os.path.join(self.output_path, f"{title}.{ext}")
                self.log_window.append(f"Download complete!\nSaved to: {final_path}")
                self.show_info("Download Complete", f"Saved to:\n{final_path}")
        except Exception as e:
            self.log_window.append(f"Download finished, but failed to resolve file path: {e}")
            self.show_error("Download Error", str(e))

    def update_progress(self, percent: int):
        self.progress.setValue(percent)
        self.progress.setFormat(f"{percent}%")
        self.log_window.append(f"Progress: {percent}%")

    def download(self):
        url = self.url_input.text()
        if not url:
            self.log_window.append("Error: URL is empty.")
            return

        is_audio = self.audio_radio.isChecked()
        format_code = self.format_dropdown.currentData() if not is_audio else None

        self.progress.setValue(0)
        self.progress.setFormat("0%")
        self.download_btn.setEnabled(False)

        if is_audio:
            self.log_window.append("Starting audio (MP3) download...")
        else:
            self.log_window.append(f"Starting video download with format: {format_code}")

        self.thread = DownloadThread(url, format_code, self.output_path, is_audio)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.download_finished)
        self.thread.error.connect(lambda e: self.show_error("Download Failed", e))
        self.thread.error.connect(lambda e: self.download_btn.setEnabled(True))
        self.thread.log.connect(self.log_window.append)
        self.thread.start()

        self.log_window.append(f"Downloading {url} to {self.output_path}")

    def _setup_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        file_menu = QMenu("&File", self)
        quit_action = QAction("&Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        menubar.addMenu(file_menu)

        info_menu = QMenu("&Info", self)
        dev_action = QAction("Developer Info", self)
        dev_action.triggered.connect(self.show_dev_info)
        update_action = QAction("Check for Update", self)
        update_action.triggered.connect(self.check_update)
        info_menu.addAction(dev_action)
        info_menu.addAction(update_action)
        menubar.addMenu(info_menu)

        # Increase menu font size
        menubar.setStyleSheet("QMenuBar { font-size: 15px; } QMenu { font-size: 15px; }")

    def show_dev_info(self):
        dev_dialog = QDialog(self)
        dev_dialog.setWindowTitle("Developer Info")
        dev_dialog.setFixedSize(400, 200)
        # Center the dialog over the main window
        parent_rect = self.geometry()
        x = parent_rect.x() + (parent_rect.width() - 400) // 2
        y = parent_rect.y() + (parent_rect.height() - 200) // 2
        dev_dialog.move(x, y)
        layout = QVBoxLayout()
        info = QLabel(
            "<h2>YouVideo Downloader</h2>"
            "<p><b>Developer:</b> Sarwar</p>"
            "<p><b>GitHub:</b> <a href='https://github.com/Sarwarhridoy4/youvideo-downloader'>https://github.com/Sarwarhridoy4/youvideo-downloader</a></p>"
        )
        info.setOpenExternalLinks(True)
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        dev_dialog.setLayout(layout)
        dev_dialog.exec()

    def check_update(self):
        try:
            resp = requests.get(GITHUB_RELEASES_URL, timeout=5)
            data = resp.json()
            latest = data.get("tag_name")
            if not latest:
                raise Exception("No tag_name in response")
            if latest != APP_VERSION:
                QMessageBox.information(self, "Update Available",
                    f"New version available: {latest}\nVisit:\nhttps://github.com/Sarwarhridoy4/youvideo-downloader/releases/tag/{latest}")
            else:
                QMessageBox.information(self, "Up to Date", "You have the latest version.")
        except Exception as e:
            QMessageBox.warning(self, "Update Error", f"Could not check for updates: {e}")
    
    def _open_output_folder(self):
        if not self.output_path:
            self.show_error("No folder", "Select an output folder first.")
            return
        if sys.platform.startswith("win"):
            os.startfile(self.output_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", self.output_path])
        else:
            subprocess.Popen(["xdg-open", self.output_path])

    def _on_back(self):
        if self._back_callback:
            self.hide()
            self._back_callback()

    def _on_formats_loaded(self, formats):
        self.format_dropdown.clear()
        for f in formats:
            label = f"{f['format_id']} - {f['ext']} - {f.get('format_note', '')} - {f.get('resolution', '') or f.get('abr', '')}"
        self.format_dropdown.addItem(label, f['format_id'])
        if self.spinner_dialog:
            self.spinner_dialog.accept()
            self.spinner_dialog = None

    def _on_formats_error(self, error_message):
        self.format_dropdown.clear()
        self.format_dropdown.addItem(f"Error: {error_message}")
        if self.spinner_dialog:
            self.spinner_dialog.accept()
            self.spinner_dialog = None
        self.show_error("Error loading formats", error_message)