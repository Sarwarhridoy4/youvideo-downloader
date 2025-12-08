# YouVideo Downloader - Build Guide

Complete documentation for building DEB and AppImage packages for YouVideo Downloader.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start - Dependency Installation](#quick-start---dependency-installation)
4. [Building DEB Package](#building-deb-package)
5. [Building AppImage](#building-appimage)
6. [Troubleshooting](#troubleshooting)
7. [Testing Your Build](#testing-your-build)
8. [Complete Dependency List](#complete-dependency-list)

---

## Overview

This guide covers building two types of Linux packages:

- **DEB Package**: For Debian-based distributions (Ubuntu, Linux Mint, etc.)
- **AppImage**: Universal format that works on most Linux distributions

Both scripts are fully automated and will:
- ✅ Check for required tools
- ✅ Install missing dependencies
- ✅ Build the executable with PyInstaller
- ✅ Create proper package structure
- ✅ Configure desktop integration
- ✅ Handle icon installation correctly
- ✅ Make the final package executable

---

## Quick Start - Dependency Installation

### **Easiest Method: Automated Installer** (Recommended)

We provide a comprehensive dependency installer that works on all major Linux distributions:

```bash
# 1. Save the install_dependencies.sh script to your project directory

# 2. Make it executable
chmod +x install_dependencies.sh

# 3. Run it with sudo
sudo ./install_dependencies.sh
```

**What it does:**
- ✅ Detects your Linux distribution automatically
- ✅ Installs Python 3.8+ and pip
- ✅ Installs FFmpeg (critical for video processing)
- ✅ Installs Qt6 libraries (PySide6 dependencies)
- ✅ Installs X11 and graphics libraries
- ✅ Installs audio libraries
- ✅ Installs packaging tools (dpkg, fuse, etc.)
- ✅ Installs PyInstaller, PySide6, and yt-dlp
- ✅ Verifies all installations

**Supported distributions:**
- Ubuntu / Debian / Linux Mint / Pop!_OS
- Fedora / RHEL / CentOS / Rocky Linux
- Arch Linux / Manjaro / EndeavourOS
- openSUSE / SLES

**After installation completes**, you can immediately run:
```bash
./build_deb.sh      # For DEB package
# OR
./build_appimage.sh # For AppImage
```

---

## Prerequisites

### System Requirements

- Linux operating system (any distribution)
- Python 3.8 or higher
- At least 500MB free disk space
- Internet connection (for downloading tools)

### Required Packages

The scripts will check and install these automatically, but you can install them manually:

#### For DEB building:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip dpkg

# Fedora
sudo dnf install python3 python3-pip dpkg
```

#### For AppImage building:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip wget fuse libfuse2

# Fedora
sudo dnf install python3 python3-pip wget fuse fuse-libs
```

---

## Building DEB Package

### Step 1: Prepare Your Environment

1. Clone the repository:
```bash
git clone https://github.com/Sarwarhridoy4/youvideo-downloader.git
cd youvideo-downloader
```

2. Save the `build_deb.sh` script to the project root directory

3. Make the script executable:
```bash
chmod +x build_deb.sh
```

### Step 2: Run the Build Script

```bash
./build_deb.sh
```

**Note**: If the script needs to install system packages, it will prompt for sudo privileges.

### Step 3: What the Script Does

The script executes these steps in order:

1. **Tool Verification** (Section 2)
   - Checks for dpkg-deb, python3, pip3
   - Installs PyInstaller if missing
   - Prompts for sudo if system packages are needed

2. **Dependency Installation** (Section 3)
   - Installs Python packages from requirements.txt
   - Verifies project structure

3. **Executable Creation** (Section 4)
   - Uses PyInstaller to create a standalone executable
   - Bundles all assets (icons, stylesheets, modules)
   - Creates dist/youvideo-downloader binary

4. **Package Structure** (Section 5)
   - Creates Debian package directory structure
   - Sets up /usr/bin, /usr/share, and other standard locations
   - Creates launcher script

5. **Desktop Integration** (Section 6)
   - Creates .desktop file for application menu
   - Installs icon to multiple standard locations
   - Ensures proper icon resolution (256x256)

6. **Control Files** (Section 7-9)
   - Creates DEBIAN/control with metadata
   - Sets up post-installation scripts
   - Configures pre-removal scripts

7. **Package Building** (Section 10)
   - Uses dpkg-deb to create .deb file
   - Shows package information and contents

### Step 4: Output

You'll get a file named: `youvideo-downloader_1.6.0_amd64.deb`

### Step 5: Install and Test

```bash
# Install the package
sudo dpkg -i youvideo-downloader_1.6.0_amd64.deb

# Fix any dependency issues (if needed)
sudo apt --fix-broken install

# Run the application
youvideo-downloader

# Or find it in your application menu
```

### Step 6: Uninstall (if needed)

```bash
sudo apt remove youvideo-downloader
```

---

## Building AppImage

### Step 1: Prepare Your Environment

1. Clone the repository:
```bash
git clone https://github.com/Sarwarhridoy4/youvideo-downloader.git
cd youvideo-downloader
```

2. Save the `build_appimage.sh` script to the project root directory

3. Make the script executable:
```bash
chmod +x build_appimage.sh
```

### Step 2: Run the Build Script

```bash
./build_appimage.sh
```

**No sudo required!** AppImage building doesn't need system-level installation.

### Step 3: What the Script Does

The script executes these steps:

1. **Tool Verification** (Section 2)
   - Checks for python3, pip3, wget/curl
   - Installs PyInstaller if missing
   - Verifies FUSE is installed

2. **AppImage Tools Download** (Section 3)
   - Downloads linuxdeploy (official AppImage tool)
   - Downloads appimagetool (AppImage packager)
   - Makes tools executable
   - Stores in appimage-tools/ directory

3. **Dependency Installation** (Section 4)
   - Installs Python requirements
   - Verifies project structure

4. **Executable Creation** (Section 5)
   - Uses PyInstaller with --onefile mode
   - Bundles all assets and modules
   - Creates single executable binary

5. **AppDir Structure** (Section 6)
   - Creates AppImage directory structure (AppDir)
   - Follows official AppImage specification
   - Sets up usr/bin, usr/share hierarchy

6. **Desktop Integration** (Section 7)
   - Creates .desktop file
   - Installs icon to multiple locations
   - Creates .DirIcon for AppImage thumbnail
   - Sets up symbolic links

7. **AppRun Script** (Section 8)
   - Creates entry point script
   - Configures environment variables
   - Sets up library paths

8. **AppImage Building** (Section 9)
   - Uses appimagetool to package AppDir
   - Compresses with gzip
   - **Makes AppImage executable** (crucial step!)

9. **Verification** (Section 10)
   - Verifies file is executable
   - Checks file type
   - Reports size

### Step 4: Output

You'll get a file named: `YouVideo_Downloader-x86_64.AppImage`

**Important**: The AppImage is already executable!

### Step 5: Use the AppImage

```bash
# Method 1: Run directly
./YouVideo_Downloader-x86_64.AppImage

# Method 2: Double-click in file manager
# Just navigate to the file and double-click it

# Method 3: Extract contents (for debugging)
./YouVideo_Downloader-x86_64.AppImage --appimage-extract
```

### Step 6: Distribution

The AppImage is portable and self-contained:
- ✅ No installation required
- ✅ Works on most Linux distributions
- ✅ Single file distribution
- ✅ Automatic desktop integration
- ✅ Can run from USB drive

---

## Troubleshooting

### DEB Package Issues

#### Issue: "dpkg-deb not found"
**Solution**: Install dpkg
```bash
sudo apt install dpkg
```

#### Issue: "Package has unmet dependencies"
**Solution**: Fix dependencies
```bash
sudo apt --fix-broken install
```

#### Issue: "Icon not showing in menu"
**Solution**: Update icon cache
```bash
sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor
update-desktop-database
```

#### Issue: "Permission denied when running script"
**Solution**: Make script executable
```bash
chmod +x build_deb.sh
```

### AppImage Issues

#### Issue: "Cannot execute binary file"
**Solution**: Make AppImage executable
```bash
chmod +x YouVideo_Downloader-x86_64.AppImage
```

#### Issue: "FUSE not installed"
**Solution**: Install FUSE
```bash
# Ubuntu/Debian
sudo apt install fuse libfuse2

# Fedora
sudo dnf install fuse fuse-libs

# Arch Linux
sudo pacman -S fuse2
```

#### Issue: "AppImage won't run on older systems"
**Solution**: Extract and run directly
```bash
./YouVideo_Downloader-x86_64.AppImage --appimage-extract
cd squashfs-root
./AppRun
```

#### Issue: "linuxdeploy download fails"
**Solution**: Download manually
```bash
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod +x linuxdeploy-x86_64.AppImage
mv linuxdeploy-x86_64.AppImage appimage-tools/
```

### Common Issues for Both

#### Issue: "PyInstaller fails to build"
**Solution**: Reinstall PyInstaller
```bash
pip3 uninstall pyinstaller
pip3 install pyinstaller
```

#### Issue: "Missing Python packages"
**Solution**: Install requirements
```bash
pip3 install -r requirements.txt
```

#### Issue: "Icon file not found"
**Solution**: Verify icon exists
```bash
ls -la assets/icons/
```
The script looks for: `app_icon.png`, `icon.png`, or `logo.png`

#### Issue: "Module not found errors"
**Solution**: Ensure all dependencies are installed
```bash
pip3 install --upgrade -r requirements.txt
```

---

## Testing Your Build

### Test DEB Package

```bash
# 1. Install the package
sudo dpkg -i youvideo-downloader_1.6.0_amd64.deb

# 2. Verify installation
dpkg -l | grep youvideo

# 3. Check installed files
dpkg -L youvideo-downloader

# 4. Test the application
youvideo-downloader

# 5. Check logs (if issues occur)
journalctl -xe

# 6. Verify desktop integration
ls -la /usr/share/applications/youvideo-downloader.desktop
ls -la /usr/share/icons/hicolor/256x256/apps/youvideo-downloader.png
```

### Test AppImage

```bash
# 1. Verify executable
ls -la YouVideo_Downloader-x86_64.AppImage

# 2. Check file type
file YouVideo_Downloader-x86_64.AppImage

# 3. Run with verbose output
./YouVideo_Downloader-x86_64.AppImage --verbose

# 4. Extract and inspect contents
./YouVideo_Downloader-x86_64.AppImage --appimage-extract
ls -la squashfs-root/

# 5. Test on different directory
mkdir test-dir
cd test-dir
../YouVideo_Downloader-x86_64.AppImage

# 6. Verify it works without installation
# Copy to /tmp and run
cp YouVideo_Downloader-x86_64.AppImage /tmp/
cd /tmp
./YouVideo_Downloader-x86_64.AppImage
```

---

## Advanced Customization

### Modify DEB Package Metadata

Edit these variables in `build_deb.sh`:
```bash
APP_NAME="youvideo-downloader"
APP_VERSION="1.6.0"
MAINTAINER="Your Name <your.email@example.com>"
DESCRIPTION="Your custom description"
```

### Modify AppImage Settings

Edit these variables in `build_appimage.sh`:
```bash
APP_NAME="YouVideo_Downloader"
APP_VERSION="1.6.0"
ARCH="x86_64"
```

### Change Icon Resolution

Both scripts look for 256x256 icons. To use different resolution:
1. Edit the icon path in the script
2. Modify the icon installation section
3. Update desktop file Icon= path

---

## Script Features

### Both Scripts Include:

✅ **Colored Output**: Easy-to-read colored messages
✅ **Error Handling**: Exits on errors with clear messages
✅ **Progress Tracking**: Shows what's happening at each step
✅ **Automatic Tool Installation**: Installs missing dependencies
✅ **Icon Support**: Properly handles application icons
✅ **Desktop Integration**: Creates .desktop files and installs icons
✅ **Cleanup Options**: Optional cleanup of build artifacts
✅ **Detailed Documentation**: Comments explain every section

### DEB Script Features:

- Creates proper Debian package structure
- Includes post-installation and pre-removal scripts
- Handles dependencies in control file
- Updates desktop and icon databases
- Creates launcher script

### AppImage Script Features:

- Downloads official AppImage tools
- Creates AppImage-compliant AppDir
- Generates AppRun entry point
- Makes AppImage executable automatically
- Includes verification step
- Creates distribution info file

---

## Build Time Estimates

- **DEB Package**: 3-5 minutes
- **AppImage**: 4-6 minutes

Times depend on:
- Internet speed (downloading tools)
- CPU speed (PyInstaller compilation)
- Project size (bundling assets)

---

## File Sizes

Expected output sizes:
- **DEB Package**: ~80-120 MB
- **AppImage**: ~100-150 MB

Sizes include:
- Python interpreter
- All dependencies
- Application code
- Assets and icons

---

## Complete Dependency List

### System Libraries

#### Core Dependencies
- **Python 3.8+** - Programming language runtime
- **pip3** - Python package installer
- **FFmpeg** - Video/audio processing (critical!)
- **build-essential** - Compiler and build tools

#### Qt6 Libraries (PySide6 Dependencies)
- libqt6core6
- libqt6gui6
- libqt6widgets6
- libqt6network6
- libqt6multimedia6
- qt6-gtk-platformtheme

#### X11 and Graphics Libraries
- libx11-6, libx11-xcb1
- libxcb1, libxcb-xinerama0, libxcb-cursor0
- libxcb-icccm4, libxcb-image0, libxcb-keysyms1
- libxcb-randr0, libxcb-render0, libxcb-shape0
- libxkbcommon0, libxkbcommon-x11-0
- libgl1, libegl1
- libdbus-1-3

#### Audio Libraries
- libasound2
- libpulse0
- gstreamer1.0-plugins-base
- gstreamer1.0-plugins-good

#### Packaging Tools
- dpkg, dpkg-dev (for DEB building)
- fuse, libfuse2 (for AppImage)
- patchelf
- desktop-file-utils

### Python Packages

#### Build Tools
- PyInstaller - Creates standalone executables
- wheel, setuptools - Python packaging tools

#### Application Dependencies
- PySide6 - Qt6 for Python (GUI framework)
- yt-dlp - YouTube downloader backend
- requests - HTTP library
- urllib3 - HTTP client
- certifi - SSL certificates

### Installation Commands by Distribution

#### Ubuntu/Debian/Mint
```bash
# System packages
sudo apt update
sudo apt install -y python3 python3-pip python3-dev build-essential \
    ffmpeg qt6-base-dev libqt6core6 libqt6gui6 libqt6widgets6 \
    libx11-6 libxcb1 libxcb-xinerama0 libxcb-cursor0 \
    libasound2 libpulse0 dpkg fuse libfuse2 patchelf

# Python packages
pip3 install --upgrade pyinstaller PySide6 yt-dlp
```

#### Fedora/RHEL
```bash
# Enable RPM Fusion for FFmpeg
sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm

# System packages
sudo dnf install -y python3 python3-pip python3-devel gcc gcc-c++ \
    ffmpeg qt6-qtbase qt6-qtbase-devel libX11 libxcb \
    alsa-lib pulseaudio-libs fuse fuse-libs patchelf

# Python packages
pip3 install --upgrade pyinstaller PySide6 yt-dlp
```

#### Arch Linux/Manjaro
```bash
# System packages
sudo pacman -S --noconfirm python python-pip base-devel \
    ffmpeg qt6-base libx11 libxcb alsa-lib libpulse \
    fuse2 fuse3 patchelf

# Python packages
pip3 install --upgrade pyinstaller PySide6 yt-dlp
```

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review script output for error messages
3. Open an issue on GitHub: https://github.com/Sarwarhridoy4/youvideo-downloader/issues

---

## License

These build scripts are provided under the MIT License, same as the YouVideo Downloader project.

---

**Happy Building! 🚀**