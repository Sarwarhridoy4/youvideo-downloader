# README.md — YouVideo Downloader (Professional)

# YouVideo Downloader

**YouVideo Downloader** is a modern, graphical video downloader for Linux built with PyQt6 and `yt-dlp`.  
It allows users to download videos from YouTube and many other platforms, select video formats, choose output folders, and track download progress with a clean interface inspired by YouTube’s dark and light themes.

---

## Table of Contents

1. [Features](#features)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Desktop Integration](#desktop-integration)
6. [Updating](#updating)
7. [Development](#development)
8. [Building a Debian Package](#building-a-debian-package)
9. [AppStream Metadata](#appstream-metadata)
10. [License](#license)
11. [Repository](#repository)

---

## Features

- Download videos and playlists from YouTube and other supported platforms
- Select video quality and format (MP4, WEBM, etc.)
- Choose custom output folder for downloads
- Modern GUI interface built with PyQt6
- Tracks download progress with notifications
- Fully packaged as a standalone `.deb` for Debian/Ubuntu/Linux Mint

---

## System Requirements

- **OS:** Debian, Ubuntu, Linux Mint (64-bit)
- **Dependencies:** `libc6`, `zlib1g`, `ffmpeg`
- **Disk space:** 100 MB (includes app and temporary download files)

---

## Installation

### Using the `.deb` package

1. Download the `.deb` package:

```bash
wget https://github.com/Sarwarhridoy4/youvideo-downloader/releases/download/v2.0.0/youvideo-downloader_2.0.0-1_amd64.deb
```

2. Install the package:

```bash
sudo dpkg -i youvideo-downloader_2.0.0-1_amd64.deb
sudo apt -f install   # fixes missing dependencies if any
```

3. Launch the app:

```bash
youvideo-downloader
```

4. To uninstall:

```bash
sudo apt purge youvideo-downloader
```

---

## Usage

1. Open the application from your menu or terminal:

```bash
youvideo-downloader
```

2. Enter a video or playlist URL
3. Select output format and folder
4. Click **Download**
5. Track progress in the GUI

---

## Desktop Integration

- A `.desktop` file is included, so the app appears in **GNOME, KDE, and Linux Mint software menus**.
- App icon installed under `/usr/share/icons/hicolor/256x256/apps/youvideo-downloader.png`
- AppStream metadata ensures proper screenshot and description in software centers

---

## Updating

- Future releases can be installed over the previous version:

```bash
sudo dpkg -i youvideo-downloader_<new-version>_amd64.deb
```

- Old versions are automatically replaced, and desktop entries remain intact.

---

## Development

If you want to build or modify the app:

1. Clone the repository:

```bash
git clone https://github.com/Sarwarhridoy4/youvideo-downloader.git
cd youvideo-downloader
```

2. Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Run the app locally:

```bash
python3 main.py
```

4. Build the PyInstaller binary:

```bash
pyinstaller --onefile --windowed main.py --name youvideo-downloader
```

---

## Building a Debian Package

**Step-by-step guide for creating a professional `.deb` package:**

1. Create the package folder structure:

```bash
mkdir -p youvideo-downloader_2.0.0_amd64/{DEBIAN,usr/bin,usr/share/applications,usr/share/icons/hicolor/256x256/apps,usr/share/doc/youvideo-downloader,usr/share/metainfo}
```

2. Copy the PyInstaller binary:

```bash
cp dist/youvideo-downloader usr/bin/youvideo-downloader
chmod 755 usr/bin/youvideo-downloader
```

3. Add desktop entry:

```text
[Desktop Entry]
Name=YouVideo Downloader
Comment=Download videos from YouTube and other platforms
Exec=youvideo-downloader
Icon=youvideo-downloader
Type=Application
Categories=Utility;Network;
Terminal=false
StartupWMClass=youvideo-downloader
```

4. Add icon:

```bash
cp assets/icon.png usr/share/icons/hicolor/256x256/apps/youvideo-downloader.png
```

5. Add documentation:

```bash
cp README.md usr/share/doc/youvideo-downloader/
gzip -9 usr/share/doc/youvideo-downloader/README.md
```

6. Create `DEBIAN/control`:

```text
Package: youvideo-downloader
Version: 2.0.0-1
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Sarwar Hossain <sarwarhridoy4@gmail.com>
Homepage: https://github.com/Sarwarhridoy4/youvideo-downloader
Depends: libc6, zlib1g, ffmpeg
Conflicts: youvideodownloader
Replaces: youvideodownloader
Description: YouVideo Downloader is a simple and efficient YouTube video downloader built with PyQt6 and yt-dlp.
```

7. Add maintainer scripts:

- `postinst`:

```sh
#!/bin/sh
set -e
command -v update-desktop-database >/dev/null && update-desktop-database -q || true
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q /usr/share/icons/hicolor || true
exit 0
```

- `prerm`:

```sh
#!/bin/sh
set -e
command -v update-desktop-database >/dev/null && update-desktop-database -q || true
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q /usr/share/icons/hicolor || true
exit 0
```

8. Add AppStream metadata:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop">
  <id>youvideo-downloader.desktop</id>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>MIT</project_license>
  <name>YouVideo Downloader</name>
  <summary>Modern GUI video downloader</summary>
  <description>
    <p>YouVideo Downloader is a modern graphical application for downloading videos from YouTube and many other platforms using yt-dlp.</p>
  </description>
  <launchable type="desktop-id">youvideo-downloader.desktop</launchable>
  <url type="homepage">https://github.com/Sarwarhridoy4/youvideo-downloader</url>
  <screenshots>
    <screenshot type="default">
      <image>https://raw.githubusercontent.com/Sarwarhridoy4/youvideo-downloader/production/assets/screenshot/welcome.png</image>
    </screenshot>
  </screenshots>
  <releases>
    <release version="2.0.0" date="2025-12-25">
      <description><p>Initial professional Debian release.</p></description>
    </release>
  </releases>
</component>
```

9. Build the package:

```bash
dpkg-deb --build youvideo-downloader_2.0.0_amd64
mv youvideo-downloader_2.0.0_amd64.deb youvideo-downloader_2.0.0-1_amd64.deb
```

10. Test installation:

```bash
sudo dpkg -i youvideo-downloader_2.0.0-1_amd64.deb
sudo apt purge youvideo-downloader
```

---

## AppStream Metadata

- Ensures software centers display the **screenshot, description, and license** correctly.
- Screenshot URL must be **raw and padding-free**.

---

## License

- **MIT License**
- Full text included in `/usr/share/doc/youvideo-downloader/copyright.gz`

---

## Repository

- GitHub: [https://github.com/Sarwarhridoy4/youvideo-downloader](https://github.com/Sarwarhridoy4/youvideo-downloader)
- Bug reports: [https://github.com/Sarwarhridoy4/youvideo-downloader/issues](https://github.com/Sarwarhridoy4/youvideo-downloader/issues)

---

## Screenshots

![Main Window](https://raw.githubusercontent.com/Sarwarhridoy4/youvideo-downloader/production/assets/screenshot/welcome.png)

---

## Summary

This README provides:

- Installation instructions
- Usage guide
- Desktop integration and AppStream details
- Full instructions for building a professional `.deb` package from PyInstaller binary

Your package is **fully distribution-ready**, Debian/Ubuntu/Linux Mint compatible, and ready for APT repository or GitHub releases.
