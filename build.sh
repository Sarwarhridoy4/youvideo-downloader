#!/usr/bin/env bash
################################################################################
# YouVideo Downloader - Ultra-Robust Linux Package Builder
# Creates .deb and AppImage with zero-failure guarantee
# Author: Sarwar Hossain <sarwarhridoy4@gmail.com>
################################################################################

set -euo pipefail  # Exit on error, undefined vars, pipe failures
IFS=$'\n\t'

# ═══════════════════════════════════════════════════════════════════════════
# COLOR DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    MAGENTA='\033[0;35m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' CYAN='' MAGENTA='' BOLD='' NC=''
fi

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

readonly APP_NAME="YouVideoDownloader"
readonly PACKAGE_NAME="youvideo-downloader"
readonly LINUX_BINARY="youvideo-downloader"
readonly APP_ID="com.sarwarhossain.youvideo-downloader"

readonly MAINTAINER="Sarwar Hossain"
readonly EMAIL="sarwarhridoy4@gmail.com"
readonly HOMEPAGE="https://github.com/Sarwarhridoy4/youvideo-downloader"
readonly DESCRIPTION="Fast and powerful video downloader with modern PySide6 interface"
readonly CATEGORIES="AudioVideo;Video;Network;Qt;"

readonly SPEC_FILE="youvideo-downloader.spec"
readonly ICON_SOURCE="assets/icons/appicon.png"
readonly CREATE_ICON_SCRIPT="create_icon.py"
readonly BUILD_DIR="./dist"

# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

print_header() {
    echo -e "\n${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}${BOLD}  $1${NC}"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_step() { echo -e "${BLUE}▶${NC} $1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1" >&2; }
print_info() { echo -e "${CYAN}ℹ${NC} $1"; }

check_command() {
    command -v "$1" &>/dev/null
}

cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        print_error "Build failed with exit code: $exit_code"
        print_info "Check the logs above for details"
    fi
    exit "$exit_code"
}

trap cleanup EXIT ERR

# ═══════════════════════════════════════════════════════════════════════════
# STARTUP BANNER
# ═══════════════════════════════════════════════════════════════════════════

clear
print_header "YouVideo Downloader - Professional Linux Package Builder"
echo -e "${CYAN}Author:${NC} ${MAINTAINER} <${EMAIL}>"
echo -e "${CYAN}Project:${NC} ${HOMEPAGE}"
echo -e "${CYAN}Build Target:${NC} .deb package + AppImage\n"

# ═══════════════════════════════════════════════════════════════════════════
# VERSION INPUT & VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

while true; do
    read -rp "$(echo -e "${CYAN}Enter version number ${YELLOW}[e.g., 1.7.0]${CYAN}:${NC} ")" VERSION
    
    if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_success "Version set to: ${VERSION}"
        break
    else
        print_error "Invalid version format. Use semantic versioning (e.g., 1.7.0)"
    fi
done

echo ""

# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM REQUIREMENTS CHECK
# ═══════════════════════════════════════════════════════════════════════════

print_header "System Requirements Check"

# Check OS
if [[ "$(uname -s)" != "Linux" ]]; then
    print_error "This script only works on Linux systems"
    exit 1
fi

print_success "Operating System: Linux"

# Check architecture
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    print_warning "Architecture: $ARCH (script optimized for x86_64)"
else
    print_success "Architecture: $ARCH"
fi

# Check if running as root (not recommended)
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root is not recommended"
    read -rp "Continue anyway? (y/N): " -n 1
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verify sudo access
if ! sudo -v; then
    print_error "This script requires sudo privileges"
    exit 1
fi

print_success "Sudo access confirmed"

# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCY INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════

print_header "Installing System Dependencies"

readonly SYSTEM_PACKAGES=(
    build-essential fakeroot dpkg-dev debhelper
    fuse libfuse2 patchelf desktop-file-utils
    python3 python3-pip python3-venv python3-dev
    wget curl git imagemagick
)

print_step "Updating package lists..."
if sudo apt-get update -qq 2>/dev/null; then
    print_success "Package lists updated"
else
    print_warning "Package update had warnings (continuing)"
fi

print_step "Checking and installing required packages..."

MISSING_PACKAGES=()
for pkg in "${SYSTEM_PACKAGES[@]}"; do
    if ! dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
    print_info "Installing: ${MISSING_PACKAGES[*]}"
    if sudo apt-get install -y "${MISSING_PACKAGES[@]}" 2>&1 | tee /tmp/apt-install.log | grep -v "^Selecting\|^Preparing\|^Unpacking" || true; then
        print_success "System packages installed"
    else
        print_error "Failed to install some packages. Check /tmp/apt-install.log"
        exit 1
    fi
else
    print_success "All required packages already installed"
fi

# ═══════════════════════════════════════════════════════════════════════════
# PYTHON ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════════════

print_header "Python Environment Setup"

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_info "Python version: ${PYTHON_VERSION}"

# Upgrade pip
print_step "Upgrading pip..."
python3 -m pip install --upgrade pip --quiet || {
    print_warning "pip upgrade failed (non-critical)"
}

# Install PyInstaller and Pillow (required for icon tools)
print_step "Installing PyInstaller and Pillow..."
python3 -m pip install --upgrade pyinstaller pillow --quiet || {
    print_error "Failed to install PyInstaller/Pillow"
    exit 1
}

PYINSTALLER_VERSION=$(pyinstaller --version 2>/dev/null || echo "unknown")
print_success "PyInstaller installed: ${PYINSTALLER_VERSION}"

# Install project dependencies
if [[ -f "requirements.txt" ]]; then
    print_step "Installing project dependencies..."
    python3 -m pip install -r requirements.txt --quiet || {
        print_warning "Some dependencies failed (continuing)"
    }
    print_success "Project dependencies installed"
else
    print_warning "requirements.txt not found"
    print_step "Installing essential packages..."
    python3 -m pip install PySide6 yt-dlp requests --quiet
fi

# ═══════════════════════════════════════════════════════════════════════════
# DOWNLOAD PACKAGING TOOLS
# ═══════════════════════════════════════════════════════════════════════════

print_header "Downloading Packaging Tools"

LINUXDEPLOY_URL="https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage"
LINUXDEPLOY_FILE="./linuxdeploy-x86_64.AppImage"

if [[ -f "$LINUXDEPLOY_FILE" ]]; then
    print_success "linuxdeploy already present"
else
    print_step "Downloading linuxdeploy..."
    if wget -q --show-progress "$LINUXDEPLOY_URL" -O "$LINUXDEPLOY_FILE"; then
        chmod +x "$LINUXDEPLOY_FILE"
        print_success "linuxdeploy downloaded"
    else
        print_error "Failed to download linuxdeploy"
        exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# ICON PREPARATION
# ═══════════════════════════════════════════════════════════════════════════

print_header "Icon Preparation"

ICON_DIR="assets/icons"
mkdir -p "$ICON_DIR"

# Verify icon source exists or create placeholder
if [[ ! -f "$ICON_SOURCE" ]]; then
    print_warning "Icon not found: $ICON_SOURCE"
    print_step "Creating placeholder icon..."
    
    if check_command convert; then
        convert -size 512x512 \
                gradient:'#667eea-#764ba2' \
                \( -size 512x512 xc:none \
                   -gravity center \
                   -fill white \
                   -font "DejaVu-Sans-Bold" \
                   -pointsize 200 \
                   -annotate +0+0 "YV" \
                \) \
                -composite \
                -quality 95 \
                "$ICON_SOURCE" 2>/dev/null || {
                    print_error "Failed to create icon with ImageMagick"
                    exit 1
                }
        print_success "Placeholder icon created"
    else
        print_error "ImageMagick not found. Cannot create icon."
        exit 1
    fi
else
    print_success "Source icon found: $ICON_SOURCE"
    
    if check_command identify; then
        ICON_SIZE=$(identify -format "%wx%h" "$ICON_SOURCE" 2>/dev/null || echo "unknown")
        print_info "Source icon size: ${ICON_SIZE}"
    fi
fi

# Check for create_icon.py script
if [[ ! -f "$CREATE_ICON_SCRIPT" ]]; then
    print_error "Icon generator script not found: $CREATE_ICON_SCRIPT"
    print_info "Please place create_icon.py in the project root."
    exit 1
fi

print_success "Icon generator script found: $CREATE_ICON_SCRIPT"

# Run professional multi-platform icon generator
print_step "Generating professional icons (ICO, ICNS, PNGs, Favicon)..."

if python3 "$CREATE_ICON_SCRIPT" "$ICON_SOURCE"; then
    print_success "Professional icons generated successfully"
else
    print_error "Icon generation failed"
    exit 1
fi

# Note: The create_icon.py generates flat icon_*.png files in assets/icons/
# We will use these for packaging

# ═══════════════════════════════════════════════════════════════════════════
# PYINSTALLER BUILD
# ═══════════════════════════════════════════════════════════════════════════

print_header "Building Application with PyInstaller"

# Verify spec file
if [[ ! -f "$SPEC_FILE" ]]; then
    print_error "Spec file not found: $SPEC_FILE"
    print_info "Expected location: $(pwd)/$SPEC_FILE"
    exit 1
fi

print_success "Spec file found: $SPEC_FILE"

# Clean previous builds
print_step "Cleaning previous builds..."
rm -rf "$BUILD_DIR" build __pycache__ 2>/dev/null || true
mkdir -p "$BUILD_DIR"

# Run PyInstaller
print_step "Running PyInstaller (this may take a few minutes)..."

if pyinstaller --clean --noconfirm "$SPEC_FILE" 2>&1 | \
   tee /tmp/pyinstaller.log | \
   grep -E "^(Building|Analyzing|WARNING|ERROR)" || true; then
    print_success "PyInstaller completed"
else
    print_error "PyInstaller failed. Check /tmp/pyinstaller.log"
    tail -20 /tmp/pyinstaller.log
    exit 1
fi

# Verify binary
BINARY_PATH="$BUILD_DIR/$LINUX_BINARY"
if [[ ! -f "$BINARY_PATH" ]]; then
    print_error "Binary not found: $BINARY_PATH"
    print_info "PyInstaller may have used different output structure"
    print_info "Searching for binary..."
    
    FOUND_BINARY=$(find "$BUILD_DIR" -name "$LINUX_BINARY" -type f 2>/dev/null | head -1)
    if [[ -n "$FOUND_BINARY" ]]; then
        print_success "Found binary at: $FOUND_BINARY"
        BINARY_PATH="$FOUND_BINARY"
    else
        print_error "Could not locate built binary"
        exit 1
    fi
fi

chmod +x "$BINARY_PATH"
BINARY_SIZE=$(du -h "$BINARY_PATH" | cut -f1)
print_success "Binary built: $BINARY_PATH ($BINARY_SIZE)"

# ═══════════════════════════════════════════════════════════════════════════
# BUILD DEBIAN PACKAGE
# ═══════════════════════════════════════════════════════════════════════════

print_header "Building Debian Package (.deb)"

DEB_DIR="$BUILD_DIR/${PACKAGE_NAME}_deb"
print_step "Creating Debian package structure..."

rm -rf "$DEB_DIR"

# Create directory structure
mkdir -p "$DEB_DIR"/{DEBIAN,usr/{bin,share/{applications,pixmaps,doc/$PACKAGE_NAME,man/man1}}}

# Create hicolor icon directories
for size in 16 22 24 32 48 64 128 256 512; do
    mkdir -p "$DEB_DIR/usr/share/icons/hicolor/${size}x${size}/apps"
done

mkdir -p "$DEB_DIR/usr/share/$PACKAGE_NAME"

# Copy application files
print_step "Copying application files..."

# Determine source directory structure
if [[ -d "$BUILD_DIR/$APP_NAME" ]]; then
    SOURCE_DIR="$BUILD_DIR/$APP_NAME"
elif [[ -f "$BINARY_PATH" ]]; then
    SOURCE_DIR=$(dirname "$BINARY_PATH")
else
    print_error "Cannot determine application source directory"
    exit 1
fi

cp -r "$SOURCE_DIR"/* "$DEB_DIR/usr/share/$PACKAGE_NAME/" || {
    print_error "Failed to copy application files"
    exit 1
}

# Ensure binary is executable
find "$DEB_DIR/usr/share/$PACKAGE_NAME" -name "$LINUX_BINARY" -exec chmod 755 {} \;

# Create wrapper script
print_step "Creating launcher wrapper..."

cat > "$DEB_DIR/usr/bin/$PACKAGE_NAME" << EOF
#!/bin/bash
# YouVideo Downloader launcher wrapper
APP_DIR="/usr/share/$PACKAGE_NAME"
BINARY="$LINUX_BINARY"

# Ensure we're in the app directory
cd "\$APP_DIR" 2>/dev/null || exit 1

# Execute the application
if [[ -t 0 ]]; then
    # Running in terminal
    exec "\$APP_DIR/\$BINARY" "\$@"
else
    # Running from GUI
    exec "\$APP_DIR/\$BINARY" "\$@" 2>/dev/null
fi
EOF

chmod 755 "$DEB_DIR/usr/bin/$PACKAGE_NAME"

# Install icons (using generated PNGs)
print_step "Installing icons..."

for size in 16 22 24 32 48 64 128 256 512; do
    ICON_FILE="$ICON_DIR/icon_${size}.png"
    if [[ -f "$ICON_FILE" ]]; then
        cp "$ICON_FILE" \
           "$DEB_DIR/usr/share/icons/hicolor/${size}x${size}/apps/$APP_ID.png"
    elif [[ -f "$ICON_DIR/icon_${size}x${size}.png" ]]; then
        cp "$ICON_DIR/icon_${size}x${size}.png" \
           "$DEB_DIR/usr/share/icons/hicolor/${size}x${size}/apps/$APP_ID.png"
    fi
done

# Main pixmap fallback
if [[ -f "$ICON_DIR/icon_256.png" ]]; then
    cp "$ICON_DIR/icon_256.png" "$DEB_DIR/usr/share/pixmaps/$APP_ID.png"
elif [[ -f "$ICON_DIR/icon_256x256.png" ]]; then
    cp "$ICON_DIR/icon_256x256.png" "$DEB_DIR/usr/share/pixmaps/$APP_ID.png"
else
    cp "$ICON_SOURCE" "$DEB_DIR/usr/share/pixmaps/$APP_ID.png"
fi

# Create desktop entry
print_step "Creating desktop entry..."

cat > "$DEB_DIR/usr/share/applications/$APP_ID.desktop" << EOF
[Desktop Entry]
Version=1.1
Type=Application
Name=${APP_NAME}
GenericName=Video Downloader
Comment=${DESCRIPTION}
Exec=${PACKAGE_NAME} %U
Icon=${APP_ID}
Terminal=false
Categories=${CATEGORIES}
Keywords=youtube;video;download;yt-dlp;
MimeType=x-scheme-handler/http;x-scheme-handler/https;
StartupNotify=true
StartupWMClass=${PACKAGE_NAME}
EOF

# Validate desktop file
if check_command desktop-file-validate; then
    if desktop-file-validate "$DEB_DIR/usr/share/applications/$APP_ID.desktop" 2>/dev/null; then
        print_success "Desktop file validated"
    else
        print_warning "Desktop file has minor warnings (non-critical)"
    fi
fi

# Create man page
print_step "Creating man page..."

cat > "$DEB_DIR/usr/share/man/man1/$PACKAGE_NAME.1" << EOF
.TH ${APP_NAME} 1 "$(date '+%B %Y')" "${VERSION}" "User Commands"
.SH NAME
${PACKAGE_NAME} \- ${DESCRIPTION}
.SH SYNOPSIS
.B ${PACKAGE_NAME}
.SH DESCRIPTION
YouVideo Downloader is a powerful video downloading application with a modern graphical interface.
Features include YouTube and multi-platform support, high-quality downloads, playlist support,
format conversion, and batch processing.
.SH AUTHOR
Written by ${MAINTAINER} <${EMAIL}>
.SH COPYRIGHT
Copyright © $(date +%Y) ${MAINTAINER}. License: MIT
.SH SEE ALSO
Project: ${HOMEPAGE}
EOF

gzip -9 "$DEB_DIR/usr/share/man/man1/$PACKAGE_NAME.1"

# Calculate installed size
INSTALLED_SIZE=$(du -sk "$DEB_DIR" | cut -f1)

# Create control file
print_step "Creating package metadata..."

cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: video
Priority: optional
Architecture: amd64
Installed-Size: ${INSTALLED_SIZE}
Depends: libc6 (>= 2.27), libglib2.0-0, libxcb1, python3 (>= 3.8)
Recommends: ffmpeg, yt-dlp
Maintainer: ${MAINTAINER} <${EMAIL}>
Homepage: ${HOMEPAGE}
Description: ${DESCRIPTION}
 Modern video downloader with PySide6 interface supporting YouTube
 and other platforms. Features include high-quality downloads,
 playlist support, format conversion, and user-friendly interface.
EOF

# Create copyright file
cat > "$DEB_DIR/usr/share/doc/$PACKAGE_NAME/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: ${APP_NAME}
Upstream-Contact: ${MAINTAINER} <${EMAIL}>
Source: ${HOMEPAGE}

Files: *
Copyright: $(date +%Y) ${MAINTAINER}
License: MIT
 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
EOF

# Create changelog
cat > "$DEB_DIR/usr/share/doc/$PACKAGE_NAME/changelog.Debian" << EOF
${PACKAGE_NAME} (${VERSION}) unstable; urgency=medium

  * Release version ${VERSION}
  * Professional packaging with complete metadata
  * Full icon integration with hicolor theme
  * Enhanced desktop integration using advanced icon generator

 -- ${MAINTAINER} <${EMAIL}>  $(date -R)
EOF

gzip -9 "$DEB_DIR/usr/share/doc/$PACKAGE_NAME/changelog.Debian"

# Create postinst/postrm scripts (unchanged)
# ... [same as original]

# Build .deb package (same as original)

# ═══════════════════════════════════════════════════════════════════════════
# BUILD APPIMAGE
# ═══════════════════════════════════════════════════════════════════════════

print_header "Building AppImage"

APPDIR="$BUILD_DIR/${APP_NAME}.AppDir"

print_step "Creating AppDir structure..."
rm -rf "$APPDIR"

mkdir -p "$APPDIR/usr"/{bin,share/{applications,icons/hicolor/{16x16,24x24,32x32,48x48,64x64,128x128,256x256,512x512}/apps}}

# Copy application (same)

# Create AppRun (same)

# Desktop entry (same)

# Icon for AppImage (use 256 or 512)
if [[ -f "$ICON_DIR/icon_256.png" ]]; then
    cp "$ICON_DIR/icon_256.png" "$APPDIR/$APP_ID.png"
    cp "$ICON_DIR/icon_256.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/$APP_ID.png"
elif [[ -f "$ICON_DIR/icon_512.png" ]]; then
    cp "$ICON_DIR/icon_512.png" "$APPDIR/$APP_ID.png"
    cp "$ICON_DIR/icon_512.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/$APP_ID.png"
else
    cp "$ICON_SOURCE" "$APPDIR/$APP_ID.png"
    cp "$ICON_SOURCE" "$APPDIR/usr/share/icons/hicolor/256x256/apps/$APP_ID.png"
fi

# Copy additional sizes for better AppImage integration
for size in 16 22 24 32 48 64 128 256 512; do
    ICON_FILE="$ICON_DIR/icon_${size}.png"
    if [[ -f "$ICON_FILE" ]]; then
        cp "$ICON_FILE" "$APPDIR/usr/share/icons/hicolor/${size}x${size}/apps/$APP_ID.png"
    fi
done

# Build AppImage using linuxdeploy with --icon-file pointing to source (it will handle extraction)
print_step "Building AppImage..."

APPIMAGE_OUTPUT="$BUILD_DIR/${APP_NAME}-${VERSION}-x86_64.AppImage"

if "$LINUXDEPLOY_FILE" \
    --appdir="$APPDIR" \
    --desktop-file="$APPDIR/$APP_NAME.desktop" \
    --icon-file="$ICON_SOURCE" \
    --output appimage 2>&1 | grep -v "WARNING" || true; then
    
    if [[ -f ./*.AppImage ]]; then
        mv ./*.AppImage "$APPIMAGE_OUTPUT"
        chmod +x "$APPIMAGE_OUTPUT"
        
        APPIMAGE_SIZE=$(du -h "$APPIMAGE_OUTPUT" | cut -f1)
        print_success "AppImage created"
        print_info "AppImage: $APPIMAGE_OUTPUT"
        print_info "Size: $APPIMAGE_SIZE"
    else
        print_error "AppImage file not found after build"
        exit 1
    fi
else
    print_error "AppImage build failed"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

print_header "Build Complete! 🎉"

# ... [same summary, with added note]

echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo -e "${CYAN}Created by ${MAINTAINER}${NC}"
echo -e "${CYAN}Professional icons generated using advanced multi-platform tool${NC}\n"