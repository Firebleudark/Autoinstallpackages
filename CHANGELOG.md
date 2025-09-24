# Changelog

## v5.0.0 — Simple Post-install + GUI wrapper

- Rewrite focused on a single, readable Bash script: `v5/simple-postinstall.sh`.
- Robust preflight checks: distro (Arch), sudo, network, pacman sync, NTP, pacman GPG keys.
- Profiles: `minimal`, `gaming`, `kde` (non-interactive with `--yes`).
- GPU drivers: AMD/Intel (Mesa/Vulkan), NVIDIA open-source `nouveau` by default with opt-in proprietary.
- System setup: multilib, Flatpak + Flathub, PipeWire/WirePlumber, NetworkManager, CUPS, virtualization (qemu/libvirt/virt-manager), TLP, UFW, useful services.
- Categories: Base, Dev, Media, Browsers, Communication, Office/Fonts, Gaming.
- Source priority policy: repo > AUR (paru auto-install if needed) > Flatpak.
- Tkinter GUI: `gui/app.py` (subtle dark theme), profiles exposed, extras toggles, preflight button, live logs.
- Repository cleanup: removed legacy GUI and complex scaffolding; simplified doc in English.

### Notes
- Requires Python `tk` for GUI. CLI does not need Python.
- A reboot is recommended after switching NVIDIA drivers.
