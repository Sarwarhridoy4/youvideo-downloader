# ui/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QComboBox,
    QProgressBar, QTextEdit, QMessageBox, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QMovie, QIcon
from downloader.yt_downloader import get_formats, download_and_merge
import os
from downloader.ffmpeg_utils import ensure_ffmpeg
from PyQt6.QtWidgets import QApplication
# Ensure the icon path is correct
icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "appicon.png")
gif_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "spinner.gif")

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, url, format_code, output_path):
        super().__init__()
        self.url = url
        self.format_code = format_code
        self.output_path = output_path
        

    def run(self):
        try:
            def hook(d):
                if d.get("status") == "downloading":
                    downloaded = d.get("downloaded_bytes") or 0
                    total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
                    percent = downloaded / total * 100
                    self.progress.emit(int(percent))
                    self.log.emit(f"Downloading: {percent:.2f}%")

            download_and_merge(self.url, self.format_code, self.output_path, hook, self.log)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class SpinnerDialog(QDialog):
    def __init__(self, message="Loading..."):
        super().__init__()
        self.setWindowTitle("Please wait")
        self.setWindowIcon(QIcon(icon_path))  # Ensure the icon path is correct
        self.setModal(True)
        self.setFixedSize(200, 150)

        layout = QVBoxLayout(self)

        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.spinner = QLabel(self)
        movie = QMovie(gif_path)
        self.spinner.setMovie(movie)
        movie.start()
        layout.addWidget(self.spinner)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouVideo Downloader")
        self.setWindowIcon(QIcon(icon_path))  # Ensure the icon path is correct
        QApplication.setWindowIcon(QIcon(icon_path))  # Taskbar icon
        self.setMinimumSize(700, 500)

        self.resize(700, 500)
        self.setup_ui()
        self.apply_theme("assets/qss/dark.qss")

        # FFmpeg check
        if not ensure_ffmpeg(self.log_window.append):
            self.show_error("FFmpeg Missing", "FFmpeg is not installed or not in PATH.")
            self.download_btn.setEnabled(False)
            self.load_formats_btn.setEnabled(False)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL")
        layout.addWidget(self.url_input)

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

        self.load_formats_btn = QPushButton("Load Formats")
        self.load_formats_btn.clicked.connect(self.load_formats)
        hlayout.addWidget(self.load_formats_btn)

        self.download_btn = QPushButton("Download")
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

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path = folder
            self.output_label.setText(f"Output folder: {folder}")

    def switch_theme(self):
        if self.current_theme == "dark":
            self.apply_theme("assets/qss/light.qss")
            self.current_theme = "light"
        else:
            self.apply_theme("assets/qss/dark.qss")
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
            # Use a GIF image as loader (e.g., gig.gif in assets/icons)
            gig_gif_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "spinner.gif")
            self.spinner_dialog = SpinnerDialog("Loading formats...")
            # Replace spinner GIF with gig GIF
            movie = QMovie(gig_gif_path)
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

        format_code = self.format_dropdown.currentData()
        if not format_code:
            self.log_window.append("Error: No format selected.")
            return

        self.progress.setValue(0)
        self.progress.setFormat("0%")
        self.download_btn.setEnabled(False)

        self.log_window.append(f"Starting download with format: {format_code}")

        self.thread = DownloadThread(url, format_code, self.output_path)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.download_finished)
        self.thread.error.connect(lambda e: self.show_error("Download Failed", e))
        self.thread.error.connect(lambda e: self.download_btn.setEnabled(True))
        self.thread.log.connect(self.log_window.append)
        self.thread.start()

        self.log_window.append("Download started...")
        self.log_window.append(f"Downloading {url} with format {format_code} to {self.output_path}")
