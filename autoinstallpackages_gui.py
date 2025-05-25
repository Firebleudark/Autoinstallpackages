#!/usr/bin/env python3
"""
AutoInstallPackages - Modern Futuristic GUI Interface
Version: 4.1-1
Author: Firebleudark
Description: Futuristic, minimalist GUI for Arch Linux post-installation
Repository: https://github.com/Firebleudark/Autoinstallpackages
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import sys
import os
import time
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple
import random

# Version information
VERSION = "4.1-1"
AUTHOR = "Firebleudark"

class FuturisticTheme:
    """Futuristic dark theme with neon accents"""
    
    # Base colors
    BG_MAIN = "#0a0a0f"
    BG_CARD = "#12121a"
    BG_CARD_HOVER = "#1a1a25"
    BG_SELECTED = "#1e1e2e"
    
    # Glassmorphism
    GLASS_BG = "#151520"
    GLASS_BORDER = "#2a2a3e"
    
    # Neon accents
    NEON_CYAN = "#00ffff"
    NEON_PURPLE = "#bd00ff"
    NEON_PINK = "#ff0080"
    NEON_GREEN = "#00ff88"
    
    # Gradients
    GRADIENT_START = "#00ffff"
    GRADIENT_END = "#bd00ff"
    
    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0b8"
    TEXT_MUTED = "#606078"
    
    # Status colors
    SUCCESS = "#00ff88"
    WARNING = "#ffaa00"
    ERROR = "#ff0055"
    INFO = "#00aaff"

class AnimatedCard(tk.Frame):
    """Animated card component with hover effects"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=FuturisticTheme.BG_CARD, relief='flat')
        self.is_hovered = False
        self.is_selected = False
        self.animation_id = None
        self.glow_intensity = 0
        
    def bind_hover_events(self):
        """Bind hover events for animation"""
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Bind to all children
        for child in self.winfo_children():
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter"""
        self.is_hovered = True
        self._animate_glow()
        
    def _on_leave(self, event):
        """Handle mouse leave"""
        self.is_hovered = False
        
    def _animate_glow(self):
        """Animate glow effect"""
        if self.is_hovered and self.glow_intensity < 1:
            self.glow_intensity = min(1, self.glow_intensity + 0.1)
        elif not self.is_hovered and self.glow_intensity > 0:
            self.glow_intensity = max(0, self.glow_intensity - 0.1)
        
        # Update background color
        if self.glow_intensity > 0:
            r, g, b = 26, 26, 37  # Base color
            r = int(r + (10 * self.glow_intensity))
            g = int(g + (10 * self.glow_intensity))
            b = int(b + (15 * self.glow_intensity))
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.configure(bg=color)
            
            # Update children backgrounds
            for child in self.winfo_children():
                if isinstance(child, (tk.Label, tk.Frame)):
                    child.configure(bg=color)
        
        # Continue animation if needed
        if self.glow_intensity > 0 or self.is_hovered:
            self.animation_id = self.after(30, self._animate_glow)

class CircularProgress(tk.Canvas):
    """Circular progress indicator"""
    
    def __init__(self, parent, size=200, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        self.size = size
        self.configure(bg=FuturisticTheme.BG_MAIN, highlightthickness=0)
        
        self.progress = 0
        self.arc_id = None
        self.text_id = None
        self.particles = []
        
        self._create_elements()
        
    def _create_elements(self):
        """Create progress elements"""
        center = self.size // 2
        radius = self.size // 2 - 20
        
        # Background circle
        self.create_oval(
            center - radius, center - radius,
            center + radius, center + radius,
            outline=FuturisticTheme.GLASS_BORDER,
            width=3
        )
        
        # Progress arc
        self.arc_id = self.create_arc(
            center - radius, center - radius,
            center + radius, center + radius,
            start=90, extent=0,
            outline=FuturisticTheme.NEON_CYAN,
            width=8,
            style='arc'
        )
        
        # Center text
        self.text_id = self.create_text(
            center, center,
            text="0%",
            font=('Segoe UI', 24, 'bold'),
            fill=FuturisticTheme.TEXT_PRIMARY
        )
        
    def set_progress(self, value):
        """Update progress value with animation"""
        self.progress = max(0, min(100, value))
        extent = -(self.progress * 3.6)  # Convert to degrees
        
        self.itemconfig(self.arc_id, extent=extent)
        self.itemconfig(self.text_id, text=f"{int(self.progress)}%")
        
        # Add particle effect at high progress
        if self.progress > 80:
            self._create_particle()
            
    def _create_particle(self):
        """Create particle effect"""
        if len(self.particles) > 10:
            return
            
        center = self.size // 2
        radius = self.size // 2 - 20
        
        # Random position on the arc
        angle = math.radians(90 - (self.progress * 3.6))
        x = center + radius * math.cos(angle)
        y = center - radius * math.sin(angle)
        
        particle = self.create_oval(
            x-3, y-3, x+3, y+3,
            fill=FuturisticTheme.NEON_CYAN,
            outline=""
        )
        
        self.particles.append(particle)
        self._animate_particle(particle, x, y)
        
    def _animate_particle(self, particle, x, y):
        """Animate particle movement"""
        dx = random.uniform(-2, 2)
        dy = random.uniform(-3, -1)
        
        def move():
            coords = self.coords(particle)
            if not coords or coords[1] < 0:
                self.delete(particle)
                self.particles.remove(particle)
                return
                
            self.move(particle, dx, dy)
            self.after(50, move)
            
        move()

class ModernAutoInstallGUI:
    """Modern futuristic GUI application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Data
        self.categories = self._initialize_categories()
        self.selected_categories = set()
        self.is_installing = False
        
        # UI elements
        self.cards = {}
        self.current_view = "selection"  # selection, installing, complete
        
        # Create UI
        self._create_main_interface()
        
    def setup_window(self):
        """Configure main window with modern styling"""
        self.root.title(f"AutoInstallPackages {VERSION}")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg=FuturisticTheme.BG_MAIN)
        
        # Make window slightly transparent (if supported)
        try:
            self.root.attributes('-alpha', 0.98)
        except:
            pass
            
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f'1200x800+{x}+{y}')
        
        # Custom window styling
        self.root.tk_setPalette(background=FuturisticTheme.BG_MAIN)
        
    def _initialize_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize package categories with icons and descriptions"""
        return {
            'gaming': {
                'name': 'Gaming',
                'icon': '🎮',
                'description': 'Ultimate gaming setup with GPU drivers',
                'color': FuturisticTheme.NEON_PURPLE,
                'packages': {
                    'pacman': ['steam', 'lutris', 'gamemode', 'lib32-mesa', 'vulkan-tools'],
                    'aur': ['heroic-games-launcher-bin', 'prismlauncher-qt5']
                }
            },
            'development': {
                'name': 'Development',
                'icon': '⚡',
                'description': 'Modern development environment',
                'color': FuturisticTheme.NEON_CYAN,
                'packages': {
                    'pacman': ['neovim', 'git', 'docker', 'nodejs', 'npm', 'base-devel'],
                    'aur': ['visual-studio-code-bin']
                }
            },
            'multimedia': {
                'name': 'Multimedia',
                'icon': '🎵',
                'description': 'Media and communication suite',
                'color': FuturisticTheme.NEON_PINK,
                'packages': {
                    'pacman': ['discord', 'thunderbird', 'vlc', 'obs-studio'],
                    'aur': ['spotify']
                }
            },
            'system': {
                'name': 'System Tools',
                'icon': '🛠️',
                'description': 'Essential system utilities',
                'color': FuturisticTheme.NEON_GREEN,
                'packages': {
                    'pacman': ['timeshift', 'htop', 'btop', 'yazi', 'fastfetch'],
                    'aur': ['arch-update']
                }
            },
            'office': {
                'name': 'Office Suite',
                'icon': '📊',
                'description': 'Productivity applications',
                'color': '#ff6b6b',
                'packages': {
                    'pacman': ['libreoffice-fresh'],
                    'aur': ['onlyoffice-bin']
                }
            },
            'privacy': {
                'name': 'Privacy',
                'icon': '🔐',
                'description': 'Security and privacy tools',
                'color': '#4ecdc4',
                'packages': {
                    'pacman': ['torbrowser-launcher', 'gnupg', 'veracrypt'],
                    'aur': ['signal-desktop']
                }
            }
        }
    
    def _create_main_interface(self):
        """Create the main interface layout"""
        # Header
        self._create_header()
        
        # Main container
        self.main_container = tk.Frame(self.root, bg=FuturisticTheme.BG_MAIN)
        self.main_container.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Selection view (default)
        self._create_selection_view()
        
        # Installation view (hidden initially)
        self._create_installation_view()
        
        # Complete view (hidden initially)
        self._create_complete_view()
        
    def _create_header(self):
        """Create futuristic header"""
        header = tk.Frame(self.root, bg=FuturisticTheme.BG_MAIN, height=120)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Logo and title container
        title_container = tk.Frame(header, bg=FuturisticTheme.BG_MAIN)
        title_container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Animated logo
        logo_canvas = tk.Canvas(
            title_container, 
            width=60, height=60,
            bg=FuturisticTheme.BG_MAIN,
            highlightthickness=0
        )
        logo_canvas.pack(side='left', padx=(0, 20))
        
        # Draw arch logo shape
        logo_canvas.create_polygon(
            30, 10, 50, 50, 30, 40, 10, 50,
            fill=FuturisticTheme.NEON_CYAN,
            outline=FuturisticTheme.NEON_PURPLE,
            width=2
        )
        
        # Title with gradient effect
        title_frame = tk.Frame(title_container, bg=FuturisticTheme.BG_MAIN)
        title_frame.pack(side='left')
        
        title = tk.Label(
            title_frame,
            text="AutoInstallPackages",
            font=('Segoe UI', 28, 'bold'),
            fg=FuturisticTheme.TEXT_PRIMARY,
            bg=FuturisticTheme.BG_MAIN
        )
        title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Arch Linux Post-Installation Suite",
            font=('Segoe UI', 11),
            fg=FuturisticTheme.TEXT_SECONDARY,
            bg=FuturisticTheme.BG_MAIN
        )
        subtitle.pack()
        
        # Version badge
        version_label = tk.Label(
            title_container,
            text=f"v{VERSION}",
            font=('Segoe UI', 9, 'bold'),
            fg=FuturisticTheme.NEON_CYAN,
            bg=FuturisticTheme.BG_CARD,
            padx=10,
            pady=3
        )
        version_label.pack(side='left', padx=(20, 0))
        
    def _create_selection_view(self):
        """Create package selection view"""
        self.selection_frame = tk.Frame(self.main_container, bg=FuturisticTheme.BG_MAIN)
        self.selection_frame.pack(fill='both', expand=True)
        
        # Instructions
        instructions = tk.Label(
            self.selection_frame,
            text="Select packages to enhance your system",
            font=('Segoe UI', 14),
            fg=FuturisticTheme.TEXT_SECONDARY,
            bg=FuturisticTheme.BG_MAIN
        )
        instructions.pack(pady=(0, 30))
        
        # Categories grid
        categories_frame = tk.Frame(self.selection_frame, bg=FuturisticTheme.BG_MAIN)
        categories_frame.pack(fill='both', expand=True)
        
        # Create category cards in a 3x2 grid
        row, col = 0, 0
        for key, category in self.categories.items():
            self._create_category_card(categories_frame, key, category, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(3):
            categories_frame.columnconfigure(i, weight=1, minsize=350)
        for i in range(2):
            categories_frame.rowconfigure(i, weight=1)
            
        # Action buttons
        self._create_action_buttons()
        
    def _create_category_card(self, parent, key, category, row, col):
        """Create an animated category card"""
        # Card container
        card = AnimatedCard(parent)
        card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
        self.cards[key] = card
        
        # Inner container with padding
        inner = tk.Frame(card, bg=FuturisticTheme.BG_CARD, padx=25, pady=20)
        inner.pack(fill='both', expand=True)
        
        # Header with icon and selection indicator
        header = tk.Frame(inner, bg=FuturisticTheme.BG_CARD)
        header.pack(fill='x', pady=(0, 15))
        
        # Icon with glow effect
        icon_frame = tk.Frame(header, bg=FuturisticTheme.BG_CARD)
        icon_frame.pack(side='left')
        
        icon_label = tk.Label(
            icon_frame,
            text=category['icon'],
            font=('Segoe UI', 32),
            bg=FuturisticTheme.BG_CARD
        )
        icon_label.pack()
        
        # Title and package count
        info_frame = tk.Frame(header, bg=FuturisticTheme.BG_CARD)
        info_frame.pack(side='left', fill='x', expand=True, padx=(15, 0))
        
        name_label = tk.Label(
            info_frame,
            text=category['name'],
            font=('Segoe UI', 16, 'bold'),
            fg=FuturisticTheme.TEXT_PRIMARY,
            bg=FuturisticTheme.BG_CARD
        )
        name_label.pack(anchor='w')
        
        # Package count with color
        total_packages = len(category['packages']['pacman']) + len(category['packages']['aur'])
        count_label = tk.Label(
            info_frame,
            text=f"{total_packages} packages",
            font=('Segoe UI', 10),
            fg=category['color'],
            bg=FuturisticTheme.BG_CARD
        )
        count_label.pack(anchor='w')
        
        # Selection indicator (checkbox styled)
        check_frame = tk.Frame(header, bg=FuturisticTheme.BG_CARD)
        check_frame.pack(side='right')
        
        check_canvas = tk.Canvas(
            check_frame,
            width=30, height=30,
            bg=FuturisticTheme.BG_CARD,
            highlightthickness=0
        )
        check_canvas.pack()
        
        # Draw custom checkbox
        check_canvas.create_rectangle(
            5, 5, 25, 25,
            outline=FuturisticTheme.GLASS_BORDER,
            width=2,
            tags="box"
        )
        
        # Checkmark (hidden initially)
        check_canvas.create_line(
            10, 15, 13, 18, 20, 11,
            fill=category['color'],
            width=3,
            state='hidden',
            tags="check"
        )
        
        card.check_canvas = check_canvas
        card.is_selected = False
        
        # Description
        desc_label = tk.Label(
            inner,
            text=category['description'],
            font=('Segoe UI', 11),
            fg=FuturisticTheme.TEXT_SECONDARY,
            bg=FuturisticTheme.BG_CARD,
            wraplength=300,
            justify='left'
        )
        desc_label.pack(anchor='w', pady=(0, 15))
        
        # Package details
        details_frame = tk.Frame(inner, bg=FuturisticTheme.BG_CARD)
        details_frame.pack(fill='x')
        
        if category['packages']['pacman']:
            pacman_label = tk.Label(
                details_frame,
                text=f"📦 {len(category['packages']['pacman'])} official",
                font=('Segoe UI', 9),
                fg=FuturisticTheme.TEXT_MUTED,
                bg=FuturisticTheme.BG_CARD
            )
            pacman_label.pack(side='left', padx=(0, 15))
            
        if category['packages']['aur']:
            aur_label = tk.Label(
                details_frame,
                text=f"🔧 {len(category['packages']['aur'])} AUR",
                font=('Segoe UI', 9),
                fg=FuturisticTheme.TEXT_MUTED,
                bg=FuturisticTheme.BG_CARD
            )
            aur_label.pack(side='left')
        
        # Bind click events
        def toggle_selection(event=None):
            self._toggle_category(key, card)
            
        card.bind("<Button-1>", toggle_selection)
        for widget in [inner, header, icon_frame, icon_label, info_frame, 
                      name_label, count_label, desc_label, details_frame]:
            widget.bind("<Button-1>", toggle_selection)
            
        # Bind hover events
        card.bind_hover_events()
        
    def _toggle_category(self, key, card):
        """Toggle category selection with animation"""
        if card.is_selected:
            self.selected_categories.remove(key)
            card.check_canvas.itemconfig("check", state='hidden')
            card.check_canvas.itemconfig("box", outline=FuturisticTheme.GLASS_BORDER)
        else:
            self.selected_categories.add(key)
            card.check_canvas.itemconfig("check", state='normal')
            card.check_canvas.itemconfig("box", outline=self.categories[key]['color'])
            
        card.is_selected = not card.is_selected
        self._update_install_button()
        
    def _create_action_buttons(self):
        """Create futuristic action buttons"""
        button_frame = tk.Frame(self.selection_frame, bg=FuturisticTheme.BG_MAIN)
        button_frame.pack(pady=30)
        
        # Select All button
        self.select_all_btn = self._create_button(
            button_frame,
            "Select All",
            FuturisticTheme.GLASS_BG,
            command=self._toggle_all
        )
        self.select_all_btn.pack(side='left', padx=10)
        
        # Install button (glowing)
        self.install_btn = self._create_button(
            button_frame,
            "Install Selected",
            FuturisticTheme.NEON_CYAN,
            fg=FuturisticTheme.BG_MAIN,
            command=self._start_installation
        )
        self.install_btn.pack(side='left', padx=10)
        self.install_btn.configure(state='disabled')
        
    def _create_button(self, parent, text, bg, fg=None, command=None):
        """Create a modern styled button"""
        if fg is None:
            fg = FuturisticTheme.TEXT_PRIMARY
            
        btn = tk.Button(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            font=('Segoe UI', 11, 'bold'),
            padx=30,
            pady=12,
            relief='flat',
            bd=0,
            cursor='hand2',
            command=command
        )
        
        # Hover effect
        def on_enter(e):
            if btn['state'] != 'disabled':
                btn.configure(bg=self._lighten_color(bg))
                
        def on_leave(e):
            if btn['state'] != 'disabled':
                btn.configure(bg=bg)
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def _lighten_color(self, color):
        """Lighten a color for hover effect"""
        if color.startswith('#'):
            # Convert hex to RGB
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            # Lighten
            r = min(255, r + 30)
            g = min(255, g + 30)
            b = min(255, b + 30)
            
            return f'#{r:02x}{g:02x}{b:02x}'
        return color
        
    def _toggle_all(self):
        """Toggle all categories"""
        all_selected = len(self.selected_categories) == len(self.categories)
        
        if all_selected:
            # Deselect all
            for key, card in self.cards.items():
                if card.is_selected:
                    self._toggle_category(key, card)
            self.select_all_btn.configure(text="Select All")
        else:
            # Select all
            for key, card in self.cards.items():
                if not card.is_selected:
                    self._toggle_category(key, card)
            self.select_all_btn.configure(text="Deselect All")
            
    def _update_install_button(self):
        """Update install button based on selection"""
        count = len(self.selected_categories)
        
        if count == 0:
            self.install_btn.configure(
                text="Install Selected",
                state='disabled',
                bg=FuturisticTheme.GLASS_BG
            )
        else:
            self.install_btn.configure(
                text=f"Install {count} Categories",
                state='normal',
                bg=FuturisticTheme.NEON_CYAN
            )
            
    def _create_installation_view(self):
        """Create installation progress view"""
        self.install_frame = tk.Frame(self.main_container, bg=FuturisticTheme.BG_MAIN)
        
        # Circular progress
        self.progress_circle = CircularProgress(self.install_frame, size=250)
        self.progress_circle.pack(pady=30)
        
        # Status text
        self.status_label = tk.Label(
            self.install_frame,
            text="Initializing installation...",
            font=('Segoe UI', 14),
            fg=FuturisticTheme.TEXT_PRIMARY,
            bg=FuturisticTheme.BG_MAIN
        )
        self.status_label.pack(pady=10)
        
        # Current package
        self.package_label = tk.Label(
            self.install_frame,
            text="",
            font=('Segoe UI', 11),
            fg=FuturisticTheme.TEXT_SECONDARY,
            bg=FuturisticTheme.BG_MAIN
        )
        self.package_label.pack()
        
        # Log area with custom styling
        log_container = tk.Frame(self.install_frame, bg=FuturisticTheme.GLASS_BG)
        log_container.pack(fill='both', expand=True, pady=20)
        
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            height=15,
            bg=FuturisticTheme.BG_CARD,
            fg=FuturisticTheme.TEXT_SECONDARY,
            font=('Consolas', 9),
            wrap=tk.WORD,
            relief='flat',
            padx=15,
            pady=15
        )
        self.log_text.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Configure log tags
        self.log_text.tag_configure("success", foreground=FuturisticTheme.SUCCESS)
        self.log_text.tag_configure("error", foreground=FuturisticTheme.ERROR)
        self.log_text.tag_configure("warning", foreground=FuturisticTheme.WARNING)
        self.log_text.tag_configure("info", foreground=FuturisticTheme.INFO)
        
    def _create_complete_view(self):
        """Create installation complete view"""
        self.complete_frame = tk.Frame(self.main_container, bg=FuturisticTheme.BG_MAIN)
        
        # Success icon
        success_canvas = tk.Canvas(
            self.complete_frame,
            width=120, height=120,
            bg=FuturisticTheme.BG_MAIN,
            highlightthickness=0
        )
        success_canvas.pack(pady=50)
        
        # Draw checkmark circle
        success_canvas.create_oval(
            10, 10, 110, 110,
            outline=FuturisticTheme.SUCCESS,
            width=4
        )
        success_canvas.create_line(
            35, 60, 50, 75, 85, 40,
            fill=FuturisticTheme.SUCCESS,
            width=6,
            capstyle='round',
            joinstyle='round'
        )
        
        # Success message
        success_label = tk.Label(
            self.complete_frame,
            text="Installation Complete!",
            font=('Segoe UI', 24, 'bold'),
            fg=FuturisticTheme.TEXT_PRIMARY,
            bg=FuturisticTheme.BG_MAIN
        )
        success_label.pack(pady=20)
        
        # Summary
        self.summary_label = tk.Label(
            self.complete_frame,
            text="",
            font=('Segoe UI', 12),
            fg=FuturisticTheme.TEXT_SECONDARY,
            bg=FuturisticTheme.BG_MAIN
        )
        self.summary_label.pack(pady=10)
        
        # Action buttons
        button_frame = tk.Frame(self.complete_frame, bg=FuturisticTheme.BG_MAIN)
        button_frame.pack(pady=30)
        
        restart_btn = self._create_button(
            button_frame,
            "Restart System",
            FuturisticTheme.NEON_GREEN,
            fg=FuturisticTheme.BG_MAIN,
            command=self._restart_system
        )
        restart_btn.pack(side='left', padx=10)
        
        close_btn = self._create_button(
            button_frame,
            "Close",
            FuturisticTheme.GLASS_BG,
            command=self.root.quit
        )
        close_btn.pack(side='left', padx=10)
        
    def _start_installation(self):
        """Start the installation process"""
        if not self.selected_categories:
            return
            
        # Confirm
        categories_text = "\n".join(f"• {self.categories[key]['name']}" for key in self.selected_categories)
        
        result = messagebox.askyesno(
            "Confirm Installation",
            f"Install the following categories?\n\n{categories_text}\n\nThis will install real packages on your system!"
        )
        
        if not result:
            return
            
        # Switch view
        self.selection_frame.pack_forget()
        self.install_frame.pack(fill='both', expand=True)
        
        # Start installation thread
        self.is_installing = True
        install_thread = threading.Thread(
            target=self._run_installation,
            daemon=True
        )
        install_thread.start()
        
    def _run_installation(self):
        """Run the actual installation process"""
        try:
            total_steps = len(self.selected_categories) + 4  # +4 for prep steps
            current_step = 0
            
            # System update
            self._update_ui(current_step, total_steps, "Updating system packages...")
            self._log("Updating system packages...", "info")
            
            if self._run_command("sudo pacman -Syu --noconfirm"):
                self._log("System updated successfully", "success")
            else:
                self._log("System update failed", "warning")
                
            current_step += 1
            
            # Install paru if needed
            self._update_ui(current_step, total_steps, "Checking AUR helper...")
            if not self._check_command("paru"):
                self._install_paru()
            else:
                self._log("Paru AUR helper already installed", "success")
                
            current_step += 1
            
            # GPU drivers
            self._update_ui(current_step, total_steps, "Installing GPU drivers...")
            self._install_gpu_drivers()
            current_step += 1
            
            # Install selected categories
            for key in self.selected_categories:
                category = self.categories[key]
                self._update_ui(current_step, total_steps, f"Installing {category['name']}...")
                self._log(f"\nInstalling {category['name']} packages...", "info")
                
                # Pacman packages
                if category['packages']['pacman']:
                    cmd = f"sudo pacman -S --needed --noconfirm {' '.join(category['packages']['pacman'])}"
                    if self._run_command(cmd):
                        self._log(f"{category['name']} official packages installed", "success")
                    else:
                        self._log(f"Some {category['name']} packages failed", "warning")
                        
                # AUR packages
                if category['packages']['aur']:
                    cmd = f"paru -S --needed --noconfirm {' '.join(category['packages']['aur'])}"
                    if self._run_command(cmd):
                        self._log(f"{category['name']} AUR packages installed", "success")
                    else:
                        self._log(f"Some {category['name']} AUR packages failed", "warning")
                        
                current_step += 1
                
            # Cleanup
            self._update_ui(current_step, total_steps, "Cleaning up...")
            self._cleanup_system()
            
            # Complete
            self._installation_complete()
            
        except Exception as e:
            self._log(f"Installation error: {str(e)}", "error")
            self.root.after(0, messagebox.showerror, "Installation Failed", str(e))
            
    def _update_ui(self, current, total, status):
        """Update UI during installation"""
        progress = (current / total) * 100
        
        self.root.after(0, self.progress_circle.set_progress, progress)
        self.root.after(0, self.status_label.configure, {'text': status})
        
    def _log(self, message, tag="info"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.root.after(0, self._append_log, formatted_message, tag)
        
    def _append_log(self, message, tag):
        """Append to log widget"""
        self.log_text.insert(tk.END, message, tag)
        self.log_text.see(tk.END)
        
    def _run_command(self, cmd):
        """Execute system command"""
        try:
            self._log(f"$ {cmd}", "info")
            
            process = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            for line in process.stdout:
                if line.strip():
                    self._log(line.strip(), "info")
                    
            process.wait()
            return process.returncode == 0
            
        except Exception as e:
            self._log(f"Command error: {str(e)}", "error")
            return False
            
    def _check_command(self, cmd):
        """Check if a command exists"""
        try:
            subprocess.run(['which', cmd], check=True, capture_output=True)
            return True
        except:
            return False
            
    def _install_paru(self):
        """Install paru AUR helper"""
        self._log("Installing paru AUR helper...", "info")
        
        commands = [
            "sudo pacman -S --needed --noconfirm base-devel git",
            "cd /tmp && rm -rf paru",
            "cd /tmp && git clone https://aur.archlinux.org/paru.git",
            "cd /tmp/paru && makepkg -si --noconfirm"
        ]
        
        for cmd in commands:
            if not self._run_command(cmd):
                self._log("Paru installation failed", "error")
                return
                
        self._log("Paru installed successfully", "success")
        
    def _install_gpu_drivers(self):
        """Detect and install GPU drivers"""
        self._log("Detecting GPU...", "info")
        
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            gpu_info = result.stdout.lower()
            
            if 'nvidia' in gpu_info:
                self._log("NVIDIA GPU detected", "info")
                self._run_command("sudo pacman -S --needed --noconfirm nvidia nvidia-utils lib32-nvidia-utils")
            elif 'amd' in gpu_info or 'radeon' in gpu_info:
                self._log("AMD GPU detected", "info")
                self._run_command("sudo pacman -S --needed --noconfirm mesa lib32-mesa vulkan-radeon lib32-vulkan-radeon")
            elif 'intel' in gpu_info:
                self._log("Intel GPU detected", "info")
                self._run_command("sudo pacman -S --needed --noconfirm mesa lib32-mesa vulkan-intel lib32-vulkan-intel")
            else:
                self._log("No specific GPU drivers needed", "info")
                
        except Exception as e:
            self._log(f"GPU detection error: {str(e)}", "warning")
            
    def _cleanup_system(self):
        """Clean up system after installation"""
        self._log("Cleaning package cache...", "info")
        self._run_command("sudo paccache -r")
        
        # Check for orphans
        result = subprocess.run(['pacman', '-Qtdq'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            self._log("Removing orphaned packages...", "info")
            self._run_command(f"sudo pacman -Rns --noconfirm {result.stdout.strip()}")
        else:
            self._log("No orphaned packages found", "info")
            
    def _installation_complete(self):
        """Handle installation completion"""
        self.is_installing = False
        
        # Calculate summary
        total_categories = len(self.selected_categories)
        category_names = [self.categories[key]['name'] for key in self.selected_categories]
        
        # Switch to complete view
        self.root.after(0, self._show_complete_view, total_categories, category_names)
        
    def _show_complete_view(self, total_categories, category_names):
        """Show the completion view"""
        self.install_frame.pack_forget()
        self.complete_frame.pack(fill='both', expand=True)
        
        summary = f"Successfully installed {total_categories} categories:\n"
        summary += "\n".join(f"✓ {name}" for name in category_names)
        self.summary_label.configure(text=summary)
        
    def _restart_system(self):
        """Restart the system"""
        result = messagebox.askyesno(
            "Restart System",
            "Are you sure you want to restart now?\n\nMake sure to save all your work."
        )
        
        if result:
            subprocess.run(["sudo", "reboot"])
            
    def run(self):
        """Start the application"""
        # Check system requirements
        if not self._check_system():
            return
            
        # Start main loop
        self.root.mainloop()
        
    def _check_system(self):
        """Check if system meets requirements"""
        # Check if Arch Linux
        try:
            with open('/etc/os-release', 'r') as f:
                if 'Arch Linux' not in f.read():
                    messagebox.showerror(
                        "System Error",
                        "This application is designed for Arch Linux only."
                    )
                    return False
        except:
            messagebox.showerror(
                "System Error",
                "Cannot verify operating system."
            )
            return False
            
        # Check if not root
        if os.geteuid() == 0:
            messagebox.showerror(
                "Permission Error",
                "Do not run this application as root.\nPlease run as a regular user with sudo privileges."
            )
            return False
            
        return True

def main():
    """Main entry point"""
    app = ModernAutoInstallGUI()
    app.run()

if __name__ == "__main__":
    main()
