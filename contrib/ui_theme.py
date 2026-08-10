#!/usr/bin/env python3
"""
PayQuant (PQN) Shared UI Theme & Widget Kit v4.0.0

Central design tokens + shared widget helpers so every PayQuant desktop GUI
(node, miner, explorer, wallet) renders with one consistent modern dark theme.
Pure stdlib - zero external dependencies.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIXMAPS_DIR = os.path.join(BASE_DIR, "share", "pixmaps")

# ---------------------------------------------------------------- palette
BG = "#060814"            # window background
BG_SOFT = "#0a0e1f"       # slightly lighter panels
PANEL = "#0c1024"         # card / panel surface
PANEL_2 = "#090d26"
HEADER = "#080c21"
TEXT = "#e2e6f1"
MUTED = "#a0aec0"
MUTED_DIM = "#6b7688"
ACCENT = "#00d4ff"        # cyan primary
GREEN = "#00ffaa"
GOLD = "#ffaa00"
PURPLE = "#7b2fbe"
RED = "#ff0055"
BORDER = "#1c2440"

FONT = "Segoe UI"
FONT_CARD_TITLE = (FONT, 9)
FONT_CARD_VALUE = (FONT, 14, "bold")
FONT_TITLE = (FONT, 17, "bold")
FONT_SUB = (FONT, 9)
FONT_BODY = (FONT, 10)
FONT_MONO = "Consolas"

PAD = 10
CARD_PAD = 12

# ---------------------------------------------------------------- dpi & icon
def enable_hi_dpi(root):
    try:
        if sys.platform == "win32":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    try:
        root.tk.call("tk", "scaling", 1.25)
    except Exception:
        pass

def set_app_icon(root, icon_name="payquant.ico"):
    """Set the window icon from share/pixmaps."""
    try:
        ico_path = os.path.join(PIXMAPS_DIR, icon_name)
        if not os.path.exists(ico_path):
            ico_path = os.path.join(PIXMAPS_DIR, "payquant.ico")
        if os.path.exists(ico_path):
            root.iconbitmap(ico_path)
    except Exception as e:
        pass

# ---------------------------------------------------------------- style
def configure_ttk(root):
    """Give ttk widgets (Notebook, Treeview) a modern dark look."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure(
        "TNotebook",
        background=BG,
        borderwidth=0,
        tabmargins=(6, 6, 6, 0),
    )
    style.configure(
        "TNotebook.Tab",
        background=PANEL,
        foreground=MUTED,
        padding=(18, 8),
        font=(FONT, 9, "bold"),
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", ACCENT)],
        foreground=[("selected", "#06121a")],
    )
    style.configure(
        "Treeview",
        background=PANEL,
        fieldbackground=PANEL,
        foreground=TEXT,
        borderwidth=0,
        rowheight=28,
        font=(FONT, 9),
    )
    style.map(
        "Treeview",
        background=[("selected", "#12306e")],
        foreground=[("selected", "#ffffff")],
    )
    style.configure(
        "Treeview.Heading",
        background=HEADER,
        foreground=ACCENT,
        borderwidth=0,
        font=(FONT, 9, "bold"),
        padding=(8, 8),
    )
    style.configure(
        "Horizontal.TProgressbar",
        troughcolor=PANEL,
        background=GREEN,
        borderwidth=0,
        thickness=8,
    )
    return style

# ---------------------------------------------------------------- widget kit
def card(parent, title=None, color=ACCENT, bg=PANEL):
    """Create a modern stat card. Returns (frame, value_label)."""
    frame = tk.Frame(parent, bg=bg, highlightbackground=color,
                     highlightthickness=1, bd=0, padx=14, pady=10)
    if title:
        tk.Label(frame, text=title, font=FONT_CARD_TITLE, fg=MUTED, bg=bg).pack(anchor="w")
    value = tk.Label(frame, text="—", font=FONT_CARD_VALUE, fg=color, bg=bg)
    value.pack(anchor="w", pady=(2, 0))
    return frame, value

def mk_button(parent, text, bg=ACCENT, fg="#060814", command=None, bold=True, padx=15, pady=8):
    font = (FONT, 10, "bold") if bold else (FONT, 10)
    btn = tk.Button(parent, text=text, font=font, bg=bg, fg=fg, bd=0,
                    padx=padx, pady=pady, command=command, cursor="hand2",
                    activebackground=bg, activeforeground=fg)
    return btn

def mk_entry(parent, font=(FONT, 10), fg=GREEN, bg=BG_SOFT, width=None):
    entry = tk.Entry(parent, font=font, bg=bg, fg=fg, insertbackground="white",
                     bd=1, relief="flat", highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=ACCENT)
    if width:
        entry.config(width=width)
    return entry

def scrollable_text(parent):
    """A Text widget with an attached scrollbar, styled to the theme."""
    frame = tk.Frame(parent, bg=BG)
    text = tk.Text(frame, bg=BG_SOFT, fg=TEXT, font=(FONT_MONO, 9), bd=0,
                   insertbackground="white", relief="flat", wrap="word")
    scroll = tk.Scrollbar(frame, orient="vertical", command=text.yview,
                          bg=PANEL, troughcolor=BG, bd=0)
    text.configure(yscrollcommand=scroll.set)
    text.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return frame, text, scroll