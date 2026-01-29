# Manual Build Guide - Debian Package

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
It is recommended to use the provided spec file for building the PyInstaller binary in `onedir` mode:
```bash
pyinstaller --clean --noconfirm youvideo-downloader.spec
```
This will create the application bundle in `dist/YouVideoDownloader/`.'

---

## Building a Debian Package

> **Recommended Professional Build:** For a fully automated and professional Debian package build that adheres to modern standards (including icon generation and AppStream metadata), it is highly recommended to use the `build.sh` script located in the project root.
>
> ```bash
> ./build.sh deb
> ```
>
> The manual steps below are provided for educational purposes, understanding the packaging process, or for highly customized build scenarios.

**Step-by-step guide for creating a professional `.deb` package:**

1. Create the package folder structure:

```bash
mkdir -p youvideo-downloader_X.Y.Z_amd64/{DEBIAN,usr/{bin,share/{applications,pixmaps,doc/youvideo-downloader,man/man1,metainfo}}}
# Replace X.Y.Z with your actual version, e.g., 2.1.0
```

2. Copy the PyInstaller application directory and create a launcher:

First, ensure you have built the application using PyInstaller with the spec file:
```bash
pyinstaller --clean --noconfirm youvideo-downloader.spec
```
Then copy the contents of the generated `dist/YouVideoDownloader` directory into the package structure:
```bash
cp -r dist/YouVideoDownloader/* youvideo-downloader_X.Y.Z_amd64/usr/share/youvideo-downloader/
chmod 755 youvideo-downloader_X.Y.Z_amd64/usr/share/youvideo-downloader/youvideo-downloader
# Replace X.Y.Z with your actual version
```
Create a launcher script in `/usr/bin` that points to the application:
```bash
cat << 'EOF' > youvideo-downloader_X.Y.Z_amd64/usr/bin/youvideo-downloader
#!/bin/bash
APP_DIR="/usr/share/youvideo-downloader"
cd "$APP_DIR"
exec "./youvideo-downloader" "$@"
EOF
chmod 755 youvideo-downloader_X.Y.Z_amd64/usr/bin/youvideo-downloader
# Replace X.Y.Z with your actual version
```

3. Add desktop entry:
Create the desktop entry file `youvideo-downloader_X.Y.Z_amd64/usr/share/applications/com.sarwarhossain.youvideo-downloader.desktop` with the following content:
```text
[Desktop Entry]
Version=1.1
Type=Application
Name=YouVideo Downloader
GenericName=Video Downloader
Comment=Fast and powerful video downloader with modern PySide6 interface
Exec=youvideo-downloader %U
Icon=com.sarwarhossain.youvideo-downloader
Terminal=false
Categories=AudioVideo;Video;Network;Qt;
Keywords=youtube;video;download;yt-dlp;
MimeType=x-scheme-handler/http;x-scheme-handler/https;
StartupNotify=true
StartupWMClass=youvideo-downloader
```

4. Generate and install icons:

Professional icon generation involves creating multiple sizes and formats. It is recommended to use the `create_icon.py` script for this:
```bash
python3 create_icon.py assets/icons/appicon.png
```
After generating the icons in `assets/icons/`, copy them to the appropriate hicolor directories and `pixmaps`:
```bash
# Replace X.Y.Z with your actual version
# Copy various sizes to hicolor
for size in 16 22 24 32 48 64 128 256 512; do
    if [[ -f assets/icons/icon_\${size}.png ]]; then
        mkdir -p youvideo-downloader_X.Y.Z_amd64/usr/share/icons/hicolor/\${size}x\${size}/apps
        cp assets/icons/icon_\${size}.png youvideo-downloader_X.Y.Z_amd64/usr/share/icons/hicolor/\${size}x\${size}/apps/com.sarwarhossain.youvideo-downloader.png
    fi
done

# Copy main icon to pixmaps
cp assets/icons/icon_256.png youvideo-downloader_X.Y.Z_amd64/usr/share/pixmaps/com.sarwarhossain.youvideo-downloader.png
```

5. Add documentation:
Create the `copyright` file:
```bash
cat << EOF > youvideo-downloader_X.Y.Z_amd64/usr/share/doc/youvideo-downloader/copyright
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: YouVideoDownloader
Upstream-Contact: Sarwar Hossain <sarwarhridoy4@gmail.com>
Source: https://github.com/Sarwarhridoy4/youvideo-downloader

Files: *
Copyright: $(date +%Y) Sarwar Hossain
License: MIT
EOF
# Replace X.Y.Z with your actual version
```
Create the `changelog.Debian` file:
```bash
cat << EOF > youvideo-downloader_X.Y.Z_amd64/usr/share/doc/youvideo-downloader/changelog.Debian
youvideo-downloader (X.Y.Z) unstable; urgency=medium

  * New release X.Y.Z
  * Integrated icon generation system
  * Professional packaging for all platforms

 -- Sarwar Hossain <sarwarhridoy4@gmail.com>  $(date -R)
EOF
gzip -9 youvideo-downloader_X.Y.Z_amd64/usr/share/doc/youvideo-downloader/changelog.Debian
# Replace X.Y.Z with your actual version in the file content and filename
```

6. Create `DEBIAN/control`:
Create the `DEBIAN/control` file (`youvideo-downloader_X.Y.Z_amd64/DEBIAN/control`) with the following content:
```text
Package: youvideo-downloader
Version: X.Y.Z
Section: video
Priority: optional
Architecture: amd64
Installed-Size: (calculate manually or leave blank)
Depends: libc6 (>= 2.27), libglib2.0-0, libxcb1, python3 (>= 3.8)
Recommends: ffmpeg, yt-dlp
Maintainer: Sarwar Hossain <sarwarhridoy4@gmail.com>
Homepage: https://github.com/Sarwarhridoy4/youvideo-downloader
Description: Fast and powerful video downloader with modern PySide6 interface
 Modern video downloader with PySide6 interface supporting YouTube
 and other platforms. Features include high-quality downloads,
 playlist support, format conversion, and user-friendly interface.
```
# Replace X.Y.Z with your actual version

7. Add maintainer scripts:
Create the `postinst` script (`youvideo-downloader_X.Y.Z_amd64/DEBIAN/postinst`):
```bash
#!/bin/bash
set -e
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database -q /usr/share/applications 2>/dev/null || true
```
And make it executable:
```bash
chmod 755 youvideo-downloader_X.Y.Z_amd64/DEBIAN/postinst
# Replace X.Y.Z with your actual version
```

Create the `prerm` script (`youvideo-downloader_X.Y.Z_amd64/DEBIAN/prerm`):
```bash
#!/bin/bash
set -e
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database -q /usr/share/applications 2>/dev/null || true
```
And make it executable:
```bash
chmod 755 youvideo-downloader_X.Y.Z_amd64/DEBIAN/prerm
# Replace X.Y.Z with your actual version
```

8. Add AppStream metadata:
Create the AppStream metainfo file (`youvideo-downloader_X.Y.Z_amd64/usr/share/metainfo/com.sarwarhossain.youvideo-downloader.metainfo.xml`) with the following content:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>com.sarwarhossain.youvideo-downloader</id>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <name>YouVideo Downloader</name>
  <summary>Fast and powerful video downloader with modern PySide6 interface</summary>
  <description>
    <p>
      YouVideo Downloader is a modern desktop application that allows you to download videos from various online platforms, including YouTube and Facebook. Built with PySide6, it offers a sleek user interface and robust features for a seamless downloading experience.
    </p>
    <p>Key Features:</p>
    <ul>
      <li>Download videos from YouTube, Facebook, and more.</li>
      <li>Automatic detection and optional installation of ffmpeg.</li>
      <li>Choose from multiple available video/audio formats.</li>
      <li>Playlist downloading with range selection.</li>
      <li>MP3 download option.</li>
      <li>Customizable output folder.</li>
      <li>Real-time progress bar.</li>
      <li>Dark and Light themes.</li>
    </ul>
  </description>
  <launchable type="desktop-id">com.sarwarhossain.youvideo-downloader.desktop</launchable>
  <screenshots>
    <screenshot type="default">
      <image>https://raw.githubusercontent.com/Sarwarhridoy4/youvideo-downloader/main/assets/screenshot/welcome.png</image>
    </screenshot>
    <screenshot>
      <image>https://raw.githubusercontent.com/Sarwarhridoy4/youvideo-downloader/main/assets/screenshot/playlist.png</image>
    </screenshot>
    <screenshot>
      <image>https://raw.githubusercontent.com/Sarwarhridoy4/youvideo-downloader/main/assets/screenshot/single.png</image>
    </screenshot>
  </screenshots>
  <url type="homepage">https://github.com/Sarwarhridoy4/youvideo-downloader</url>
  <url type="bugtracker">https://github.com/Sarwarhridoy4/youvideo-downloader/issues</url>
  <url type="help">https://github.com/Sarwarhridoy4/youvideo-downloader/wiki</url>
  <url type="donation">https://github.com/Sarwarhridoy4/youvideo-downloader</url>
  <developer_name>Sarwar Hossain</developer_name>
  <update_contact>sarwarhridoy4@gmail.com</update_contact>
  <project_group>Multimedia</project_group>
  <keywords>
    <keyword>youtube</keyword>
    <keyword>video</keyword>
    <keyword>downloader</keyword>
    <keyword>pyside6</keyword>
    <keyword>yt-dlp</keyword>
    <keyword>ffmpeg</keyword>
  </keywords>
  <releases>
    <release version="X.Y.Z" date="$(date +%Y-%m-%d)">
      <description>
        <p>New release X.Y.Z with integrated icon generation and professional packaging for all platforms.</p>
        <ul>
          <li>Integrated icon generation system.</li>
          <li>Improved packaging for Debian and AppImage.</li>
          <li>General bug fixes and performance improvements.</li>
        </ul>
      </description>
    </release>
  </releases>
</component>
```
# Replace X.Y.Z with your actual version

9. Build the package:

```bash
dpkg-deb --build youvideo-downloader_X.Y.Z_amd64
# The above command will produce: youvideo-downloader_X.Y.Z_amd64.deb
# If you want to rename it to include a Debian revision (e.g., 2.1.0-1), use:
# mv youvideo-downloader_X.Y.Z_amd64.deb youvideo-downloader_X.Y.Z-1_amd64.deb
# Replace X.Y.Z with your actual version
```

10. Test installation:

```bash
sudo dpkg -i youvideo-downloader_X.Y.Z_amd64.deb # Or youvideo-downloader_X.Y.Z-1_amd64.deb if renamed
sudo apt --fix-broken install # Fix any missing dependencies
sudo apt purge youvideo-downloader
# Replace X.Y.Z with your actual version
```

## AppStream Metadata

AppStream metadata (`.metainfo.xml`) is crucial for modern Linux software centers (like GNOME Software or KDE Discover) to properly display application information, including screenshots, descriptions, and licensing.

- The `build.sh` script automates the generation of this file based on project configuration.
- The screenshot URLs used in the metadata should be raw and padding-free for correct display.
- The metadata is installed to `/usr/share/metainfo/com.sarwarhossain.youvideo-downloader.metainfo.xml`.

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
