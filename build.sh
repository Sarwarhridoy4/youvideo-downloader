#!/usr/bin/env bash
set -e

APP_NAME="YouVideoDownloader"
PACKAGE_NAME="youvideodownloader"       # Keep SAME package name
LINUX_BINARY="youvideo-downloader"      # Real binary from PyInstaller
SAFE_BIN_NAME="youvideo-downloader-app" # Prevent conflict with system package
APP_ID="com.youvideo.downloader"
VERSION="1.7.0"

MAINTAINER="Sarwar Hossain"
EMAIL="sarwarhridoy4@gmail.com"

SPEC_FILE="./YouVideoDownloader.spec"

BUILD_DIR="./dist"
APPDIR="${BUILD_DIR}/${APP_NAME}.AppDir"
SPEC_OUTPUT_DIR="${BUILD_DIR}/${APP_NAME}"

echo "=== Installing required packaging tools ==="
sudo apt update
sudo apt install -y fakeroot dpkg-dev debhelper fuse patchelf desktop-file-utils appstream imagemagick

# Download linuxdeploy if missing
if [ ! -f ./linuxdeploy-x86_64.AppImage ]; then
    echo "Downloading linuxdeploy..."
    wget -q https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
    chmod +x linuxdeploy-x86_64.AppImage
fi

echo
echo "=== Running PyInstaller build ==="
pyinstaller "$SPEC_FILE"

# Validate binary exists
if [ ! -f "${SPEC_OUTPUT_DIR}/${LINUX_BINARY}" ]; then
    echo "❌ ERROR: Linux binary ${LINUX_BINARY} not found!"
    exit 1
fi

chmod +x "${SPEC_OUTPUT_DIR}/${LINUX_BINARY}"

# ------------------------------------------------------------------------------
#                               BUILD .deb
# ------------------------------------------------------------------------------

DEB_DIR="${BUILD_DIR}/${APP_NAME}_deb"
echo
echo "=== Creating .deb structure ==="
rm -rf "$DEB_DIR"
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$DEB_DIR/usr/share/${APP_NAME}"

# Copy binary
cp "${SPEC_OUTPUT_DIR}/${LINUX_BINARY}" "$DEB_DIR/usr/share/${APP_NAME}/${LINUX_BINARY}"
chmod 755 "$DEB_DIR/usr/share/${APP_NAME}/${LINUX_BINARY}"

# Avoid conflict: create safe public binary name
ln -sf "/usr/share/${APP_NAME}/${LINUX_BINARY}" "$DEB_DIR/usr/bin/${SAFE_BIN_NAME}"

# Ensure icon exists
if [ ! -f assets/icons/appicon.png ]; then
    echo "⚠️ Missing icon: generating placeholder..."
    convert -size 256x256 xc:'#444' assets/icons/appicon.png
fi

cp assets/icons/appicon.png \
   "$DEB_DIR/usr/share/icons/hicolor/256x256/apps/${APP_ID}.png"

# Desktop entry
cat <<EOF > "$DEB_DIR/usr/share/applications/${APP_NAME}.desktop"
[Desktop Entry]
Name=${APP_NAME}
Exec=${SAFE_BIN_NAME}
Icon=${APP_ID}
Type=Application
Categories=Utility;
EOF

# Control metadata
cat <<EOF > "$DEB_DIR/DEBIAN/control"
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: ${MAINTAINER} <${EMAIL}>
Description: ${APP_NAME} - Fast and powerful YouTube video downloader for Linux.
EOF

echo
echo "=== Building .deb package ==="
fakeroot dpkg-deb --build "$DEB_DIR" "${BUILD_DIR}/${APP_NAME}_${VERSION}_amd64.deb"

# ------------------------------------------------------------------------------
#                               AppImage
# ------------------------------------------------------------------------------

echo
echo "=== Creating AppDir structure ==="
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

cp "${SPEC_OUTPUT_DIR}/${LINUX_BINARY}" "$APPDIR/usr/bin/${SAFE_BIN_NAME}"
chmod 755 "$APPDIR/usr/bin/${SAFE_BIN_NAME}"

cat <<EOF > "$APPDIR/usr/share/applications/${APP_NAME}.desktop"
[Desktop Entry]
Name=${APP_NAME}
Exec=${SAFE_BIN_NAME}
Icon=${APP_ID}
Type=Application
Categories=Utility;
EOF

cp assets/icons/appicon.png \
   "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_ID}.png"

echo
echo "=== Building AppImage ==="
./linuxdeploy-x86_64.AppImage \
    --appdir="$APPDIR" \
    --desktop-file="$APPDIR/usr/share/applications/${APP_NAME}.desktop" \
    --icon-file="assets/icons/appicon.png" \
    --output appimage

mv ./*.AppImage "${BUILD_DIR}/${APP_NAME}-${VERSION}.AppImage"

echo
echo "============================================="
echo "  🎉 BUILD COMPLETE!"
echo "  ✔ .deb:      ${BUILD_DIR}/${APP_NAME}_${VERSION}_amd64.deb"
echo "  ✔ AppImage:  ${BUILD_DIR}/${APP_NAME}-${VERSION}.AppImage"
echo "============================================="
