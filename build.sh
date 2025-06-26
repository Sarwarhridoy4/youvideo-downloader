#!/bin/bash
set -e

# ── Core metadata ─────────────────────────────────────────────────────────────
APP_NAME="youvideo-downloader"
EXECUTABLE="YouVideoDownloader"
VERSION="1.5.0"
ARCH="$(dpkg --print-architecture)"
MAINTAINER="Sarwar Hossain <sarwarhridoy4@gmail.com>"
HOMEPAGE="https://github.com/Sarwarhridoy4/youvideo-downloader"
DESCRIPTION="Elegant and modern YouTube/Video Downloader with PyQt6"

DIST_DIR="dist/${EXECUTABLE}"
BUILD_DIR="${APP_NAME}-deb"
ICON_SRC="assets/icons/appicon.png"

# ── Clean old build ────────────────────────────────────────────────────────────
echo "🧹 Cleaning previous build ..."
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"/{usr/bin,usr/share/{applications,icons/hicolor/256x256/apps},usr/share/doc/${APP_NAME},DEBIAN}

# ── Copy files ─────────────────────────────────────────────────────────────────
echo "📁 Copying PyInstaller bundle ..."
cp -r "${DIST_DIR}/"* "${BUILD_DIR}/usr/bin/"

echo "🖼  Installing icon ..."
cp "${ICON_SRC}" "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/youvideo.png"

echo "📄 Creating .desktop file ..."
cat > "${BUILD_DIR}/usr/share/applications/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=YouVideo Downloader
Exec=${EXECUTABLE}
Icon=youvideo
Terminal=false
Categories=AudioVideo;Network;Utility;
StartupNotify=true
EOF

echo "📜 Creating control file ..."
cat > "${BUILD_DIR}/DEBIAN/control" <<EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: video
Priority: optional
Architecture: ${ARCH}
Depends: libc6 (>= 2.31), ffmpeg
Maintainer: ${MAINTAINER}
Homepage: ${HOMEPAGE}
Description: ${DESCRIPTION}
 YouVideo Downloader is a powerful video downloader built with PySide6 and Python 3.
 It supports downloading from YouTube and other video sources via yt-dlp,
 with a modern UI, clipboard monitoring, and theme switching.
EOF

# ── Docs ───────────────────────────────────────────────────────────────────────
if [[ -f README.md ]]; then
  cp README.md  "${BUILD_DIR}/usr/share/doc/${APP_NAME}/readme"
  gzip -9 "${BUILD_DIR}/usr/share/doc/${APP_NAME}/readme"
fi

if [[ -f LICENSE ]]; then
  cp LICENSE    "${BUILD_DIR}/usr/share/doc/${APP_NAME}/copyright"
  gzip -9 "${BUILD_DIR}/usr/share/doc/${APP_NAME}/copyright"
fi

# ── Permissions ───────────────────────────────────────────────────────────────
chmod -R 755 "${BUILD_DIR}/usr"
chmod 755    "${BUILD_DIR}/DEBIAN"

# ── Build the .deb ────────────────────────────────────────────────────────────
echo "📦 Building Debian package ..."
dpkg-deb --build "${BUILD_DIR}"
DEB_FILE="${APP_NAME}_${VERSION}_${ARCH}.deb"
mv "${BUILD_DIR}.deb" "${DEB_FILE}"

echo "✅ Created: ${DEB_FILE}"

# ── Install package & update icon cache ───────────────────────────────────────
echo "📥 Installing ${DEB_FILE} ..."
sudo dpkg -i "${DEB_FILE}"

echo "🔄 Updating icon cache ..."
sudo gtk-update-icon-cache /usr/share/icons/hicolor

echo "✅ Done! YouVideo Downloader should now appear with icon in Dash."
# ── Cleanup ───────────────────────────────────────────────────────────────────