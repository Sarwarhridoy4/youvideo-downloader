from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
import os

from utils.pathfinder import resource_path

icon_path = resource_path("assets/icons/appicon.png")

class WelcomeScreen(QWidget):
    """
    A QWidget-based welcome screen for the YouVideo Downloader application.
    This screen displays the application icon, title, subtitle, and a "Continue" button.
    It loads and applies a QSS stylesheet for custom appearance.
    Args:
        on_continue (callable): Callback function to be called when the "Continue" button is clicked.
    Attributes:
        None (all widgets are local to __init__).
    Raises:
        Prints an error message if the QSS stylesheet cannot be loaded.
    UI Elements:
        - App icon (QLabel with QPixmap)
        - Title (QLabel)
        - Subtitle (QLabel)
        - Continue button (QPushButton)
    """
    def __init__(self, on_continue):
        super().__init__()
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
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # App icon
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)

        # Title
        title = QLabel("YouVideo Downloader")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Download YouTube,Facebook and Others videos easily in your favorite format.\nFast, simple, and free.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Continue button
        continue_btn = QPushButton("Continue")
        continue_btn.clicked.connect(on_continue)
        layout.addWidget(continue_btn)

        credit_label = QLabel()
        credit_label.setText(
        'Made with ❤️ by <a href="https://sarwar-hossain-vert.vercel.app"style="color:#007acc; text-decoration:none;">Sarwar Hossain</a>'
        )
        credit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credit_label.setOpenExternalLinks(True)  # so link opens in browser
        credit_label.setObjectName("credit_label")
        layout.addWidget(credit_label)
