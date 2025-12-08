# YouVideo Downloader - Build Scripts Documentation

Complete documentation for the automated build system that creates DEB packages and AppImages for YouVideo Downloader.

---

## 📦 What's Included

This build system provides **4 comprehensive scripts**:

1. **`build.sh`** - Master build script with interactive menu
2. **`install_dependencies.sh`** - Automated dependency installer
3. **`build_deb.sh`** - DEB package builder for Debian-based systems
4. **`build_appimage.sh`** - AppImage builder for universal Linux distribution

Plus **2 documentation files**:
- **`BUILD_GUIDE.md`** - Complete step-by-step build guide
- **`QUICK_REFERENCE.md`** - Command cheat sheet and quick reference

---

## 🎯 Why Use These Scripts?

### ✅ Fully Automated
- Automatically checks for required tools
- Installs missing dependencies
- Handles all build steps
- Creates production-ready packages

### ✅ Well Documented
- Every section clearly explained with comments
- Colored output shows progress
- Error messages guide you to solutions
- Step-by-step instructions included

### ✅ Handles Everything
- **FFmpeg** - Video processing (critical!)
- **PySide6** - Qt6 GUI framework with all dependencies
- **PyInstaller** - Executable creation
- **System libraries** - Qt6, X11, audio, graphics
- **Icon installation** - Multiple locations for compatibility
- **Desktop integration** - .desktop files and launchers

### ✅ Cross-Distribution Support
Works on:
- Ubuntu / Debian / Linux Mint / Pop!_OS
- Fedora / RHEL / CentOS / Rocky Linux
- Arch Linux / Manjaro / EndeavourOS
- openSUSE / SLES

---

## 🚀 Quick Start

### Easiest Method (Recommended)

```bash
# 1. Make master script executable
chmod +x build.sh

# 2. Run it
./build.sh

# 3. Follow the interactive menu
```

The master script will:
1. Check if dependencies are installed
2. Offer to install missing dependencies
3. Let you choose what to build (DEB, AppImage, or both)
4. Build your packages automatically

---

## 📜 Script Details

### 1. build.sh - Master Build Script

**Purpose:** Unified interface for all build operations

**Features:**
- Interactive menu system
- Automatic dependency checking
- Can call all other scripts
- Provides helpful guidance

**Usage:**
```bash
./build.sh              # Interactive menu
./build.sh deps         # Install dependencies
./build.sh deb          # Build DEB
./build.sh appimage     # Build AppImage
./build.sh all          # Build both
./build.sh check        # Check dependencies
```

**Sections:**
1. Utility functions (colors, messages)
2. Script verification
3. Dependency checking
4. Dependency installation
5. DEB building
6. AppImage building
7. Build all packages
8. Interactive menu
9. Main function

---

### 2. install_dependencies.sh - Dependency Installer

**Purpose:** Install all required dependencies on any Linux distribution

**Features:**
- Auto-detects Linux distribution
- Supports multiple package managers (apt, dnf, pacman, zypper)
- Installs system packages AND Python packages
- Verifies all installations

**Usage:**
```bash
sudo ./install_dependencies.sh
```

**What it installs:**

**System Packages:**
- Python 3.8+ and pip
- Build tools (gcc, make, etc.)
- FFmpeg (video/audio processing)
- Qt6 libraries (PySide6 dependencies)
- X11 libraries (GUI display)
- Audio libraries (ALSA, PulseAudio)
- Packaging tools (dpkg, fuse, etc.)

**Python Packages:**
- PyInstaller (creates executables)
- PySide6 (Qt6 for Python)
- yt-dlp (YouTube downloader)
- Supporting libraries

**Sections:**
1. Utility functions
2. Distribution detection
3. Root privilege check
4. Package list update
5. System dependencies installation
6. FFmpeg installation
7. Qt6 libraries installation
8. X11 libraries installation
9. Audio libraries installation
10. Packaging tools installation
11. Python packages installation
12. Project requirements installation
13. Installation verification
14. Summary display

---

### 3. build_deb.sh - DEB Package Builder

**Purpose:** Create `.deb` packages for Debian-based Linux distributions

**Features:**
- Checks and installs required tools
- Builds executable with PyInstaller
- Creates proper Debian package structure
- Handles icon installation (multiple locations)
- Creates desktop integration files
- Generates control files with dependencies
- Creates post-install and pre-remove scripts

**Usage:**
```bash
./build_deb.sh
```

**Output:** `youvideo-downloader_1.6.0_amd64.deb`

**Package Structure:**
```
youvideo-downloader_1.6.0_amd64/
├── DEBIAN/
│   ├── control          # Package metadata
│   ├── postinst         # Post-installation script
│   └── prerm            # Pre-removal script
├── usr/
│   ├── bin/
│   │   └── youvideo-downloader  # Launcher script
│   └── share/
│       ├── applications/
│       │   └── youvideo-downloader.desktop
│       ├── icons/
│       │   └── hicolor/256x256/apps/
│       │       └── youvideo-downloader.png
│       ├── pixmaps/
│       │   └── youvideo-downloader.png
│       └── youvideo-downloader/
│           └── youvideo-downloader  # Main executable
```

**Dependencies in control file:**
- python3 (>= 3.8)
- ffmpeg
- libqt6core6, libqt6gui6, libqt6widgets6
- libx11-6, libxcb1, libxcb-xinerama0, libxcb-cursor0

**Sections:**
1. Utility functions
2. Tool checking and installation
3. Dependency preparation
4. Executable building (PyInstaller)
5. DEB structure creation
6. Desktop integration setup
7. Control file creation
8. Post-install script creation
9. Pre-removal script creation
10. DEB package building
11. Package testing instructions
12. Cleanup

---

### 4. build_appimage.sh - AppImage Builder

**Purpose:** Create portable AppImages that work on most Linux distributions

**Features:**
- Downloads official AppImage tools (linuxdeploy, appimagetool)
- Builds executable with PyInstaller
- Creates AppDir structure (AppImage specification)
- Generates AppRun entry point script
- Handles icon installation (including .DirIcon)
- Makes AppImage executable automatically
- Verifies AppImage integrity

**Usage:**
```bash
./build_appimage.sh
```

**Output:** `YouVideo_Downloader-x86_64.AppImage`

**AppDir Structure:**
```
YouVideo_Downloader.AppDir/
├── AppRun                    # Entry point script
├── youvideo-downloader.desktop
├── youvideo-downloader.png   # Icon
├── .DirIcon                  # Thumbnail icon
└── usr/
    ├── bin/
    │   └── YouVideo_Downloader  # Executable
    └── share/
        ├── applications/
        │   └── youvideo-downloader.desktop
        └── icons/
            └── hicolor/256x256/apps/
                └── youvideo-downloader.png
```

**Why AppImage is special:**
- Single file distribution
- No installation required
- Works on most Linux distributions
- Portable (can run from USB)
- Automatic desktop integration
- Self-contained with all dependencies

**Sections:**
1. Utility functions
2. Tool checking and installation
3. AppImage tools download
4. Dependency preparation
5. Executable building (PyInstaller)
6. AppDir structure creation
7. Desktop integration setup
8. AppRun script creation
9. AppImage building (appimagetool)
10. AppImage verification
11. Testing instructions
12. Cleanup
13. Distribution info creation

---

## 🔧 Technical Details

### Icon Handling

All scripts properly handle application icons:

**Search Locations:**
- `assets/icons/app_icon.png`
- `assets/icons/icon.png`
- `assets/icons/logo.png`

**Installation Locations:**

**For DEB:**
- `/usr/share/icons/hicolor/256x256/apps/`
- `/usr/share/pixmaps/`

**For AppImage:**
- `AppDir/usr/share/icons/hicolor/256x256/apps/`
- `AppDir/usr/share/pixmaps/`
- `AppDir/.DirIcon` (for thumbnail)
- `AppDir/youvideo-downloader.png` (root)

### PyInstaller Configuration

Both build scripts use PyInstaller with:
- `--onefile` - Single executable file
- `--windowed` - GUI application (no console)
- `--icon` - Application icon
- `--add-data` - Bundle assets, ui, downloader, utils folders
- `--name` - Executable name

### Desktop Entry

Standard `.desktop` file created:
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=YouVideo Downloader
Comment=Download YouTube videos with ease
Exec=youvideo-downloader
Icon=youvideo-downloader
Terminal=false
Categories=Network;AudioVideo;
Keywords=youtube;downloader;video;
StartupNotify=true
```

---

## 🎨 Script Features

### Colored Output

All scripts use consistent color coding:
- 🔵 **Blue [INFO]** - Information messages
- 🟢 **Green [SUCCESS]** - Success messages
- 🟡 **Yellow [WARNING]** - Warnings
- 🔴 **Red [ERROR]** - Error messages

### Error Handling

Scripts use `set -e` to exit on errors and provide:
- Clear error messages
- Suggestions for fixes
- Links to documentation

### Progress Tracking

Each major step is clearly labeled:
```
================================
Installing FFmpeg
================================
[INFO] FFmpeg is required for video processing
[SUCCESS] FFmpeg installed
```

---

## 📊 Build Process Flow

### DEB Package Build Flow
```
1. Check tools (dpkg-deb, python3, pip3, ffmpeg, Qt6 libs)
   ↓
2. Install missing tools (if needed)
   ↓
3. Install Python dependencies (requirements.txt)
   ↓
4. Build executable with PyInstaller
   ↓
5. Create DEB directory structure
   ↓
6. Copy executable and create launcher
   ↓
7. Create .desktop file
   ↓
8. Install icons
   ↓
9. Create control file
   ↓
10. Create post-install script
   ↓
11. Create pre-removal script
   ↓
12. Build .deb with dpkg-deb
   ↓
13. Verify package
```

### AppImage Build Flow
```
1. Check tools (python3, pip3, wget/curl, ffmpeg)
   ↓
2. Download linuxdeploy and appimagetool
   ↓
3. Install Python dependencies
   ↓
4. Build executable with PyInstaller
   ↓
5. Create AppDir structure
   ↓
6. Copy executable to AppDir
   ↓
7. Create .desktop file
   ↓
8. Install icons (including .DirIcon)
   ↓
9. Create AppRun script
   ↓
10. Build AppImage with appimagetool
   ↓
11. Make AppImage executable (chmod +x)
   ↓
12. Verify AppImage
```

---

## 🧪 Testing Recommendations

### Before Releasing

1. **Test DEB package:**
   ```bash
   # Install on clean system
   sudo dpkg -i youvideo-downloader_1.6.0_amd64.deb
   
   # Check if icon appears in menu
   # Launch from menu
   # Launch from terminal: youvideo-downloader
   
   # Uninstall
   sudo apt remove youvideo-downloader
   ```

2. **Test AppImage:**
   ```bash
   # Test on multiple distributions
   ./YouVideo_Downloader-x86_64.AppImage
   
   # Test from different directory
   cp YouVideo_Downloader-x86_64.AppImage /tmp/
   cd /tmp
   ./YouVideo_Downloader-x86_64.AppImage
   ```

3. **Test functionality:**
   - Download a video
   - Test different formats
   - Check playlist downloads
   - Test MP3 conversion
   - Verify FFmpeg integration

---

## 📝 Customization

### Change Application Version

Edit in each script:
```bash
# build_deb.sh
APP_VERSION="1.6.0"

# build_appimage.sh
APP_VERSION="1.6.0"
```

### Change Application Name

Edit in each script:
```bash
# build_deb.sh
APP_NAME="youvideo-downloader"

# build_appimage.sh
APP_NAME="YouVideo_Downloader"
```

### Change Maintainer

Edit in `build_deb.sh`:
```bash
MAINTAINER="Your Name <your.email@example.com>"
```

### Add Dependencies

Edit in `build_deb.sh` control file section:
```bash
Depends: python3 (>= 3.8), ffmpeg, your-package
```

---

## 🆘 Common Issues & Solutions

### Issue: "Permission denied"
**Solution:**
```bash
chmod +x build.sh
chmod +x install_dependencies.sh
chmod +x build_deb.sh
chmod +x build_appimage.sh
```

### Issue: "dpkg-deb not found"
**Solution:**
```bash
sudo apt install dpkg
```

### Issue: "FFmpeg not found"
**Solution:**
```bash
./install_dependencies.sh
# OR manually:
sudo apt install ffmpeg
```

### Issue: "AppImage won't run"
**Solution:**
```bash
chmod +x YouVideo_Downloader-x86_64.AppImage
sudo apt install fuse libfuse2
```

### Issue: "PyInstaller fails"
**Solution:**
```bash
pip3 uninstall pyinstaller
pip3 install --upgrade pyinstaller
```

---

## 📚 References

- [AppImage Documentation](https://docs.appimage.org/)
- [Debian Packaging Guide](https://www.debian.org/doc/manuals/maint-guide/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)

---

## 🤝 Contributing

To improve these build scripts:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple distributions
5. Submit a pull request

---

## 📄 License

These build scripts are provided under the MIT License, same as the YouVideo Downloader project.

---

## ✨ Credits

Build scripts created for the YouVideo Downloader project:
- **Project:** https://github.com/Sarwarhridoy4/youvideo-downloader
- **Original Author:** Sarwar Hossain

---

**Last Updated:** December 2024  
**Version:** 1.6.0  
**Maintainer:** Sarwar Hossain <sarwarhridoy4@gmail.com>