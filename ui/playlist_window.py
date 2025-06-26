"""Playlist window for YouVideo‑Downloader
------------------------------------------------
A PySide6 widget that can:
• Load a YouTube playlist.
• Optionally limit the loaded videos via a human‑friendly range box.
    – Empty  → all items
    – "N-M" → items N through M (inclusive)
    – "K"   → first K items
• Show the items in a selectable list.
• Download selected videos in the BestVideo+BestAudio combo and merge to MP4
  using `download_and_merge()` from downloader.yt_downloader.

Dependencies (already present in your project):
    utils.pathfinder.resource_path
    downloader.yt_downloader.get_playlist_videos
    downloader.yt_downloader.download_and_merge

Save this as ``playlist_window.py`` (or any module name) and import it into
``main.py``.
"""

from __future__ import annotations

import os
import sys
import subprocess
from typing import List

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
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
    QVBoxLayout,
    QWidget,
)

from utils.pathfinder import resource_path
from downloader.yt_downloader import get_playlist_videos, download_and_merge


# ──────────────────────────── paths & constants ─────────────────────────────
icon_path = resource_path("assets/icons/appicon.png")
qss_path = resource_path("assets/qss/dark.qss")


# ──────────────────────────── helpers ───────────────────────────────────────

def slice_by_range(txt: str, length: int) -> List[int]:
    """Return indices (0‑based) selected by a user‑typed range string.

    The string *txt* may be one of:
        ""       → full list         (1‑length)
        "K"      → first *K* items   (1‑K)
        "N-M"    → items N..M        (order ignored)
        "-M"     → items 1..M
        "N-"     → items N..end

    Any value outside 1..length is clipped.  If *start* ends up > *end*, they
    are swapped.
    """
    txt = txt.replace(" ", "")
    if not txt:
        return list(range(length))

    if "-" in txt:
        left, right = txt.split("-", 1)
        start = int(left) if left else 1
        end = int(right) if right else length
    else:
        start, end = 1, int(txt)

    start = max(1, start)
    end = min(length, end)
    if start > end:
        start, end = end, start

    return list(range(start - 1, end))


# ──────────────────────────── worker threads ────────────────────────────────
class PlaylistLoaderThread(QThread):
    """Fetch the list of videos from a playlist URL (yt‑dlp runs elsewhere)."""

    loaded = Signal(list)
    error = Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self) -> None:  # noqa: D401
        try:
            videos = get_playlist_videos(self.url)
            self.loaded.emit(videos)
        except Exception as exc:  # pragma: no cover – pass all errors up
            self.error.emit(str(exc))


class PlaylistDownloadThread(QThread):
    """Download & merge the selected playlist items in the background."""

    progress = Signal(int)  # overall percent 0‑100
    log = Signal(str)       # text for GUI log
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

    # ―― progress hook passed to yt‑dl / yt‑dlp ――――――――――――――――――――――――――
    def _hook(self, d: dict) -> None:
        if d.get("status") == "downloading":
            pct = d.get("_percent_str", "0%" ).strip()
            self.log.emit(f"    ↳ {pct}")

    # ―― thread main ―――――――――――――――――――――――――――――――――――――――――――――――――――
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
        self._setup_ui()
        self._apply_stylesheet()

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

        self.output_label = QLabel("Output folder: Not selected")
        browse_btn = QPushButton("Select output folder")
        browse_btn.clicked.connect(self._browse_folder)  # type: ignore[arg-type]

        # — footer buttons
        hlayout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self._on_back)  # type: ignore[arg-type]

        self.download_btn = QPushButton("Download selected")
        self.download_btn.clicked.connect(self._download_selected)  # type: ignore[arg-type]

        open_folder_btn = QPushButton("Open output folder")
        open_folder_btn.clicked.connect(self._open_output_folder)  # type: ignore[arg-type]

        hlayout.addWidget(back_btn)
        hlayout.addWidget(self.download_btn)
        hlayout.addWidget(open_folder_btn)

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

        self.output_path = os.getcwd()

    def _apply_stylesheet(self) -> None:
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as exc:
            print(f"[PlaylistWindow] Could not load stylesheet: {exc}")

    # ―― actions ——————————————————————————————————————————————
    # 1) choose folder --------------------------------------------------------
    def _browse_folder(self) -> None:  # noqa: D401
        folder = QFileDialog.getExistingDirectory(self, "Select output folder")
        if folder:
            self.output_path = folder
            self.output_label.setText(f"Output folder: {folder}")

    # 2) load playlist --------------------------------------------------------
    def _load_playlist_videos(self) -> None:  # noqa: D401
        url = self.url_input.text().strip()
        if not url:
            self._show_error("Missing URL", "Please enter a playlist URL")
            return

        self.video_list.clear()
        self.load_btn.setEnabled(False)
        self.load_btn.setText("Loading…")
        self.log_window.append("Loading playlist videos…")

        self.loader_thread = PlaylistLoaderThread(url)
        self.loader_thread.loaded.connect(self._videos_fetched)  # type: ignore[arg-type]
        self.loader_thread.error.connect(self._on_videos_error)  # type: ignore[arg-type]
        self.loader_thread.start()

    def _videos_fetched(self, all_videos: List[dict]) -> None:
        self._all_videos = all_videos  # keep whole list in case needed
        wanted = slice_by_range(self.range_input.text().strip(), len(all_videos))
        self.videos = [all_videos[i] for i in wanted]

        self.video_list.clear()
        for i, v in enumerate(self.videos, 1):
            self.video_list.addItem(QListWidgetItem(f"{i}. {v['title']}"))

        self.load_btn.setEnabled(True)
        self.load_btn.setText("Load playlist videos")
        self.log_window.append(f"Loaded {len(self.videos)} videos.\n")

    def _on_videos_error(self, msg: str) -> None:  # noqa: D401
        self.load_btn.setEnabled(True)
        self.load_btn.setText("Load playlist videos")
        self._show_error("Error", msg)

    # 3) download selection ---------------------------------------------------
    def _download_selected(self) -> None:  # noqa: D401
        if not getattr(self, "videos", None):
            self._show_error("No playlist", "Load a playlist first.")
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

    # 4) misc ---------------------------------------------------------------
    def _open_output_folder(self) -> None:  # noqa: D401
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
