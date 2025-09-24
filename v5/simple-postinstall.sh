#!/usr/bin/env bash
# Simple, readable Arch Linux post-install script (Bash)
# - App categories (pacman + AUR if available)
# - Classic tasks: multilib, GPU drivers, Flatpak/Flathub, useful services
# - Interactive prompts (or --yes for safe defaults)

set -euo pipefail

YES=0
DRY_RUN=0
SKIP_AUR=0
PROFILE=""
# Optional flags for extras (used by GUI)
EXTRAS_GAMING=0
FLAG_CHROMIUM=0
FLAG_CHROME=0
FLAG_SPOTIFY=0

usage() {
  cat <<EOF
Usage: $(basename "$0") [--yes] [--dry-run] [--skip-aur] [--profile minimal|gaming|kde] [--check]

Options:
  --yes                Apply safe defaults (non-interactive)
  --dry-run            Print commands without executing
  --skip-aur           Skip AUR even if paru/yay is present
  --profile            Use a preset profile (minimal|gaming|kde)
  --check              Run non-intrusive preflight checks and exit
  --gaming-extras      Install Lutris/Heroic/Bottles/Prism/ProtonUp (no prompt)
  --install-chromium   Install Chromium (repo)
  --install-chrome     Install Google Chrome (AUR/Flatpak)
  --install-spotify    Install Spotify (AUR/Flatpak)

Notes:
  - Requires sudo for system operations.
  - AUR: uses paru or yay if detected.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) YES=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --skip-aur) SKIP_AUR=1; shift ;;
    --profile) PROFILE=${2:-}; shift 2 ;;
    --check) DO_CHECK=1; shift ;;
    --gaming-extras) EXTRAS_GAMING=1; shift ;;
    --install-chromium) FLAG_CHROMIUM=1; shift ;;
    --install-chrome) FLAG_CHROME=1; shift ;;
    --install-spotify) FLAG_SPOTIFY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Option inconnue: $1" >&2; usage; exit 2 ;;
  esac
done

msg() { echo -e "\e[1;32m[+]\e[0m $*"; }
warn() { echo -e "\e[1;33m[!]\e[0m $*"; }
err()  { echo -e "\e[1;31m[x]\e[0m $*" >&2; }

run() {
  echo "# $*"
  if (( DRY_RUN == 0 )); then "$@"; fi
}

ask_yn() {
  local prompt="$1"; local def="${2:-N}"; local ans
  if (( YES == 1 )); then
    [[ "$def" =~ ^[Yy]$ ]] && return 0 || return 1
  fi
  read -rp "$prompt [y/N] " ans || true
  ans=${ans:-$def}
  [[ "$ans" =~ ^[Yy]$ ]]
}

need_cmd() { command -v "$1" >/dev/null 2>&1 || { err "Missing required command: $1"; return 1; }; }

detect_aur_helper() {
  (( SKIP_AUR == 1 )) && { echo ""; return 0; }
  if command -v paru >/dev/null 2>&1; then echo paru; return 0; fi
  if command -v yay  >/dev/null 2>&1; then echo yay; return 0; fi
  echo ""
}

ensure_aur_helper() {
  (( SKIP_AUR == 1 )) && return 1
  local helper
  helper=$(detect_aur_helper)
  if [[ -n "$helper" ]]; then
    echo "$helper"
    return 0
  fi
  if ask_yn "Install an AUR helper (paru)?" Y; then
    msg "Installing paru (AUR)…"
    run sudo pacman -S --needed --noconfirm base-devel git
    local tmp
    tmp=$(mktemp -d)
    ( set -e; cd "$tmp"; run git clone https://aur.archlinux.org/paru-bin.git; cd paru-bin; run makepkg -si --noconfirm )
    rm -rf "$tmp"
    detect_aur_helper
    return 0
  fi
  return 1
}

pacman_pkg_available() { pacman -Si -- "$1" >/dev/null 2>&1; }

ensure_flatpak_ready() {
  if ! command -v flatpak >/dev/null 2>&1; then
    if ask_yn "Install Flatpak + Flathub to continue?" Y; then
      install_flatpak
    else
      return 1
    fi
  fi
  if ! flatpak remote-list | grep -q flathub; then
    run sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
  fi
  return 0
}

flatpak_install_ids() {
  local ids=("$@")
  ((${#ids[@]})) || return 0
  ensure_flatpak_ready || return 1
  msg "Flatpak: ${#ids[@]} application(s)"
  run flatpak install -y --noninteractive -- "${ids[@]}"
}

install_app_priority() {
  # Usage: install_app_priority <label> <repo_pkg|-> <aur_pkg|-> <flatpak_id|->
  local label="$1"; local repo_pkg="$2"; local aur_pkg="$3"; local flat_id="$4"
  msg "Installing: $label (priority repo > AUR > Flatpak)"
  if [[ -n "$repo_pkg" ]] && pacman_pkg_available "$repo_pkg"; then
    install_from_repo "$repo_pkg"
    return $?
  fi
  if [[ -n "$aur_pkg" ]]; then
    local helper
    helper=$(ensure_aur_helper && detect_aur_helper || echo "")
    if [[ -n "$helper" ]]; then
      install_from_aur "$helper" "$aur_pkg"
      return $?
    fi
  fi
  if [[ -n "$flat_id" ]]; then
    flatpak_install_ids "$flat_id"
    return $?
  fi
  warn "Aucune source disponible pour $label."
  return 1
}

# -------- Preflight checks --------
check_distro() {
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    if [[ "${ID:-}" != "arch" && "${ID_LIKE:-}" != *"arch"* ]]; then
      err "Detected distro: ${PRETTY_NAME:-unknown}. This script targets Arch and derivatives."
      return 1
    fi
  elif [[ ! -f /etc/arch-release ]]; then
    err "/etc/arch-release missing. This script is for Arch."
    return 1
  fi
  need_cmd pacman || { err "pacman is required"; return 1; }
}

ensure_sudo() {
  if [[ $EUID -eq 0 ]]; then
    return 0
  fi
  need_cmd sudo || { err "sudo is required for system operations"; return 1; }
  msg "Validating sudo (may prompt for password)…"
  if (( DRY_RUN == 0 )); then sudo -v || { err "sudo denied"; return 1; }; fi
}

check_network() {
  msg "Checking network…"
  if command -v ping >/dev/null 2>&1; then
    ping -c1 -W2 1.1.1.1 >/dev/null 2>&1 || { err "No network connectivity (ICMP)."; return 1; }
  fi
  if command -v curl >/dev/null 2>&1; then
    curl -fsSLI https://archlinux.org >/dev/null 2>&1 || warn "DNS/HTTPS to archlinux.org failed (continuing)."
  fi
}

ensure_pacman_db() {
  msg "Syncing pacman databases…"
  run sudo pacman -Sy --noconfirm
}

ensure_timesync() {
  msg "Checking NTP…"
  if command -v timedatectl >/dev/null 2>&1; then
    if ! timedatectl show -p NTPSynchronized --value | grep -q true; then
      warn "NTP not synchronized. Enabling systemd-timesyncd."
      run sudo systemctl enable --now systemd-timesyncd.service
    fi
  fi
}

ensure_pacman_keys() {
  msg "Verifying pacman GPG keys…"
  if [[ ! -d /etc/pacman.d/gnupg ]]; then
    run sudo pacman-key --init
  fi
  run sudo pacman-key --populate archlinux || true
}

preflight_report() {
  echo "Preflight checks:"
  local ok=1
  if check_distro; then echo "  Distro: OK"; else echo "  Distro: FAIL"; ok=0; fi
  if command -v sudo >/dev/null 2>&1; then echo "  Sudo: OK"; else echo "  Sudo: MISSING"; ok=0; fi
  if check_network; then echo "  Network: OK"; else echo "  Network: FAIL"; ok=0; fi
  if command -v pacman >/dev/null 2>&1; then echo "  Pacman: OK"; else echo "  Pacman: MISSING"; ok=0; fi
  if command -v flatpak >/dev/null 2>&1; then echo "  Flatpak: Present"; else echo "  Flatpak: Not installed"; fi
  detect_aur_helper >/dev/null && echo "  AUR helper: $(detect_aur_helper || echo none)" || echo "  AUR helper: none"
  return $ok
}

summary_hardware() {
  local gpu virt
  gpu=$(lspci | grep -E 'VGA|3D' || true)
  virt=$(systemd-detect-virt || true)
  echo "$gpu" | sed 's/^/  GPU: /'
  [[ -n "$virt" ]] && echo "  Virt: $virt"
}

enable_multilib() {
  msg "Enabling multilib (if needed)…"
  if grep -Pzo '\[multilib\]\n#?Include = /etc/pacman.d/mirrorlist' /etc/pacman.conf >/dev/null 2>&1; then
    run sudo sed -i '/^\[multilib\]/,/^Include/ s/^#//' /etc/pacman.conf
    run sudo pacman -Sy
  else
    warn "[multilib] block not found in /etc/pacman.conf (already enabled?)."
  fi
}

install_flatpak() {
  msg "Installing Flatpak + Flathub…"
  run sudo pacman -S --needed --noconfirm flatpak
  if ! flatpak remote-list | grep -q flathub; then
    run sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
  fi
}

install_gpu_drivers() {
  msg "Detecting GPU and installing drivers…"
  local info
  info=$(lspci | grep -E 'VGA|3D' || true)
  if echo "$info" | grep -qi nvidia; then
    warn "NVIDIA detected. Preference: open‑source drivers (nouveau)."
    if ask_yn "Use open-source drivers (nouveau)?" Y; then
      switch_to_nouveau
    else
      run sudo pacman -S --needed --noconfirm nvidia nvidia-utils lib32-nvidia-utils || true
    fi
  elif echo "$info" | grep -qi amd; then
    run sudo pacman -S --needed --noconfirm mesa vulkan-radeon lib32-mesa lib32-vulkan-radeon || true
  elif echo "$info" | grep -qi intel; then
    run sudo pacman -S --needed --noconfirm mesa vulkan-intel lib32-mesa lib32-vulkan-intel || true
  else
    warn "GPU not clearly detected. Skipping automatic drivers."
  fi
}

enable_services() {
  msg "Enabling useful services (idempotent)…"
  run sudo systemctl enable --now fstrim.timer || true
  if systemctl list-unit-files | grep -q bluetooth.service; then
    ask_yn "Enable Bluetooth now?" N && run sudo systemctl enable --now bluetooth.service
  fi
}

setup_audio() {
  msg "Audio: PipeWire (pulse/alsa)…"
  run sudo pacman -S --needed --noconfirm pipewire pipewire-alsa pipewire-pulse wireplumber
}

setup_network() {
  msg "Network: NetworkManager…"
  run sudo pacman -S --needed --noconfirm networkmanager
  run sudo systemctl enable --now NetworkManager
}

setup_printing() {
  msg "Printing: CUPS + tools…"
  run sudo pacman -S --needed --noconfirm cups system-config-printer gutenprint
  run sudo systemctl enable --now cups.service
}

setup_virtualization() {
  msg "Virtualization: libvirt/qemu/virt-manager…"
  run sudo pacman -S --needed --noconfirm qemu-base libvirt virt-manager dnsmasq iptables-nft edk2-ovmf
  run sudo systemctl enable --now libvirtd
  warn "Add your user to libvirt group if needed: sudo usermod -aG libvirt $USER"
}

setup_laptop() {
  msg "Laptop optimizations: tlp/powertop…"
  run sudo pacman -S --needed --noconfirm tlp tlp-rdw powertop
  run sudo systemctl enable --now tlp
  run sudo systemctl mask systemd-rfkill.service systemd-rfkill.socket || true
}

setup_fonts() {
  msg "Common fonts…"
  run sudo pacman -S --needed --noconfirm ttf-dejavu noto-fonts noto-fonts-cjk noto-fonts-emoji
}

setup_firewall() {
  if ! command -v ufw >/dev/null 2>&1; then
    run sudo pacman -S --needed --noconfirm ufw
  fi
  msg "Firewall: UFW…"
  run sudo systemctl enable --now ufw
  run sudo ufw default deny incoming
  run sudo ufw default allow outgoing
  run sudo ufw allow OpenSSH || true
  run sudo ufw --force enable
}

install_kde_full() {
  msg "Installing full KDE Plasma + SDDM…"
  run sudo pacman -S --needed --noconfirm xorg-server sddm plasma-meta kde-applications-meta packagekit-qt5
  setup_audio
  setup_network
  setup_fonts
  run sudo systemctl enable --now sddm
}

# ---------- NVIDIA open-source (nouveau) ----------
switch_to_nouveau() {
  msg "Switching to NVIDIA open‑source drivers (nouveau)…"
  if pacman -Qq | grep -Eq '^(nvidia|nvidia-dkms|nvidia-utils|lib32-nvidia-utils)$'; then
    warn "Removing proprietary NVIDIA packages…"
    run sudo pacman -Rns --noconfirm nvidia nvidia-dkms nvidia-utils lib32-nvidia-utils || true
  fi
  local pkgs=(xf86-video-nouveau mesa lib32-mesa)
  run sudo pacman -S --needed --noconfirm "${pkgs[@]}"
  if pacman -Si vulkan-nouveau >/dev/null 2>&1; then
    run sudo pacman -S --needed --noconfirm vulkan-nouveau lib32-vulkan-nouveau || true
  fi
  warn "A reboot is recommended after switching to nouveau."
}

install_from_repo() {
  local -a pkgs=("$@")
  ((${#pkgs[@]})) || return 0
  msg "Pacman: ${#pkgs[@]} paquet(s)"
  run sudo pacman -S --needed --noconfirm -- "${pkgs[@]}"
}

install_from_aur() {
  local helper="$1"; shift
  local -a pkgs=("$@")
  ((${#pkgs[@]})) || return 0
  [[ -z "$helper" ]] && { warn "AUR helper non trouvé, skip AUR."; return 0; }
  msg "AUR ($helper): ${#pkgs[@]} paquet(s)"
  run "$helper" -S --needed --noconfirm -- "${pkgs[@]}"
}

# Catégories (modifiables facilement)
PKG_BASE=(git base-devel curl wget nano vim htop unzip p7zip zip unrar ufw openssh)
PKG_DEV=(gcc make cmake python python-pip nodejs npm docker)
PKG_MEDIA=(vlc gimp obs-studio)
PKG_BROWSERS=(firefox)
PKG_COMM=(discord telegram-desktop)
PKG_OFFICE=(libreoffice-fresh hunspell-fr noto-fonts ttf-dejavu)
PKG_GAMING=(steam gamemode mangohud)

AUR_DEV=(visual-studio-code-bin)
AUR_GAMING=(protonup-qt)

main() {
  DO_CHECK=${DO_CHECK:-0}
  if (( DO_CHECK == 1 )); then
    preflight_report
    exit 0
  fi
  check_distro || exit 1
  ensure_sudo || exit 1
  check_network || exit 1
  ensure_pacman_db || exit 1
  ensure_timesync || true
  ensure_pacman_keys || true

  echo "Hardware Summary:"
  summary_hardware || true
  echo

  # Profils prédéfinis (non-interactifs si --yes)
  if [[ -n "$PROFILE" && $YES -eq 1 ]]; then
    case "$PROFILE" in
      minimal)
        msg "Profile: minimal"
        # Minimal: no multilib/flatpak/KDE, open-source drivers, base utils, audio, network, firewall
        install_gpu_drivers
        install_from_repo "${PKG_BASE[@]}"
        setup_audio
        setup_network
        setup_firewall
        enable_services
        msg "Minimal profile applied."
        exit 0
        ;;
      gaming)
        msg "Profile: Gaming"
        enable_multilib
        install_flatpak
        install_gpu_drivers
        install_from_repo "${PKG_BASE[@]}" "${PKG_GAMING[@]}"
        # Extras gaming avec priorités
        install_app_priority "Lutris" lutris lutris "net.lutris.Lutris"
        install_app_priority "Heroic" "" heroic-games-launcher-bin "com.heroicgameslauncher.hgl"
        install_app_priority "Bottles" bottles bottles "com.usebottles.bottles"
        install_app_priority "PrismLauncher" prismlauncher prismlauncher-bin "org.prismlauncher.PrismLauncher"
        install_app_priority "ProtonUp-Qt" protonup-qt protonup-qt "net.davidotek.pupgui2"
        setup_audio
        setup_network
        enable_services
        msg "Gaming profile applied."
        exit 0
        ;;
      kde)
        msg "Profile: full KDE"
        enable_multilib
        install_flatpak
        install_gpu_drivers
        install_kde_full
        install_from_repo "${PKG_BASE[@]}"
        setup_audio
        setup_network
        enable_services
        msg "KDE profile applied."
        exit 0
        ;;
      *) warn "Unknown profile: $PROFILE (ignored)" ;;
    esac
  fi

  # Interactive post-install choices
  if ask_yn "Enable multilib?" Y; then enable_multilib; fi
  if ask_yn "Install Flatpak + Flathub?" Y; then install_flatpak; fi
  if ask_yn "Install detected GPU drivers?" Y; then install_gpu_drivers; fi
  if ask_yn "Install full KDE (Plasma + apps + SDDM)?" N; then install_kde_full; fi

  # Repo categories
  if ask_yn "Install Base utils (recommended)?" Y; then install_from_repo "${PKG_BASE[@]}"; fi
  if ask_yn "Install Dev?" N; then install_from_repo "${PKG_DEV[@]}"; fi
  if ask_yn "Install Media?" N; then install_from_repo "${PKG_MEDIA[@]}"; fi
  if ask_yn "Install Browsers?" N; then install_from_repo "${PKG_BROWSERS[@]}"; fi
  if ask_yn "Install Communication?" N; then install_from_repo "${PKG_COMM[@]}"; fi
  if ask_yn "Install Office/Fonts?" N; then install_from_repo "${PKG_OFFICE[@]}"; fi
  if ask_yn "Install Gaming?" N; then install_from_repo "${PKG_GAMING[@]}"; fi

  # Extras Gaming (priorités repo > AUR > Flatpak)
  if (( EXTRAS_GAMING == 1 )) || ask_yn "Installer extras Gaming (Lutris, Heroic, Bottles, PrismLauncher, ProtonUp-Qt) ?" N; then
    install_app_priority "Lutris" lutris lutris "net.lutris.Lutris"
    install_app_priority "Heroic" "" heroic-games-launcher-bin "com.heroicgameslauncher.hgl"
    install_app_priority "Bottles" bottles bottles "com.usebottles.bottles"
    install_app_priority "PrismLauncher" prismlauncher prismlauncher-bin "org.prismlauncher.PrismLauncher"
    install_app_priority "ProtonUp-Qt" protonup-qt protonup-qt "net.davidotek.pupgui2"
  fi

  # Browser extras
  if (( FLAG_CHROMIUM == 1 )) || ask_yn "Install Chromium (repo)?" N; then install_from_repo chromium; fi
  if (( FLAG_CHROME == 1 )) || ask_yn "Install Google Chrome (AUR/Flatpak)?" N; then
    install_app_priority "Google Chrome" "" google-chrome "com.google.Chrome"
  fi
  # Media extras
  if (( FLAG_SPOTIFY == 1 )) || ask_yn "Install Spotify (AUR/Flatpak)?" N; then
    install_app_priority "Spotify" "" spotify "com.spotify.Client"
  fi

  # AUR (optional)
  local helper
  helper=$(detect_aur_helper)
  if [[ -n "$helper" ]]; then
    if ask_yn "Install Dev (AUR)?" N; then install_from_aur "$helper" "${AUR_DEV[@]}"; fi
    if ask_yn "Install Gaming (AUR)?" N; then install_from_aur "$helper" "${AUR_GAMING[@]}"; fi
  else
    warn "AUR helper not detected (paru/yay). Skipping AUR."
  fi

  # Useful services
  if ask_yn "Enable useful services (fstrim, optional Bluetooth)?" Y; then enable_services; fi
  if ask_yn "Configure audio (PipeWire)?" Y; then setup_audio; fi
  if ask_yn "Configure network (NetworkManager)?" Y; then setup_network; fi
  if ask_yn "Configure printing (CUPS)?" N; then setup_printing; fi
  if ask_yn "Configure virtualization (qemu/libvirt/virt-manager)?" N; then setup_virtualization; fi
  if ask_yn "Laptop optimizations (TLP)?" N; then setup_laptop; fi
  if ask_yn "Enable firewall UFW?" N; then setup_firewall; fi

  msg "Post-install complete. Enjoy!"
}

main "$@"
