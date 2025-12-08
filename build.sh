#!/bin/bash

################################################################################
# YouVideo Downloader - Master Build Script
# 
# This is a unified build script that can:
# - Check and install dependencies
# - Build DEB packages
# - Build AppImage packages
# - Build both packages
#
# Usage:
#   ./build.sh deps         # Install dependencies only
#   ./build.sh deb          # Build DEB package
#   ./build.sh appimage     # Build AppImage
#   ./build.sh all          # Build both DEB and AppImage
#   ./build.sh              # Interactive mode
#
# Author: Based on YouVideo Downloader project
# Repository: https://github.com/Sarwarhridoy4/youvideo-downloader
################################################################################

set -e  # Exit on any error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

################################################################################
# Utility Functions
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
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} $1"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
}

print_banner() {
    clear
    echo -e "${MAGENTA}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                                                          ║"
    echo "║        YouVideo Downloader - Build System               ║"
    echo "║                                                          ║"
    echo "║        Build DEB packages and AppImages easily          ║"
    echo "║                                                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

################################################################################
# Check if required scripts exist
################################################################################

check_scripts() {
    local scripts=("build_deb.sh" "build_appimage.sh")
    local missing=()
    
    for script in "${scripts[@]}"; do
        if [ ! -f "$script" ]; then
            missing+=("$script")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        print_error "Missing required scripts: ${missing[*]}"
        print_info "Please ensure all build scripts are in the current directory"
        exit 1
    fi
    
    # Make scripts executable
    chmod +x build_deb.sh build_appimage.sh 2>/dev/null || true
}

################################################################################
# Check Dependencies
################################################################################

check_dependencies() {
    print_header "Checking Dependencies"
    
    local deps_ok=true
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found"
        deps_ok=false
    else
        print_success "Python: $(python3 --version)"
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 not found"
        deps_ok=false
    else
        print_success "pip: found"
    fi
    
    # Check FFmpeg
    if ! command -v ffmpeg &> /dev/null; then
        print_warning "FFmpeg not found (required for video processing)"
        deps_ok=false
    else
        print_success "FFmpeg: found"
    fi
    
    # Check PyInstaller
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        print_warning "PyInstaller not found"
        deps_ok=false
    else
        print_success "PyInstaller: found"
    fi
    
    # Check PySide6
    if ! python3 -c "import PySide6" 2>/dev/null; then
        print_warning "PySide6 not found"
        deps_ok=false
    else
        print_success "PySide6: found"
    fi
    
    if [ "$deps_ok" = false ]; then
        echo ""
        print_warning "Some dependencies are missing!"
        print_info "Would you like to install them now? (requires sudo)"
        read -p "Install dependencies? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_dependencies
        else
            print_error "Cannot proceed without dependencies"
            exit 1
        fi
    else
        print_success "All dependencies found!"
    fi
}

################################################################################
# Install Dependencies
################################################################################

install_dependencies() {
    print_header "Installing Dependencies"
    
    if [ -f "install_dependencies.sh" ]; then
        print_info "Running automated dependency installer..."
        chmod +x install_dependencies.sh
        sudo ./install_dependencies.sh
    else
        print_warning "install_dependencies.sh not found"
        print_info "Installing basic dependencies manually..."
        
        # Detect package manager
        if command -v apt &> /dev/null; then
            print_info "Using APT package manager..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-dev build-essential ffmpeg
        elif command -v dnf &> /dev/null; then
            print_info "Using DNF package manager..."
            sudo dnf install -y python3 python3-pip python3-devel gcc ffmpeg
        elif command -v pacman &> /dev/null; then
            print_info "Using Pacman package manager..."
            sudo pacman -S --noconfirm python python-pip base-devel ffmpeg
        else
            print_error "Unable to detect package manager"
            exit 1
        fi
        
        # Install Python packages
        print_info "Installing Python packages..."
        pip3 install --upgrade pyinstaller PySide6 yt-dlp
    fi
    
    print_success "Dependencies installed!"
}

################################################################################
# Build DEB Package
################################################################################

build_deb() {
    print_header "Building DEB Package"
    
    if [ ! -f "build_deb.sh" ]; then
        print_error "build_deb.sh not found"
        exit 1
    fi
    
    print_info "Starting DEB build process..."
    ./build_deb.sh
    
    if [ $? -eq 0 ]; then
        print_success "DEB package built successfully!"
        if [ -f "youvideo-downloader_1.6.0_amd64.deb" ]; then
            echo ""
            print_info "Package location: $(pwd)/youvideo-downloader_1.6.0_amd64.deb"
            print_info "Package size: $(du -h youvideo-downloader_1.6.0_amd64.deb | cut -f1)"
        fi
    else
        print_error "DEB build failed"
        exit 1
    fi
}

################################################################################
# Build AppImage
################################################################################

build_appimage() {
    print_header "Building AppImage"
    
    if [ ! -f "build_appimage.sh" ]; then
        print_error "build_appimage.sh not found"
        exit 1
    fi
    
    print_info "Starting AppImage build process..."
    ./build_appimage.sh
    
    if [ $? -eq 0 ]; then
        print_success "AppImage built successfully!"
        if [ -f "YouVideo_Downloader-x86_64.AppImage" ]; then
            echo ""
            print_info "AppImage location: $(pwd)/YouVideo_Downloader-x86_64.AppImage"
            print_info "AppImage size: $(du -h YouVideo_Downloader-x86_64.AppImage | cut -f1)"
            print_warning "Remember to make it executable: chmod +x YouVideo_Downloader-x86_64.AppImage"
        fi
    else
        print_error "AppImage build failed"
        exit 1
    fi
}

################################################################################
# Build Both Packages
################################################################################

build_all() {
    print_header "Building All Packages"
    
    print_info "This will build both DEB and AppImage packages"
    echo ""
    
    # Build DEB
    build_deb
    
    echo ""
    print_info "Press Enter to continue with AppImage build..."
    read
    
    # Build AppImage
    build_appimage
    
    # Summary
    print_header "Build Summary"
    echo ""
    
    if [ -f "youvideo-downloader_1.6.0_amd64.deb" ]; then
        print_success "DEB: $(du -h youvideo-downloader_1.6.0_amd64.deb | cut -f1)"
    fi
    
    if [ -f "YouVideo_Downloader-x86_64.AppImage" ]; then
        print_success "AppImage: $(du -h YouVideo_Downloader-x86_64.AppImage | cut -f1)"
    fi
    
    echo ""
    print_info "All packages built successfully!"
}

################################################################################
# Interactive Menu
################################################################################

show_menu() {
    print_banner
    
    echo -e "${CYAN}Please select an option:${NC}"
    echo ""
    echo "  1) Install dependencies only"
    echo "  2) Build DEB package"
    echo "  3) Build AppImage"
    echo "  4) Build both (DEB + AppImage)"
    echo "  5) Check dependencies"
    echo "  6) Exit"
    echo ""
    read -p "Enter your choice [1-6]: " choice
    
    case $choice in
        1)
            install_dependencies
            ;;
        2)
            check_dependencies
            build_deb
            ;;
        3)
            check_dependencies
            build_appimage
            ;;
        4)
            check_dependencies
            build_all
            ;;
        5)
            check_dependencies
            ;;
        6)
            print_info "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid option"
            exit 1
            ;;
    esac
}

################################################################################
# Main Function
################################################################################

main() {
    # Check if required scripts exist
    check_scripts
    
    # Parse command line arguments
    case "${1:-}" in
        deps|dependencies)
            print_banner
            install_dependencies
            ;;
        deb)
            print_banner
            check_dependencies
            build_deb
            ;;
        appimage)
            print_banner
            check_dependencies
            build_appimage
            ;;
        all|both)
            print_banner
            check_dependencies
            build_all
            ;;
        check)
            print_banner
            check_dependencies
            ;;
        -h|--help|help)
            print_banner
            echo "Usage: $0 [option]"
            echo ""
            echo "Options:"
            echo "  deps        Install dependencies only"
            echo "  deb         Build DEB package"
            echo "  appimage    Build AppImage"
            echo "  all         Build both packages"
            echo "  check       Check dependencies"
            echo "  help        Show this help message"
            echo ""
            echo "No option   Interactive menu"
            exit 0
            ;;
        "")
            # No arguments - show interactive menu
            show_menu
            ;;
        *)
            print_error "Unknown option: $1"
            print_info "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
    
    # Final message
    echo ""
    print_header "Done!"
    print_success "Build process completed successfully!"
    echo ""
}

# Run main function
main "$@"