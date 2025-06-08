# ui/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QComboBox, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from downloader.yt_downloader import get_formats, download_and_merge
import os


class DownloadThread(QThread):
    progress = pyqtSignal(int)  # emits int percentage
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouVideo Downloader")
        self.resize(700, 500)
        self.setup_ui()
        self.apply_theme("assets/qss/dark.qss")

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
        self.progress.setFormat("0%")  # show percentage inside progress bar
        layout.addWidget(self.progress)

        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)
        layout.addWidget(self.log_window)

        hlayout = QHBoxLayout()

        load_formats_btn = QPushButton("Load Formats")
        load_formats_btn.clicked.connect(self.load_formats)
        hlayout.addWidget(load_formats_btn)

        download_btn = QPushButton("Download")
        download_btn.clicked.connect(self.download)
        hlayout.addWidget(download_btn)

        theme_btn = QPushButton("Switch Theme")
        theme_btn.clicked.connect(self.switch_theme)
        hlayout.addWidget(theme_btn)

        layout.addLayout(hlayout)
        central.setLayout(layout)

        self.output_path = os.getcwd()
        self.current_theme = "dark"

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
            print("Error loading theme:", e)

    def load_formats(self):
        url = self.url_input.text()
        if not url:
            return
        try:
            formats = get_formats(url)
            self.format_dropdown.clear()
            for f in formats:
                label = f"{f['format_id']} - {f['ext']} - {f.get('format_note', '')} - {f.get('resolution', '') or f.get('abr', '')}"
                self.format_dropdown.addItem(label, f['format_id'])
        except Exception as e:
            self.format_dropdown.clear()
            self.format_dropdown.addItem(f"Error: {e}")

    def download_finished(self):
        self.progress.setValue(100)
        self.progress.setFormat("100%")
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
        except Exception as e:
            self.log_window.append(f"Download finished, but failed to resolve file path: {e}")

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
        self.log_window.append(f"Starting download with format: {format_code}")

        self.thread = DownloadThread(url, format_code, self.output_path)
        self.thread.progress.connect(self.update_progress)  # use custom slot
        self.thread.finished.connect(self.download_finished)
        self.thread.error.connect(lambda e: self.log_window.append(f"Error: {e}"))
        self.thread.log.connect(self.log_window.append)
        self.thread.start()

        self.log_window.append("Download started...")
        self.log_window.append(f"Downloading {url} with format {format_code} to {self.output_path}")
