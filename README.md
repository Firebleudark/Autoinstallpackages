# Autoinstallpackages — Simple Arch Post-install

Simple, readable Arch Linux post-install tool. It performs essential preflight checks, installs drivers, configures core services, and offers app categories. Three ready-to-use profiles: minimal, gaming, and full KDE.

## Features
- Preflight: distro check (Arch), sudo validation, network reachability, pacman database sync, NTP sync, pacman GPG keys.
- GPU drivers: AMD/Intel (Mesa/Vulkan), NVIDIA (nouveau by default; proprietary optional).
- System setup: multilib, Flatpak + Flathub, PipeWire/WirePlumber, NetworkManager, printing (CUPS), virtualization (qemu/libvirt/virt-manager), laptop (TLP), firewall (UFW), useful services (fstrim + optional Bluetooth).
- App categories: Base, Dev, Media, Browsers, Communication, Office/Fonts, Gaming.
- Source priority: repo > AUR (paru auto if needed) > Flatpak.
- GUI wrapper: optional Tkinter app with subtle dark theme and direct controls.

## Requirements
- Arch Linux (or derivative with pacman).
- Internet access; sudo privileges.
- For GUI: Python 3 and Tk (package `tk`).
- Tools used: `pciutils` (lspci), `curl`, `ping` (optional), `systemd` (timedatectl), `git` and `base-devel` (for AUR helper install when needed), `flatpak` (if chosen).

## Profiles
- minimal: open-source GPU drivers, Base utils, audio, network, firewall; no multilib/Flatpak/KDE.
- gaming: multilib + Flatpak, GPU drivers, Base + Gaming (Steam, Gamemode, MangoHUD) + gaming extras (Lutris, Heroic, Bottles, PrismLauncher, ProtonUp-Qt), audio/network, services.
- kde: full KDE Plasma + KDE Apps + SDDM, Base utils, audio/network, services.

## Source Priority Policy
When installing a specific app, the tool tries in this order:
1) Official Arch repo via pacman
2) AUR via `paru` (or `yay`) — if no helper is present, it offers to install `paru` automatically
3) Flatpak from Flathub

## CLI Usage
```bash
# Interactive
bash v5/simple-postinstall.sh

# Non-interactive profiles
bash v5/simple-postinstall.sh --profile minimal --yes
bash v5/simple-postinstall.sh --profile gaming  --yes
bash v5/simple-postinstall.sh --profile kde     --yes

# Dry-run (no changes)
bash v5/simple-postinstall.sh --dry-run

# Skip AUR entirely
bash v5/simple-postinstall.sh --skip-aur

# Preflight only (report and exit)
bash v5/simple-postinstall.sh --check

# Extras toggles (non-interactive)
bash v5/simple-postinstall.sh --yes --profile minimal \
  --gaming-extras --install-chromium --install-chrome --install-spotify
```

## GUI Usage
```bash
python3 gui/app.py
```
- Select a profile (Minimal, Gaming, KDE) and optional extras.
- Preflight button runs non-intrusive checks.
- Install button runs the Bash script with your selection.

## Notes on NVIDIA Drivers
- The default path for NVIDIA is open-source `nouveau` (removes proprietary `nvidia*` if present and installs `xf86-video-nouveau` + `mesa`, and `vulkan-nouveau` when available).
- You can opt-in to proprietary drivers during the prompt.
- A reboot is recommended after switching drivers.

## Safety & Idempotency
- Most operations are idempotent (safe to re-run).
- The script prompts before major changes (unless `--yes`).
- Preflight tries to auto-fix safe items (NTP, pacman keys) when reasonable.

## License
[GPLv3](LICENSE)
