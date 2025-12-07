#!/usr/bin/env bash
# ==============================================================================
# YouVideo Downloader — Professional AppImage Builder
# Version: 2025.12 Enterprise Edition
# Author : Sarwar Hossain <sarwarhridoy4@gmail.com>
# Project: https://github.com/Sarwarhridoy4/youvideo-downloader
# License: MIT
#
# Builds a production-ready AppImage with automatic dependency detection,
# tool installation, and comprehensive error handling.
# ==============================================================================

set -Eeuo pipefail
IFS=$'\n\t'

# ─────────────────────────────── Colors & Logging ─────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'
log()   { echo -e "${GREEN}[+] $1${NC}"; }
warn()  { echo -e "${YELLOW}[!] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}" >&2; exit 1; }

# ──────────────────────────────────  Core Metadata  ───────────────────────────
readonly APP_NAME="youvideo-downloader"
readonly EXECUTABLE="YouVideoDownloader"              # PyInstaller launcher name
readonly VERSION="1.6.2"
ARCH="$(uname -m)"                                    # x86_64, aarch64, etc. (NOT readonly - appimagetool needs it)
readonly DESCRIPTION="Elegant and modern YouTube/Video Downloader with PyQt6"
readonly HOMEPAGE="https://github.com/Sarwarhridoy4/youvideo-downloader"

readonly DIST_DIR="dist/${EXECUTABLE}"                # PyInstaller one-folder bundle
readonly BUILD_DIR="AppDir"
readonly ICON_SRC="assets/icons/appicon.png"          # 256×256 PNG
readonly APPIMAGE_TOOL="appimagetool-${ARCH}.AppImage"
readonly FINAL_IMAGE="${APP_NAME}-${VERSION}-${ARCH}.AppImage"

log "Starting AppImage build for YouVideo Downloader v${VERSION} (${ARCH})"

# ───────────────────────────  Install Missing Dependencies  ──────────────────
install_dependencies() {
    local missing_tools=()
    
    # Check for required commands
    command -v curl >/dev/null 2>&1 || missing_tools+=("curl")
    command -v file >/dev/null 2>&1 || missing_tools+=("file")
    command -v desktop-file-validate >/dev/null 2>&1 || missing_tools+=("desktop-file-utils")
    
    # Check for FUSE (required for appimagetool)
    if [[ ! -e /dev/fuse ]] && ! ldconfig -p | grep -q libfuse.so.2; then
        if command -v apt-get >/dev/null 2>&1; then
            missing_tools+=("libfuse2")
        elif command -v dnf >/dev/null 2>&1; then
            missing_tools+=("fuse-libs")
        elif command -v pacman >/dev/null 2>&1; then
            missing_tools+=("fuse2")
        fi
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log "Installing missing dependencies: ${missing_tools[*]}"
        
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update -qq
            sudo apt-get install -y "${missing_tools[@]}"
        elif command -v dnf >/dev/null 2>&1; then
            sudo dnf install -y "${missing_tools[@]}"
        elif command -v pacman >/dev/null 2>&1; then
            sudo pacman -S --noconfirm "${missing_tools[@]}"
        else
            warn "Could not detect package manager. Please install manually: ${missing_tools[*]}"
        fi
    fi
}

install_dependencies

# ─────────────────────────  Verify PyInstaller Output Exists  ────────────────
if [[ ! -d "${DIST_DIR}" ]]; then
    error "PyInstaller output not found at: ${DIST_DIR}\nRun: pyinstaller youvideo-downloader.spec"
fi

if [[ ! -f "${DIST_DIR}/${EXECUTABLE}" ]] && [[ ! -f "${DIST_DIR}/YouVideo Downloader" ]]; then
    error "Executable not found in ${DIST_DIR}/"
fi

# Handle executable name (with or without spaces)
if [[ -f "${DIST_DIR}/YouVideo Downloader" ]]; then
    ACTUAL_EXEC="YouVideo Downloader"
else
    ACTUAL_EXEC="${EXECUTABLE}"
fi

log "Found PyInstaller bundle: ${DIST_DIR}/"

# ───────────────────────────────  Clean Previous Build  ──────────────────────
log "Cleaning previous build artifacts..."
rm -rf "${BUILD_DIR}" "${FINAL_IMAGE}" "${APP_NAME}.AppImage" "${APP_NAME}-"*.AppImage
mkdir -p "${BUILD_DIR}/usr/"{bin,share/{applications,icons/hicolor/256x256/apps,doc/"${APP_NAME}"}}

# ─────────────────────────────  Copy Application Files  ──────────────────────
log "Copying PyInstaller bundle to AppDir..."
cp -r "${DIST_DIR}/"* "${BUILD_DIR}/usr/bin/"

# Rename executable if it has spaces
if [[ -f "${BUILD_DIR}/usr/bin/YouVideo Downloader" ]]; then
    mv "${BUILD_DIR}/usr/bin/YouVideo Downloader" "${BUILD_DIR}/usr/bin/${EXECUTABLE}"
fi

chmod +x "${BUILD_DIR}/usr/bin/${EXECUTABLE}"
log "Executable installed: ${EXECUTABLE}"

# ────────────────────────────────  Icon Installation  ────────────────────────
if [[ ! -f "${ICON_SRC}" ]]; then
    error "Icon not found: ${ICON_SRC}"
fi

log "Installing application icon..."
cp "${ICON_SRC}" "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/youvideo.png"
cp "${ICON_SRC}" "${BUILD_DIR}/youvideo.png"
cp "${ICON_SRC}" "${BUILD_DIR}/.DirIcon"  # AppImage thumbnail

# ────────────────────────────────  Desktop Entry  ────────────────────────────
log "Creating desktop entry..."
cat > "${BUILD_DIR}/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=YouVideo Downloader
GenericName=Video Downloader
Comment=${DESCRIPTION}
Exec=AppRun %U
Icon=youvideo
Terminal=false
Categories=AudioVideo;Video;Network;Qt;
Keywords=youtube;downloader;video;yt-dlp;audio;playlist;
StartupNotify=true
MimeType=x-scheme-handler/http;x-scheme-handler/https;
X-AppImage-Version=${VERSION}
EOF

install -Dm644 "${BUILD_DIR}/${APP_NAME}.desktop" \
               "${BUILD_DIR}/usr/share/applications/${APP_NAME}.desktop"

# Validate desktop file
if command -v desktop-file-validate >/dev/null 2>&1; then
    if desktop-file-validate "${BUILD_DIR}/${APP_NAME}.desktop" 2>/dev/null; then
        log "Desktop entry validated successfully"
    else
        warn "Desktop entry validation returned warnings (non-fatal)"
    fi
fi

# ────────────────────────────────  AppRun Wrapper  ───────────────────────────
log "Creating AppRun launcher script..."
cat > "${BUILD_DIR}/AppRun" <<'APPRUN_EOF'
#!/bin/bash
# AppRun wrapper for YouVideo Downloader

set -e
HERE="$(dirname "$(readlink -f "$0")")"

# Set up environment
export QT_QPA_PLATFORM_PLUGIN_PATH="$HERE/usr/bin/platforms"
export LD_LIBRARY_PATH="$HERE/usr/lib:$LD_LIBRARY_PATH"
export PATH="$HERE/usr/bin:$PATH"

# Ensure Qt can find its resources
export QT_PLUGIN_PATH="$HERE/usr/bin"
export QML2_IMPORT_PATH="$HERE/usr/bin/qml"

# Run the application
cd "$HERE/usr/bin"
exec "./YouVideoDownloader" "$@"
APPRUN_EOF

chmod +x "${BUILD_DIR}/AppRun"

# ───────────────────────────────  Optional Documentation  ────────────────────
if [[ -f README.md ]]; then
    log "Including README..."
    install -Dm644 README.md "${BUILD_DIR}/usr/share/doc/${APP_NAME}/README.md"
fi

if [[ -f LICENSE ]]; then
    log "Including LICENSE..."
    install -Dm644 LICENSE "${BUILD_DIR}/usr/share/doc/${APP_NAME}/LICENSE"
fi

# ─────────────────────────  Ensure appimagetool Available  ───────────────────
get_appimagetool() {
    if command -v appimagetool >/dev/null 2>&1; then
        APPIMAGE_TOOL_CMD="$(command -v appimagetool)"
        log "Using system appimagetool: ${APPIMAGE_TOOL_CMD}"
        return
    fi
    
    if [[ -x "./${APPIMAGE_TOOL}" ]]; then
        # Test if it can run (FUSE check)
        if "./${APPIMAGE_TOOL}" --version >/dev/null 2>&1; then
            APPIMAGE_TOOL_CMD="./${APPIMAGE_TOOL}"
            log "Using local appimagetool: ${APPIMAGE_TOOL_CMD}"
            return
        else
            warn "Local appimagetool cannot run (FUSE issue) — extracting binary..."
            rm -rf squashfs-root
            "./${APPIMAGE_TOOL}" --appimage-extract >/dev/null 2>&1
            if [[ -x squashfs-root/AppRun ]]; then
                APPIMAGE_TOOL_CMD="$(pwd)/squashfs-root/AppRun"
                log "Using extracted appimagetool: ${APPIMAGE_TOOL_CMD}"
                return
            fi
        fi
    fi
    
    log "appimagetool not found — downloading..."
    local download_url="https://github.com/AppImage/AppImageKit/releases/download/continuous/${APPIMAGE_TOOL}"
    
    if ! curl -L --fail --progress-bar "${download_url}" -o "${APPIMAGE_TOOL}"; then
        error "Failed to download appimagetool from ${download_url}"
    fi
    
    chmod +x "${APPIMAGE_TOOL}"
    
    # Test if downloaded version can run
    if "./${APPIMAGE_TOOL}" --version >/dev/null 2>&1; then
        APPIMAGE_TOOL_CMD="./${APPIMAGE_TOOL}"
        log "Downloaded appimagetool successfully"
    else
        warn "Downloaded appimagetool needs extraction (FUSE not available)..."
        rm -rf squashfs-root
        "./${APPIMAGE_TOOL}" --appimage-extract >/dev/null 2>&1
        if [[ -x squashfs-root/AppRun ]]; then
            APPIMAGE_TOOL_CMD="$(pwd)/squashfs-root/AppRun"
            log "Using extracted appimagetool from squashfs-root/"
        else
            error "Failed to extract appimagetool. Please install FUSE: sudo apt install libfuse2"
        fi
    fi
}

get_appimagetool

# ───────────────────────────────  Build AppImage  ────────────────────────────
log "Building AppImage with appimagetool..."
echo

# Build with verbose output and no GPG signature (optional)
ARCH="${ARCH}" "${APPIMAGE_TOOL_CMD}" "${BUILD_DIR}" "${FINAL_IMAGE}"

# Verify the output
if [[ ! -f "${FINAL_IMAGE}" ]]; then
    error "AppImage build failed — output file not created"
fi

chmod +x "${FINAL_IMAGE}"

# ─────────────────────────────  Success Summary  ─────────────────────────────
echo
echo "════════════════════════════════════════════════════════════════"
echo "       APPIMAGE SUCCESSFULLY BUILT"
echo "════════════════════════════════════════════════════════════════"
echo "  Output   : ${FINAL_IMAGE}"
echo "  Size     : $(du -h "${FINAL_IMAGE}" | cut -f1)"
echo "  Arch     : ${ARCH}"
echo "  Version  : ${VERSION}"
echo
echo "  Installation:"
echo "    chmod +x ${FINAL_IMAGE}"
echo "    sudo mv ${FINAL_IMAGE} /usr/local/bin/${APP_NAME}"
echo
echo "  Or run directly:"
echo "    ./${FINAL_IMAGE}"
echo
echo "  Integration test:"
echo "    ./${FINAL_IMAGE} --help"
echo "════════════════════════════════════════════════════════════════"

# Optional: Create a symlink for convenience
if [[ ! -L "${APP_NAME}.AppImage" ]]; then
    ln -sf "${FINAL_IMAGE}" "${APP_NAME}.AppImage"
    chmod +x "${APP_NAME}.AppImage"
    log "Created convenience symlink: ${APP_NAME}.AppImage -> ${FINAL_IMAGE}"
fi

# Offer to make it executable
read -rp "Make ${FINAL_IMAGE} executable now? [Y/n] " -n 1 response
echo
if [[ "$response" =~ ^[Yy]$|^$ ]]; then
    chmod +x "${FINAL_IMAGE}"
    log "✓ ${FINAL_IMAGE} is now executable"
else
    warn "Remember to run: chmod +x ${FINAL_IMAGE}"
fi

exit 0