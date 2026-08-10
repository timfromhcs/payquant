#!/usr/bin/env python3
"""
PayQuant (PQN) Standalone GUI Full Node Application v4.0.0

Desktop GUI Node with Persistent RocksDB Engine, Config Storage, Live Peer Topology,
Zero-Port P2P Discovery, Chain ZIP Backup, and Real-Time Node Debug Stream.
"""

import sys
import os
import time
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

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
    import contrib.wallet_storage as wallet_storage
except ModuleNotFoundError:
    from chain_db import get_db
    import p2p_chain_transfer as p2p_transfer
    import irc_p2p_signaling as irc_signaling
    import ui_theme as theme
    import wallet_storage as wallet_storage

NODE_CONFIG_FILE = os.path.join(wallet_storage.user_data_dir(), "node_config.json")

def load_node_config():
    defaults = {"p2p_port": 28333, "max_peers": 64, "auto_start": True, "log_level": "INFO"}
    try:
        if os.path.exists(NODE_CONFIG_FILE):
            with open(NODE_CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    defaults.update(data)
    except Exception:
        pass
    return defaults

def save_node_config(cfg):
    try:
        os.makedirs(os.path.dirname(NODE_CONFIG_FILE), exist_ok=True)
        with open(NODE_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

class PayQuantNodeGUI:
    def __init__(self, root):
        theme.enable_hi_dpi(root)
        self.root = root
        self.root.title("PayQuant (PQN) Full Node GUI – v4.0.0")
        self.root.geometry("960x680")
        self.root.configure(bg=theme.BG)
        theme.set_app_icon(self.root, "payquant-node.ico")

        self.db = get_db()
        self.cfg = load_node_config()
        self.node_running = False

        self.setup_ui()
        if self.cfg.get("auto_start", True):
            self.start_node_services()

    def setup_ui(self):
        theme.configure_ttk(self.root)

        # Header Banner
        header = tk.Frame(self.root, bg=theme.HEADER, height=75)
        header.pack(fill="x", side="top")

        tk.Label(header, text="🖥️ PayQuant Full Node Engine", font=theme.FONT_TITLE, fg=theme.ACCENT, bg=theme.HEADER).pack(side="left", padx=20, pady=10)
        tk.Label(header, text="RocksDB Persistent Chain state | Zero-Port P2P Transport", font=theme.FONT_SUB, fg=theme.MUTED, bg=theme.HEADER).pack(side="left", pady=18)

        self.status_pill = tk.Label(header, text="🟢 NODE ONLINE", font=(theme.FONT, 10, "bold"), fg=theme.GREEN, bg=theme.HEADER)
        self.status_pill.pack(side="right", padx=20)

        # Main Layout Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=15)

        # Tab 1: Dashboard & Metrics
        tab_dash = tk.Frame(notebook, bg=theme.BG, padx=10, pady=10)
        notebook.add(tab_dash, text=" 📊 Node Dashboard ")

        # Stats Cards Row
        stats_frame = tk.Frame(tab_dash, bg=theme.BG)
        stats_frame.pack(fill="x", pady=(0, 15))

        self.card_blocks = self._mk_card(stats_frame, "Block Height", str(self.db.getLastHeight()), theme.ACCENT)
        self.card_mined = self._mk_card(stats_frame, "Blocks Mined", "0", theme.GOLD)
        self.card_nodes = self._mk_card(stats_frame, "Connected Peers", "0", theme.PURPLE)
        self.card_miners = self._mk_card(stats_frame, "Active Miners", "0", theme.RED)
        self.card_hash = self._mk_card(stats_frame, "Best Block Hash", "0000...", theme.GREEN)

        # Live Log Console Frame
        log_frame = tk.LabelFrame(tab_dash, text=" Real-Time Node Console & Debug Stream ",
                                  font=(theme.FONT, 10, "bold"), fg=theme.ACCENT, bg=theme.BG,
                                  bd=1, highlightthickness=1, highlightbackground=theme.BORDER)
        log_frame.pack(fill="both", expand=True, pady=(0, 15))

        log_frame, self.log_text, _ = theme.scrollable_text(log_frame)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Action Buttons
        btn_frame = tk.Frame(tab_dash, bg=theme.BG)
        btn_frame.pack(fill="x")

        self.btn_toggle = theme.mk_button(btn_frame, "⏹ Stop Node", bg=theme.RED, fg="white", command=self.toggle_node, padx=18)
        self.btn_toggle.pack(side="left", padx=(0, 10))

        theme.mk_button(btn_frame, "💾 Export Chain ZIP Backup", bg=theme.ACCENT, fg=theme.BG, command=self.export_backup, padx=18).pack(side="left", padx=(0, 10))
        theme.mk_button(btn_frame, "🛠 Repair Database", bg=theme.PANEL_2, fg=theme.GOLD, command=self.repair_database, padx=14).pack(side="left", padx=(0, 10))

        theme.mk_button(btn_frame, "Clear Logs", bg=theme.PANEL, fg=theme.TEXT, bold=False, command=lambda: self.log_text.delete('1.0', tk.END)).pack(side="right")

        # Tab 2: Peers Map
        tab_peers = tk.Frame(notebook, bg=theme.BG, padx=10, pady=10)
        notebook.add(tab_peers, text=" 🌐 Active P2P Peers ")
        self.setup_peers_tab(tab_peers)

        # Tab 3: Node Settings
        tab_settings = tk.Frame(notebook, bg=theme.BG_SOFT, padx=15, pady=15)
        notebook.add(tab_settings, text=" ⚙️ Settings ")
        self.setup_settings_tab(tab_settings)

    def _mk_card(self, parent, title, value, color):
        frame, value_lbl = theme.card(parent, title, color)
        frame.pack(side="left", fill="both", expand=True, padx=5)
        return value_lbl

    def setup_peers_tab(self, parent):
        self.peers_tree = ttk.Treeview(parent, columns=("ip", "port", "height", "trust", "last_seen"), show="headings")
        self.peers_tree.heading("ip", text="Node IP Address")
        self.peers_tree.heading("port", text="P2P Port")
        self.peers_tree.heading("height", text="Reported Height")
        self.peers_tree.heading("trust", text="Trust Score")
        self.peers_tree.heading("last_seen", text="Last Active")

        self.peers_tree.column("ip", width=220, anchor="center")
        self.peers_tree.column("port", width=100, anchor="center")
        self.peers_tree.column("height", width=140, anchor="center")
        self.peers_tree.column("trust", width=120, anchor="center")
        self.peers_tree.column("last_seen", width=180, anchor="center")

        self.peers_tree.pack(fill="both", expand=True)

    def setup_settings_tab(self, parent):
        tk.Label(parent, text="Node Configuration Settings", font=theme.FONT_TITLE, fg=theme.ACCENT, bg=theme.BG_SOFT).pack(anchor="w", pady=(0, 15))

        tk.Label(parent, text="P2P Port:", font=(theme.FONT, 10, "bold"), fg=theme.TEXT, bg=theme.BG_SOFT).pack(anchor="w")
        self.entry_port = theme.mk_entry(parent, font=("Consolas", 10), width=30)
        self.entry_port.insert(0, str(self.cfg.get("p2p_port", 28333)))
        self.entry_port.pack(anchor="w", pady=(2, 15))

        tk.Label(parent, text="Max Connected Peers:", font=(theme.FONT, 10, "bold"), fg=theme.TEXT, bg=theme.BG_SOFT).pack(anchor="w")
        self.entry_max_peers = theme.mk_entry(parent, font=("Consolas", 10), width=30)
        self.entry_max_peers.insert(0, str(self.cfg.get("max_peers", 64)))
        self.entry_max_peers.pack(anchor="w", pady=(2, 20))

        theme.mk_button(parent, "💾 Save Configuration", bg=theme.GREEN, fg=theme.BG, command=self.save_settings, padx=20, pady=8).pack(anchor="w")

    def save_settings(self):
        try:
            self.cfg["p2p_port"] = int(self.entry_port.get().strip())
            self.cfg["max_peers"] = int(self.entry_max_peers.get().strip())
            save_node_config(self.cfg)
            self.log("CONFIG", "Saved node settings to node_config.json")
            messagebox.showinfo("Settings Saved", "Node settings saved successfully!")
        except ValueError:
            messagebox.showerror("Error", "Port and Max Peers must be valid integers.")

    def log(self, tag, msg):
        t = time.strftime("%H:%M:%S")
        line = f"[{t}] [{tag}] {msg}\n"
        self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)

    def start_node_services(self):
        self.node_running = True
        self.log("STARTUP", "PayQuant Full Node GUI v4.0.0 initializing...")
        self.log("STORAGE", f"RocksDB Persistent Engine loaded at: {self.db.db_file}")
        self.log("SECURITY", "NIST FIPS 204 ML-DSA-65 signature validator online.")
        self.log("CONSENSUS", "21,000,000 PQN Max Cap | 210,000 Block Halvings | 40-Block Hashrate-Adaptive Rewards")

        p2p_port = self.cfg.get("p2p_port", 28333)
        p2p_transfer.start_p2p_server(p2p_port)
        self.log("P2P", f"Direct TCP Chain Transfer & Multi-Node Verification active on port {p2p_port}.")

        irc_signaling.start_background_signaling()
        self.log("IRC", "Zero-Server IRC P2P Peer Discovery active (TLS + plain, multi-network).")

        threading.Thread(target=self.metrics_loop, daemon=True).start()

    def metrics_loop(self):
        start_height = self.db.getLastHeight()
        while True:
            if self.node_running:
                try:
                    height = self.db.getLastHeight()
                    best = self.db.getBestBlock()
                    best_hash = best.get("hash", "0000...") if best else "0000..."
                    peers_count = irc_signaling.get_node_count()
                    miner_count = irc_signaling.get_miner_count()
                    mined_delta = max(0, height - start_height)
                    peers_list = irc_signaling.get_all_peer_infos()

                    self.root.after(0, self.update_card_labels, height, mined_delta, peers_count, miner_count, best_hash[:16] + "...", peers_list)
                except Exception:
                    pass
            time.sleep(2.5)

    def update_card_labels(self, height, mined, nodes, miners, best_hash, peers_list):
        self.card_blocks.config(text=str(height))
        self.card_mined.config(text=f"{mined} Mined")
        self.card_nodes.config(text=f"{nodes} Peers")
        self.card_miners.config(text=f"{miners} Miners")
        self.card_hash.config(text=best_hash)

        # Update peers table
        for item in self.peers_tree.get_children():
            self.peers_tree.delete(item)
        for p in peers_list:
            t_str = time.strftime("%H:%M:%S", time.localtime(p.get("last_seen", time.time())))
            self.peers_tree.insert("", tk.END, values=(p.get("ip"), p.get("port", 28333), p.get("height", 0), f"{p.get('trust_score', 100)}/100", t_str))

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

    def repair_database(self):
        res = self.db.repair_db()
        if res:
            messagebox.showinfo("Database Integrity", "Chainstate RocksDB integrity repair passed cleanly!")
            self.log("REPAIR", "Database integrity repair completed successfully.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("PayQuant (PQN) Standalone Full Node GUI v4.0.0")
        sys.exit(0)
    root = tk.Tk()
    app = PayQuantNodeGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()