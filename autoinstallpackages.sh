#!/bin/bash

# AutoInstallPackages - Enhanced Arch Linux Post-Installation Script
# Version: 4.0
# Author: Firebleudark
# Description: Modern post-installation script with GUI support for Arch Linux
# Repository: https://github.com/Firebleudark/Autoinstallpackages

set -euo pipefail

# Script configuration
readonly SCRIPT_NAME="AutoInstallPackages"
readonly SCRIPT_VERSION="4.0"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/tmp/autoinstallpackages.log"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# Logging functions
log() {
    local level="$1"
    shift
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $*" | tee -a "$LOG_FILE"
}

info() {
    log "INFO" "$1"
    echo -e "${CYAN}ℹ${NC} $1"
}

success() {
    log "SUCCESS" "$1"
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    log "WARNING" "$1"
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    log "ERROR" "$1"
    echo -e "${RED}✗${NC} $1" >&2
}

error_exit() {
    error "$1"
    exit 1
}

# Header display
print_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${BOLD}              $SCRIPT_NAME v$SCRIPT_VERSION                     ║${NC}"
    echo -e "${CYAN}║${YELLOW}     Enhanced Arch Linux Post-Installation Script        ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo
}

# System validation
validate_system() {
    info "Validating system requirements..."
    
    # Check if Arch Linux
    if [[ ! -f /etc/os-release ]] || ! grep -q "Arch Linux" /etc/os-release; then
        error_exit "This script is only for Arch Linux systems"
    fi
    success "Arch Linux detected"
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        error_exit "Do not run this script as root"
    fi
    success "Running as regular user"
    
    # Check sudo permissions
    if ! sudo -v; then
        error_exit "Sudo permissions required"
    fi
    success "Sudo permissions validated"
    
    # Check internet connection
    if ! ping -c 1 google.com &>/dev/null; then
        error_exit "Internet connection required"
    fi
    success "Internet connection available"
}

# Install dependencies for GUI
install_gui_dependencies() {
    info "Installing GUI dependencies..."
    
    local gui_deps=("python" "tk")
    local missing_deps=()
    
    for dep in "${gui_deps[@]}"; do
        if ! pacman -Q "$dep" &>/dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        info "Installing missing dependencies: ${missing_deps[*]}"
        sudo pacman -S --needed --noconfirm "${missing_deps[@]}"
        success "GUI dependencies installed"
    else
        success "GUI dependencies already installed"
    fi
    
    # Test Python and tkinter
    if ! python3 -c "import tkinter" 2>/dev/null; then
        error_exit "Python tkinter not working properly"
    fi
    success "Python GUI support verified"
}

# Install paru AUR helper
install_paru() {
    if command -v paru &>/dev/null; then
        success "Paru AUR helper already installed"
        return 0
    fi
    
    info "Installing paru AUR helper..."
    
    # Install base-devel if not present
    sudo pacman -S --needed --noconfirm base-devel git
    
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    git clone https://aur.archlinux.org/paru.git
    cd paru
    makepkg -si --noconfirm
    
    cd - > /dev/null
    rm -rf "$temp_dir"
    
    if command -v paru &>/dev/null; then
        success "Paru installed successfully"
    else
        error_exit "Failed to install paru"
    fi
}

# Check and enable multilib repository
enable_multilib() {
    info "Checking multilib repository..."
    
    if grep -q "^\[multilib\]" /etc/pacman.conf; then
        success "Multilib repository already enabled"
        return 0
    fi
    
    warning "Multilib repository not enabled"
    echo -e "${YELLOW}Multilib is required for 32-bit support (gaming, wine, etc.)${NC}"
    
    if ask_user "Enable multilib repository?"; then
        info "Enabling multilib repository..."
        
        # Backup pacman.conf
        sudo cp /etc/pacman.conf /etc/pacman.conf.backup
        
        # Enable multilib
        echo -e "\n[multilib]\nInclude = /etc/pacman.d/mirrorlist" | sudo tee -a /etc/pacman.conf
        
        # Update package database
        sudo pacman -Sy
        
        success "Multilib repository enabled"
    else
        warning "Multilib repository not enabled - some packages may not be available"
    fi
}

# User interaction function
ask_user() {
    local prompt="$1"
    local response
    
    while true; do
        echo -ne "${CYAN}$prompt (y/n): ${NC}"
        read -r response
        case "$response" in
            [Yy]|[Yy][Ee][Ss]) return 0 ;;
            [Nn]|[Nn][Oo]) return 1 ;;
            *) echo -e "${RED}Please answer yes or no${NC}" ;;
        esac
    done
}

# Launch GUI interface
launch_gui() {
    info "Launching GUI interface..."
    
    local gui_script="$SCRIPT_DIR/autoinstallpackages_gui.py"
    
    if [[ ! -f "$gui_script" ]]; then
        error "GUI script not found: $gui_script"
        error "Make sure autoinstallpackages_gui.py is in the same directory"
        return 1
    fi
    
    # Make sure GUI dependencies are installed
    install_gui_dependencies
    
    # Launch GUI
    python3 "$gui_script"
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        success "GUI interface completed successfully"
    else
        error "GUI interface exited with error code: $exit_code"
    fi
    
    return $exit_code
}

# CLI mode installation
cli_installation() {
    info "Starting CLI installation mode..."
    
    # System update
    info "Updating system..."
    sudo pacman -Syu --noconfirm
    success "System updated"
    
    echo -e "\n${YELLOW}This is a simplified CLI mode.${NC}"
    echo -e "${CYAN}For the full experience with all features, use the GUI mode.${NC}"
    echo -e "${YELLOW}Launch GUI with: ./autoinstallpackages.sh --gui${NC}"
    echo
    
    success "CLI installation completed! Use --gui for the full interface."
}

# Show help
show_help() {
    cat << EOF
$SCRIPT_NAME v$SCRIPT_VERSION - Enhanced Arch Linux Post-Installation Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --gui           Launch graphical user interface (default)
    --cli           Use simplified command-line mode  
    --install-deps  Install GUI dependencies only
    --check         Check system requirements
    --help, -h      Show this help message
    --version       Show version information

EXAMPLES:
    $0              # Launch GUI interface (default)
    $0 --gui        # Launch GUI interface explicitly
    $0 --cli        # Use simplified CLI mode
    $0 --check      # Check system compatibility

DESCRIPTION:
    AutoInstallPackages is a modern post-installation script for Arch Linux
    that helps you quickly install essential software packages organized by
    categories such as gaming, development, multimedia, and more.

    Features:
    • Modern GUI interface with dark theme
    • Automatic GPU driver detection and installation
    • AUR support with paru
    • System optimizations for gaming and performance
    • ML4W dotfiles integration for Hyprland
    • Flatpak support
    • Automatic system cleanup

REQUIREMENTS:
    • Arch Linux
    • Internet connection
    • Sudo privileges
    • Python 3 with tkinter (for GUI mode - auto-installed)

REPOSITORY:
    https://github.com/Firebleudark/Autoinstallpackages

EOF
}

# Main function
main() {
    # Create log directory and initialize log
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "=== AutoInstallPackages v$SCRIPT_VERSION started at $(date) ===" > "$LOG_FILE"
    
    # Parse command line arguments
    case "${1:-}" in
        --gui|"")
            # Default behavior: launch GUI
            print_header
            validate_system
            enable_multilib
            install_paru
            launch_gui
            ;;
        --cli)
            print_header
            validate_system
            enable_multilib
            install_paru
            cli_installation
            ;;
        --install-deps)
            print_header
            validate_system
            install_gui_dependencies
            success "GUI dependencies installation completed"
            ;;
        --check)
            print_header
            validate_system
            install_gui_dependencies
            success "System check completed successfully"
            ;;
        --version)
            echo "$SCRIPT_NAME v$SCRIPT_VERSION"
            ;;
        --help|-h)
            show_help
            ;;
        *)
            error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
    
    # Log completion
    echo "=== AutoInstallPackages completed at $(date) ===" >> "$LOG_FILE"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi