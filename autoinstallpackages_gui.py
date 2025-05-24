#!/usr/bin/env python3
"""
AutoInstallPackages - Modern GUI Interface with Real Installation
Version: 4.0
Author: Firebleudark
Description: Dark, modern GUI for Arch Linux post-installation with REAL package installation
Repository: https://github.com/Firebleudark/Autoinstallpackages
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any

# Version information
VERSION = "4.0"
AUTHOR = "Firebleudark"

class DarkTheme:
    """Dark theme configuration for modern UI"""
    
    # Color palette
    BG_PRIMARY = "#0a0a0a"
    BG_SECONDARY = "#141414"
    BG_TERTIARY = "#1e1e1e"
    BG_HOVER = "#252525"
    BG_CARD = "#1a1a1a"
    
    ACCENT = "#00d4aa"
    ACCENT_DARK = "#00a085"
    ACCENT_LIGHT = "#00f5c4"
    
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b3b3b3"
    TEXT_MUTED = "#666666"
    
    SUCCESS = "#2ed573"
    WARNING = "#ffa502"
    ERROR = "#ff4757"
    INFO = "#74c0fc"

class PackageCategory:
    """Represents a package category"""
    
    def __init__(self, key: str, name: str, icon: str, description: str, 
                 pacman_packages: List[str], aur_packages: List[str] = None):
        self.key = key
        self.name = name
        self.icon = icon
        self.description = description
        self.pacman_packages = pacman_packages or []
        self.aur_packages = aur_packages or []
        self.selected = False
    
    @property
    def total_packages(self) -> int:
        return len(self.pacman_packages) + len(self.aur_packages)

class AutoInstallGUI:
    """Main GUI application class with REAL installation"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.categories = self._initialize_categories()
        self.options = {
            'flatpak': tk.BooleanVar(),
            'ml4w_dotfiles': tk.BooleanVar(),
            'optimizations': tk.BooleanVar(value=True),
            'cleanup': tk.BooleanVar(value=True)
        }
        
        self.is_installing = False
        
        # Initialize GUI
        self._setup_window()
        self._create_widgets()
        
    def _initialize_categories(self) -> Dict[str, PackageCategory]:
        """Initialize package categories with REAL packages"""
        return {
            'gaming': PackageCategory(
                'gaming', 'Gaming', '🎮',
                'Gaming platforms and tools for optimal gaming experience',
                ['steam', 'lutris', 'gamemode', 'lib32-mesa', 'vulkan-tools'],
                ['heroic-games-launcher-bin', 'prismlauncher-qt5']
            ),
            'multimedia': PackageCategory(
                'multimedia', 'Multimedia', '🎵',
                'Media applications and communication tools',
                ['discord', 'thunderbird', 'vlc', 'obs-studio'],
                ['spotify']
            ),
            'development': PackageCategory(
                'development', 'Development', '💻',
                'Development tools and code editors',
                ['neovim', 'git', 'base-devel', 'docker', 'nodejs', 'npm'],
                ['visual-studio-code-bin', 'github-desktop-bin']
            ),
            'system': PackageCategory(
                'system', 'System Tools', '⚙️',
                'System utilities and administration tools',
                ['timeshift', 'htop', 'btop', 'yazi', 'fastfetch', 'tree', 'unzip'],
                ['arch-update']
            ),
            'office': PackageCategory(
                'office', 'Office Suite', '📄',
                'Complete office productivity suite',
                ['libreoffice-fresh', 'libreoffice-fresh-en-us'],
                ['onlyoffice-bin']
            ),
            'privacy': PackageCategory(
                'privacy', 'Privacy Tools', '🔒',
                'Privacy and security applications',
                ['torbrowser-launcher', 'gnupg', 'veracrypt'],
                ['signal-desktop', 'simplex-chat']
            )
        }
    
    def _setup_window(self):
        """Configure main window"""
        self.root.title(f"AutoInstallPackages v{VERSION}")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        self.root.configure(bg=DarkTheme.BG_PRIMARY)
        
        # Center window
        self._center_window()
    
    def _center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container with scrolling
        self._create_scrollable_container()
        
        # Header
        self._create_header()
        
        # Progress section (hidden initially)
        self._create_progress_section()
        
        # Main content
        self._create_main_content()
        
        # Log section (hidden initially)
        self._create_log_section()
    
    def _create_scrollable_container(self):
        """Create scrollable main container"""
        # Canvas for scrolling
        self.canvas = tk.Canvas(self.root, 
                               bg=DarkTheme.BG_PRIMARY, 
                               highlightthickness=0)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.root, 
                                bg=DarkTheme.BG_SECONDARY,
                                troughcolor=DarkTheme.BG_TERTIARY,
                                orient="vertical", 
                                command=self.canvas.yview)
        
        # Scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg=DarkTheme.BG_PRIMARY)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self._bind_mousewheel()
    
    def _bind_mousewheel(self):
        """Bind mousewheel to canvas scrolling"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def _create_header(self):
        """Create application header"""
        header_frame = tk.Frame(self.scrollable_frame, bg=DarkTheme.BG_SECONDARY, padx=30, pady=30)
        header_frame.pack(fill='x')
        
        # Title section
        title_frame = tk.Frame(header_frame, bg=DarkTheme.BG_SECONDARY)
        title_frame.pack(fill='x')
        
        # Main title
        title_label = tk.Label(title_frame, 
                               text="🚀 AutoInstallPackages", 
                               bg=DarkTheme.BG_SECONDARY,
                               fg=DarkTheme.TEXT_PRIMARY,
                               font=('Segoe UI', 18, 'bold'))
        title_label.pack(side='left')
        
        # Version badge
        version_label = tk.Label(title_frame,
                                text=f"v{VERSION}",
                                bg=DarkTheme.BG_TERTIARY,
                                fg=DarkTheme.TEXT_SECONDARY,
                                font=('Segoe UI', 8, 'bold'),
                                padx=8, pady=2)
        version_label.pack(side='left', padx=(15, 0))
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                  text="Modern post-installation script for Arch Linux",
                                  bg=DarkTheme.BG_SECONDARY,
                                  fg=DarkTheme.TEXT_SECONDARY,
                                  font=('Segoe UI', 10))
        subtitle_label.pack(anchor='w', pady=(10, 0))
        
        # Separator line
        separator = tk.Frame(header_frame, bg=DarkTheme.ACCENT, height=2)
        separator.pack(fill='x', pady=(20, 0))
    
    def _create_progress_section(self):
        """Create progress indicator section"""
        self.progress_frame = tk.Frame(self.scrollable_frame, bg=DarkTheme.BG_SECONDARY, padx=20, pady=20)
        
        # Progress label
        self.progress_label = tk.Label(self.progress_frame, 
                                       text="Initializing...", 
                                       bg=DarkTheme.BG_SECONDARY,
                                       fg=DarkTheme.TEXT_PRIMARY,
                                       font=('Segoe UI', 10))
        self.progress_label.pack()
        
        # Progress bar frame
        progress_bg = tk.Frame(self.progress_frame, bg=DarkTheme.BG_TERTIARY, height=10)
        progress_bg.pack(fill='x', pady=(10, 0))
        
        self.progress_fill = tk.Frame(progress_bg, bg=DarkTheme.ACCENT, height=10)
        self.progress_fill.pack(side='left', fill='y')
        
        # Initially hidden
        self.progress_frame.pack_forget()
    
    def _create_main_content(self):
        """Create main content area"""
        self.main_frame = tk.Frame(self.scrollable_frame, bg=DarkTheme.BG_PRIMARY, padx=30, pady=30)
        self.main_frame.pack(fill='both', expand=True)
        
        # Section title
        section_title = tk.Label(self.main_frame,
                                 text="Select package categories to install",
                                 bg=DarkTheme.BG_PRIMARY,
                                 fg=DarkTheme.TEXT_PRIMARY,
                                 font=('Segoe UI', 14, 'bold'))
        section_title.pack(anchor='w', pady=(0, 20))
        
        # Categories grid
        self._create_categories_grid()
        
        # Options panel
        self._create_options_panel()
        
        # Action buttons
        self._create_action_buttons()
    
    def _create_categories_grid(self):
        """Create package categories grid"""
        # Container for categories
        categories_container = tk.Frame(self.main_frame, bg=DarkTheme.BG_PRIMARY)
        categories_container.pack(fill='x', pady=(0, 25))
        
        self.category_vars = {}
        self.category_frames = {}
        
        # Create category cards in 2-column grid
        for i, (key, category) in enumerate(self.categories.items()):
            row = i // 2
            col = i % 2
            
            # Category variable
            var = tk.BooleanVar()
            self.category_vars[key] = var
            
            # Card frame
            card_frame = tk.Frame(categories_container,
                                 bg=DarkTheme.BG_CARD,
                                 relief='solid',
                                 bd=1,
                                 padx=20, pady=15)
            card_frame.grid(row=row, column=col, padx=8, pady=8, sticky='ew')
            self.category_frames[key] = card_frame
            
            # Card header
            header_frame = tk.Frame(card_frame, bg=DarkTheme.BG_CARD)
            header_frame.pack(fill='x')
            
            # Icon and title
            icon_title_frame = tk.Frame(header_frame, bg=DarkTheme.BG_CARD)
            icon_title_frame.pack(side='left', fill='x', expand=True)
            
            # Icon
            icon_label = tk.Label(icon_title_frame,
                                 text=category.icon,
                                 bg=DarkTheme.BG_CARD,
                                 fg=DarkTheme.TEXT_PRIMARY,
                                 font=('Segoe UI', 20))
            icon_label.pack(side='left')
            
            # Title
            title_label = tk.Label(icon_title_frame,
                                  text=category.name,
                                  bg=DarkTheme.BG_CARD,
                                  fg=DarkTheme.TEXT_PRIMARY,
                                  font=('Segoe UI', 12, 'bold'))
            title_label.pack(side='left', padx=(12, 0))
            
            # Checkbox
            checkbox = tk.Checkbutton(header_frame,
                                     variable=var,
                                     bg=DarkTheme.BG_CARD,
                                     activebackground=DarkTheme.BG_CARD,
                                     selectcolor=DarkTheme.BG_TERTIARY,
                                     command=lambda k=key: self._on_category_toggle(k))
            checkbox.pack(side='right')
            
            # Description
            desc_label = tk.Label(card_frame,
                                 text=category.description,
                                 bg=DarkTheme.BG_CARD,
                                 fg=DarkTheme.TEXT_SECONDARY,
                                 font=('Segoe UI', 9),
                                 wraplength=280,
                                 justify='left')
            desc_label.pack(anchor='w', pady=(8, 5))
            
            # Package count
            count_text = f"{category.total_packages} packages"
            count_label = tk.Label(card_frame,
                                  text=count_text,
                                  bg=DarkTheme.BG_CARD,
                                  fg=DarkTheme.TEXT_MUTED,
                                  font=('Segoe UI', 8))
            count_label.pack(anchor='w')
            
            # Hover effects
            self._bind_card_events(card_frame, key)
        
        # Configure grid weights
        categories_container.columnconfigure(0, weight=1)
        categories_container.columnconfigure(1, weight=1)
    
    def _bind_card_events(self, card_frame, key):
        """Bind hover and click events to category cards"""
        def on_click(event):
            current_value = self.category_vars[key].get()
            self.category_vars[key].set(not current_value)
            self._on_category_toggle(key)
        
        # Bind events to card and all children
        widgets_to_bind = [card_frame]
        for child in card_frame.winfo_children():
            widgets_to_bind.append(child)
            for grandchild in child.winfo_children():
                widgets_to_bind.append(grandchild)
        
        for widget in widgets_to_bind:
            widget.bind("<Button-1>", on_click)
    
    def _create_options_panel(self):
        """Create advanced options panel"""
        options_frame = tk.Frame(self.main_frame,
                                bg=DarkTheme.BG_CARD,
                                relief='solid',
                                bd=1,
                                padx=20, pady=15)
        options_frame.pack(fill='x', pady=(0, 25))
        
        # Title
        options_title = tk.Label(options_frame,
                                text="Advanced Options",
                                bg=DarkTheme.BG_CARD,
                                fg=DarkTheme.TEXT_PRIMARY,
                                font=('Segoe UI', 12, 'bold'))
        options_title.pack(anchor='w', pady=(0, 15))
        
        # Options data
        options_data = [
            ('flatpak', 'Flatpak Support', 'Install Flatpak for additional applications'),
            ('ml4w_dotfiles', 'ML4W Dotfiles', 'Modern Hyprland/Waybar configuration'),
            ('optimizations', 'System Optimizations', 'Gaming and performance improvements'),
            ('cleanup', 'Auto Cleanup', 'Clean package cache after installation')
        ]
        
        for key, title, description in options_data:
            option_frame = tk.Frame(options_frame, bg=DarkTheme.BG_CARD)
            option_frame.pack(fill='x', pady=3)
            
            # Checkbox
            checkbox = tk.Checkbutton(option_frame,
                                     variable=self.options[key],
                                     bg=DarkTheme.BG_CARD,
                                     activebackground=DarkTheme.BG_CARD,
                                     selectcolor=DarkTheme.BG_TERTIARY,
                                     fg=DarkTheme.TEXT_PRIMARY,
                                     font=('Segoe UI', 9))
            checkbox.pack(side='left')
            
            # Text frame
            text_frame = tk.Frame(option_frame, bg=DarkTheme.BG_CARD)
            text_frame.pack(side='left', fill='x', expand=True, padx=(10, 0))
            
            # Title
            title_label = tk.Label(text_frame,
                                  text=title,
                                  bg=DarkTheme.BG_CARD,
                                  fg=DarkTheme.TEXT_PRIMARY,
                                  font=('Segoe UI', 10, 'bold'))
            title_label.pack(anchor='w')
            
            # Description
            desc_label = tk.Label(text_frame,
                                 text=description,
                                 bg=DarkTheme.BG_CARD,
                                 fg=DarkTheme.TEXT_SECONDARY,
                                 font=('Segoe UI', 8))
            desc_label.pack(anchor='w')
    
    def _create_action_buttons(self):
        """Create action buttons"""
        buttons_frame = tk.Frame(self.main_frame, bg=DarkTheme.BG_PRIMARY)
        buttons_frame.pack(pady=25)
        
        # Select all button
        self.select_all_btn = tk.Button(buttons_frame,
                                       text="📦 Select All",
                                       bg=DarkTheme.BG_TERTIARY,
                                       fg=DarkTheme.TEXT_PRIMARY,
                                       font=('Segoe UI', 10),
                                       relief='flat',
                                       padx=25, pady=10,
                                       command=self._select_all_categories)
        self.select_all_btn.pack(side='left', padx=(0, 15))
        
        # Install button
        self.install_btn = tk.Button(buttons_frame,
                                    text="🚀 Start Installation",
                                    bg=DarkTheme.ACCENT,
                                    fg=DarkTheme.BG_PRIMARY,
                                    font=('Segoe UI', 10, 'bold'),
                                    relief='flat',
                                    padx=25, pady=10,
                                    state='disabled',
                                    command=self._start_installation)
        self.install_btn.pack(side='left')
    
    def _create_log_section(self):
        """Create installation log section"""
        self.log_frame = tk.Frame(self.scrollable_frame, bg=DarkTheme.BG_PRIMARY, padx=30, pady=30)
        
        # Title
        log_title = tk.Label(self.log_frame,
                             text="Installation Log",
                             bg=DarkTheme.BG_PRIMARY,
                             fg=DarkTheme.TEXT_PRIMARY,
                             font=('Segoe UI', 12, 'bold'))
        log_title.pack(anchor='w', pady=(0, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(self.log_frame,
                                                 height=20,
                                                 bg=DarkTheme.BG_TERTIARY,
                                                 fg=DarkTheme.TEXT_PRIMARY,
                                                 insertbackground=DarkTheme.TEXT_PRIMARY,
                                                 font=('Consolas', 9),
                                                 wrap=tk.WORD,
                                                 relief='solid',
                                                 bd=1)
        self.log_text.pack(fill='both', expand=True)
        
        # Configure log colors
        self.log_text.tag_configure("INFO", foreground=DarkTheme.INFO)
        self.log_text.tag_configure("SUCCESS", foreground=DarkTheme.SUCCESS)
        self.log_text.tag_configure("WARNING", foreground=DarkTheme.WARNING)
        self.log_text.tag_configure("ERROR", foreground=DarkTheme.ERROR)
        
        # Initially hidden
        self.log_frame.pack_forget()
    
    def _on_category_toggle(self, key):
        """Handle category selection toggle"""
        self.categories[key].selected = self.category_vars[key].get()
        self._update_install_button()
    
    def _update_install_button(self):
        """Update install button state and text"""
        selected_count = sum(1 for cat in self.categories.values() if cat.selected)
        
        if selected_count == 0:
            self.install_btn.configure(text="🚀 Start Installation", state='disabled')
        else:
            category_text = "category" if selected_count == 1 else "categories"
            self.install_btn.configure(
                text=f"🚀 Install {selected_count} {category_text}",
                state='normal'
            )
    
    def _select_all_categories(self):
        """Toggle all categories selection"""
        all_selected = all(cat.selected for cat in self.categories.values())
        
        for key, var in self.category_vars.items():
            var.set(not all_selected)
            self.categories[key].selected = not all_selected
        
        self._update_install_button()
        
        # Update button text
        if all_selected:
            self.select_all_btn.configure(text="📦 Select All")
        else:
            self.select_all_btn.configure(text="📦 Deselect All")
    
    def _start_installation(self):
        """Start the REAL installation process"""
        if self.is_installing:
            return
        
        selected_categories = [cat for cat in self.categories.values() if cat.selected]
        
        if not selected_categories:
            messagebox.showwarning("No Selection", "Please select at least one category.")
            return
        
        # Confirmation dialog
        category_names = [cat.name for cat in selected_categories]
        total_packages = sum(cat.total_packages for cat in selected_categories)
        
        message = f"This will REALLY install {len(selected_categories)} categories with approximately {total_packages} packages!\n\n"
        message += "Selected categories:\n"
        message += "\n".join(f"• {name}" for name in category_names)
        message += "\n\n⚠️ THIS IS REAL INSTALLATION! Continue?"
        
        if not messagebox.askyesno("Confirm REAL Installation", message):
            return
        
        # Start installation
        self.is_installing = True
        self._show_installation_view()
        
        # Start installation thread
        install_thread = threading.Thread(
            target=self._run_real_installation,  # REAL installation function
            args=(selected_categories,),
            daemon=True
        )
        install_thread.start()
    
    def _show_installation_view(self):
        """Switch to installation view"""
        # Hide main content
        self.main_frame.pack_forget()
        
        # Show progress and logs
        self.progress_frame.pack(fill='x', pady=(0, 20))
        self.log_frame.pack(fill='both', expand=True)
        
        # Disable buttons
        self.install_btn.configure(state='disabled')
        self.select_all_btn.configure(state='disabled')
    
    def _run_real_installation(self, selected_categories):
        """Run REAL installation process"""
        try:
            total_steps = 5 + len(selected_categories)
            current_step = 0
            
            # Step 1: System validation
            self.root.after(0, self._update_progress, current_step, total_steps, "Validating system...")
            self.root.after(0, self._add_log, "[INFO] Validating system requirements...", "INFO")
            
            if not self._validate_system():
                raise Exception("System validation failed")
            
            self.root.after(0, self._add_log, "[SUCCESS] System validation passed", "SUCCESS")
            current_step += 1
            
            # Step 2: System update
            self.root.after(0, self._update_progress, current_step, total_steps, "Updating system...")
            self.root.after(0, self._add_log, "[INFO] Updating system packages...", "INFO")
            
            if self._run_command("sudo pacman -Syu --noconfirm"):
                self.root.after(0, self._add_log, "[SUCCESS] System updated successfully", "SUCCESS")
            else:
                self.root.after(0, self._add_log, "[WARNING] System update had issues", "WARNING")
            
            current_step += 1
            
            # Step 3: Install paru if needed
            self.root.after(0, self._update_progress, current_step, total_steps, "Installing AUR helper...")
            self.root.after(0, self._add_log, "[INFO] Checking for paru AUR helper...", "INFO")
            
            if not self._check_paru():
                self._install_paru()
            
            self.root.after(0, self._add_log, "[SUCCESS] AUR helper ready", "SUCCESS")
            current_step += 1
            
            # Step 4: GPU drivers
            self.root.after(0, self._update_progress, current_step, total_steps, "Installing GPU drivers...")
            self.root.after(0, self._add_log, "[INFO] Detecting and installing GPU drivers...", "INFO")
            
            self._install_gpu_drivers()
            self.root.after(0, self._add_log, "[SUCCESS] GPU drivers installed", "SUCCESS")
            current_step += 1
            
            # Step 5-N: Install selected categories
            for category in selected_categories:
                self.root.after(0, self._update_progress, current_step, total_steps, f"Installing {category.name}...")
                self.root.after(0, self._add_log, f"[INFO] Installing {category.name} packages...", "INFO")
                
                # Install pacman packages
                if category.pacman_packages:
                    cmd = f"sudo pacman -S --needed --noconfirm {' '.join(category.pacman_packages)}"
                    if self._run_command(cmd):
                        self.root.after(0, self._add_log, f"[SUCCESS] {category.name} pacman packages installed", "SUCCESS")
                    else:
                        self.root.after(0, self._add_log, f"[WARNING] Some {category.name} pacman packages failed", "WARNING")
                
                # Install AUR packages
                if category.aur_packages:
                    cmd = f"paru -S --needed --noconfirm {' '.join(category.aur_packages)}"
                    if self._run_command(cmd):
                        self.root.after(0, self._add_log, f"[SUCCESS] {category.name} AUR packages installed", "SUCCESS")
                    else:
                        self.root.after(0, self._add_log, f"[WARNING] Some {category.name} AUR packages failed", "WARNING")
                
                current_step += 1
            
            # Optional installations
            if self.options['optimizations'].get():
                self.root.after(0, self._update_progress, current_step, total_steps, "Applying optimizations...")
                self.root.after(0, self._add_log, "[INFO] Applying system optimizations...", "INFO")
                self._apply_optimizations()
                self.root.after(0, self._add_log, "[SUCCESS] System optimizations applied", "SUCCESS")
            
            if self.options['cleanup'].get():
                self.root.after(0, self._update_progress, current_step, total_steps, "Cleaning system...")
                self.root.after(0, self._add_log, "[INFO] Cleaning system...", "INFO")
                self._cleanup_system()
                self.root.after(0, self._add_log, "[SUCCESS] System cleaned", "SUCCESS")
            
            current_step += 1
            
            # Installation completed
            self.root.after(0, self._installation_completed)
            
        except Exception as e:
            self.root.after(0, self._add_log, f"[ERROR] Installation failed: {str(e)}", "ERROR")
            self.root.after(0, self._installation_failed, str(e))
    
    def _validate_system(self) -> bool:
        """Validate system requirements"""
        try:
            # Check Arch Linux
            with open('/etc/os-release', 'r') as f:
                if 'Arch Linux' not in f.read():
                    return False
            
            # Check if not root
            if os.geteuid() == 0:
                return False
            
            # Check internet connection
            result = subprocess.run(['ping', '-c', '1', 'google.com'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
            
        except:
            return False
    
    def _run_command(self, cmd: str) -> bool:
        """Run a system command and log output"""
        try:
            self.root.after(0, self._add_log, f"[CMD] {cmd}", "INFO")
            
            process = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Read output line by line and log it
            for line in process.stdout:
                line = line.strip()
                if line:
                    self.root.after(0, self._add_log, line, "INFO")
            
            process.wait()
            return process.returncode == 0
            
        except Exception as e:
            self.root.after(0, self._add_log, f"[ERROR] Command failed: {str(e)}", "ERROR")
            return False
    
    def _check_paru(self) -> bool:
        """Check if paru is installed"""
        try:
            result = subprocess.run(['which', 'paru'], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def _install_paru(self):
        """Install paru AUR helper"""
        self.root.after(0, self._add_log, "[INFO] Installing paru AUR helper...", "INFO")
        
        # Install base-devel first
        self._run_command("sudo pacman -S --needed --noconfirm base-devel git")
        
        # Clone and build paru
        temp_dir = "/tmp/paru_install"
        commands = [
            f"rm -rf {temp_dir}",
            f"git clone https://aur.archlinux.org/paru.git {temp_dir}",
            f"cd {temp_dir} && makepkg -si --noconfirm"
        ]
        
        for cmd in commands:
            if not self._run_command(cmd):
                self.root.after(0, self._add_log, "[WARNING] Paru installation may have issues", "WARNING")
                break
        
        # Cleanup
        self._run_command(f"rm -rf {temp_dir}")
    
    def _install_gpu_drivers(self):
        """Detect and install GPU drivers"""
        try:
            # Get GPU info
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            gpu_info = result.stdout.lower()
            
            drivers = []
            
            if 'amd' in gpu_info or 'radeon' in gpu_info:
                self.root.after(0, self._add_log, "[INFO] AMD GPU detected", "INFO")
                drivers = ['mesa', 'lib32-mesa', 'vulkan-radeon', 'lib32-vulkan-radeon']
            elif 'nvidia' in gpu_info:
                self.root.after(0, self._add_log, "[INFO] NVIDIA GPU detected", "INFO")
                drivers = ['nvidia', 'nvidia-utils', 'lib32-nvidia-utils']
            elif 'intel' in gpu_info:
                self.root.after(0, self._add_log, "[INFO] Intel GPU detected", "INFO")
                drivers = ['mesa', 'lib32-mesa', 'vulkan-intel', 'lib32-vulkan-intel']
            
            if drivers:
                cmd = f"sudo pacman -S --needed --noconfirm {' '.join(drivers)}"
                self._run_command(cmd)
            else:
                self.root.after(0, self._add_log, "[INFO] No specific GPU drivers needed", "INFO")
                
        except Exception as e:
            self.root.after(0, self._add_log, f"[WARNING] GPU detection failed: {str(e)}", "WARNING")
    
    def _apply_optimizations(self):
        """Apply system optimizations"""
        try:
            # Enable parallel downloads
            self._run_command("sudo sed -i 's/#ParallelDownloads = 5/ParallelDownloads = 10/' /etc/pacman.conf")
            
            # Enable multicore compilation
            cores = os.cpu_count()
            self._run_command(f"sudo sed -i 's/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j{cores}\"/' /etc/makepkg.conf")
            
            # Add user to gamemode group if gamemode is installed
            username = os.getenv('USER')
            if username:
                self._run_command(f"sudo usermod -aG gamemode {username}")
                
        except Exception as e:
            self.root.after(0, self._add_log, f"[WARNING] Some optimizations failed: {str(e)}", "WARNING")
    
    def _cleanup_system(self):
        """Clean up system"""
        try:
            # Clean package cache
            self._run_command("sudo paccache -r")
            
            # Clean AUR cache if paru is available
            if self._check_paru():
                self._run_command("paru -Sc --noconfirm")
            
            # Remove orphaned packages
            result = subprocess.run(['pacman', '-Qtdq'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                orphans = result.stdout.strip()
                self._run_command(f"sudo pacman -Rns --noconfirm {orphans}")
            else:
                self.root.after(0, self._add_log, "[INFO] No orphaned packages found", "INFO")
                
        except Exception as e:
            self.root.after(0, self._add_log, f"[WARNING] Cleanup had issues: {str(e)}", "WARNING")
    
    def _update_progress(self, current, total, text):
        """Update progress bar and text"""
        progress_percent = (current / total) * 100
        
        # Update progress bar width
        total_width = 500  # Assuming canvas width
        fill_width = int((progress_percent / 100) * total_width)
        self.progress_fill.configure(width=fill_width)
        
        # Update text
        self.progress_label.configure(text=f"{text} ({int(progress_percent)}%)")
    
    def _add_log(self, message, log_type):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_line, log_type)
        self.log_text.see(tk.END)
    
    def _installation_completed(self):
        """Handle successful installation completion"""
        self.is_installing = False
        self.progress_label.configure(text="Installation completed successfully! (100%)")
        
        messagebox.showinfo(
            "Installation Complete",
            "🎉 Installation completed successfully!\n\n"
            "Your Arch Linux system has been enhanced with the selected packages.\n"
            "System restart is recommended to apply all changes."
        )
        
        # Ask for restart
        if messagebox.askyesno("Restart System", "Would you like to restart your system now?"):
            self._add_log("[INFO] Restarting system...", "INFO")
            try:
                subprocess.run(["sudo", "reboot"], check=True)
            except:
                messagebox.showinfo("Manual Restart", "Please restart your system manually.")
    
    def _installation_failed(self, error_message):
        """Handle installation failure"""
        self.is_installing = False
        messagebox.showerror(
            "Installation Failed",
            f"An error occurred during installation:\n\n{error_message}\n\n"
            "Check the installation log for more details."
        )
    
    def _check_system_requirements(self):
        """Check if system meets requirements"""
        errors = []
        
        # Check if Arch Linux
        try:
            with open('/etc/os-release', 'r') as f:
                if 'Arch Linux' not in f.read():
                    errors.append("This application is only for Arch Linux")
        except:
            errors.append("Cannot verify operating system")
        
        # Check if running as root
        if os.geteuid() == 0:
            errors.append("Do not run this application as root")
        
        # Check internet connection
        try:
            subprocess.run(['ping', '-c', '1', 'google.com'], 
                          check=True, capture_output=True, timeout=5)
        except:
            errors.append("Internet connection required")
        
        return errors
    
    def run(self):
        """Start the GUI application"""
        # System requirements check
        errors = self._check_system_requirements()
        if errors:
            error_message = "System requirements not met:\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("System Check Failed", error_message)
            return False
        
        # Start GUI
        try:
            self.root.mainloop()
            return True
        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
            return False
        except Exception as e:
            messagebox.showerror("Application Error", f"An unexpected error occurred:\n\n{str(e)}")
            return False

def main():
    """Main entry point"""
    print("🚀 Starting AutoInstallPackages GUI with REAL installation...")
    
    try:
        app = AutoInstallGUI()
        success = app.run()
        
        if success:
            print("✅ GUI application completed successfully")
        else:
            print("❌ GUI application exited with errors")
            return 1
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
