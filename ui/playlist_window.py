"""Playlist window for YouVideo‑Downloader
------------------------------------------------
Improvements 2025‑06‑28
~~~~~~~~~~~~~~~~~~~~~~
• Faster *playlist* loading by asking ``get_playlist_videos`` to fetch **only the
  requested slice** when possible (falls back gracefully).
• The *range* is analysed **before** the worker starts, so we never fetch more
  videos than we need.
• The **Download** button is *disabled* until the user picks an output folder –
  no more accidental downloads into the current working directory.
• Added small UX touches (busy cursor while loading, clearer log entries).

Save this as ``playlist_window.py`` and import it from ``main.py`` as before.
"""
from __future__ import annotations

import os
import sys
import subprocess
from typing import List, Sequence

import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QAction, QCursor
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QProgressBar,
    QTextEdit,
    QWidget,
    QMenuBar,
    QMenu,
    QApplication,
)

from utils.pathfinder import resource_path
from downloader.yt_downloader import get_playlist_videos, download_and_merge

# ──────────────────────────── paths & constants ─────────────────────────────
icon_path = resource_path("assets/icons/appicon.png")
qss_path = resource_path("assets/qss/dark.qss")

APP_VERSION = "1.0.0"
GITHUB_RELEASES_URL = (
    "https://api.github.com/repos/Sarwarhridoy4/youvideo-downloader/releases/latest"
)

# ──────────────────────────── helpers ───────────────────────────────────────

def slice_by_range(txt: str, length: int | None = None) -> List[int]:
    """Return 0‑based indices selected by a user‑typed *range* string.

    >>> slice_by_range("", 5)          # full list
    [0, 1, 2, 3, 4]
    >>> slice_by_range("3-1", 5)       # order ignored / clipped
    [0, 1, 2]
    >>> slice_by_range("4-", 5)
    [3, 4]
    """

    txt = txt.replace(" ", "")
    if not txt:
        # If *length* is unknown (None) we return empty – caller decides.
        return list(range(length)) if length is not None else []

    if "-" in txt:
        left, right = txt.split("-", 1)
        start = int(left) if left else 1
        end = int(right) if right else (length if length is not None else start)
    else:
        start, end = 1, int(txt)

    if length is not None:
        start = max(1, min(start, length))
        end = max(1, min(end, length))
    if start > end:
        start, end = end, start

    return list(range(start - 1, end))


# ──────────────────────────── worker threads ────────────────────────────────
class PlaylistLoaderThread(QThread):
    """Fetch playlist slice in a worker thread (non‑blocking UI)."""

    loaded = Signal(list)  # list[dict]
    error = Signal(str)

    def __init__(self, url: str, wanted_indices: Sequence[int]):
        super().__init__()
        self.url = url
        self.wanted_indices = wanted_indices

    def run(self) -> None:  # noqa: D401
        try:
            # Ask downstream helper to *only* fetch the wanted items if supported
            # (yt‑dlp understands "playlist_items") – we detect support at run‑time.
            videos: List[dict]
            indices_str = ",".join(str(i + 1) for i in self.wanted_indices)
            try:
                videos = get_playlist_videos(
                    self.url, playlist_items=indices_str if indices_str else None
                )
            except TypeError:
                # Fallback: helper does not accept kwargs → fetch full list.
                videos = get_playlist_videos(self.url)
            # Ensure correct order/selection if fallback path was used.
            if len(videos) > len(self.wanted_indices):
                videos = [videos[i] for i in self.wanted_indices]
            self.loaded.emit(videos)
        except Exception as exc:  # pragma: no cover – propagate all errors up
            self.error.emit(str(exc))


class PlaylistDownloadThread(QThread):
    """Download & merge selected playlist items in the background."""

    progress = Signal(int)  # overall percent 0‑100
    log = Signal(str)  # text for GUI log
    finished = Signal()

    def __init__(
        self,
        videos: List[dict],
        indices: List[int],
        out_dir: str,
        fmt_code: str = "bestvideo",  # yt‑dlp will add +bestaudio
    ) -> None:
        super().__init__()
        self.videos = videos
        self.indices = indices
        self.out_dir = out_dir
        self.fmt_code = fmt_code

    def _hook(self, d: dict) -> None:
        if d.get("status") == "downloading":
            pct = d.get("_percent_str", "0%").strip()
            self.log.emit(f"    ↳ {pct}")

    def run(self) -> None:  # noqa: D401 – required signature
        total = len(self.indices)
        for n, idx in enumerate(self.indices, start=1):
            video = self.videos[idx]
            title = video["title"]
            url = video["url"]

            self.log.emit(f"▶ {title}")
            try:
                download_and_merge(
                    url,
                    self.fmt_code,
                    self.out_dir,
                    self._hook,
                    self.log,
                )
                self.log.emit("✔ done\n")
            except Exception as exc:  # keep going on per‑file error
                self.log.emit(f"❌ {exc}\n")

            self.progress.emit(int(n * 100 / total))

        self.finished.emit()


# ──────────────────────────── main window ───────────────────────────────────
class PlaylistWindow(QMainWindow):
    """Main GUI class for playlist handling."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__()
        self._back_callback = None

        self.setWindowTitle("YouVideo Downloader – Playlist")
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(900, 650)

        self.output_path: str | None = None  # ➟ user *must* choose!
        self.current_theme = "dark"  # default theme

        self._setup_ui()
        self._apply_stylesheet()
        self._setup_menu()

    # ―― UI assembly ―――――――――――――――――――――――――――――――――――――――――――――――――――
    def _setup_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # — URL & range input
        self.url_input = QLineEdit(placeholderText="Enter playlist URL")
        self.range_input = QLineEdit(placeholderText="Optional: range (e.g. 1-5)")

        # — buttons & list
        self.load_btn = QPushButton("Load playlist videos")
        self.load_btn.clicked.connect(self._load_playlist_videos)  # type: ignore[arg-type]

        self.video_list = QListWidget(selectionMode=QListWidget.MultiSelection)

        self.output_label = QLabel("Output folder: <b>Not selected</b>")
        browse_btn = QPushButton("Select output folder")
        browse_btn.clicked.connect(self._browse_folder)  # type: ignore[arg-type]

        # — footer buttons
        hlayout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self._on_back)  # type: ignore[arg-type]

        self.download_btn = QPushButton("Download selected")
        self.download_btn.setEnabled(False)  # ⛔ disabled until folder chosen
        self.download_btn.clicked.connect(self._download_selected)  # type: ignore[arg-type]

        open_folder_btn = QPushButton("Open output folder")
        open_folder_btn.clicked.connect(self._open_output_folder)  # type: ignore[arg-type]

        theme_btn = QPushButton("Switch Theme")
        theme_btn.clicked.connect(self.switch_theme)

        # button layout
        for w in (back_btn, theme_btn, self.download_btn, open_folder_btn):
            hlayout.addWidget(w)

        # — progress + log
        self.progress = QProgressBar(format="0%")
        self.log_window = QTextEdit(readOnly=True)

        # — pack widgets
        for w in (
            self.url_input,
            self.range_input,
            self.load_btn,
            self.video_list,
            self.output_label,
            browse_btn,
            hlayout,
            self.progress,
            self.log_window,
        ):
            (layout.addLayout(w) if isinstance(w, QHBoxLayout) else layout.addWidget(w))

    # ―――――――――――――――― appearance helpers ――――――――――――――――――――――――――
    def _apply_stylesheet(self) -> None:
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as exc:
            print(f"[PlaylistWindow] Could not load stylesheet: {exc}")

    # ──────────────────────────── menu bar ─────────────────────────────────
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
        menubar.setStyleSheet(
            "QMenuBar { font-size: 15px; } QMenu { font-size: 15px; }"
        )

    # ───────────────────────────── info/actions ────────────────────────────
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
                QMessageBox.information(
                    self,
                    "Update Available",
                    (
                        f"New version available: {latest}\nVisit:\n"
                        f"https://github.com/Sarwarhridoy4/youvideo-downloader/releases/tag/{latest}"
                    ),
                )
            else:
                QMessageBox.information(self, "Up to Date", "You have the latest version.")
        except Exception as e:
            QMessageBox.warning(self, "Update Error", f"Could not check for updates: {e}")

    # ───────────────────────────── folders/ui ──────────────────────────────
    def _browse_folder(self) -> None:  # noqa: D401
        folder = QFileDialog.getExistingDirectory(self, "Select output folder")
        if folder:
            self.output_path = folder
            self.output_label.setText(f"Output folder: {folder}")
            self.download_btn.setEnabled(True)  # ✅ ready to download

    # ───────────────────────────── playlist load ───────────────────────────
    def _load_playlist_videos(self) -> None:  # noqa: D401
        url = self.url_input.text().strip()
        if not url:
            self._show_error("Missing URL", "Please enter a playlist URL")
            return

        # Determine which indices we *really* need.
        self._all_videos = []  # reset cache
        range_txt = self.range_input.text().strip()
        wanted_indices: List[int] = []  # may stay empty → loader decides
        if range_txt:
            # We don't yet know the playlist length → let worker slice after fetch.
            # For helpers that support "playlist_items" we pre‑calculate indices up
            # to an arbitrary large value – if playlist shorter, it's clipped.
            wanted_indices = slice_by_range(range_txt, length=10_000)

        self.video_list.clear()
        self.load_btn.setEnabled(False)
        self.load_btn.setText("Loading…")
        self.log_window.append("Loading playlist videos…")
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        self.loader_thread = PlaylistLoaderThread(url, wanted_indices)
        self.loader_thread.loaded.connect(self._videos_fetched)  # type: ignore[arg-type]
        self.loader_thread.error.connect(self._on_videos_error)  # type: ignore[arg-type]
        self.loader_thread.start()

    def _videos_fetched(self, videos: List[dict]) -> None:
        QApplication.restoreOverrideCursor()
        self.videos = videos  # already sliced
        self.video_list.clear()
        for i, v in enumerate(videos, 1):
            self.video_list.addItem(QListWidgetItem(f"{i}. {v['title']}"))

        self.load_btn.setEnabled(True)
        self.load_btn.setText("Load playlist videos")
        self.log_window.append(f"Loaded {len(videos)} videos.\n")

    def _on_videos_error(self, msg: str) -> None:  # noqa: D401
        QApplication.restoreOverrideCursor()
        self.load_btn.setEnabled(True)
        self.load_btn.setText("Load playlist videos")
        self._show_error("Error", msg)

    # ───────────────────────────── download ────────────────────────────────
    def _download_selected(self) -> None:  # noqa: D401
        if not getattr(self, "videos", None):
            self._show_error("No playlist", "Load a playlist first.")
            return

        if self.output_path is None:
            self._show_error("No folder", "Please choose an output folder first.")
            return

        selected_rows = [i.row() for i in self.video_list.selectedIndexes()]
        if not selected_rows:
            self.log_window.append("Select at least one video.")
            return

        # fire worker
        self.progress.setValue(0)
        self.progress.setFormat("0%")
        self.download_btn.setEnabled(False)
        self.log_window.append("Starting downloads…\n")

        self.dl_thread = PlaylistDownloadThread(
            self.videos,
            selected_rows,
            self.output_path,
            fmt_code="bestvideo",  # download_and_merge adds +bestaudio
        )
        self.dl_thread.log.connect(self.log_window.append)  # type: ignore[arg-type]
        self.dl_thread.progress.connect(self._update_progress)  # type: ignore[arg-type]
        self.dl_thread.finished.connect(self._download_finished)  # type: ignore[arg-type]
        self.dl_thread.start()

    def _update_progress(self, pct: int) -> None:
        self.progress.setValue(pct)
        self.progress.setFormat(f"{pct}%")

    def _download_finished(self) -> None:  # noqa: D401
        self.progress.setValue(100)
        self.progress.setFormat("100%")
        self.download_btn.setEnabled(True)
        self.log_window.append("All downloads complete!\n")

    # ──────────────────────────── misc helpers ─────────────────────────────
    def _open_output_folder(self) -> None:  # noqa: D401
        if not self.output_path:
            self._show_error("No folder", "Select a folder first.")
            return
        path = self.output_path
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[arg-type]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _show_error(self, title: str, msg: str) -> None:
        QMessageBox.critical(self, title, msg)

    # back navigation supplied by main app ----------------------------------
    def set_back_callback(self, cb):
        self._back_callback = cb

    def _on_back(self):
        if self._back_callback:
            self.hide()
            self._back_callback()

    # Theme switching --------------------------------------------------------
    def apply_theme(self, theme_path):
        try:
            with open(theme_path, "r") as f:
                style = f.read()
                self.setStyleSheet(style)
        except Exception as e:
            self._show_error("Error loading theme", str(e))

    def switch_theme(self):
        if self.current_theme == "dark":
            self.apply_theme(resource_path("assets/qss/light.qss"))
            self.current_theme = "light"
        else:
            self.apply_theme(resource_path("assets/qss/dark.qss"))
            self.current_theme = "dark"
