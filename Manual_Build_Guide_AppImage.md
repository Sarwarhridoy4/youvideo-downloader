# Manual Build Guide - AppImage

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
It is recommended to use the provided spec file for building the PyInstaller binary in `onedir` mode:
```bash
pyinstaller --clean --noconfirm youvideo-downloader.spec
```
This will create the application bundle in `dist/YouVideoDownloader/`.'

---

## AppImage Build Instructions

> **Recommended Professional Build:** For a fully automated and professional AppImage build that adheres to modern standards (including icon generation and AppStream metadata), it is highly recommended to use the `build.sh` script located in the project root.
>
> ```bash
> ./build.sh appimage
> ```
>
> The manual steps below are provided for educational purposes, understanding the packaging process, or for highly customized build scenarios.

**Step-by-step professional build:**

1. Create AppDir structure:

```bash
mkdir -p YouVideoDownloader.AppDir/usr/{bin,share/{applications,metainfo}}
# Create hicolor directories for icons
for size in 16x16 22x22 24x24 32x32 48x48 64x64 128x128 256x256 512x512; do
    mkdir -p YouVideoDownloader.AppDir/usr/share/icons/hicolor/\${size}/apps
done
```

2. Copy files:

First, ensure you have built the application using PyInstaller with the spec file:
```bash
pyinstaller --clean --noconfirm youvideo-downloader.spec
```
Copy the contents of the generated `dist/YouVideoDownloader` directory into the AppDir:
```bash
cp -r dist/YouVideoDownloader/* YouVideoDownloader.AppDir/usr/bin/
chmod +x YouVideoDownloader.AppDir/usr/bin/youvideo-downloader
```

Create the desktop entry file `YouVideoDownloader.AppDir/YouVideoDownloader.desktop` and copy it to `usr/share/applications/`:
```text
[Desktop Entry]
Type=Application
Name=YouVideo Downloader
Comment=Fast and powerful video downloader with modern PySide6 interface
Exec=youvideo-downloader
Icon=com.sarwarhossain.youvideo-downloader
Terminal=false
Categories=AudioVideo;Video;Network;Qt;
```
Copy it:
```bash
cat << EOF > YouVideoDownloader.AppDir/YouVideoDownloader.desktop
[Desktop Entry]
Type=Application
Name=YouVideo Downloader
Comment=Fast and powerful video downloader with modern PySide6 interface
Exec=youvideo-downloader
Icon=com.sarwarhossain.youvideo-downloader
Terminal=false
Categories=AudioVideo;Video;Network;Qt;
EOF
cp YouVideoDownloader.AppDir/YouVideoDownloader.desktop YouVideoDownloader.AppDir/usr/share/applications/
```

Generate and install icons:
Professional icon generation involves creating multiple sizes and formats. It is recommended to use the `create_icon.py` script for this:
```bash
python3 create_icon.py assets/icons/appicon.png
```
After generating the icons in `assets/icons/`, copy them to the appropriate hicolor directories and to the AppDir root:
```bash
# Copy main icon to AppDir root (e.g., 256x256 or 512x512)
cp assets/icons/icon_256.png YouVideoDownloader.AppDir/com.sarwarhossain.youvideo-downloader.png

# Copy various sizes to hicolor
for size in 16 22 24 32 48 64 128 256 512; do
    if [[ -f assets/icons/icon_\${size}.png ]]; then
        cp assets/icons/icon_\${size}.png YouVideoDownloader.AppDir/usr/share/icons/hicolor/\${size}x\${size}/apps/com.sarwarhossain.youvideo-downloader.png
    fi
done
```

Generate AppStream metainfo:
Create the AppStream metainfo file `YouVideoDownloader.AppDir/usr/share/metainfo/com.sarwarhossain.youvideo-downloader.metainfo.xml` with the following content:
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

3. Add AppRun launcher:
Create the `AppRun` script (`YouVideoDownloader.AppDir/AppRun`) with the following content:
```bash
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
cd "${HERE}/usr/bin"
exec "./youvideo-downloader" "$@"
```
And make it executable:
```bash
chmod +x YouVideoDownloader.AppDir/AppRun
```'

4. Build AppImage:
It is recommended to use `linuxdeploy` for building the AppImage, as it handles a lot of the complexities. First, download `linuxdeploy`:
```bash
wget -q --show-progress https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage -O ./linuxdeploy-x86_64.AppImage
chmod +x ./linuxdeploy-x86_64.AppImage
```
Then build the AppImage:
```bash
./linuxdeploy-x86_64.AppImage \
    --appdir=YouVideoDownloader.AppDir \
    --desktop-file=YouVideoDownloader.AppDir/YouVideoDownloader.desktop \
    --icon-file=YouVideoDownloader.AppDir/com.sarwarhossain.youvideo-downloader.png \
    --output appimage
```
This will generate an AppImage file (e.g., `YouVideoDownloader-x86_64.AppImage`).
Finally, rename the generated AppImage to include the version:
```bash
# Assuming the generated file is named YouVideoDownloader-x86_64.AppImage
mv YouVideoDownloader-x86_64.AppImage YouVideoDownloader-X.Y.Z-x86_64.AppImage
# Replace X.Y.Z with your actual version
```

---

## AppStream Metadata

AppStream metadata (`.metainfo.xml`) is crucial for modern Linux software centers (like GNOME Software or KDE Discover) to properly display application information, including screenshots, descriptions, and licensing.

- The `build.sh` script automates the generation of this file based on project configuration.
- The screenshot URLs used in the metadata should be raw and padding-free for correct display.
- The metadata is installed to `YouVideoDownloader.AppDir/usr/share/metainfo/com.sarwarhossain.youvideo-downloader.metainfo.xml`.'

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


