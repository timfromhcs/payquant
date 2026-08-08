#!/usr/bin/env python3
"""
PayQuant (PQN) Standalone GUI Node Application v3.0.0
Desktop GUI Node with Persistent LevelDB/Chainstate, Live Metrics, IRC P2P Peer Discovery,
Visual Log Feed, and ZIP Database Backup.
"""

import sys
import os
import time
import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from contrib.chain_db import get_db
import contrib.p2p_chain_transfer as p2p_transfer
import contrib.irc_p2p_signaling as irc_signaling

class PayQuantNodeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PayQuant (PQN) Full Node GUI – v3.0.0")
        self.root.geometry("880x620")
        self.root.configure(bg="#060814")

        self.db = get_db()
        self.node_running = False

        self.setup_ui()
        self.start_node_services()

    def setup_ui(self):
        # Header Banner
        header = tk.Frame(self.root, bg="#0c1024", height=70)
        header.pack(fill="x", side="top")

        title_lbl = tk.Label(header, text="PayQuant (PQN) Full Node", font=("Segoe UI", 18, "bold"), fg="#00d4ff", bg="#0c1024")
        title_lbl.pack(side="left", padx=20, pady=10)

        sub_lbl = tk.Label(header, text="Post-Quantum ML-DSA-65 | Persistent Chainstate | IRC P2P", font=("Segoe UI", 9), fg="#a0aec0", bg="#0c1024")
        sub_lbl.pack(side="left", pady=18)

        self.status_pill = tk.Label(header, text="🟢 NODE ONLINE", font=("Segoe UI", 10, "bold"), fg="#00ffaa", bg="#0c1024")
        self.status_pill.pack(side="right", padx=20)

        # Main Layout
        main_frame = tk.Frame(self.root, bg="#060814", padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        # Stats Cards Row
        stats_frame = tk.Frame(main_frame, bg="#060814")
        stats_frame.pack(fill="x", pady=(0, 15))

        self.card_blocks = self.create_card(stats_frame, "Block Height", "0", "#00d4ff")
        self.card_peers = self.create_card(stats_frame, "P2P Peers (IRC)", "0", "#7b2fbe")
        self.card_hash = self.create_card(stats_frame, "Best Block Hash", "0000...0000", "#00ffaa")

        # Live Log Console
        log_frame = tk.LabelFrame(main_frame, text=" Live Visual Log & P2P Stream ", font=("Segoe UI", 10, "bold"), fg="#00d4ff", bg="#060814", bd=1)
        log_frame.pack(fill="both", expand=True, pady=(0, 15))

        self.log_text = tk.Text(log_frame, bg="#04050d", fg="#e0e0e0", font=("Consolas", 9), bd=0, insertbackground="white")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Control Action Buttons Bar
        btn_frame = tk.Frame(main_frame, bg="#060814")
        btn_frame.pack(fill="x")

        self.btn_toggle = tk.Button(btn_frame, text="⏹ Stop Node", font=("Segoe UI", 10, "bold"), bg="#ff0055", fg="white", bd=0, padx=15, pady=8, command=self.toggle_node)
        self.btn_toggle.pack(side="left", padx=(0, 10))

        self.btn_backup = tk.Button(btn_frame, text="💾 Export Chain ZIP Backup", font=("Segoe UI", 10, "bold"), bg="#00d4ff", fg="#060814", bd=0, padx=15, pady=8, command=self.export_backup)
        self.btn_backup.pack(side="left", padx=(0, 10))

        self.btn_clear = tk.Button(btn_frame, text="Clear Logs", font=("Segoe UI", 10), bg="#1a2035", fg="#e0e0e0", bd=0, padx=15, pady=8, command=lambda: self.log_text.delete('1.0', tk.END))
        self.btn_clear.pack(side="right")

    def create_card(self, parent, title, val, color):
        card = tk.Frame(parent, bg="#0c1024", highlightbackground=color, highlightthickness=1, bd=0, padx=15, pady=12)
        card.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(card, text=title, font=("Segoe UI", 9), fg="#a0aec0", bg="#0c1024").pack(anchor="w")
        val_lbl = tk.Label(card, text=val, font=("Segoe UI", 13, "bold"), fg=color, bg="#0c1024")
        val_lbl.pack(anchor="w", pady=(4, 0))
        return val_lbl

    def log(self, tag, msg):
        t = time.strftime("%H:%M:%S")
        line = f"[{t}] [{tag}] {msg}\n"
        self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)

    def start_node_services(self):
        self.node_running = True
        self.log("INIT", "PayQuant Persistent Full Node v3.0.0 Initialized.")
        
        # Start P2P TCP Server
        p2p_transfer.start_p2p_server(28333)
        self.log("P2P", "Direct TCP Chain Transfer & Multi-Node Verification active on port 28333.")

        # Start IRC Signaling
        irc_signaling.start_background_signaling()
        self.log("IRC", "Zero-Server IRC P2P Peer Discovery active on Libera/OFTC (#payquant-mainnet).")

        # Background metrics updater loop
        threading.Thread(target=self.metrics_loop, daemon=True).start()

    def metrics_loop(self):
        while True:
            if self.node_running:
                height = self.db.getLastHeight()
                best = self.db.getBestBlock()
                best_hash = best.get("hash", "0000...") if best else "0000..."
                peers_count = len(irc_signaling.DISCOVERED_PEERS)

                self.root.after(0, self.update_card_labels, height, peers_count, best_hash[:16] + "...")
            time.sleep(2)

    def update_card_labels(self, height, peers, best_hash):
        self.card_blocks.config(text=str(height))
        self.card_peers.config(text=f"{peers} Peers Online")
        self.card_hash.config(text=best_hash)

    def toggle_node(self):
        if self.node_running:
            self.node_running = False
            self.status_pill.config(text="🔴 NODE STOPPED", fg="#ff0055")
            self.btn_toggle.config(text="▶ Start Node", bg="#00ffaa", fg="#060814")
            self.log("NODE", "Node daemon stopped by user.")
        else:
            self.node_running = True
            self.status_pill.config(text="🟢 NODE ONLINE", fg="#00ffaa")
            self.btn_toggle.config(text="⏹ Stop Node", bg="#ff0055", fg="white")
            self.log("NODE", "Node daemon resumed.")

    def export_backup(self):
        zip_path = self.db.exportChainZip()
        if os.path.exists(zip_path):
            messagebox.showinfo("Backup Exported", f"Chain Database ZIP Backup successfully created at:\n{zip_path}")
            self.log("BACKUP", f"Exported Chain ZIP to {zip_path}")

def main():
    root = tk.Tk()
    app = PayQuantNodeGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
