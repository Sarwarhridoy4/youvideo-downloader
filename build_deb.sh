#!/bin/bash

################################################################################
# YouVideo Downloader - Debian Package Build Script
# 
# This script builds a .deb package for YouVideo Downloader.
# It checks for all necessary tools, installs missing dependencies,
# creates the proper directory structure, and builds the package.
#
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
APP_NAME="youvideo-downloader"
APP_VERSION="1.6.0"
MAINTAINER="Sarwar Hossain <sarwarhridoy4@gmail.com>"
DESCRIPTION="YouTube video downloader with PySide6 interface"
ARCH="amd64"

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
    
    local tools_needed=()
    local qt_libs_needed=()
    
    # Check for dpkg-deb (Debian package builder)
    if ! command -v dpkg-deb &> /dev/null; then
        print_warning "dpkg-deb not found"
        tools_needed+=("dpkg")
    else
        print_success "dpkg-deb found"
    fi
    
    # Check for python3
    if ! command -v python3 &> /dev/null; then
        print_warning "python3 not found"
        tools_needed+=("python3")
    else
        print_success "python3 found: $(python3 --version)"
    fi
    
    # Check for pip3
    if ! command -v pip3 &> /dev/null; then
        print_warning "pip3 not found"
        tools_needed+=("python3-pip")
    else
        print_success "pip3 found"
    fi
    
    # Check for ffmpeg (critical dependency)
    if ! command -v ffmpeg &> /dev/null; then
        print_warning "ffmpeg not found - required for video processing"
        tools_needed+=("ffmpeg")
    else
        print_success "ffmpeg found: $(ffmpeg -version | head -n1)"
    fi
    
    # Check for Python development headers (needed for some pip packages)
    if ! dpkg -l | grep -q python3-dev; then
        print_warning "python3-dev not found - needed for building some Python packages"
        tools_needed+=("python3-dev")
    else
        print_success "python3-dev found"
    fi
    
    # Check for essential build tools
    if ! command -v gcc &> /dev/null; then
        print_warning "gcc not found - needed for compiling"
        tools_needed+=("build-essential")
    else
        print_success "build-essential found"
    fi
    
    # Check for Qt6 libraries (PySide6 dependencies)
    print_info "Checking Qt6/PySide6 system dependencies..."
    
    # Core Qt6 libraries needed by PySide6
    local qt_packages=(
        "libqt6core6"
        "libqt6gui6"
        "libqt6widgets6"
        "libqt6network6"
        "qt6-gtk-platformtheme"
        "libxcb-xinerama0"
        "libxcb-cursor0"
    )
    
    for pkg in "${qt_packages[@]}"; do
        if ! dpkg -l | grep -q "^ii.*$pkg"; then
            print_warning "$pkg not found"
            qt_libs_needed+=("$pkg")
        fi
    done
    
    if [ ${#qt_libs_needed[@]} -eq 0 ]; then
        print_success "Qt6 libraries found"
    fi
    
    # X11 libraries (needed for GUI)
    if ! dpkg -l | grep -q libx11-6; then
        print_warning "X11 libraries not found"
        tools_needed+=("libx11-6" "libx11-xcb1" "libxext6" "libxrender1")
    else
        print_success "X11 libraries found"
    fi
    
    # Check for PyInstaller
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        print_warning "PyInstaller not found"
        print_info "Will install PyInstaller via pip"
    else
        print_success "PyInstaller found"
    fi
    
    # Combine all needed packages
    local all_packages=("${tools_needed[@]}" "${qt_libs_needed[@]}")
    
    # Install missing tools
    if [ ${#all_packages[@]} -gt 0 ]; then
        print_info "Installing missing packages: ${all_packages[*]}"
        
        # Check if running with sudo privileges
        if [ "$EUID" -ne 0 ]; then
            print_error "This script needs sudo privileges to install missing packages"
            print_info "Please run: sudo $0"
            exit 1
        fi
        
        # Update package list
        print_info "Updating package list..."
        apt-get update
        
        # Install packages (with error handling for unavailable packages)
        print_info "Installing packages..."
        for pkg in "${all_packages[@]}"; do
            if apt-cache show "$pkg" &> /dev/null; then
                apt-get install -y "$pkg" || print_warning "Failed to install $pkg"
            else
                print_warning "Package $pkg not available in repositories"
            fi
        done
        print_success "Package installation completed"
    fi
    
    # Install PyInstaller and essential Python packages if not present
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        print_info "Installing PyInstaller..."
        pip3 install --upgrade pyinstaller
        print_success "PyInstaller installed"
    fi
    
    # Install PySide6 if not present (will be needed for packaging)
    if ! python3 -c "import PySide6" 2>/dev/null; then
        print_info "Installing PySide6..."
        pip3 install PySide6
        print_success "PySide6 installed"
    else
        print_success "PySide6 found"
    fi
} 

################################################################################
# SECTION 3: Prepare Project Dependencies
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
# SECTION 4: Build Executable with PyInstaller
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
    PYINSTALLER_CMD="pyinstaller --onefile --windowed"
    
    if [ -n "$ICON_PATH" ]; then
        PYINSTALLER_CMD="$PYINSTALLER_CMD --icon=$ICON_PATH"
    fi
    
    # Add data files (icons, qss stylesheets, etc.)
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
    
    print_success "Executable built successfully: dist/$APP_NAME"
}

################################################################################
# SECTION 5: Create Debian Package Structure
################################################################################

create_deb_structure() {
    print_header "Creating Debian Package Structure"
    
    # Define package directory
    PKG_DIR="${APP_NAME}_${APP_VERSION}_${ARCH}"
    
    # Remove old package directory
    print_info "Cleaning old package directory..."
    rm -rf "$PKG_DIR"
    
    # Create directory structure
    print_info "Creating directory structure..."
    mkdir -p "$PKG_DIR/DEBIAN"
    mkdir -p "$PKG_DIR/usr/bin"
    mkdir -p "$PKG_DIR/usr/share/applications"
    mkdir -p "$PKG_DIR/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "$PKG_DIR/usr/share/pixmaps"
    mkdir -p "$PKG_DIR/usr/share/$APP_NAME"
    
    print_success "Directory structure created"
    
    # Copy executable
    print_info "Copying executable to package..."
    cp "dist/$APP_NAME" "$PKG_DIR/usr/share/$APP_NAME/"
    chmod +x "$PKG_DIR/usr/share/$APP_NAME/$APP_NAME"
    
    # Create launcher script in /usr/bin
    print_info "Creating launcher script..."
    cat > "$PKG_DIR/usr/bin/$APP_NAME" << EOF
#!/bin/bash
# Launcher script for YouVideo Downloader
cd /usr/share/$APP_NAME
./$APP_NAME "\$@"
EOF
    chmod +x "$PKG_DIR/usr/bin/$APP_NAME"
    
    print_success "Executable and launcher configured"
}

################################################################################
# SECTION 6: Create Desktop Entry and Icon
################################################################################

setup_desktop_integration() {
    print_header "Setting Up Desktop Integration"
    
    PKG_DIR="${APP_NAME}_${APP_VERSION}_${ARCH}"
    
    # Create .desktop file
    print_info "Creating desktop entry..."
    cat > "$PKG_DIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=YouVideo Downloader
Comment=Download YouTube videos with ease
Exec=$APP_NAME %U
Icon=$APP_NAME
Terminal=false
Categories=Network;AudioVideo;
Keywords=youtube;downloader;video;
StartupNotify=true
EOF
    
    chmod 644 "$PKG_DIR/usr/share/applications/$APP_NAME.desktop"
    print_success "Desktop entry created"
    
    # Copy and install icon
    print_info "Installing application icon..."
    
    # Try different icon locations
    ICON_FOUND=0
    for icon_path in "assets/icons/app_icon.png" "assets/icons/icon.png" "assets/icons/logo.png"; do
        if [ -f "$icon_path" ]; then
            cp "$icon_path" "$PKG_DIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"
            cp "$icon_path" "$PKG_DIR/usr/share/pixmaps/$APP_NAME.png"
            print_success "Icon installed from $icon_path"
            ICON_FOUND=1
            break
        fi
    done
    
    if [ $ICON_FOUND -eq 0 ]; then
        print_warning "No icon found, package will use default icon"
    fi
}

################################################################################
# SECTION 7: Create Debian Control File
################################################################################

create_control_file() {
    print_header "Creating Debian Control File"
    
    PKG_DIR="${APP_NAME}_${APP_VERSION}_${ARCH}"
    
    # Calculate installed size (in KB)
    INSTALLED_SIZE=$(du -sk "$PKG_DIR" | cut -f1)
    
    print_info "Creating control file..."
    cat > "$PKG_DIR/DEBIAN/control" << EOF
Package: $APP_NAME
Version: $APP_VERSION
Section: net
Priority: optional
Architecture: $ARCH
Installed-Size: $INSTALLED_SIZE
Depends: python3 (>= 3.8), ffmpeg, libqt6core6, libqt6gui6, libqt6widgets6, libx11-6, libxcb1, libxcb-xinerama0, libxcb-cursor0
Recommends: qt6-gtk-platformtheme
Maintainer: $MAINTAINER
Description: $DESCRIPTION
 YouVideo Downloader is a simple and efficient YouTube video downloader
 built with PySide6 and yt-dlp. It allows users to select video formats,
 choose output folders, and track download progress with a clean,
 modern interface inspired by YouTube's dark and light themes.
 .
 Features:
  - Download YouTube, Facebook, and other videos
  - Auto-detect and install ffmpeg if missing
  - Multiple video/audio format selection
  - Playlist support with range selection
  - MP3 audio extraction
  - Real-time progress tracking
  - Dark and light theme support
Homepage: https://github.com/Sarwarhridoy4/youvideo-downloader
EOF
    
    chmod 644 "$PKG_DIR/DEBIAN/control"
    print_success "Control file created"
}

################################################################################
# SECTION 8: Create Post-installation Script
################################################################################

create_postinst_script() {
    print_header "Creating Post-installation Script"
    
    PKG_DIR="${APP_NAME}_${APP_VERSION}_${ARCH}"
    
    print_info "Creating postinst script..."
    cat > "$PKG_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
# Post-installation script

set -e

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database -q
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor
fi

echo "YouVideo Downloader installed successfully!"
echo "You can launch it from your application menu or run 'youvideo-downloader' in terminal."

exit 0
EOF
    
    chmod 755 "$PKG_DIR/DEBIAN/postinst"
    print_success "Post-installation script created"
}

################################################################################
# SECTION 9: Create Pre-removal Script
################################################################################

create_prerm_script() {
    print_header "Creating Pre-removal Script"
    
    PKG_DIR="${APP_NAME}_${APP_VERSION}_${ARCH}"
    
    print_info "Creating prerm script..."
    cat > "$PKG_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
# Pre-removal script

set -e

echo "Removing YouVideo Downloader..."

exit 0
EOF
    
    chmod 755 "$PKG_DIR/DEBIAN/prerm"
    print_success "Pre-removal script created"
}

################################################################################
# SECTION 10: Build the .deb Package
################################################################################

build_deb_package() {
    print_header "Building Debian Package"
    
    PKG_DIR="${APP_NAME}_${APP_VERSION}_${ARCH}"
    DEB_FILE="${APP_NAME}_${APP_VERSION}_${ARCH}.deb"
    
    # Remove old .deb file if exists
    if [ -f "$DEB_FILE" ]; then
        print_info "Removing old package file..."
        rm "$DEB_FILE"
    fi
    
    # Build the package
    print_info "Building package with dpkg-deb..."
    dpkg-deb --build --root-owner-group "$PKG_DIR"
    
    if [ ! -f "${PKG_DIR}.deb" ]; then
        print_error "Failed to create .deb package"
        exit 1
    fi
    
    # Rename to standard name
    mv "${PKG_DIR}.deb" "$DEB_FILE"
    
    print_success "Debian package created: $DEB_FILE"
    
    # Show package information
    print_info "Package information:"
    dpkg-deb --info "$DEB_FILE"
    
    # Show package contents
    echo ""
    print_info "Package contents:"
    dpkg-deb --contents "$DEB_FILE"
}

################################################################################
# SECTION 11: Test the Package (Optional)
################################################################################

test_package() {
    print_header "Package Testing Information"
    
    DEB_FILE="${APP_NAME}_${APP_VERSION}_${ARCH}.deb"
    
    print_info "To install and test the package, run:"
    echo "  sudo dpkg -i $DEB_FILE"
    echo ""
    print_info "To remove the package later:"
    echo "  sudo apt remove $APP_NAME"
    echo ""
    print_info "To check for dependency issues:"
    echo "  sudo apt --fix-broken install"
}

################################################################################
# SECTION 12: Cleanup (Optional)
################################################################################

cleanup() {
    print_header "Cleanup"
    
    PKG_DIR="${APP_NAME}_${APP_VERSION}_${ARCH}"
    
    read -p "Do you want to clean up build files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        rm -rf build dist *.spec "$PKG_DIR"
        print_success "Cleanup completed"
    else
        print_info "Skipping cleanup"
    fi
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    print_header "YouVideo Downloader - Debian Package Builder"
    print_info "Version: $APP_VERSION"
    print_info "Architecture: $ARCH"
    echo ""
    
    # Execute build steps
    check_and_install_tools
    prepare_dependencies
    build_executable
    create_deb_structure
    setup_desktop_integration
    create_control_file
    create_postinst_script
    create_prerm_script
    build_deb_package
    test_package
    cleanup
    
    # Final success message
    print_header "Build Complete!"
    print_success "Your Debian package is ready: ${APP_NAME}_${APP_VERSION}_${ARCH}.deb"
    echo ""
}

# Run main function
main "$@"