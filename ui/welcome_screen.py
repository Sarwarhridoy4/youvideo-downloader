from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal
import os

from utils.pathfinder import resource_path

icon_path = resource_path("assets/icons/appicon.png")
dark_qss_path = resource_path("assets/qss/welcome_dark.qss")
light_qss_path = resource_path("assets/qss/welcome_light.qss")


class WelcomeScreen(QWidget):
    """
    A QWidget-based welcome screen for the YouVideo Downloader application.
    This screen displays the application icon, title, subtitle, two buttons
    ("Single Video" and "Playlist"), and a theme toggle button.
    """
    
    # Signal to notify parent about theme changes
    theme_changed = Signal(str)  # Emits "dark" or "light"

    def __init__(self, on_single_video=None, on_playlist=None):
        super().__init__()
        self._on_single_video = on_single_video
        self._on_playlist = on_playlist
        self.current_theme = "dark"  # Default theme
        
        self.setWindowTitle("Welcome - YouVideo Downloader")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(720, 520)

        self._setup_ui()
        self._apply_theme(dark_qss_path)

    def _setup_ui(self):
        """Build the welcome screen UI with theme toggle."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(40, 30, 40, 30)

        # Top bar with theme toggle
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        
        self.theme_toggle_btn = QPushButton("🌙")
        self.theme_toggle_btn.setObjectName("themeToggle")
        self.theme_toggle_btn.setToolTip("Switch to light theme")
        self.theme_toggle_btn.setFixedSize(40, 40)
        self.theme_toggle_btn.clicked.connect(self._toggle_theme)
        top_bar.addWidget(self.theme_toggle_btn)
        
        main_layout.addLayout(top_bar)
        
        # Spacer
        main_layout.addSpacing(10)

        # App icon
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(icon_label)

        # Title
        title = QLabel("YouVideo Downloader")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(
            "Download YouTube, Facebook and other videos easily in your favorite format.\n"
            "Fast, simple, and free."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        main_layout.addWidget(subtitle)
        
        # Spacer
        main_layout.addSpacing(10)

        # Buttons container (side by side)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(16)
        
        # Single Video button with icon
        single_btn = QPushButton("🎬 Single Video")
        single_btn.setObjectName("actionButton")
        single_btn.setMinimumHeight(50)
        single_btn.setMinimumWidth(200)
        single_btn.clicked.connect(self._handle_single)
        buttons_layout.addWidget(single_btn)

        # Playlist button with icon
        playlist_btn = QPushButton("📋 Playlist")
        playlist_btn.setObjectName("actionButton")
        playlist_btn.setMinimumHeight(50)
        playlist_btn.setMinimumWidth(200)
        playlist_btn.clicked.connect(self._handle_playlist)
        buttons_layout.addWidget(playlist_btn)
        
        main_layout.addLayout(buttons_layout)
        
        # Spacer
        main_layout.addSpacing(10)

        # Credit
        credit_label = QLabel()
        credit_label.setText(
            'Made with ❤️ by <a href="https://sarwar-hossain-vert.vercel.app" '
            'style="color:#007acc; text-decoration:none;">Sarwar Hossain</a>'
        )
        credit_label.setAlignment(Qt.AlignCenter)
        credit_label.setOpenExternalLinks(True)
        credit_label.setObjectName("credit_label")
        main_layout.addWidget(credit_label)

    def _apply_theme(self, theme_path: str):
        """Apply QSS theme from file."""
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load theme: {e}")

    def _toggle_theme(self):
        """Toggle between dark and light themes."""
        if self.current_theme == "dark":
            # Switch to light
            self.current_theme = "light"
            self.theme_toggle_btn.setText("☀️")
            self.theme_toggle_btn.setToolTip("Switch to dark theme")
            
            # Apply light theme if available
            if os.path.exists(light_qss_path):
                self._apply_theme(light_qss_path)
            else:
                # Fallback: modify current stylesheet
                self._apply_light_theme_inline()
        else:
            # Switch to dark
            self.current_theme = "dark"
            self.theme_toggle_btn.setText("🌙")
            self.theme_toggle_btn.setToolTip("Switch to light theme")
            self._apply_theme(dark_qss_path)
        
        # Notify parent about theme change
        self.theme_changed.emit(self.current_theme)

    def _apply_light_theme_inline(self):
        """Fallback light theme using inline stylesheet - matches welcome_light.qss exactly."""
        light_style = """
            QWidget {
                background: #ffffff;
                color: #0f0f0f;
                font-family: 'Roboto', 'Segoe UI', sans-serif;
                border-radius: 22px;
            }
            
            QLabel#title {
                color: #0f0f0f;
                font-size: 30px;
                font-weight: bold;
                letter-spacing: 1px;
                padding: 18px 0 8px 0;
            }
            
            QLabel#subtitle {
                color: #606060;
                font-size: 16px;
                margin-bottom: 22px;
            }
            
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff0000, stop:1 #cc0000);
                color: #ffffff;
                font-size: 18px;
                border: none;
                border-radius: 18px;
                padding: 14px 40px;
                margin-top: 22px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff1a1a, stop:1 #e60000);
                border: 2px solid #ff0000;
            }
            
            QPushButton:pressed {
                background-color: #cc0000;
                border: 2px solid #990000;
            }
            
            QPushButton:disabled {
                background-color: #e8eaed;
                color: #9e9e9e;
                border: none;
            }
            
            QPushButton#actionButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff0000, stop:1 #cc0000);
                color: #ffffff;
                font-size: 15px;
                border: none;
                border-radius: 16px;
                padding: 12px 24px;
                margin-top: 0px;
                font-weight: 600;
                letter-spacing: 0.3px;
                min-width: 180px;
                max-width: 220px;
            }
            
            QPushButton#actionButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff1a1a, stop:1 #e60000);
                border: 2px solid #ff0000;
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(255, 0, 0, 0.3);
            }
            
            QPushButton#actionButton:pressed {
                background-color: #cc0000;
                border: 2px solid #990000;
                transform: translateY(0px);
            }
            
            QPushButton#themeToggle {
                background-color: rgba(248, 249, 250, 0.95);
                border: 1px solid #dadce0;
                border-radius: 20px;
                padding: 8px 12px;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
                font-size: 16px;
                margin: 0;
                text-transform: none;
                letter-spacing: 0;
            }
            
            QPushButton#themeToggle:hover {
                background-color: rgba(241, 243, 244, 1);
                border-color: #ff0000;
                box-shadow: 0 4px 12px rgba(255, 0, 0, 0.15);
            }
            
            #credit_label {
                font-size: 14px;
                color: #606060;
                margin-top: 2rem;
                margin-bottom: 2rem;
            }
            
            #credit_label:hover {
                color: #0f0f0f;
            }
            
            #credit_label a {
                color: #3ea6ff;
                text-decoration: none;
                font-weight: 500;
            }
            
            #credit_label a:hover {
                color: #65b8ff;
                text-decoration: underline;
            }
        """
        self.setStyleSheet(light_style)

    def set_callbacks(self, on_single_video, on_playlist):
        """Set callbacks for button clicks."""
        self._on_single_video = on_single_video
        self._on_playlist = on_playlist

    def _handle_single(self):
        """Handle single video button click."""
        if self._on_single_video:
            self._on_single_video()

    def _handle_playlist(self):
        """Handle playlist button click."""
        if self._on_playlist:
            self._on_playlist()
    
    def get_current_theme(self) -> str:
        """Get the current theme name."""
        return self.current_theme
    
    def set_theme(self, theme: str):
        """Set theme programmatically (used by parent window)."""
        if theme == self.current_theme:
            return
            
        if theme == "light":
            self.current_theme = "light"
            self.theme_toggle_btn.setText("☀️")
            self.theme_toggle_btn.setToolTip("Switch to dark theme")
            
            if os.path.exists(light_qss_path):
                self._apply_theme(light_qss_path)
            else:
                self._apply_light_theme_inline()
        else:
            self.current_theme = "dark"
            self.theme_toggle_btn.setText("🌙")
            self.theme_toggle_btn.setToolTip("Switch to light theme")
            self._apply_theme(dark_qss_path)