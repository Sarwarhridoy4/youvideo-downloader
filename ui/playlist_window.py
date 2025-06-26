from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
    QProgressBar, QTextEdit, QHBoxLayout, QMessageBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from utils.pathfinder import resource_path
import os
import subprocess
import sys
from downloader.yt_downloader import get_playlist_videos

icon_path = resource_path("assets/icons/appicon.png")
qss_path = resource_path("assets/qss/dark.qss")

class PlaylistLoaderThread(QThread):
    loaded = Signal(list)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            videos = get_playlist_videos(self.url)
            self.loaded.emit(videos)
        except Exception as e:
            self.error.emit(str(e))

class PlaylistWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._back_callback = None
        self.setWindowTitle("YouVideo Downloader - Playlist")
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(900, 650)
        self.setup_ui()
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load dark.qss: {e}")

    def set_back_callback(self, callback):
        self._back_callback = callback

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Playlist URL")
        layout.addWidget(self.url_input)

        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("Optional: Range (e.g. 1-5)")
        layout.addWidget(self.range_input)

        self.load_btn = QPushButton("Load Playlist Videos")
        self.load_btn.clicked.connect(self.load_playlist_videos)
        layout.addWidget(self.load_btn)

        self.video_list = QListWidget()
        self.video_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.video_list)

        self.output_label = QLabel("Output folder: Not selected")
        layout.addWidget(self.output_label)

        browse_btn = QPushButton("Select Output Folder")
        browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(browse_btn)

        hlayout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self._on_back)
        hlayout.addWidget(back_btn)

        self.download_btn = QPushButton("Download Selected")
        self.download_btn.clicked.connect(self.download_selected)
        hlayout.addWidget(self.download_btn)

        open_folder_btn = QPushButton("Open Output Folder")
        open_folder_btn.clicked.connect(self.open_output_folder)
        hlayout.addWidget(open_folder_btn)

        layout.addLayout(hlayout)

        self.progress = QProgressBar()
        self.progress.setFormat("0%")
        layout.addWidget(self.progress)

        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)
        layout.addWidget(self.log_window)

        central.setLayout(layout)
        self.output_path = os.getcwd()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path = folder
            self.output_label.setText(f"Output folder: {folder}")

    def load_playlist_videos(self):
        url = self.url_input.text()
        if not url:
            self.show_error("Missing URL", "Please enter a playlist URL.")
            return
        self.video_list.clear()
        self.load_btn.setEnabled(False)
        self.load_btn.setText("Loading...")
        self.log_window.append("Loading playlist videos...")
        self.loader_thread = PlaylistLoaderThread(url)
        self.loader_thread.loaded.connect(self.on_videos_loaded)
        self.loader_thread.error.connect(self.on_videos_error)
        self.loader_thread.start()

    def on_videos_loaded(self, videos):
        self.video_list.clear()
        for idx, v in enumerate(videos):
            item = QListWidgetItem(f"{idx+1}. {v['title']}")
            self.video_list.addItem(item)
        self.load_btn.setEnabled(True)
        self.load_btn.setText("Load Playlist Videos")
        self.log_window.append(f"Loaded {len(videos)} videos.")

    def on_videos_error(self, error):
        self.load_btn.setEnabled(True)
        self.load_btn.setText("Load Playlist Videos")
        self.show_error("Error", error)

    def download_selected(self):
        url = self.url_input.text()
        if not url:
            self.log_window.append("Error: URL is empty.")
            return
        selected = self.video_list.selectedIndexes()
        if not selected:
            self.log_window.append("Select at least one video.")
            return
        indices = [i.row() for i in selected]

        # Handle range input
        range_text = self.range_input.text().strip()
        if range_text:
            try:
                parts = range_text.split('-')
                if len(parts) == 2:
                    start, end = map(int, parts)
                    indices = [i for i in indices if start-1 <= i <= end-1]
            except Exception:
                self.log_window.append("Invalid range format. Use e.g. 1-5")
                return

        self.progress.setValue(0)
        self.progress.setFormat("0%")
        self.download_btn.setEnabled(False)
        # ... Start your download thread as before, passing indices ...
        # self.thread = PlaylistDownloadThread(url, self.output_path, indices)
        # ... connect signals and start thread ...

    def update_progress(self, percent: int):
        self.progress.setValue(percent)
        self.progress.setFormat(f"{percent}%")
        self.log_window.append(f"Progress: {percent}%")

    def download_finished(self):
        self.progress.setValue(100)
        self.progress.setFormat("100%")
        self.download_btn.setEnabled(True)
        self.log_window.append("All downloads complete!")

    def open_output_folder(self):
        path = self.output_path
        if os.name == "nt":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def _on_back(self):
        if self._back_callback:
            self.hide()
            self._back_callback()