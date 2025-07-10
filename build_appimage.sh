#!/usr/bin/env bash
set -e

# ──────────────────────────────────  Core metadata  ───────────────────────────
APP_NAME="youvideo-downloader"
EXECUTABLE="YouVideoDownloader"              # PyInstaller launcher
VERSION="1.6.0"
ARCH="$(uname -m)"                           # x86_64, aarch64, …
DESCRIPTION="Elegant and modern YouTube/Video Downloader with PyQt6"
HOMEPAGE="https://github.com/SarwarHridoy4/youvideo-downloader"

DIST_DIR="dist/${EXECUTABLE}"                # PyInstaller one-folder bundle
BUILD_DIR="AppDir"
ICON_SRC="assets/icons/appicon.png"          # 256 × 256 PNG
APPIMAGE_TOOL="appimagetool-${ARCH}.AppImage"
FINAL_IMAGE="${APP_NAME}-${VERSION}-${ARCH}.AppImage"

# ───────────────────────────────  Clean previous build  ───────────────────────
echo "🧹 Cleaning previous AppDir ..."
rm -rf "${BUILD_DIR}" "${FINAL_IMAGE}" "${APP_NAME}.AppImage"
mkdir -p "${BUILD_DIR}/usr/bin" \
         "${BUILD_DIR}/usr/share/applications" \
         "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps"

# ─────────────────────────────  Copy application files  ───────────────────────
echo "📁 Copying PyInstaller bundle ..."
cp -r "${DIST_DIR}/"* "${BUILD_DIR}/usr/bin/"
chmod +x "${BUILD_DIR}/usr/bin/${EXECUTABLE}"

# ────────────────────────────────  Icon & .desktop  ───────────────────────────
echo "🖼  Installing icon ..."
cp "${ICON_SRC}" "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/youvideo.png"
cp "${ICON_SRC}" "${BUILD_DIR}/youvideo.png"

echo "📄 Creating .desktop file ..."
cat > "${BUILD_DIR}/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=YouVideo Downloader
Comment=${DESCRIPTION}
Exec=AppRun
Icon=youvideo
Terminal=false
Categories=AudioVideo;Video;
StartupNotify=true
EOF

install -Dm644 "${BUILD_DIR}/${APP_NAME}.desktop" \
               "${BUILD_DIR}/usr/share/applications/${APP_NAME}.desktop"

# ────────────────────────────────  AppRun wrapper  ────────────────────────────
echo "🔗 Creating AppRun launcher ..."
cat > "${BUILD_DIR}/AppRun" <<'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
export QT_QPA_PLATFORM_PLUGIN_PATH="$HERE/usr/bin/platforms"
exec "$HERE/usr/bin/YouVideoDownloader"
EOF

chmod +x "${BUILD_DIR}/AppRun"

# ───────────────────────────────  Optional README  ────────────────────────────
if [[ -f README.md ]]; then
  install -Dm644 README.md \
    "${BUILD_DIR}/usr/share/doc/${APP_NAME}/README.md"
fi

# ─────────────────────────────  Ensure appimagetool  ──────────────────────────
if command -v appimagetool >/dev/null 2>&1; then
  APPIMAGE_TOOL_CMD=$(command -v appimagetool)
elif [[ -x "./${APPIMAGE_TOOL}" ]]; then
  APPIMAGE_TOOL_CMD="./${APPIMAGE_TOOL}"
else
  echo "⬇️  appimagetool not found – downloading ..."
  curl -L \
    "https://github.com/AppImage/AppImageKit/releases/latest/download/${APPIMAGE_TOOL}" \
    -o "${APPIMAGE_TOOL}"
  chmod +x "${APPIMAGE_TOOL}"
  APPIMAGE_TOOL_CMD="./${APPIMAGE_TOOL}"
fi
echo "✅ Using appimagetool at: ${APPIMAGE_TOOL_CMD}"

# ───────────────────────────────  Build AppImage  ─────────────────────────────
echo "📦 Building AppImage ..."
"${APPIMAGE_TOOL_CMD}" "${BUILD_DIR}"
mv "${APP_NAME}.AppImage" "${FINAL_IMAGE}"

echo "✅ Created: ${FINAL_IMAGE}"
echo -e "\n🚀 Run it anywhere with:\n  ./$(printf '%q' "${FINAL_IMAGE}")"
