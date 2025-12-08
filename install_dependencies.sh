#!/bin/bash

################################################################################
# YouVideo Downloader - Dependency Installation Script
# 
# This script installs ALL required dependencies for building and running
# YouVideo Downloader on Linux systems. It supports multiple distributions.
#
# Usage: sudo ./install_dependencies.sh
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

################################################################################
# SECTION 1: Utility Functions
################################################################################

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

print_header() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

################################################################################
# SECTION 2: Detect Linux Distribution
################################################################################

detect_distro() {
    print_header "Detecting Linux Distribution"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_VERSION=$VERSION_ID
        print_success "Detected: $NAME $VERSION"
    else
        print_error "Cannot detect Linux distribution"
        exit 1
    fi
    
    # Determine package manager
    case $DISTRO in
        ubuntu|debian|linuxmint|pop)
            PKG_MANAGER="apt"
            print_info "Package manager: APT"
            ;;
        fedora|rhel|centos|rocky|almalinux)
            PKG_MANAGER="dnf"
            print_info "Package manager: DNF"
            ;;
        arch|manjaro|endeavouros)
            PKG_MANAGER="pacman"
            print_info "Package manager: Pacman"
            ;;
        opensuse*|sles)
            PKG_MANAGER="zypper"
            print_info "Package manager: Zypper"
            ;;
        *)
            print_warning "Unknown distribution: $DISTRO"
            print_info "Defaulting to APT package manager"
            PKG_MANAGER="apt"
            ;;
    esac
}

################################################################################
# SECTION 3: Check Root Privileges
################################################################################

check_root() {
    print_header "Checking Privileges"
    
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run with sudo privileges"
        print_info "Please run: sudo $0"
        exit 1
    fi
    
    print_success "Running with sudo privileges"
}

################################################################################
# SECTION 4: Update Package Lists
################################################################################

update_package_lists() {
    print_header "Updating Package Lists"
    
    case $PKG_MANAGER in
        apt)
            print_info "Running: apt update"
            apt update
            ;;
        dnf)
            print_info "Running: dnf check-update"
            dnf check-update || true
            ;;
        pacman)
            print_info "Running: pacman -Sy"
            pacman -Sy
            ;;
        zypper)
            print_info "Running: zypper refresh"
            zypper refresh
            ;;
    esac
    
    print_success "Package lists updated"
}

################################################################################
# SECTION 5: Install System Dependencies
################################################################################

install_system_dependencies() {
    print_header "Installing System Dependencies"
    
    print_info "This includes: Python, pip, build tools, and system libraries"
    
    case $PKG_MANAGER in
        apt)
            print_info "Installing packages for Debian/Ubuntu..."
            
            # Core tools
            apt install -y \
                python3 \
                python3-pip \
                python3-dev \
                python3-venv \
                build-essential \
                gcc \
                g++ \
                make \
                pkg-config \
                wget \
                curl \
                git
            
            print_success "Core tools installed"
            ;;
            
        dnf)
            print_info "Installing packages for Fedora/RHEL..."
            
            # Core tools
            dnf install -y \
                python3 \
                python3-pip \
                python3-devel \
                gcc \
                gcc-c++ \
                make \
                pkgconfig \
                wget \
                curl \
                git
            
            print_success "Core tools installed"
            ;;
            
        pacman)
            print_info "Installing packages for Arch Linux..."
            
            # Core tools
            pacman -S --noconfirm \
                python \
                python-pip \
                base-devel \
                wget \
                curl \
                git
            
            print_success "Core tools installed"
            ;;
            
        zypper)
            print_info "Installing packages for openSUSE..."
            
            # Core tools
            zypper install -y \
                python3 \
                python3-pip \
                python3-devel \
                gcc \
                gcc-c++ \
                make \
                wget \
                curl \
                git
            
            print_success "Core tools installed"
            ;;
    esac
}

################################################################################
# SECTION 6: Install FFmpeg
################################################################################

install_ffmpeg() {
    print_header "Installing FFmpeg"
    
    print_info "FFmpeg is required for video/audio processing and merging"
    
    case $PKG_MANAGER in
        apt)
            apt install -y ffmpeg
            ;;
        dnf)
            # For Fedora, might need RPM Fusion repositories
            print_info "Enabling RPM Fusion repositories for FFmpeg..."
            dnf install -y \
                https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm || true
            dnf install -y ffmpeg
            ;;
        pacman)
            pacman -S --noconfirm ffmpeg
            ;;
        zypper)
            zypper install -y ffmpeg
            ;;
    esac
    
    if command -v ffmpeg &> /dev/null; then
        print_success "FFmpeg installed: $(ffmpeg -version | head -n1)"
    else
        print_error "FFmpeg installation failed"
        print_info "You may need to install it manually from: https://ffmpeg.org/"
    fi
}

################################################################################
# SECTION 7: Install Qt6 Libraries (PySide6 Dependencies)
################################################################################

install_qt6_libraries() {
    print_header "Installing Qt6 Libraries"
    
    print_info "These are required for PySide6 GUI framework"
    
    case $PKG_MANAGER in
        apt)
            print_info "Installing Qt6 libraries for Debian/Ubuntu..."
            
            # Qt6 base libraries
            apt install -y \
                qt6-base-dev \
                libqt6core6 \
                libqt6gui6 \
                libqt6widgets6 \
                libqt6network6 \
                libqt6multimedia6 \
                libqt6opengl6 \
                qt6-gtk-platformtheme \
                qml6-module-qtquick \
                qml6-module-qtquick-controls || true
            
            print_success "Qt6 libraries installed"
            ;;
            
        dnf)
            print_info "Installing Qt6 libraries for Fedora/RHEL..."
            
            # Qt6 base libraries
            dnf install -y \
                qt6-qtbase \
                qt6-qtbase-devel \
                qt6-qtbase-gui \
                qt6-qtmultimedia || true
            
            print_success "Qt6 libraries installed"
            ;;
            
        pacman)
            print_info "Installing Qt6 libraries for Arch Linux..."
            
            # Qt6 base libraries
            pacman -S --noconfirm \
                qt6-base \
                qt6-multimedia \
                qt6-svg || true
            
            print_success "Qt6 libraries installed"
            ;;
            
        zypper)
            print_info "Installing Qt6 libraries for openSUSE..."
            
            # Qt6 base libraries
            zypper install -y \
                libQt6Core6 \
                libQt6Gui6 \
                libQt6Widgets6 || true
            
            print_success "Qt6 libraries installed"
            ;;
    esac
}

################################################################################
# SECTION 8: Install X11 and Graphics Libraries
################################################################################

install_x11_libraries() {
    print_header "Installing X11 and Graphics Libraries"
    
    print_info "These are required for GUI display"
    
    case $PKG_MANAGER in
        apt)
            apt install -y \
                libx11-6 \
                libx11-dev \
                libx11-xcb1 \
                libxcb1 \
                libxcb-xinerama0 \
                libxcb-cursor0 \
                libxcb-icccm4 \
                libxcb-image0 \
                libxcb-keysyms1 \
                libxcb-randr0 \
                libxcb-render0 \
                libxcb-render-util0 \
                libxcb-shape0 \
                libxcb-shm0 \
                libxcb-sync1 \
                libxcb-xfixes0 \
                libxcb-xkb1 \
                libxkbcommon0 \
                libxkbcommon-x11-0 \
                libxext6 \
                libxrender1 \
                libgl1 \
                libglu1-mesa \
                libegl1 \
                libdbus-1-3
            ;;
            
        dnf)
            dnf install -y \
                libX11 \
                libX11-devel \
                libxcb \
                xcb-util \
                xcb-util-image \
                xcb-util-keysyms \
                xcb-util-renderutil \
                xcb-util-wm \
                libxkbcommon \
                libxkbcommon-x11 \
                mesa-libGL \
                mesa-libEGL \
                dbus-libs
            ;;
            
        pacman)
            pacman -S --noconfirm \
                libx11 \
                libxcb \
                xcb-util \
                xcb-util-image \
                xcb-util-keysyms \
                xcb-util-renderutil \
                xcb-util-wm \
                libxkbcommon \
                libxkbcommon-x11 \
                mesa \
                dbus
            ;;
            
        zypper)
            zypper install -y \
                libX11-6 \
                libxcb1 \
                libxkbcommon0 \
                libxkbcommon-x11-0 \
                Mesa-libGL1 \
                dbus-1
            ;;
    esac
    
    print_success "X11 and graphics libraries installed"
}

################################################################################
# SECTION 9: Install Audio Libraries
################################################################################

install_audio_libraries() {
    print_header "Installing Audio Libraries"
    
    print_info "These may be needed for multimedia playback"
    
    case $PKG_MANAGER in
        apt)
            apt install -y \
                libasound2 \
                libpulse0 \
                pulseaudio-utils \
                gstreamer1.0-plugins-base \
                gstreamer1.0-plugins-good \
                gstreamer1.0-pulseaudio || true
            ;;
            
        dnf)
            dnf install -y \
                alsa-lib \
                pulseaudio-libs \
                gstreamer1-plugins-base \
                gstreamer1-plugins-good || true
            ;;
            
        pacman)
            pacman -S --noconfirm \
                alsa-lib \
                libpulse \
                gst-plugins-base \
                gst-plugins-good || true
            ;;
            
        zypper)
            zypper install -y \
                alsa \
                libpulse0 \
                gstreamer-plugins-base \
                gstreamer-plugins-good || true
            ;;
    esac
    
    print_success "Audio libraries installed"
}

################################################################################
# SECTION 10: Install Packaging Tools
################################################################################

install_packaging_tools() {
    print_header "Installing Packaging Tools"
    
    print_info "These are needed for building DEB and AppImage packages"
    
    case $PKG_MANAGER in
        apt)
            apt install -y \
                dpkg \
                dpkg-dev \
                debhelper \
                fakeroot \
                file \
                fuse \
                libfuse2 \
                patchelf \
                desktop-file-utils
            ;;
            
        dnf)
            dnf install -y \
                rpm-build \
                file \
                fuse \
                fuse-libs \
                patchelf \
                desktop-file-utils
            ;;
            
        pacman)
            pacman -S --noconfirm \
                file \
                fuse2 \
                fuse3 \
                patchelf \
                desktop-file-utils
            ;;
            
        zypper)
            zypper install -y \
                rpm-build \
                file \
                fuse \
                patchelf \
                desktop-file-utils
            ;;
    esac
    
    print_success "Packaging tools installed"
}

################################################################################
# SECTION 11: Install Python Packages
################################################################################

install_python_packages() {
    print_header "Installing Python Packages"
    
    print_info "Installing PyInstaller, PySide6, and other Python dependencies"
    
    # Upgrade pip first
    print_info "Upgrading pip..."
    python3 -m pip install --upgrade pip
    
    # Install core Python packages
    print_info "Installing core packages..."
    pip3 install --upgrade \
        wheel \
        setuptools
    
    # Install PyInstaller (for creating executables)
    print_info "Installing PyInstaller..."
    pip3 install --upgrade pyinstaller
    
    # Install PySide6 (Qt6 for Python)
    print_info "Installing PySide6..."
    pip3 install --upgrade PySide6
    
    # Install yt-dlp (YouTube downloader backend)
    print_info "Installing yt-dlp..."
    pip3 install --upgrade yt-dlp
    
    # Install other common dependencies
    print_info "Installing additional packages..."
    pip3 install --upgrade \
        requests \
        urllib3 \
        certifi
    
    print_success "Python packages installed"
    
    # Verify installations
    print_info "Verifying installations..."
    python3 -c "import PyInstaller; print(f'PyInstaller: {PyInstaller.__version__}')"
    python3 -c "import PySide6; print(f'PySide6: {PySide6.__version__}')"
    python3 -c "import yt_dlp; print(f'yt-dlp: {yt_dlp.version.__version__}')"
}

################################################################################
# SECTION 12: Install Project-Specific Requirements
################################################################################

install_project_requirements() {
    print_header "Installing Project Requirements"
    
    if [ -f "requirements.txt" ]; then
        print_info "Found requirements.txt, installing..."
        pip3 install --upgrade -r requirements.txt
        print_success "Project requirements installed"
    else
        print_warning "requirements.txt not found in current directory"
        print_info "Skipping project-specific requirements"
    fi
}

################################################################################
# SECTION 13: Verify Installation
################################################################################

verify_installation() {
    print_header "Verifying Installation"
    
    local all_ok=true
    
    # Check Python
    if command -v python3 &> /dev/null; then
        print_success "Python: $(python3 --version)"
    else
        print_error "Python not found"
        all_ok=false
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_success "pip: $(pip3 --version | cut -d' ' -f2)"
    else
        print_error "pip not found"
        all_ok=false
    fi
    
    # Check FFmpeg
    if command -v ffmpeg &> /dev/null; then
        print_success "FFmpeg: $(ffmpeg -version 2>&1 | head -n1 | cut -d' ' -f3)"
    else
        print_warning "FFmpeg not found"
    fi
    
    # Check PyInstaller
    if python3 -c "import PyInstaller" 2>/dev/null; then
        print_success "PyInstaller: installed"
    else
        print_error "PyInstaller not installed"
        all_ok=false
    fi
    
    # Check PySide6
    if python3 -c "import PySide6" 2>/dev/null; then
        print_success "PySide6: installed"
    else
        print_error "PySide6 not installed"
        all_ok=false
    fi
    
    # Check yt-dlp
    if python3 -c "import yt_dlp" 2>/dev/null; then
        print_success "yt-dlp: installed"
    else
        print_warning "yt-dlp not installed"
    fi
    
    # Check FUSE
    if command -v fusermount &> /dev/null || command -v fusermount3 &> /dev/null; then
        print_success "FUSE: installed"
    else
        print_warning "FUSE not found (needed for running AppImages)"
    fi
    
    if [ "$all_ok" = true ]; then
        print_success "All critical dependencies verified!"
    else
        print_error "Some critical dependencies are missing"
        return 1
    fi
}

################################################################################
# SECTION 14: Display Summary
################################################################################

display_summary() {
    print_header "Installation Summary"
    
    echo ""
    echo "Installed Components:"
    echo "  ✓ Python 3 and pip"
    echo "  ✓ Build tools (gcc, make, etc.)"
    echo "  ✓ FFmpeg (video processing)"
    echo "  ✓ Qt6 libraries (GUI framework)"
    echo "  ✓ X11 libraries (display)"
    echo "  ✓ Audio libraries"
    echo "  ✓ Packaging tools (dpkg/rpm, fuse)"
    echo "  ✓ PyInstaller (executable builder)"
    echo "  ✓ PySide6 (Qt6 for Python)"
    echo "  ✓ yt-dlp (YouTube downloader)"
    echo ""
    
    print_info "You can now build YouVideo Downloader packages:"
    echo "  - For DEB package: ./build_deb.sh"
    echo "  - For AppImage: ./build_appimage.sh"
    echo ""
    
    print_info "To run the application directly:"
    echo "  python3 main.py"
    echo ""
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    print_header "YouVideo Downloader - Dependency Installer"
    print_info "This will install all required dependencies for building and running"
    print_info "YouVideo Downloader on your Linux system."
    echo ""
    
    # Execute installation steps
    check_root
    detect_distro
    update_package_lists
    install_system_dependencies
    install_ffmpeg
    install_qt6_libraries
    install_x11_libraries
    install_audio_libraries
    install_packaging_tools
    install_python_packages
    install_project_requirements
    verify_installation
    display_summary
    
    # Final message
    print_header "Installation Complete!"
    print_success "All dependencies have been installed successfully!"
    echo ""
}

# Run main function
main "$@"