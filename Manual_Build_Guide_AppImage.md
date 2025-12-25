# YouVideo Downloader (AppImage)

**YouVideo Downloader** is a modern GUI video downloader for Linux, built with PyQt6 and `yt-dlp`.  
It allows users to download videos from YouTube and other supported platforms, select video formats, choose output folders, and track progress with a clean, modern interface.

---

## Table of Contents

1. [Features](#features)
2. [System Requirements](#system-requirements)
3. [Downloading the AppImage](#downloading-the-appimage)
4. [Making the AppImage Executable](#making-the-appimage-executable)
5. [Running the AppImage](#running-the-appimage)
6. [Desktop Integration](#desktop-integration)
7. [Updating](#updating)
8. [Development](#development)
9. [AppImage Build Instructions](#appimage-build-instructions)
10. [AppStream Metadata](#appstream-metadata)
11. [License](#license)
12. [Repository](#repository)

---

## Features

- Download individual videos or playlists from YouTube and other platforms
- Select video quality and format (MP4, WEBM, etc.)
- Choose custom output folder
- Track download progress in a clean PyQt6 GUI
- Standalone AppImage — no installation required
- Fully compatible with GNOME, KDE, Linux Mint software centers

---

## System Requirements

- **OS:** Linux x86_64
- **Dependencies:** `libc6`, `zlib1g`, `ffmpeg`
- **Disk space:** 100 MB (binary + temporary files)

---

## Downloading the AppImage

Get the latest release from GitHub:

```bash
wget https://github.com/Sarwarhridoy4/youvideo-downloader/releases/download/v2.0.0/YouVideoDownloader-x86_64.AppImage
```

---

## Making the AppImage Executable

Before running, mark it as executable:

```bash
chmod +x YouVideoDownloader-x86_64.AppImage
```

---

## Running the AppImage

Launch the application directly:

```bash
./YouVideoDownloader-x86_64.AppImage
```

Optional: move to `~/Applications` or `/opt` for easier access.

---

## Desktop Integration

- AppImage includes a **desktop entry** and **icon**, so it can integrate with:

  - GNOME Software
  - KDE Discover
  - Linux Mint menu

- AppStream metadata ensures **screenshot, description, and license** appear correctly in software centers.

---

## Updating

To update:

1. Download the new AppImage release
2. Replace the old file:

```bash
mv YouVideoDownloader-x86_64.AppImage ~/Applications/YouVideoDownloader-x86_64.AppImage
chmod +x ~/Applications/YouVideoDownloader-x86_64.AppImage
```

- No uninstall needed — AppImage is self-contained.

---

## Development

1. Clone the repository:

```bash
git clone https://github.com/Sarwarhridoy4/youvideo-downloader.git
cd youvideo-downloader
```

2. Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Run locally:

```bash
python3 main.py
```

4. Build standalone binary with PyInstaller:

```bash
pyinstaller --onefile --windowed main.py --name youvideo-downloader
```

---

## AppImage Build Instructions

**Step-by-step professional build:**

1. Create AppDir structure:

```bash
mkdir -p YouVideoDownloader.AppDir/usr/bin
mkdir -p YouVideoDownloader.AppDir/usr/share/applications
mkdir -p YouVideoDownloader.AppDir/usr/share/icons/hicolor/256x256/apps
mkdir -p YouVideoDownloader.AppDir/usr/share/metainfo
mkdir -p YouVideoDownloader.AppDir/usr/share/doc/youvideo-downloader
```

2. Copy files:

```bash
cp dist/youvideo-downloader YouVideoDownloader.AppDir/usr/bin/
chmod +x YouVideoDownloader.AppDir/usr/bin/youvideo-downloader

cp assets/youvideo-downloader.desktop YouVideoDownloader.AppDir/usr/share/applications/
cp assets/icon.png YouVideoDownloader.AppDir/usr/share/icons/hicolor/256x256/apps/youvideo-downloader.png
cp usr/share/metainfo/youvideo-downloader.metainfo.xml YouVideoDownloader.AppDir/usr/share/metainfo/
cp README.md YouVideoDownloader.AppDir/usr/share/doc/youvideo-downloader/
```

3. Add AppRun launcher:

```bash
nano YouVideoDownloader.AppDir/AppRun
```

```bash
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="$HERE/usr/bin:$PATH"
exec "$HERE/usr/bin/youvideo-downloader" "$@"
```

```bash
chmod +x YouVideoDownloader.AppDir/AppRun
```

4. Build AppImage:

```bash
appimagetool YouVideoDownloader.AppDir
```

- Result: `YouVideoDownloader-x86_64.AppImage`

---

## AppStream Metadata

- Ensures software centers display **description, screenshot, and license**
- Screenshot URL must be **raw and padding-free**
- Metadata file: `usr/share/metainfo/youvideo-downloader.metainfo.xml`

---

## License

- **MIT License**
- Full text included in `usr/share/doc/youvideo-downloader/`

---

## Repository

- GitHub: [https://github.com/Sarwarhridoy4/youvideo-downloader](https://github.com/Sarwarhridoy4/youvideo-downloader)
- Issues & bug reports: [https://github.com/Sarwarhridoy4/youvideo-downloader/issues](https://github.com/Sarwarhridoy4/youvideo-downloader/issues)

---

## Screenshots

![Main Window](https://raw.githubusercontent.com/Sarwarhridoy4/youvideo-downloader/production/assets/screenshot/welcome.png)

---

## Summary

This README includes:

- Installation & usage instructions for AppImage
- Desktop integration and AppStream details
- Development and build guide
- Step-by-step instructions to create a **professional AppImage** ready for distribution

```

---

This README is **fully professional**, mirrors your `.deb` README, and now serves **end users, developers, and maintainers** for AppImage releases.

It can also be **included in the AppImage itself** under `/usr/share/doc/youvideo-downloader/README.md`.

---

If you want, I can also create a **single “Universal Build & Release Workflow” README** covering both `.deb` and AppImage in one place, including GitHub Actions automation.

Do you want me to do that?
```
