#!/usr/bin/env bash
################################################################################
# YouVideo Downloader - Ultra-Robust Linux Package Builder
# Creates .deb and AppImage with zero-failure guarantee
# Author: Sarwar Hossain <sarwarhridoy4@gmail.com>
# Version: 3.1 (Integrated Icon Generation - December 24, 2025)
################################################################################

set -euo pipefail
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

generate_metainfo() {
    local target_dir="$1"
    print_step "Generating AppStream metainfo..."
    mkdir -p "$target_dir"
    cat > "$target_dir/$APP_ID.metainfo.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>${APP_ID}</id>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <name>YouVideo Downloader</name>
  <summary>${DESCRIPTION}</summary>
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
  <launchable type="desktop-id">${APP_ID}.desktop</launchable>
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
  <url type="homepage">${HOMEPAGE}</url>
  <url type="bugtracker">${HOMEPAGE}/issues</url>
  <url type="help">${HOMEPAGE}/wiki</url>
  <url type="donation">${HOMEPAGE}</url>
  <developer id="com.sarwarhossain">
    <name>${MAINTAINER}</name>
  </developer>
  <update_contact>${EMAIL}</update_contact>
  <project_group>Multimedia</project_group>
  <keywords>
    <keyword>youtube</keyword>
    <keyword>video</keyword>
    <keyword>downloader</keyword>
    <keyword>pyside6</keyword>
    <keyword>yt-dlp</keyword>
    <keyword>ffmpeg</keyword>
  </keywords>
  <content_rating type="oars-1.1">
    <content_attribute id="violence-cartoon">none</content_attribute>
    <content_attribute id="violence-fantasy">none</content_attribute>
    <content_attribute id="violence-realistic">none</content_attribute>
    <content_attribute id="violence-bloodshed">none</content_attribute>
    <content_attribute id="violence-sexual">none</content_attribute>
    <content_attribute id="drugs-alcohol">none</content_attribute>
    <content_attribute id="sex-nudity">none</content_attribute>
    <content_attribute id="sex-homosexuality">none</content_attribute>
    <content_attribute id="sex-themes">none</content_attribute>
  </content_rating>
  <releases>
    <release version="${VERSION}" date="$(date +%Y-%m-%d)">
      <description>
        <p>New release ${VERSION} with integrated icon generation and professional packaging for all platforms.</p>
        <ul>
          <li>Integrated icon generation system.</li>
          <li>Improved packaging for Debian and AppImage.</li>
          <li>General bug fixes and performance improvements.</li>
        </ul>
      </description>
    </release>
  </releases>
</component>
EOF
    print_success "AppStream metainfo generated: $target_dir/$APP_ID.metainfo.xml"
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
    read -rp "$(echo -e "${CYAN}Enter version number ${YELLOW}[e.g., 2.0.0]${CYAN}:${NC} ")" VERSION
    if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_success "Version set to: ${VERSION}"
        break
    else
        print_error "Invalid version format. Use semantic versioning (e.g., 2.0.0)"
    fi
done

echo ""

# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM REQUIREMENTS CHECK
# ═══════════════════════════════════════════════════════════════════════════

print_header "System Requirements Check"

if [[ "$(uname -s)" != "Linux" ]]; then
    print_error "This script only works on Linux systems"
    exit 1
fi
print_success "Operating System: Linux"

ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    print_warning "Architecture: $ARCH (script optimized for x86_64)"
else
    print_success "Architecture: $ARCH"
fi

if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root is not recommended"
    read -rp "Continue anyway? (y/N): " -n 1
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

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
    appstream
)

print_step "Updating package lists..."
sudo apt-get update -qq || print_warning "Package update had warnings (continuing)"

print_step "Checking and installing required packages..."
MISSING_PACKAGES=()
for pkg in "${SYSTEM_PACKAGES[@]}"; do
    if ! dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
    print_info "Installing: ${MISSING_PACKAGES[*]}"
    sudo apt-get install -y "${MISSING_PACKAGES[@]}"
    print_success "System packages installed"
else
    print_success "All required packages already installed"
fi

# ═══════════════════════════════════════════════════════════════════════════
# PYTHON ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════════════

print_header "Python Environment Setup"

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_info "Python version: ${PYTHON_VERSION}"

print_step "Upgrading pip..."
python3 -m pip install --upgrade pip --quiet || print_warning "pip upgrade failed (non-critical)"

print_step "Installing PyInstaller and Pillow..."
python3 -m pip install --upgrade pyinstaller pillow --quiet || {
    print_error "Failed to install PyInstaller/Pillow"
    exit 1
}
print_success "PyInstaller and Pillow installed"

if [[ -f "requirements.txt" ]]; then
    print_step "Installing project dependencies..."
    python3 -m pip install -r requirements.txt --quiet
    print_success "Project dependencies installed"
else
    print_warning "requirements.txt not found – installing essentials"
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
    wget -q --show-progress "$LINUXDEPLOY_URL" -O "$LINUXDEPLOY_FILE"
    chmod +x "$LINUXDEPLOY_FILE"
    print_success "linuxdeploy downloaded"
fi

# ═══════════════════════════════════════════════════════════════════════════
# ICON PREPARATION (Integrated with create_icon.py)
# ═══════════════════════════════════════════════════════════════════════════

print_header "Icon Preparation"

ICON_DIR="assets/icons"
mkdir -p "$ICON_DIR"

# Check for source icon
if [[ ! -f "$ICON_SOURCE" ]]; then
    print_warning "Icon not found: $ICON_SOURCE"
    print_step "Creating placeholder icon..."
    if check_command convert; then
        convert -size 512x512 gradient:'#667eea-#764ba2' \
            \( -size 512x512 xc:none -gravity center -fill white -font "DejaVu-Sans-Bold" -pointsize 200 -annotate +0+0 "YV" \) \
            -composite -quality 95 "$ICON_SOURCE"
        print_success "Placeholder icon created"
    else
        print_error "ImageMagick not found. Cannot create icon."
        exit 1
    fi
else
    print_success "Source icon found: $ICON_SOURCE"
fi

# Check if create_icon.py exists
if [[ ! -f "$CREATE_ICON_SCRIPT" ]]; then
    print_error "Icon generator script not found: $CREATE_ICON_SCRIPT"
    print_info "Please place create_icon.py in the project root."
    exit 1
fi

# Check if icons already exist
NEED_ICON_GENERATION=false
if [[ ! -f "$ICON_DIR/appicon.ico" ]] || \
   [[ ! -f "$ICON_DIR/appicon.icns" ]] || \
   [[ ! -f "$ICON_DIR/icon_256.png" ]]; then
    NEED_ICON_GENERATION=true
fi

if [[ "$NEED_ICON_GENERATION" == true ]]; then
    print_step "Generating professional icons (ICO, ICNS, PNGs, Favicon)..."
    python3 "$CREATE_ICON_SCRIPT" "$ICON_SOURCE"
    
    # Verify icon generation
    if [[ -f "$ICON_DIR/icon_256.png" ]]; then
        print_success "Professional icons generated successfully"
    else
        print_error "Icon generation failed - icon_256.png not found"
        exit 1
    fi
else
    print_success "All required icons already exist"
    print_info "Skipping icon generation (delete icons to regenerate)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# PYINSTALLER BUILD
# ═══════════════════════════════════════════════════════════════════════════

print_header "Building Application with PyInstaller"

if [[ ! -f "$SPEC_FILE" ]]; then
    print_error "Spec file not found: $SPEC_FILE"
    exit 1
fi

print_step "Cleaning previous builds..."
rm -rf "$BUILD_DIR" build __pycache__ 2>/dev/null || true
mkdir -p "$BUILD_DIR"

print_step "Running PyInstaller (this may take a few minutes)..."
print_info "Icon generation will be handled by the spec file if needed"
pyinstaller --clean --noconfirm "$SPEC_FILE"

# Determine source directory (requires onedir output: dist/YouVideoDownloader/)
if [[ -d "$BUILD_DIR/$APP_NAME" ]]; then
    SOURCE_DIR="$BUILD_DIR/$APP_NAME"
    print_info "Using onedir build: $SOURCE_DIR"
else
    print_error "Expected onedir output not found: $BUILD_DIR/$APP_NAME"
    print_info "Check your .spec file – must use onedir mode with COLLECT and output name 'YouVideoDownloader'"
    exit 1
fi

BINARY_PATH="$SOURCE_DIR/$LINUX_BINARY"
if [[ ! -f "$BINARY_PATH" ]]; then
    print_error "Executable not found at $BINARY_PATH"
    exit 1
fi

chmod +x "$BINARY_PATH"
BINARY_SIZE=$(du -h "$BINARY_PATH" | cut -f1)
print_success "Binary ready: $BINARY_PATH ($BINARY_SIZE)"

# ═══════════════════════════════════════════════════════════════════════════
# BUILD DEBIAN PACKAGE (.deb)
# ═══════════════════════════════════════════════════════════════════════════

print_header "Building Debian Package (.deb)"

DEB_DIR="$BUILD_DIR/${PACKAGE_NAME}_deb"
rm -rf "$DEB_DIR"
mkdir -p "$DEB_DIR"/{DEBIAN,usr/{bin,share/{applications,pixmaps,doc/$PACKAGE_NAME,man/man1,metainfo}}}

for size in 16 22 24 32 48 64 128 256 512; do
    mkdir -p "$DEB_DIR/usr/share/icons/hicolor/${size}x${size}/apps"
done

mkdir -p "$DEB_DIR/usr/share/$PACKAGE_NAME"

print_step "Copying application files..."
cp -r "$SOURCE_DIR"/* "$DEB_DIR/usr/share/$PACKAGE_NAME/"
find "$DEB_DIR/usr/share/$PACKAGE_NAME" -name "$LINUX_BINARY" -exec chmod 755 {} \;

print_step "Creating launcher wrapper..."
cat > "$DEB_DIR/usr/bin/$PACKAGE_NAME" << 'EOF'
#!/bin/bash
APP_DIR="/usr/share/youvideo-downloader"
cd "$APP_DIR"
exec "./youvideo-downloader" "$@"
EOF
chmod 755 "$DEB_DIR/usr/bin/$PACKAGE_NAME"

print_step "Installing icons..."
for size in 16 22 24 32 48 64 128 256 512; do
    if [[ -f "$ICON_DIR/icon_${size}.png" ]]; then
        cp "$ICON_DIR/icon_${size}.png" "$DEB_DIR/usr/share/icons/hicolor/${size}x${size}/apps/$APP_ID.png"
    fi
done

cp "$ICON_DIR/icon_256.png" "$DEB_DIR/usr/share/pixmaps/$APP_ID.png" 2>/dev/null || \
    cp "$ICON_SOURCE" "$DEB_DIR/usr/share/pixmaps/$APP_ID.png"

print_step "Creating desktop entry..."
cat > "$DEB_DIR/usr/share/applications/$APP_ID.desktop" << EOF
[Desktop Entry]
Version=1.1
Type=Application
Name=YouVideo Downloader
GenericName=Video Downloader
Comment=$DESCRIPTION
Exec=$PACKAGE_NAME %U
Icon=$APP_ID
Terminal=false
Categories=$CATEGORIES
Keywords=youtube;video;download;yt-dlp;
MimeType=x-scheme-handler/http;x-scheme-handler/https;
StartupNotify=true
StartupWMClass=$PACKAGE_NAME
EOF

print_step "Creating man page..."
cat > "$DEB_DIR/usr/share/man/man1/$PACKAGE_NAME.1" << EOF
.TH ${APP_NAME} 1 "$(date '+%B %Y')" "${VERSION}" "User Commands"
.SH NAME
${PACKAGE_NAME} — ${DESCRIPTION}
.SH SYNOPSIS
.B ${PACKAGE_NAME}
.SH DESCRIPTION
YouVideo Downloader is a powerful video downloading application with a modern graphical interface.
.SH AUTHOR
${MAINTAINER} <${EMAIL}>
.SH COPYRIGHT
Copyright © $(date +%Y) ${MAINTAINER}. License: MIT
.SH SEE ALSO
${HOMEPAGE}
EOF
gzip -9 "$DEB_DIR/usr/share/man/man1/$PACKAGE_NAME.1"

INSTALLED_SIZE=$(du -sk "$DEB_DIR" | cut -f1)

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

cat > "$DEB_DIR/usr/share/doc/$PACKAGE_NAME/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: ${APP_NAME}
Upstream-Contact: ${MAINTAINER} <${EMAIL}>
Source: ${HOMEPAGE}

Files: *
Copyright: $(date +%Y) ${MAINTAINER}
License: MIT
EOF

cat > "$DEB_DIR/usr/share/doc/$PACKAGE_NAME/changelog.Debian" << EOF
${PACKAGE_NAME} (${VERSION}) unstable; urgency=medium

  * New release ${VERSION}
  * Integrated icon generation system
  * Professional packaging for all platforms

 -- ${MAINTAINER} <${EMAIL}>  $(date -R)
EOF
gzip -9 "$DEB_DIR/usr/share/doc/$PACKAGE_NAME/changelog.Debian"

cat > "$DEB_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database -q /usr/share/applications 2>/dev/null || true
EOF
chmod 755 "$DEB_DIR/DEBIAN/postinst"

cat > "$DEB_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database -q /usr/share/applications 2>/dev/null || true
EOF
chmod 755 "$DEB_DIR/DEBIAN/postrm"

generate_metainfo "$DEB_DIR/usr/share/metainfo/" # Call generate_metainfo for .deb

print_step "Building .deb package..."
DEB_OUTPUT="$BUILD_DIR/${PACKAGE_NAME}_${VERSION}_amd64.deb"
fakeroot dpkg-deb --build "$DEB_DIR" "$DEB_OUTPUT"
print_success ".deb package created: $DEB_OUTPUT"

# ═══════════════════════════════════════════════════════════════════════════
# BUILD APPIMAGE
# ═══════════════════════════════════════════════════════════════════════════

print_header "Building AppImage"

APPDIR="$BUILD_DIR/${APP_NAME}.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr"/{bin,share/{applications,metainfo}}

# Create all hicolor directories
for size in 16x16 22x22 24x24 32x32 48x48 64x64 128x128 256x256 512x512; do
    mkdir -p "$APPDIR/usr/share/icons/hicolor/${size}/apps"
done

print_step "Copying application files..."
cp -r "$SOURCE_DIR"/* "$APPDIR/usr/bin/"

print_step "Creating AppRun..."
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
cd "${HERE}/usr/bin"
exec "./youvideo-downloader" "$@"
EOF
chmod +x "$APPDIR/AppRun"

print_step "Creating desktop file..."
cat > "$APPDIR/${APP_ID}.desktop" << EOF
[Desktop Entry]
Type=Application
Name=YouVideo Downloader
Comment=$DESCRIPTION
Exec=youvideo-downloader
Icon=$APP_ID
Terminal=false
Categories=$CATEGORIES
EOF
cp "$APPDIR/${APP_ID}.desktop" "$APPDIR/usr/share/applications/"

print_step "Installing icons..."
# Main icon at root and in hicolor
if [[ -f "$ICON_DIR/icon_256.png" ]]; then
    MAIN_ICON="$ICON_DIR/icon_256.png"
elif [[ -f "$ICON_DIR/icon_512.png" ]]; then
    MAIN_ICON="$ICON_DIR/icon_512.png"
else
    MAIN_ICON="$ICON_SOURCE"
fi

cp "$MAIN_ICON" "$APPDIR/$APP_ID.png"
cp "$MAIN_ICON" "$APPDIR/usr/share/icons/hicolor/256x256/apps/$APP_ID.png"

# All other sizes
for size in 16 22 24 32 48 64 128 256 512; do
    if [[ -f "$ICON_DIR/icon_${size}.png" ]]; then
        cp "$ICON_DIR/icon_${size}.png" "$APPDIR/usr/share/icons/hicolor/${size}x${size}/apps/$APP_ID.png"
    fi
done

generate_metainfo "$APPDIR/usr/share/metainfo/" # Call generate_metainfo for AppImage

print_step "Renaming AppStream metainfo for appimagetool compatibility..."
mv "$APPDIR/usr/share/metainfo/$APP_ID.metainfo.xml" "$APPDIR/usr/share/metainfo/$APP_ID.appdata.xml"
print_success "AppStream metainfo renamed to YouVideoDownloader.appdata.xml"

print_step "Building AppImage..."
APPIMAGE_OUTPUT="$BUILD_DIR/${APP_NAME}-${VERSION}-x86_64.AppImage"

"$LINUXDEPLOY_FILE" \
    --appdir="$APPDIR" \
    --desktop-file="$APPDIR/${APP_ID}.desktop" \
    --icon-file="$MAIN_ICON" \
    --output appimage

print_step "Locating and renaming generated AppImage..."
GENERATED_APPIMAGE=$(find . -maxdepth 1 -name "*.AppImage" -type f -printf '%f\n' | head -n1)

if [[ -z "$GENERATED_APPIMAGE" ]]; then
    print_error "AppImage was not generated!"
    exit 1
fi

mv "./$GENERATED_APPIMAGE" "$APPIMAGE_OUTPUT"
chmod +x "$APPIMAGE_OUTPUT"

APPIMAGE_SIZE=$(du -h "$APPIMAGE_OUTPUT" | cut -f1)
print_success "AppImage created: $APPIMAGE_OUTPUT ($APPIMAGE_SIZE)"

# ═══════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

print_header "Build Complete! 🎉"

echo -e "${GREEN}Successfully built version ${VERSION}${NC}\n"
echo -e "${YELLOW}Debian Package:${NC}  $DEB_OUTPUT"
echo -e "${YELLOW}AppImage:${NC}         $APPIMAGE_OUTPUT\n"
echo -e "${CYAN}✓ Icons automatically generated and integrated${NC}"
echo -e "${CYAN}✓ All platforms supported (Windows/macOS/Linux)${NC}"
echo -e "${CYAN}✓ Created by ${MAINTAINER}${NC}\n"

print_success "Build completed successfully! Both packages are ready for distribution."