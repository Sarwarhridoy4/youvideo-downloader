from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
import os

from utils.pathfinder import resource_path

icon_path = resource_path("assets/icons/appicon.png")

class WelcomeScreen(QWidget):
    """
    A QWidget-based welcome screen for the YouVideo Downloader application.
    This screen displays the application icon, title, subtitle, and two buttons:
    "Single Video" and "Playlist".
    """

    def __init__(self, on_single_video=None, on_playlist=None):
        super().__init__()
        self._on_single_video = on_single_video
        self._on_playlist = on_playlist
        self.setWindowTitle("Welcome - YouVideo Downloader")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(640, 400)

        # Load and apply QSS style from assets/qss/welcome.qss
        qss_path = resource_path("assets/qss/welcome.qss")
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load welcome.qss: {e}")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # App icon
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

        # Title
        title = QLabel("YouVideo Downloader")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Download YouTube, Facebook and Others videos easily in your favorite format.\nFast, simple, and free.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Single Video button
        single_btn = QPushButton("Single Video")
        single_btn.clicked.connect(self._handle_single)
        layout.addWidget(single_btn)

        # Playlist button
        playlist_btn = QPushButton("Playlist")
        playlist_btn.clicked.connect(self._handle_playlist)
        layout.addWidget(playlist_btn)

        # Credit
        credit_label = QLabel()
        credit_label.setText(
            'Made with ❤️ by <a href="https://sarwar-hossain-vert.vercel.app" style="color:#007acc; text-decoration:none;">Sarwar Hossain</a>'
        )
        credit_label.setAlignment(Qt.AlignCenter)
        credit_label.setOpenExternalLinks(True)
        credit_label.setObjectName("credit_label")
        layout.addWidget(credit_label)

    def set_callbacks(self, on_single_video, on_playlist):
        self._on_single_video = on_single_video
        self._on_playlist = on_playlist

    def _handle_single(self):
        if self._on_single_video:
            self._on_single_video()

    def _handle_playlist(self):
        if self._on_playlist:
            self._on_playlist()
