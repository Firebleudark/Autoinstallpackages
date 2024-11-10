#!/bin/bash

# Colors for better readability
RED=${RED:-'\033[0;31m'}
GREEN=${GREEN:-'\033[0;32m'}
YELLOW=${YELLOW:-'\033[0;33m'}
BLUE=${BLUE:-'\033[0;34m'}
NC=${NC:-'\033[0m'} # No color

# Add some introductory information
clear

echo -e "${BLUE}-----------------------------------------------${NC}"

echo -e "${BLUE}   Welcome to the Arch Linux Setup Script!     ${NC}"

echo -e "${BLUE}-----------------------------------------------${NC}"
echo -e "${YELLOW}This script will update your system, install essential packages for gaming and multimedia, and clean up unnecessary files.${NC}"

# Check if the script is run as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: this script should not be run as root.${NC}"
    exit 1
fi

echo -e "${YELLOW}Checking for sudo permissions...${NC}"
# Request sudo permissions at the beginning
if ! sudo -v; then
    echo -e "${RED}Error: please run the script with sudo permissions.${NC}"
    exit 1
fi

echo -e "${GREEN}Sudo permissions obtained successfully.${NC}"

# Function to display an error message in red and exit
error_exit() {
    echo -e "${RED}$1${NC}" 1>&2
    exit 1
}

# Function to display a progress message
info() {
    echo -e "${YELLOW}$1${NC}"
}

# Function to display a success message
success() {
    echo -e "${GREEN}$1${NC}"
}

# Check if the distribution is Arch Linux
echo -e "${YELLOW}Checking if the system is running Arch Linux...${NC}"
if [[ ! -f /etc/os-release ]] || ! grep -q "Arch Linux" /etc/os-release; then
    error_exit "Error: this script is only intended for Arch Linux."
fi
success "Arch Linux detected. Proceeding..."

# Function to install a package if not already installed
install_package() {
    local package="$1"
    if ! pacman -Q $package &> /dev/null; then
        info "Installing $package..."
        if sudo pacman -S --noconfirm --needed $package; then
            success "$package was successfully installed."
        else
            error_exit "Error installing $package."
        fi
    else
        success "$package is already installed."
    fi
}

# Function to install a package from AUR using paru if not already installed
install_aur_package() {
    local package="$1"
    if ! pacman -Q $package &> /dev/null; then
        info "Installing $package from AUR..."
        if paru -S --noconfirm --needed $package; then
            success "$package was successfully installed from AUR."
        else
            error_exit "Error installing $package from AUR."
        fi
    else
        success "$package is already installed."
    fi
}


echo -e "${BLUE}-----------------------------------------------${NC}"

echo -e "${BLUE}     Starting Package Installation...          ${NC}"

echo -e "${BLUE}-----------------------------------------------${NC}"

# List of packages to install via pacman
packages_pacman=("neovim" "steam" "goverlay" "lutris" "discord" "timeshift" "xorg-xhost" "htop" "yazi" "thunderbird" "fastfetch" "libreoffice-fresh")

# List of packages to install via AUR
packages_aur=("arch-update" "heroic-games-launcher-bin" "prismlauncher-qt5" "visual-studio-code-bin")

# Check if paru is installed for AUR
echo -e "${YELLOW}Checking if paru is installed...${NC}"
if ! pacman -Q paru &> /dev/null; then
    info "Installing paru..."
    if sudo pacman -S --noconfirm --needed paru; then
        if ! pacman -Q paru &> /dev/null; then
            error_exit "Error: paru installation verification failed. Please install paru manually."
        fi
        success "paru was successfully installed."
    else
        error_exit "Error installing paru."
    fi
fi
success "Paru is installed."

# Install required packages via pacman
for pkg in "${packages_pacman[@]}"; do
    install_package "$pkg"
done

# Install required packages via AUR
for pkg in "${packages_aur[@]}"; do
    install_aur_package "$pkg"
done

# Step to ask user about privacy protection applications
echo
echo -e "${YELLOW}Would you like to install privacy-protection applications (Tor/Signal/SimpleX) ? (y/n)${NC}"
read -r install_privacy_apps
if [[ "$install_privacy_apps" == "y" || "$install_privacy_apps" == "Y" ]]; then
    echo -e "${YELLOW}Installing privacy-protection applications...${NC}"
    # Install Tor Browser, SimpleX Chat, and Signal
    install_package "torbrowser-launcher"
    install_aur_package "simplex-chat"
    install_aur_package "signal-desktop"
    success "Privacy-protection applications installed successfully."
else
    echo -e "${YELLOW}Skipping privacy-protection applications installation.${NC}"
fi

echo

echo -e "${BLUE}-----------------------------------------------${NC}"

echo -e "${BLUE}     Post-Configuration Of The Script...       ${NC}"

echo -e "${BLUE}-----------------------------------------------${NC}"
# Add user to the gamemode group

echo -e "${BLUE} Add user to the gamemode group ${NC}"
if getent group gamemode > /dev/null 2>&1; then
    sudo usermod -aG gamemode $(whoami)
    success "User added to the gamemode group successfully."
else
    info "The 'gamemode' group does not exist. Skipping user addition."
fi

echo

echo -e "${BLUE}-----------------------------------------------${NC}"

echo -e "${BLUE}        Cleaning Up System Cache...            ${NC}"

echo -e "${BLUE}-----------------------------------------------${NC}"
# Function to clean the system
clean_system() {
    info "Cleaning the system cache..."
    echo -e "${YELLOW}Are you sure you want to clean the system cache? This will remove all cached packages. (y/n)${NC}"
    read -r confirm_clean
    if [[ "$confirm_clean" == "y" || "$confirm_clean" == "Y" ]]; then
        if sudo paccache -r; then
            success "System cache cleaned successfully."
        else
            error_exit "Error cleaning the system cache."
        fi
    else
        info "System cache cleaning was skipped."
    fi
}

# Clean the system
clean_system

echo

echo -e "${BLUE}-----------------------------------------------${NC}"

echo -e "${GREEN} All operations were completed successfully.  ${NC}"

echo -e "${BLUE}-----------------------------------------------${NC}"
