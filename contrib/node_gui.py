#!/usr/bin/env python3
"""
PayQuant (PQN) Standalone GUI Node Application v6.6.0
Desktop GUI Node with Persistent Chain DB, Live Metrics, IRC P2P Peer Discovery,
Visual Log Feed, and ZIP Database Backup. Modern shared dark UI theme.
"""

import sys
import os
import time
import threading
import tkinter as tk
from tkinter import messagebox, filedialog

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if getattr(sys, 'frozen', False):
    MEIPASS = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    if MEIPASS not in sys.path:
        sys.path.insert(0, MEIPASS)

try:
    from contrib.chain_db import get_db
    import contrib.p2p_chain_transfer as p2p_transfer
    import contrib.irc_p2p_signaling as irc_signaling
    import contrib.ui_theme as theme
except ModuleNotFoundError:
    from chain_db import get_db
    import p2p_chain_transfer as p2p_transfer
    import irc_p2p_signaling as irc_signaling
    import ui_theme as theme

class PayQuantNodeGUI:
    def __init__(self, root):
        theme.enable_hi_dpi(root)
        self.root = root
        self.root.title("PayQuant (PQN) Full Node GUI – v6.6.0")
        self.root.geometry("900x640")
        self.root.configure(bg=theme.BG)

        self.db = get_db()
        self.node_running = False

        self.setup_ui()
        self.start_node_services()

    def setup_ui(self):
        theme.configure_ttk(self.root)

        # Header Banner
        header = tk.Frame(self.root, bg=theme.HEADER, height=70)
        header.pack(fill="x", side="top")

        tk.Label(header, text="PayQuant (PQN) Full Node", font=theme.FONT_TITLE, fg=theme.ACCENT, bg=theme.HEADER).pack(side="left", padx=20, pady=10)
        tk.Label(header, text="Post-Quantum ML-DSA-65 | RocksDB Storage | Zero-Port P2P", font=theme.FONT_SUB, fg=theme.MUTED, bg=theme.HEADER).pack(side="left", pady=18)

        self.status_pill = tk.Label(header, text="🟢 NODE ONLINE", font=(theme.FONT, 10, "bold"), fg=theme.GREEN, bg=theme.HEADER)
        self.status_pill.pack(side="right", padx=20)

        # Main Layout
        main_frame = tk.Frame(self.root, bg=theme.BG, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        # Stats Cards Row
        stats_frame = tk.Frame(main_frame, bg=theme.BG)
        stats_frame.pack(fill="x", pady=(0, 15))
        self.card_blocks = self._mk_card(stats_frame, "Block Height", "0", theme.ACCENT)
        self.card_peers = self._mk_card(stats_frame, "P2P Peers (IRC)", "0", theme.PURPLE)
        self.card_hash = self._mk_card(stats_frame, "Best Block Hash", "0000...", theme.GREEN)

        # Live Log Console
        log_frame = tk.LabelFrame(main_frame, text=" Real-Time Node Console & Debug Stream ",
                                  font=(theme.FONT, 10, "bold"), fg=theme.ACCENT, bg=theme.BG,
                                  bd=1, highlightthickness=1, highlightbackground=theme.BORDER)
        log_frame.pack(fill="both", expand=True, pady=(0, 15))

        log_frame, self.log_text, _ = theme.scrollable_text(log_frame)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Control Action Buttons Bar
        btn_frame = tk.Frame(main_frame, bg=theme.BG)
        btn_frame.pack(fill="x")

        self.btn_toggle = theme.mk_button(btn_frame, "⏹ Stop Node", bg=theme.RED, fg="white", command=self.toggle_node, padx=18)
        self.btn_toggle.pack(side="left", padx=(0, 10))

        theme.mk_button(btn_frame, "💾 Export Chain ZIP Backup", bg=theme.ACCENT, fg=theme.BG, command=self.export_backup, padx=18).pack(side="left", padx=(0, 10))

        theme.mk_button(btn_frame, "Clear Logs", bg=theme.PANEL, fg=theme.TEXT, bold=False, command=lambda: self.log_text.delete('1.0', tk.END)).pack(side="right")

    def _mk_card(self, parent, title, value, color):
        frame, value_lbl = theme.card(parent, title, color)
        frame.pack(side="left", fill="both", expand=True, padx=5)
        return value_lbl

    def log(self, tag, msg):
        t = time.strftime("%H:%M:%S")
        line = f"[{t}] [{tag}] {msg}\n"
        self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)

    def start_node_services(self):
        self.node_running = True
        self.log("STARTUP", "PayQuant Full Node GUI v6.6.0 initializing...")
        self.log("STORAGE", f"RocksDB Persistent State Engine loaded at: {self.db.db_file}")
        self.log("SECURITY", "NIST FIPS 204 ML-DSA-65 signature validator online.")

        # Start P2P TCP Server
        p2p_transfer.start_p2p_server(28333)
        self.log("P2P", "Direct TCP Chain Transfer & Multi-Node Verification active on port 28333.")

        # Start IRC Signaling
        irc_signaling.start_background_signaling()
        self.log("IRC", "Zero-Server IRC P2P Peer Discovery active (TLS + plain, multi-network).")

        # Background metrics updater loop
        threading.Thread(target=self.metrics_loop, daemon=True).start()

    def metrics_loop(self):
        while True:
            if self.node_running:
                height = self.db.getLastHeight()
                best = self.db.getBestBlock()
                best_hash = best.get("hash", "0000...") if best else "0000..."
                peers_count = irc_signaling.get_node_count()

                self.root.after(0, self.update_card_labels, height, peers_count, best_hash[:16] + "...")
            time.sleep(2)

    def update_card_labels(self, height, peers, best_hash):
        self.card_blocks.config(text=str(height))
        self.card_peers.config(text=f"{peers} Peers Online")
        self.card_hash.config(text=best_hash)

    def toggle_node(self):
        if self.node_running:
            self.node_running = False
            self.status_pill.config(text="🔴 NODE STOPPED", fg=theme.RED)
            self.btn_toggle.config(text="▶ Start Node", bg=theme.GREEN, fg=theme.BG)
            self.log("NODE", "Node daemon stopped by user.")
        else:
            self.node_running = True
            self.status_pill.config(text="🟢 NODE ONLINE", fg=theme.GREEN)
            self.btn_toggle.config(text="⏹ Stop Node", bg=theme.RED, fg="white")
            self.log("NODE", "Node daemon resumed.")

    def export_backup(self):
        zip_path = self.db.exportChainZip()
        if os.path.exists(zip_path):
            messagebox.showinfo("Backup Exported", f"Chain Database ZIP Backup successfully created at:\n{zip_path}")
            self.log("BACKUP", f"Exported Chain ZIP to {zip_path}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("PayQuant (PQN) Standalone Full Node GUI v6.6.0")
        sys.exit(0)
    root = tk.Tk()
    app = PayQuantNodeGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()