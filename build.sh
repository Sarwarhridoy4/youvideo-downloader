#!/usr/bin/env bash
# ==============================================================================
# YouVideo Downloader - Professional Linux Package Builder
# Creates both .deb and AppImage with proper icons, dependencies, and metadata
# Author: Sarwar Hossain <sarwarhridoy4@gmail.com>
# ==============================================================================

set -e  # Exit on any error

# Color output for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ────────────────────────────── Configuration ──────────────────────────────

APP_NAME="YouVideoDownloader"
PACKAGE_NAME="youvideodownloader"
LINUX_BINARY="youvideo-downloader"
SAFE_BIN_NAME="youvideo-downloader"
APP_ID="com.youvideo.downloader"

MAINTAINER="Sarwar Hossain"
EMAIL="sarwarhridoy4@gmail.com"
DESCRIPTION="Fast and powerful YouTube video downloader with modern PyQt6 interface"
LONG_DESCRIPTION="YouVideo Downloader is a powerful and user-friendly application for downloading videos from YouTube and other platforms. Features include modern PyQt6 interface, high-quality video/audio downloads, playlist support, format conversion, and batch downloads."
CATEGORIES="AudioVideo;Video;Network;Qt;"
KEYWORDS="youtube;video;downloader;yt-dlp;audio;media;converter;"

SPEC_FILE="./YouVideoDownloader.spec"
ICON_SOURCE="assets/icons/appicon.png"

BUILD_DIR="./dist"
APPDIR="${BUILD_DIR}/${APP_NAME}.AppDir"
SPEC_OUTPUT_DIR="${BUILD_DIR}/${APP_NAME}"

# ────────────────────────────── Functions ──────────────────────────────

print_header() {
    echo -e "${CYAN}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# ────────────────────────────── Version Input ──────────────────────────────

print_header "YouVideo Downloader - Professional Linux Package Builder"
echo -e "${CYAN}Author:${NC} ${MAINTAINER} <${EMAIL}>"
echo -e "${CYAN}Project:${NC} https://github.com/Sarwarhridoy4/youvideo-downloader"
echo

# Prompt for version
read -p "$(echo -e ${CYAN}Enter version number ${YELLOW}[e.g., 1.7.0]${CYAN}:${NC} )" VERSION

# Validate version format
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format. Please use semantic versioning (e.g., 1.7.0)"
    exit 1
fi

echo
print_success "Version set to: ${VERSION}"
echo

# ────────────────────────────── System Check ──────────────────────────────

print_header "Checking System Requirements"

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then 
    print_warning "Running as root is not recommended. Please run as a normal user."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check sudo access
if ! sudo -v; then
    print_error "This script requires sudo privileges. Please run with sudo access."
    exit 1
fi

print_success "System check passed"
echo

# ────────────────────────────── Install Dependencies ──────────────────────────────

print_header "Installing System Dependencies"

# System packages required for packaging
SYSTEM_PACKAGES=(
    "build-essential"
    "fakeroot"
    "dpkg-dev"
    "debhelper"
    "fuse"
    "patchelf"
    "desktop-file-utils"
    "appstream"
    "imagemagick"
    "python3"
    "python3-pip"
    "python3-venv"
    "python3-dev"
    "wget"
    "curl"
    "git"
)

print_step "Updating package list..."
sudo apt update -qq

print_step "Installing system packages..."
PACKAGES_TO_INSTALL=()
for package in "${SYSTEM_PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii  $package"; then
        PACKAGES_TO_INSTALL+=("$package")
    fi
done

if [ ${#PACKAGES_TO_INSTALL[@]} -gt 0 ]; then
    echo "Installing: ${PACKAGES_TO_INSTALL[*]}"
    sudo apt install -y "${PACKAGES_TO_INSTALL[@]}" || {
        print_error "Failed to install system packages"
        exit 1
    }
    print_success "System packages installed"
else
    print_success "All system packages already installed"
fi

echo

# ────────────────────────────── Python Environment Setup ──────────────────────────────

print_header "Setting Up Python Environment"

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_step "Python version: ${PYTHON_VERSION}"

if ! check_command pip3; then
    print_error "pip3 not found. Installing..."
    sudo apt install -y python3-pip
fi

# Upgrade pip
print_step "Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

# Install PyInstaller
print_step "Installing PyInstaller..."
python3 -m pip install --upgrade pyinstaller --quiet
print_success "PyInstaller installed: $(pyinstaller --version)"

# Install Pillow for icon generation
print_step "Installing Pillow for icon generation..."
python3 -m pip install --upgrade Pillow --quiet
print_success "Pillow installed"

# Install project dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    print_step "Installing project dependencies from requirements.txt..."
    python3 -m pip install -r requirements.txt --quiet
    print_success "Project dependencies installed"
else
    print_warning "requirements.txt not found. Installing essential packages..."
    python3 -m pip install PyQt6 yt-dlp requests --quiet
    print_success "Essential packages installed"
fi

echo

# ────────────────────────────── Download Tools ──────────────────────────────

print_header "Downloading Packaging Tools"

# Download linuxdeploy
if [ ! -f ./linuxdeploy-x86_64.AppImage ]; then
    print_step "Downloading linuxdeploy..."
    wget -q --show-progress https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
    chmod +x linuxdeploy-x86_64.AppImage
    print_success "linuxdeploy downloaded"
else
    print_success "linuxdeploy already present"
fi

echo

# ────────────────────────────── Icon Preparation ──────────────────────────────

print_header "Preparing Application Icons"

ICON_DIR="assets/icons"
mkdir -p "$ICON_DIR"

# Check if source icon exists
if [ ! -f "$ICON_SOURCE" ]; then
    print_warning "Icon not found: $ICON_SOURCE"
    print_step "Generating professional placeholder icon..."
    
    # Create a modern gradient icon with YV text
    convert -size 512x512 \
            gradient:'#667eea-#764ba2' \
            \( -size 512x512 xc:none \
               -gravity center \
               -fill white \
               -font "DejaVu-Sans-Bold" \
               -pointsize 240 \
               -annotate +0+0 "YV" \
            \) \
            -composite \
            -quality 95 \
            "$ICON_SOURCE"
    
    print_success "Professional icon created"
else
    print_success "Icon found: $ICON_SOURCE"
    
    # Validate icon
    ICON_SIZE=$(identify -format "%wx%h" "$ICON_SOURCE")
    print_step "Icon size: ${ICON_SIZE}"
    
    # Check if icon is large enough
    WIDTH=$(echo $ICON_SIZE | cut -d'x' -f1)
    if [ "$WIDTH" -lt 256 ]; then
        print_warning "Icon is smaller than 256x256. Recommended: 512x512 or larger"
    fi
fi

# Generate all icon sizes
print_step "Generating platform-specific icon sizes..."

cat > /tmp/generate_icons.py << 'PYTHON_SCRIPT'
import sys
from pathlib import Path
from PIL import Image

def create_icons(source_png):
    source = Path(source_png)
    output_dir = source.parent
    
    img = Image.open(source)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Standard Linux icon sizes for hicolor theme
    sizes = [16, 22, 24, 32, 48, 64, 128, 256, 512]
    
    created_count = 0
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        out_path = output_dir / f"icon_{size}x{size}.png"
        resized.save(out_path, 'PNG', optimize=True)
        created_count += 1
    
    print(f"✓ Generated {created_count} icon sizes")

if __name__ == "__main__":
    try:
        create_icons(sys.argv[1])
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
PYTHON_SCRIPT

python3 /tmp/generate_icons.py "$ICON_SOURCE"
rm /tmp/generate_icons.py

print_success "All icon sizes prepared"
echo

# ────────────────────────────── PyInstaller Build ──────────────────────────────

print_header "Building Application with PyInstaller"

# Verify spec file exists
if [ ! -f "$SPEC_FILE" ]; then
    print_error "Spec file not found: $SPEC_FILE"
    print_error "Please ensure YouVideoDownloader.spec is in the current directory"
    exit 1
fi

print_step "Cleaning previous builds..."
rm -rf "$BUILD_DIR" build
mkdir -p "$BUILD_DIR"

print_step "Running PyInstaller build..."
echo "This may take a few minutes..."
pyinstaller --clean --noconfirm "$SPEC_FILE" 2>&1 | tee /tmp/pyinstaller.log | grep -E "(Writing|Building|Copying|Analyzing|WARNING|ERROR)" || true

# Validate binary exists
if [ ! -f "${SPEC_OUTPUT_DIR}/${LINUX_BINARY}" ]; then
    print_error "Build failed! Binary not found: ${SPEC_OUTPUT_DIR}/${LINUX_BINARY}"
    print_error "Check /tmp/pyinstaller.log for details"
    exit 1
fi

chmod +x "${SPEC_OUTPUT_DIR}/${LINUX_BINARY}"
print_success "Application built successfully"

# Get binary info
BINARY_SIZE=$(du -h "${SPEC_OUTPUT_DIR}/${LINUX_BINARY}" | cut -f1)
print_step "Binary size: ${BINARY_SIZE}"
print_step "Binary location: ${SPEC_OUTPUT_DIR}/${LINUX_BINARY}"
echo

# ══════════════════════════════════════════════════════════════════════════════
#                               BUILD .deb PACKAGE
# ══════════════════════════════════════════════════════════════════════════════

print_header "Building Debian Package (.deb)"

DEB_DIR="${BUILD_DIR}/${APP_NAME}_deb"
print_step "Creating Debian package structure..."
rm -rf "$DEB_DIR"

# Create directory structure according to Debian policy
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/pixmaps"
mkdir -p "$DEB_DIR/usr/share/${PACKAGE_NAME}"
mkdir -p "$DEB_DIR/usr/share/doc/${PACKAGE_NAME}"
mkdir -p "$DEB_DIR/usr/share/man/man1"

# Standard hicolor icon directories
for size in 16 22 24 32 48 64 128 256 512; do
    mkdir -p "$DEB_DIR/usr/share/icons/hicolor/${size}x${size}/apps"
done

# Copy application files
print_step "Copying application files..."
cp -r "${SPEC_OUTPUT_DIR}/"* "$DEB_DIR/usr/share/${PACKAGE_NAME}/"
chmod 755 "$DEB_DIR/usr/share/${PACKAGE_NAME}/${LINUX_BINARY}"

# Create wrapper script for /usr/bin
print_step "Creating launcher wrapper..."
cat > "$DEB_DIR/usr/bin/${SAFE_BIN_NAME}" << 'WRAPPER_SCRIPT'
#!/bin/bash
# YouVideo Downloader wrapper script
# Ensures proper execution environment

APP_DIR="/usr/share/PACKAGE_NAME"
BINARY="LINUX_BINARY"

# Check if running in terminal or GUI
if [ -t 0 ]; then
    # Running in terminal
    exec "$APP_DIR/$BINARY" "$@"
else
    # Running from GUI (desktop entry)
    cd "$APP_DIR"
    exec "./$BINARY" "$@" 2>/dev/null
fi
WRAPPER_SCRIPT

sed -i "s/PACKAGE_NAME/${PACKAGE_NAME}/g" "$DEB_DIR/usr/bin/${SAFE_BIN_NAME}"
sed -i "s/LINUX_BINARY/${LINUX_BINARY}/g" "$DEB_DIR/usr/bin/${SAFE_BIN_NAME}"
chmod 755 "$DEB_DIR/usr/bin/${SAFE_BIN_NAME}"

# Install icons
print_step "Installing icons to hicolor theme..."
for size in 16 22 24 32 48 64 128 256 512; do
    if [ -f "$ICON_DIR/icon_${size}x${size}.png" ]; then
        cp "$ICON_DIR/icon_${size}x${size}.png" \
           "$DEB_DIR/usr/share/icons/hicolor/${size}x${size}/apps/${APP_ID}.png"
    fi
done

# Main pixmap icon (256x256 is standard)
if [ -f "$ICON_DIR/icon_256x256.png" ]; then
    cp "$ICON_DIR/icon_256x256.png" "$DEB_DIR/usr/share/pixmaps/${APP_ID}.png"
else
    cp "$ICON_SOURCE" "$DEB_DIR/usr/share/pixmaps/${APP_ID}.png"
fi

# Create FreeDesktop-compliant desktop entry
print_step "Creating desktop entry..."
cat > "$DEB_DIR/usr/share/applications/${APP_ID}.desktop" << DESKTOP_ENTRY
[Desktop Entry]
Version=1.1
Type=Application
Name=${APP_NAME}
GenericName=Video Downloader
Comment=${DESCRIPTION}
Exec=${SAFE_BIN_NAME} %U
Icon=${APP_ID}
Terminal=false
Categories=${CATEGORIES}
Keywords=${KEYWORDS}
MimeType=x-scheme-handler/http;x-scheme-handler/https;
StartupNotify=true
StartupWMClass=${APP_NAME}
X-GNOME-SingleWindow=true
DESKTOP_ENTRY

# Validate desktop file
if ! desktop-file-validate "$DEB_DIR/usr/share/applications/${APP_ID}.desktop" 2>&1; then
    print_warning "Desktop file has validation warnings (non-critical)"
fi

# Create man page
print_step "Creating man page..."
cat > "$DEB_DIR/usr/share/man/man1/${SAFE_BIN_NAME}.1" << MANPAGE
.TH ${APP_NAME} 1 "$(date '+%B %Y')" "${VERSION}" "${APP_NAME} Manual"
.SH NAME
${SAFE_BIN_NAME} \- ${DESCRIPTION}
.SH SYNOPSIS
.B ${SAFE_BIN_NAME}
.SH DESCRIPTION
${LONG_DESCRIPTION}
.SH OPTIONS
Launch from application menu or command line.
.SH AUTHOR
Written by ${MAINTAINER} <${EMAIL}>
.SH COPYRIGHT
Copyright © $(date +%Y) ${MAINTAINER}. License: MIT
.SH SEE ALSO
Project homepage: https://github.com/Sarwarhridoy4/youvideo-downloader
MANPAGE

gzip -9 "$DEB_DIR/usr/share/man/man1/${SAFE_BIN_NAME}.1"

# Calculate installed size
INSTALLED_SIZE=$(du -sk "$DEB_DIR" | cut -f1)

# Create control file with proper dependencies
print_step "Creating package metadata..."
cat > "$DEB_DIR/DEBIAN/control" << CONTROL_FILE
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: video
Priority: optional
Architecture: amd64
Installed-Size: ${INSTALLED_SIZE}
Depends: libc6 (>= 2.27), libglib2.0-0 (>= 2.56), libx11-6, libxcb1, libxext6, libxrender1, libxinerama1, libxi6, libxrandr2, libxcursor1, libxcomposite1, libxdamage1, libxfixes3, libdbus-1-3, libfontconfig1, libfreetype6, python3 (>= 3.8)
Recommends: ffmpeg, libavcodec-extra, yt-dlp, python3-pyqt6
Suggests: atomicparsley
Maintainer: ${MAINTAINER} <${EMAIL}>
Homepage: https://github.com/Sarwarhridoy4/youvideo-downloader
Description: ${DESCRIPTION}
 ${LONG_DESCRIPTION}
 .
 Key Features:
  * Modern PyQt6 user interface with dark/light themes
  * Download videos from YouTube, Facebook, and other platforms
  * Automatic ffmpeg detection and installation
  * Multiple video/audio format options
  * MP3 audio extraction support
  * Playlist download with range selection
  * Real-time progress tracking
  * Custom output folder selection
  * Automatic audio/video merging
  * Neumorphism-inspired modern UI design
 .
 Perfect for content creators, educators, researchers, and media enthusiasts
 who need reliable video downloading capabilities.
CONTROL_FILE

# Create copyright file
cat > "$DEB_DIR/usr/share/doc/${PACKAGE_NAME}/copyright" << COPYRIGHT_FILE
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: ${APP_NAME}
Upstream-Contact: ${MAINTAINER} <${EMAIL}>
Source: https://github.com/Sarwarhridoy4/youvideo-downloader

Files: *
Copyright: $(date +%Y) ${MAINTAINER}
License: MIT
 MIT License
 .
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
COPYRIGHT_FILE

# Create changelog
cat > "$DEB_DIR/usr/share/doc/${PACKAGE_NAME}/changelog.Debian" << CHANGELOG
${PACKAGE_NAME} (${VERSION}) unstable; urgency=medium

  * Release version ${VERSION}
  * Professional Debian packaging with full metadata
  * Complete icon integration with hicolor theme
  * FreeDesktop-compliant desktop entry
  * Proper dependency management
  * Man page documentation
  * Improved ffmpeg integration
  * Enhanced UI/UX with modern themes

 -- ${MAINTAINER} <${EMAIL}>  $(date -R)
CHANGELOG

gzip -9 "$DEB_DIR/usr/share/doc/${PACKAGE_NAME}/changelog.Debian"

# Create postinst script
print_step "Creating post-installation scripts..."
cat > "$DEB_DIR/DEBIAN/postinst" << 'POSTINST'
#!/bin/bash
set -e

if [ "$1" = "configure" ]; then
    # Update icon cache for all sizes
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
    fi
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database -q /usr/share/applications 2>/dev/null || true
    fi
    
    # Update mime database
    if command -v update-mime-database >/dev/null 2>&1; then
        update-mime-database /usr/share/mime 2>/dev/null || true
    fi
    
    echo "YouVideo Downloader installed successfully!"
    echo "Launch from your application menu or run: youvideo-downloader"
fi

exit 0
POSTINST

chmod 755 "$DEB_DIR/DEBIAN/postinst"

# Create postrm script
cat > "$DEB_DIR/DEBIAN/postrm" << 'POSTRM'
#!/bin/bash
set -e

if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    # Update icon cache
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
    fi
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database -q /usr/share/applications 2>/dev/null || true
    fi
    
    # Update mime database
    if command -v update-mime-database >/dev/null 2>&1; then
        update-mime-database /usr/share/mime 2>/dev/null || true
    fi
fi

exit 0
POSTRM

chmod 755 "$DEB_DIR/DEBIAN/postrm"

# Build .deb package
print_step "Building .deb package..."
DEB_OUTPUT="${BUILD_DIR}/${PACKAGE_NAME}_${VERSION}_amd64.deb"
fakeroot dpkg-deb --build "$DEB_DIR" "$DEB_OUTPUT" > /dev/null 2>&1

# Verify package
print_step "Verifying .deb package..."
if dpkg-deb -I "$DEB_OUTPUT" > /dev/null 2>&1; then
    print_success ".deb package created successfully"
    DEB_SIZE=$(du -h "$DEB_OUTPUT" | cut -f1)
    echo -e "  ${MAGENTA}Package:${NC} $DEB_OUTPUT"
    echo -e "  ${MAGENTA}Size:${NC} ${DEB_SIZE}"
    
    # Run lintian if available
    if check_command lintian; then
        print_step "Running lintian checks..."
        lintian "$DEB_OUTPUT" 2>&1 | head -20 || true
    fi
else
    print_error ".deb package verification failed"
    exit 1
fi

echo

# ══════════════════════════════════════════════════════════════════════════════
#                               BUILD AppImage
# ══════════════════════════════════════════════════════════════════════════════

print_header "Building AppImage"

print_step "Creating AppDir structure..."
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/lib"

# Copy application
print_step "Copying application files..."
cp -r "${SPEC_OUTPUT_DIR}/"* "$APPDIR/usr/bin/"
chmod 755 "$APPDIR/usr/bin/${LINUX_BINARY}"

# Create AppRun launcher
print_step "Creating AppRun launcher..."
cat > "$APPDIR/AppRun" << 'APPRUN'
#!/bin/bash
# YouVideo Downloader AppImage launcher

SELF=$(readlink -f "$0")
HERE=${SELF%/*}

# Set up environment
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONHOME="${HERE}/usr"
export PYTHONPATH="${HERE}/usr/lib:${PYTHONPATH}"

# Change to app directory
cd "${HERE}/usr/bin"

# Execute application
exec "${HERE}/usr/bin/LINUX_BINARY" "$@"
APPRUN

sed -i "s/LINUX_BINARY/${LINUX_BINARY}/g" "$APPDIR/AppRun"
chmod 755 "$APPDIR/AppRun"

# Desktop entry for AppImage
cat > "$APPDIR/${APP_NAME}.desktop" << DESKTOP_ENTRY
[Desktop Entry]
Version=1.1
Type=Application
Name=${APP_NAME}
GenericName=Video Downloader
Comment=${DESCRIPTION}
Exec=${LINUX_BINARY}
Icon=${APP_ID}
Terminal=false
Categories=${CATEGORIES}
DESKTOP_ENTRY

cp "$APPDIR/${APP_NAME}.desktop" "$APPDIR/usr/share/applications/"

# Copy icons
if [ -f "$ICON_DIR/icon_256x256.png" ]; then
    cp "$ICON_DIR/icon_256x256.png" "$APPDIR/${APP_ID}.png"
    cp "$ICON_DIR/icon_256x256.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_ID}.png"
else
    cp "$ICON_SOURCE" "$APPDIR/${APP_ID}.png"
    cp "$ICON_SOURCE" "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_ID}.png"
fi

# Build AppImage
print_step "Building AppImage with linuxdeploy..."
APPIMAGE_OUTPUT="${BUILD_DIR}/${APP_NAME}-${VERSION}-x86_64.AppImage"

./linuxdeploy-x86_64.AppImage \
    --appdir="$APPDIR" \
    --desktop-file="$APPDIR/${APP_NAME}.desktop" \
    --icon-file="$ICON_SOURCE" \
    --output appimage 2>&1 | grep -v "WARNING" || true

# Move and rename AppImage
if [ -f ./*.AppImage ]; then
    mv ./*.AppImage "$APPIMAGE_OUTPUT"
    chmod +x "$APPIMAGE_OUTPUT"
    print_success "AppImage created successfully"
    APPIMAGE_SIZE=$(du -h "$APPIMAGE_OUTPUT" | cut -f1)
    echo -e "  ${MAGENTA}AppImage:${NC} $APPIMAGE_OUTPUT"
    echo -e "  ${MAGENTA}Size:${NC} ${APPIMAGE_SIZE}"
else
    print_error "AppImage creation failed"
    exit 1
fi

echo

# ══════════════════════════════════════════════════════════════════════════════
#                               FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

print_header "Build Complete! 🎉"

echo -e "${GREEN}✨ Successfully created Linux packages:${NC}"
echo
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "${YELLOW}📦 Debian Package (.deb)${NC}"
echo -e "   Location: ${MAGENTA}${DEB_OUTPUT}${NC}"
echo -e "   Size: ${DEB_SIZE}"
echo
echo -e "   ${GREEN}Installation:${NC}"
echo -e "   ${BLUE}sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_amd64.deb${NC}"
echo -e "   ${BLUE}sudo apt --fix-broken install${NC}  ${YELLOW}# If dependencies missing${NC}"
echo
echo -e "   ${GREEN}After Installation:${NC}"
echo -e "   • Find in application menu: ${MAGENTA}${APP_NAME}${NC}"
echo -e "   • Or run in terminal: ${MAGENTA}${SAFE_BIN_NAME}${NC}"
echo
echo -e "   ${GREEN}Uninstall:${NC}"
echo -e "   ${BLUE}sudo apt remove ${PACKAGE_NAME}${NC}"
echo
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "${YELLOW}📦 AppImage (Portable)${NC}"
echo -e "   Location: ${MAGENTA}${APPIMAGE_OUTPUT}${NC}"
echo -e "   Size: ${APPIMAGE_SIZE}"
echo
echo -e "   ${GREEN}Usage:${NC}"
echo -e "   ${BLUE}chmod +x ${APP_NAME}-${VERSION}-x86_64.AppImage${NC}"
echo -e "   ${BLUE}./${APP_NAME}-${VERSION}-x86_64.AppImage${NC}"
echo
echo -e "   ${GREEN}Integration (Optional):${NC}"
echo -e "   • Install AppImageLauncher for desktop integration"
echo -e "   • Or use: ${BLUE}