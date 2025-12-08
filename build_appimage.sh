#!/bin/bash

################################################################################
# YouVideo Downloader - AppImage Build Script
# 
# This script builds an AppImage for YouVideo Downloader.
# AppImage is a universal Linux package format that runs on most distributions.
# It checks for all necessary tools, downloads linuxdeploy and appimagetool,
# creates the AppDir structure, and builds the AppImage.
#
# Official AppImage Documentation: https://docs.appimage.org/
# Author: Based on YouVideo Downloader project
# Repository: https://github.com/Sarwarhridoy4/youvideo-downloader
################################################################################

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Application information
APP_NAME="YouVideo_Downloader"
APP_VERSION="1.6.0"
ARCH="x86_64"
DESKTOP_FILE_NAME="youvideo-downloader"

################################################################################
# SECTION 1: Utility Functions
################################################################################

# Print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print section header
print_header() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

################################################################################
# SECTION 2: Check and Install Required Tools
################################################################################

check_and_install_tools() {
    print_header "Checking Required Tools"
    
    # Check for wget or curl
    if ! command -v wget &> /dev/null && ! command -v curl &> /dev/null; then
        print_error "Neither wget nor curl found. Please install one of them."
        print_info "Ubuntu/Debian: sudo apt install wget"
        print_info "Fedora: sudo dnf install wget"
        exit 1
    fi
    
    # Check for python3
    if ! command -v python3 &> /dev/null; then
        print_error "python3 not found"
        print_info "Please install Python 3.8 or higher"
        exit 1
    else
        print_success "python3 found: $(python3 --version)"
    fi
    
    # Check for pip3
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 not found"
        print_info "Ubuntu/Debian: sudo apt install python3-pip"
        exit 1
    else
        print_success "pip3 found"
    fi
    
    # Check for ffmpeg (critical dependency)
    if ! command -v ffmpeg &> /dev/null; then
        print_warning "ffmpeg not found - required for video processing"
        print_info "The application needs ffmpeg to merge video and audio"
        print_info "Ubuntu/Debian: sudo apt install ffmpeg"
        print_info "Fedora: sudo dnf install ffmpeg"
        print_info "You can continue, but users will need to install ffmpeg separately"
        read -p "Continue without ffmpeg? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "ffmpeg found: $(ffmpeg -version | head -n1)"
    fi
    
    # Check for PyInstaller
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        print_warning "PyInstaller not found, installing..."
        pip3 install --upgrade pyinstaller
        print_success "PyInstaller installed"
    else
        print_success "PyInstaller found"
    fi
    
    # Check for PySide6
    if ! python3 -c "import PySide6" 2>/dev/null; then
        print_warning "PySide6 not found, installing..."
        pip3 install PySide6
        print_success "PySide6 installed"
    else
        print_success "PySide6 found"
    fi
    
    # Check for file command (needed for AppImage)
    if ! command -v file &> /dev/null; then
        print_warning "file command not found"
        print_info "This is needed for AppImage. Install it with:"
        print_info "Ubuntu/Debian: sudo apt install file"
        print_info "Fedora: sudo dnf install file"
    else
        print_success "file command found"
    fi
    
    # Check for FUSE (needed to run AppImage)
    if ! command -v fusermount &> /dev/null && ! command -v fusermount3 &> /dev/null; then
        print_warning "FUSE not found"
        print_info "FUSE is needed to run AppImages. Install with:"
        print_info "Ubuntu/Debian: sudo apt install fuse libfuse2"
        print_info "Fedora: sudo dnf install fuse fuse-libs"
        print_info "The AppImage will still be created but may not run on systems without FUSE"
    else
        print_success "FUSE found"
    fi
    
    # Check for Qt6 libraries (for runtime on target systems)
    print_info "Checking Qt6 libraries (informational)..."
    if dpkg -l 2>/dev/null | grep -q libqt6core6; then
        print_success "Qt6 libraries found on build system"
    else
        print_warning "Qt6 libraries not found on build system"
        print_info "PyInstaller will bundle them from PySide6"
    fi
    
    # Check for essential X11 libraries
    print_info "Checking X11 libraries (needed for GUI)..."
    if ldconfig -p 2>/dev/null | grep -q libX11.so; then
        print_success "X11 libraries found"
    else
        print_warning "X11 libraries may not be available"
        print_info "Install with: sudo apt install libx11-6 libxcb1"
    fi
}

################################################################################
# SECTION 3: Download AppImage Tools
################################################################################

download_appimage_tools() {
    print_header "Downloading AppImage Tools"
    
    # Create tools directory
    TOOLS_DIR="appimage-tools"
    mkdir -p "$TOOLS_DIR"
    
    # Define tool URLs
    LINUXDEPLOY_URL="https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage"
    APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    
    # Download linuxdeploy if not present
    if [ ! -f "$TOOLS_DIR/linuxdeploy-x86_64.AppImage" ]; then
        print_info "Downloading linuxdeploy..."
        if command -v wget &> /dev/null; then
            wget -q --show-progress "$LINUXDEPLOY_URL" -O "$TOOLS_DIR/linuxdeploy-x86_64.AppImage"
        else
            curl -L "$LINUXDEPLOY_URL" -o "$TOOLS_DIR/linuxdeploy-x86_64.AppImage"
        fi
        chmod +x "$TOOLS_DIR/linuxdeploy-x86_64.AppImage"
        print_success "linuxdeploy downloaded"
    else
        print_success "linuxdeploy already exists"
    fi
    
    # Download appimagetool if not present
    if [ ! -f "$TOOLS_DIR/appimagetool-x86_64.AppImage" ]; then
        print_info "Downloading appimagetool..."
        if command -v wget &> /dev/null; then
            wget -q --show-progress "$APPIMAGETOOL_URL" -O "$TOOLS_DIR/appimagetool-x86_64.AppImage"
        else
            curl -L "$APPIMAGETOOL_URL" -o "$TOOLS_DIR/appimagetool-x86_64.AppImage"
        fi
        chmod +x "$TOOLS_DIR/appimagetool-x86_64.AppImage"
        print_success "appimagetool downloaded"
    else
        print_success "appimagetool already exists"
    fi
    
    # Set paths
    LINUXDEPLOY="$TOOLS_DIR/linuxdeploy-x86_64.AppImage"
    APPIMAGETOOL="$TOOLS_DIR/appimagetool-x86_64.AppImage"
}

################################################################################
# SECTION 4: Prepare Project Dependencies
################################################################################

prepare_dependencies() {
    print_header "Preparing Project Dependencies"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found in current directory"
        print_info "Make sure you're running this script from the project root"
        exit 1
    fi
    
    # Install Python requirements
    print_info "Installing Python dependencies..."
    pip3 install -r requirements.txt
    print_success "Python dependencies installed"
    
    # Check for main.py
    if [ ! -f "main.py" ]; then
        print_error "main.py not found in current directory"
        exit 1
    fi
    
    print_success "Project structure verified"
}

################################################################################
# SECTION 5: Build Executable with PyInstaller
################################################################################

build_executable() {
    print_header "Building Executable with PyInstaller"
    
    # Clean previous builds
    print_info "Cleaning previous builds..."
    rm -rf build dist *.spec
    
    # Determine icon path
    ICON_PATH=""
    if [ -f "assets/icons/app_icon.png" ]; then
        ICON_PATH="assets/icons/app_icon.png"
        print_info "Found application icon: $ICON_PATH"
    elif [ -f "assets/icons/icon.png" ]; then
        ICON_PATH="assets/icons/icon.png"
        print_info "Found application icon: $ICON_PATH"
    else
        print_warning "No icon found in assets/icons/"
    fi
    
    # Build PyInstaller command
    # Note: For AppImage, we use --onefile mode which creates a single executable
    PYINSTALLER_CMD="pyinstaller --onefile --windowed"
    
    if [ -n "$ICON_PATH" ]; then
        PYINSTALLER_CMD="$PYINSTALLER_CMD --icon=$ICON_PATH"
    fi
    
    # Add data files (icons, qss stylesheets, etc.)
    # These will be included in the executable
    PYINSTALLER_CMD="$PYINSTALLER_CMD --add-data assets:assets"
    PYINSTALLER_CMD="$PYINSTALLER_CMD --add-data ui:ui"
    PYINSTALLER_CMD="$PYINSTALLER_CMD --add-data downloader:downloader"
    PYINSTALLER_CMD="$PYINSTALLER_CMD --add-data utils:utils"
    
    # Set application name
    PYINSTALLER_CMD="$PYINSTALLER_CMD --name $APP_NAME"
    
    # Add main.py
    PYINSTALLER_CMD="$PYINSTALLER_CMD main.py"
    
    print_info "Running PyInstaller..."
    print_info "Command: $PYINSTALLER_CMD"
    
    eval $PYINSTALLER_CMD
    
    if [ ! -f "dist/$APP_NAME" ]; then
        print_error "PyInstaller failed to create executable"
        exit 1
    fi
    
    # Make executable
    chmod +x "dist/$APP_NAME"
    
    print_success "Executable built successfully: dist/$APP_NAME"
}

################################################################################
# SECTION 6: Create AppDir Structure
################################################################################

create_appdir_structure() {
    print_header "Creating AppDir Structure"
    
    # Define AppDir
    APPDIR="$APP_NAME.AppDir"
    
    # Remove old AppDir
    print_info "Cleaning old AppDir..."
    rm -rf "$APPDIR"
    
    # Create AppDir structure according to AppImage specification
    # Reference: https://docs.appimage.org/reference/appdir.html
    print_info "Creating AppDir structure..."
    mkdir -p "$APPDIR/usr/bin"
    mkdir -p "$APPDIR/usr/share/applications"
    mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "$APPDIR/usr/share/pixmaps"
    
    print_success "AppDir structure created"
    
    # Copy executable to AppDir
    print_info "Copying executable to AppDir..."
    cp "dist/$APP_NAME" "$APPDIR/usr/bin/"
    chmod +x "$APPDIR/usr/bin/$APP_NAME"
    
    print_success "Executable copied to AppDir"
}

################################################################################
# SECTION 7: Setup Desktop Integration
################################################################################

setup_desktop_integration() {
    print_header "Setting Up Desktop Integration"
    
    APPDIR="$APP_NAME.AppDir"
    
    # Create .desktop file
    # This is required by the AppImage specification
    print_info "Creating desktop entry..."
    cat > "$APPDIR/usr/share/applications/$DESKTOP_FILE_NAME.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=YouVideo Downloader
Comment=Download YouTube videos with ease
Exec=$APP_NAME
Icon=$DESKTOP_FILE_NAME
Terminal=false
Categories=Network;AudioVideo;
Keywords=youtube;downloader;video;
StartupNotify=true
X-AppImage-Version=$APP_VERSION
EOF
    
    chmod 644 "$APPDIR/usr/share/applications/$DESKTOP_FILE_NAME.desktop"
    print_success "Desktop entry created"
    
    # Install icon
    print_info "Installing application icon..."
    
    ICON_FOUND=0
    for icon_path in "assets/icons/app_icon.png" "assets/icons/icon.png" "assets/icons/logo.png"; do
        if [ -f "$icon_path" ]; then
            # Copy icon to multiple locations as per AppImage best practices
            cp "$icon_path" "$APPDIR/usr/share/icons/hicolor/256x256/apps/$DESKTOP_FILE_NAME.png"
            cp "$icon_path" "$APPDIR/usr/share/pixmaps/$DESKTOP_FILE_NAME.png"
            # Also copy to AppDir root (required for AppImage)
            cp "$icon_path" "$APPDIR/$DESKTOP_FILE_NAME.png"
            cp "$icon_path" "$APPDIR/.DirIcon"
            print_success "Icon installed from $icon_path"
            ICON_FOUND=1
            break
        fi
    done
    
    if [ $ICON_FOUND -eq 0 ]; then
        print_warning "No icon found, AppImage will use default icon"
    fi
    
    # Create symbolic links in AppDir root (required by AppImage specification)
    print_info "Creating AppDir root symlinks..."
    cd "$APPDIR"
    ln -sf "usr/share/applications/$DESKTOP_FILE_NAME.desktop" "$DESKTOP_FILE_NAME.desktop"
    cd ..
    
    print_success "Desktop integration configured"
}

################################################################################
# SECTION 8: Create AppRun Script
################################################################################

create_apprun_script() {
    print_header "Creating AppRun Script"
    
    APPDIR="$APP_NAME.AppDir"
    
    # AppRun is the entry point for the AppImage
    # It sets up the environment and launches the application
    print_info "Creating AppRun script..."
    cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash

# AppRun script for YouVideo Downloader
# This script is the entry point for the AppImage

# Get the directory where the AppImage is mounted
APPDIR="$(dirname "$(readlink -f "$0")")"

# Set up environment
export PATH="${APPDIR}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"

# Set XDG directories for proper integration
export XDG_DATA_DIRS="${APPDIR}/usr/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"

# Change to a writable directory
cd "$HOME"

# Launch the application
exec "${APPDIR}/usr/bin/YouVideo_Downloader" "$@"
EOF
    
    chmod +x "$APPDIR/AppRun"
    print_success "AppRun script created and made executable"
}

################################################################################
# SECTION 9: Build AppImage with appimagetool
################################################################################

build_appimage() {
    print_header "Building AppImage"
    
    APPDIR="$APP_NAME.AppDir"
    OUTPUT_APPIMAGE="${APP_NAME}-${ARCH}.AppImage"
    
    # Remove old AppImage if exists
    if [ -f "$OUTPUT_APPIMAGE" ]; then
        print_info "Removing old AppImage..."
        rm "$OUTPUT_APPIMAGE"
    fi
    
    # Build AppImage using appimagetool
    # The ARCH environment variable tells appimagetool which architecture to build for
    print_info "Building AppImage with appimagetool..."
    print_info "This may take a few minutes..."
    
    # Extract the AppImage tools first (they run as AppImages themselves)
    export ARCH="$ARCH"
    
    # Use appimagetool to create the AppImage
    # --no-appstream: Skip AppStream validation (optional)
    # --comp gzip: Use gzip compression (faster than default)
    "$APPIMAGETOOL" "$APPDIR" "$OUTPUT_APPIMAGE" --no-appstream --comp gzip
    
    if [ ! -f "$OUTPUT_APPIMAGE" ]; then
        print_error "Failed to create AppImage"
        exit 1
    fi
    
    # Make AppImage executable (very important!)
    chmod +x "$OUTPUT_APPIMAGE"
    
    print_success "AppImage created: $OUTPUT_APPIMAGE"
    print_success "AppImage is executable and ready to use"
    
    # Show file info
    print_info "AppImage details:"
    ls -lh "$OUTPUT_APPIMAGE"
    file "$OUTPUT_APPIMAGE"
}

################################################################################
# SECTION 10: Verify AppImage
################################################################################

verify_appimage() {
    print_header "Verifying AppImage"
    
    OUTPUT_APPIMAGE="${APP_NAME}-${ARCH}.AppImage"
    
    # Check if file is executable
    if [ -x "$OUTPUT_APPIMAGE" ]; then
        print_success "AppImage is executable ✓"
    else
        print_error "AppImage is not executable"
        print_info "Making it executable..."
        chmod +x "$OUTPUT_APPIMAGE"
    fi
    
    # Check file type
    FILE_TYPE=$(file "$OUTPUT_APPIMAGE")
    if echo "$FILE_TYPE" | grep -q "executable"; then
        print_success "AppImage file type is correct ✓"
    else
        print_warning "AppImage file type might be incorrect"
        print_info "File type: $FILE_TYPE"
    fi
    
    # Calculate size
    SIZE=$(du -h "$OUTPUT_APPIMAGE" | cut -f1)
    print_info "AppImage size: $SIZE"
    
    print_success "Verification complete"
}

################################################################################
# SECTION 11: Test Instructions
################################################################################

show_test_instructions() {
    print_header "Testing Instructions"
    
    OUTPUT_APPIMAGE="${APP_NAME}-${ARCH}.AppImage"
    
    print_info "To test the AppImage:"
    echo "  ./$OUTPUT_APPIMAGE"
    echo ""
    print_info "To run with debug output:"
    echo "  ./$OUTPUT_APPIMAGE --verbose"
    echo ""
    print_info "To extract the AppImage contents (for debugging):"
    echo "  ./$OUTPUT_APPIMAGE --appimage-extract"
    echo ""
    print_info "To integrate with desktop environment:"
    echo "  Just double-click the AppImage file in your file manager"
    echo ""
    print_warning "Note: First run might be slower as AppImage extracts files"
}

################################################################################
# SECTION 12: Cleanup
################################################################################

cleanup() {
    print_header "Cleanup"
    
    APPDIR="$APP_NAME.AppDir"
    
    read -p "Do you want to clean up build files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        rm -rf build dist *.spec "$APPDIR"
        print_success "Cleanup completed (AppImage tools kept for future builds)"
    else
        print_info "Skipping cleanup"
    fi
}

################################################################################
# SECTION 13: Create Distribution Info
################################################################################

create_distribution_info() {
    print_header "Creating Distribution Info"
    
    OUTPUT_APPIMAGE="${APP_NAME}-${ARCH}.AppImage"
    INFO_FILE="${APP_NAME}_info.txt"
    
    print_info "Creating distribution info file..."
    cat > "$INFO_FILE" << EOF
YouVideo Downloader AppImage
============================

Version: $APP_VERSION
Architecture: $ARCH
File: $OUTPUT_APPIMAGE
Build Date: $(date)

Installation Instructions:
--------------------------
1. Download the AppImage file
2. Make it executable: chmod +x $OUTPUT_APPIMAGE
3. Run it: ./$OUTPUT_APPIMAGE

The AppImage is portable and doesn't require installation.
It will integrate with your desktop environment automatically.

System Requirements:
-------------------
- Linux kernel 2.6.32 or later
- FUSE support (usually pre-installed)
- X11 or Wayland display server

If you can't run the AppImage, install FUSE:
- Ubuntu/Debian: sudo apt install fuse libfuse2
- Fedora: sudo dnf install fuse fuse-libs

For more information, visit:
https://github.com/Sarwarhridoy4/youvideo-downloader
EOF
    
    print_success "Distribution info created: $INFO_FILE"
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    print_header "YouVideo Downloader - AppImage Builder"
    print_info "Version: $APP_VERSION"
    print_info "Architecture: $ARCH"
    echo ""
    
    # Execute build steps
    check_and_install_tools
    download_appimage_tools
    prepare_dependencies
    build_executable
    create_appdir_structure
    setup_desktop_integration
    create_apprun_script
    build_appimage
    verify_appimage
    create_distribution_info
    show_test_instructions
    cleanup
    
    # Final success message
    print_header "Build Complete!"
    print_success "Your AppImage is ready: ${APP_NAME}-${ARCH}.AppImage"
    print_success "The AppImage is executable and portable!"
    print_info "You can now distribute this single file to users"
    echo ""
}

# Run main function
main "$@"