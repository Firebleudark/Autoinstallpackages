#!/usr/bin/env python3
# Simple Tkinter GUI wrapper for the Bash post-install script.
# - Subtle dark theme, minimal controls
# - Profiles exposed: minimal, gaming, KDE
# - Extras toggles: gaming extras, Chromium, Google Chrome, Spotify
# - Preflight button runs non-intrusive checks
import os
import sys
import threading
import subprocess
import queue
import tkinter as tk
from tkinter import ttk, messagebox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'v5', 'simple-postinstall.sh')


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Autoinstall Post-Install (Arch)')
        self.geometry('900x600')
        self._setup_theme()
        self._build_ui()
        self.proc = None
        self.q = queue.Queue()

    def _setup_theme(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        # Subtle palette
        self.configure(bg='#111418')
        style.configure('.', background='#111418', foreground='#D6D7D9')
        style.configure('TButton', background='#1a1f24', foreground='#E6E7E8')
        style.map('TButton', background=[('active', '#232a31')])
        style.configure('TCheckbutton', background='#111418', foreground='#D6D7D9')
        style.configure('TRadiobutton', background='#111418', foreground='#D6D7D9')
        style.configure('TFrame', background='#111418')
        style.configure('TLabel', background='#111418', foreground='#D6D7D9')
        style.configure('TNotebook', background='#111418')
        style.configure('TNotebook.Tab', background='#1a1f24', foreground='#D6D7D9')

    def _build_ui(self):
        container = ttk.Frame(self)
        container.pack(fill='both', expand=True, padx=12, pady=12)

        # Top controls
        top = ttk.Frame(container)
        top.pack(fill='x', pady=(0, 8))

        self.profile = tk.StringVar(value='minimal')
        ttk.Label(top, text='Profile:').pack(side='left')
        for val, txt in [('minimal', 'Minimal'), ('gaming', 'Gaming'), ('kde', 'KDE')]:
            ttk.Radiobutton(top, text=txt, value=val, variable=self.profile).pack(side='left', padx=6)

        ttk.Separator(container).pack(fill='x', pady=6)

        # Extras
        ex = ttk.Frame(container)
        ex.pack(fill='x')
        ttk.Label(ex, text='Extras:').grid(row=0, column=0, sticky='w')
        self.var_gaming = tk.BooleanVar(value=False)
        self.var_chromium = tk.BooleanVar(value=False)
        self.var_chrome = tk.BooleanVar(value=False)
        self.var_spotify = tk.BooleanVar(value=False)
        ttk.Checkbutton(ex, text='Gaming extras (Lutris, Heroic, Bottles, Prism, ProtonUp)', variable=self.var_gaming).grid(row=1, column=0, sticky='w')
        ttk.Checkbutton(ex, text='Chromium (repo)', variable=self.var_chromium).grid(row=2, column=0, sticky='w')
        ttk.Checkbutton(ex, text='Google Chrome (AUR/Flatpak)', variable=self.var_chrome).grid(row=3, column=0, sticky='w')
        ttk.Checkbutton(ex, text='Spotify (AUR/Flatpak)', variable=self.var_spotify).grid(row=4, column=0, sticky='w')

        # Buttons
        btns = ttk.Frame(container)
        btns.pack(fill='x', pady=8)
        ttk.Button(btns, text='Preflight', command=self.run_check).pack(side='left')
        self.btn_install = ttk.Button(btns, text='Install', command=self.run_install)
        self.btn_install.pack(side='left', padx=8)
        self.progress = ttk.Progressbar(btns, mode='indeterminate')
        self.progress.pack(side='right', fill='x', expand=True)

        # Log area
        logf = ttk.Frame(container)
        logf.pack(fill='both', expand=True)
        self.txt = tk.Text(logf, bg='#0f1317', fg='#D6D7D9', insertbackground='#D6D7D9')
        self.txt.pack(fill='both', expand=True)
        self.txt.tag_config('ok', foreground='#7bd88f')
        self.txt.tag_config('warn', foreground='#ffcc66')
        self.txt.tag_config('err', foreground='#ff6e6e')

        self.after(100, self._poll_queue)

    def append(self, s, tag=None):
        self.txt.insert('end', s + '\n', tag)
        self.txt.see('end')

    def run_check(self):
        if not os.path.exists(SCRIPT):
            messagebox.showerror('Error', f'Script not found: {SCRIPT}')
            return
        self._run_async(["bash", SCRIPT, "--check"], title='Preflight…')

    def run_install(self):
        if not os.path.exists(SCRIPT):
            messagebox.showerror('Error', f'Script not found: {SCRIPT}')
            return
        profile = self.profile.get()
        args = ["bash", SCRIPT, "--yes", "--profile", profile]
        if self.var_gaming.get():
            args.append("--gaming-extras")
        # Ensure gaming extras are installed when profile is "gaming"
        if profile == 'gaming' and "--gaming-extras" not in args:
            args.append("--gaming-extras")
        if self.var_chromium.get():
            args.append("--install-chromium")
        if self.var_chrome.get():
            args.append("--install-chrome")
        if self.var_spotify.get():
            args.append("--install-spotify")
        self._run_async(args, title='Installing…')

    def _run_async(self, args, title='Exécution…'):
        if self.proc and self.proc.poll() is None:
            messagebox.showwarning('Running', 'An execution is already in progress.')
            return
        self.append('=' * 60)
        self.append(title)
        self.progress.start(10)
        self.btn_install.state(['disabled'])
        def worker():
            try:
                self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                for line in self.proc.stdout:
                    self.q.put(line.rstrip('\n'))
                rc = self.proc.wait()
                self.q.put(f"[exit {rc}]")
            except Exception as e:
                self.q.put(f"[error] {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _poll_queue(self):
        try:
            while True:
                line = self.q.get_nowait()
                tag = None
                if 'FAIL' in line or 'error' in line.lower():
                    tag = 'err'
                elif 'OK' in line or 'done' in line.lower():
                    tag = 'ok'
                elif 'warn' in line.lower():
                    tag = 'warn'
                self.append(line, tag)
        except queue.Empty:
            pass
        finally:
            if self.proc and self.proc.poll() is not None:
                self.progress.stop()
                self.btn_install.state(['!disabled'])
        self.after(100, self._poll_queue)


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
