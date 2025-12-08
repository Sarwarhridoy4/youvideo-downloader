# YouVideo Downloader - Quick Reference

## 🚀 Quick Start (Easiest)

```bash
# 1. Clone the repository
git clone https://github.com/Sarwarhridoy4/youvideo-downloader.git
cd youvideo-downloader

# 2. Make master script executable
chmod +x build.sh

# 3. Run interactive build menu
./build.sh
```

That's it! The master script will guide you through everything.

---

## 📜 All Available Scripts

### 1. **build.sh** - Master Build Script (Recommended)
The easiest way to build packages. Provides an interactive menu.

```bash
# Interactive menu
./build.sh

# Or use direct commands:
./build.sh deps        # Install dependencies
./build.sh deb         # Build DEB package
./build.sh appimage    # Build AppImage
./build.sh all         # Build both
./build.sh check       # Check dependencies
./build.sh help        # Show help
```

### 2. **install_dependencies.sh** - Dependency Installer
Installs ALL required dependencies on any Linux distribution.

```bash
chmod +x install_dependencies.sh
sudo ./install_dependencies.sh
```

**Features:**
- ✅ Auto-detects your Linux distribution
- ✅ Installs system packages (Python, FFmpeg, Qt6, etc.)
- ✅ Installs Python packages (PyInstaller, PySide6, yt-dlp)
- ✅ Verifies all installations
- ✅ Works on Ubuntu, Fedora, Arch, openSUSE

### 3. **build_deb.sh** - DEB Package Builder
Creates `.deb` packages for Debian-based systems.

```bash
chmod +x build_deb.sh
./build_deb.sh
```

**Output:** `youvideo-downloader_1.6.0_amd64.deb`

### 4. **build_appimage.sh** - AppImage Builder
Creates portable AppImages that work on most Linux distributions.

```bash
chmod +x build_appimage.sh
./build_appimage.sh
```

**Output:** `YouVideo_Downloader-x86_64.AppImage`

---

## 🎯 Common Workflows

### First Time Setup
```bash
# Clone repository
git clone https://github.com/Sarwarhridoy4/youvideo-downloader.git
cd youvideo-downloader

# Install all dependencies
chmod +x install_dependencies.sh
sudo ./install_dependencies.sh

# Build your package
chmod +x build_deb.sh        # or build_appimage.sh
./build_deb.sh               # or ./build_appimage.sh
```

### Quick Build (if dependencies already installed)
```bash
# For DEB
./build_deb.sh

# For AppImage
./build_appimage.sh

# For both
./build.sh all
```

### Update and Rebuild
```bash
# Pull latest changes
git pull origin production

# Reinstall Python dependencies
pip3 install --upgrade -r requirements.txt

# Rebuild package
./build_deb.sh  # or ./build_appimage.sh
```

---

## 📦 Installation Commands

### Install DEB Package
```bash
# Install
sudo dpkg -i youvideo-downloader_1.6.0_amd64.deb

# Fix any dependency issues
sudo apt --fix-broken install

# Run the application
youvideo-downloader
```

### Run AppImage
```bash
# Make executable (if not already)
chmod +x YouVideo_Downloader-x86_64.AppImage

# Run it
./YouVideo_Downloader-x86_64.AppImage

# Or double-click in file manager
```

### Uninstall DEB Package
```bash
sudo apt remove youvideo-downloader
```

---

## 🔍 Dependency Check Commands

### Check if all dependencies are installed
```bash
# Quick check
./build.sh check

# Manual check
python3 --version
pip3 --version
ffmpeg -version
python3 -c "import PyInstaller"
python3 -c "import PySide6"
python3 -c "import yt_dlp"
```

### Install missing Python packages
```bash
pip3 install --upgrade pyinstaller PySide6 yt-dlp
```

### Install system dependencies (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg \
    libqt6core6 libqt6gui6 libqt6widgets6 \
    libx11-6 libxcb1 dpkg fuse libfuse2
```

---

## 🐛 Troubleshooting Quick Fixes

### "Permission denied" when running script
```bash
chmod +x build.sh            # Make executable
```

### "dpkg-deb not found"
```bash
sudo apt install dpkg        # Debian/Ubuntu
```

### "FFmpeg not found"
```bash
sudo apt install ffmpeg      # Debian/Ubuntu
sudo dnf install ffmpeg      # Fedora (may need RPM Fusion)
sudo pacman -S ffmpeg        # Arch Linux
```

### "PyInstaller not found"
```bash
pip3 install --upgrade pyinstaller
```

### "PySide6 not found"
```bash
pip3 install --upgrade PySide6
```

### "AppImage won't run"
```bash
# Make it executable
chmod +x YouVideo_Downloader-x86_64.AppImage

# Install FUSE if needed
sudo apt install fuse libfuse2   # Debian/Ubuntu
```

### "Icon not showing"
```bash
# Update icon cache
sudo gtk-update-icon-cache -f /usr/share/icons/hicolor
update-desktop-database
```

### Build fails with "No module named 'X'"
```bash
# Reinstall all requirements
pip3 install --upgrade -r requirements.txt
```

---

## 📊 Build Output Reference

### DEB Package
- **File:** `youvideo-downloader_1.6.0_amd64.deb`
- **Size:** ~80-120 MB
- **Location:** Project root directory
- **Install:** `sudo dpkg -i youvideo-downloader_1.6.0_amd64.deb`

### AppImage
- **File:** `YouVideo_Downloader-x86_64.AppImage`
- **Size:** ~100-150 MB
- **Location:** Project root directory
- **Run:** `./YouVideo_Downloader-x86_64.AppImage`

### Intermediate Files (can be deleted)
- `build/` - PyInstaller build directory
- `dist/` - PyInstaller distribution directory
- `*.spec` - PyInstaller spec files
- `YouVideo_Downloader.AppDir/` - AppImage build directory
- `youvideo-downloader_1.6.0_amd64/` - DEB package directory
- `appimage-tools/` - AppImage tools (keep for future builds)

---

## 🧹 Cleanup Commands

### After successful build
```bash
# Remove build artifacts (keep packages)
rm -rf build dist *.spec
rm -rf YouVideo_Downloader.AppDir
rm -rf youvideo-downloader_1.6.0_amd64

# Keep: *.deb, *.AppImage, appimage-tools/
```

### Complete cleanup (removes everything)
```bash
# Remove all build files
rm -rf build dist *.spec
rm -rf YouVideo_Downloader.AppDir
rm -rf youvideo-downloader_1.6.0_amd64
rm -rf appimage-tools

# Remove packages (optional)
rm -f *.deb *.AppImage
```

---

## 📝 Script Options Summary

### build.sh (Master Script)
| Command | Description |
|---------|-------------|
| `./build.sh` | Interactive menu |
| `./build.sh deps` | Install dependencies |
| `./build.sh deb` | Build DEB package |
| `./build.sh appimage` | Build AppImage |
| `./build.sh all` | Build both packages |
| `./build.sh check` | Check dependencies |
| `./build.sh help` | Show help |

### Individual Scripts
| Script | Purpose | Sudo Required |
|--------|---------|---------------|
| `install_dependencies.sh` | Install all dependencies | Yes |
| `build_deb.sh` | Build DEB package | Only if deps missing |
| `build_appimage.sh` | Build AppImage | No |

---

## ⏱️ Time Estimates

| Task | Estimated Time |
|------|----------------|
| Install dependencies | 5-15 minutes |
| Build DEB package | 3-5 minutes |
| Build AppImage | 4-6 minutes |
| Build both packages | 7-11 minutes |

*Times vary based on internet speed and CPU performance*

---

## 🎓 Tips & Best Practices

1. **Always install dependencies first**
   ```bash
   sudo ./install_dependencies.sh
   ```

2. **Use the master script for convenience**
   ```bash
   ./build.sh all
   ```

3. **Keep appimage-tools after first build**
   - Speeds up subsequent AppImage builds
   - No need to re-download tools

4. **Test before distributing**
   ```bash
   # Test DEB
   sudo dpkg -i youvideo-downloader_1.6.0_amd64.deb
   youvideo-downloader
   
   # Test AppImage
   ./YouVideo_Downloader-x86_64.AppImage
   ```

5. **Clean build for releases**
   ```bash
   # Remove old artifacts
   rm -rf build dist *.spec
   
   # Build fresh
   ./build.sh all
   ```

---

## 📚 Additional Resources

- **Full Documentation:** [BUILD_GUIDE.md](BUILD_GUIDE.md)
- **Project Repository:** https://github.com/Sarwarhridoy4/youvideo-downloader
- **Report Issues:** https://github.com/Sarwarhridoy4/youvideo-downloader/issues
- **AppImage Documentation:** https://docs.appimage.org/
- **Debian Packaging:** https://www.debian.org/doc/manuals/maint-guide/

---

## 🆘 Getting Help

If you encounter issues:

1. Check this quick reference
2. Read the [BUILD_GUIDE.md](BUILD_GUIDE.md)
3. Review script output for error messages
4. Search existing issues on GitHub
5. Open a new issue with:
   - Your Linux distribution and version
   - Complete error output
   - Steps to reproduce

---

**Last Updated:** December 2024  
**Version:** 1.6.0