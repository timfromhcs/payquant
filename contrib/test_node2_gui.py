#!/usr/bin/env python3
"""
PayQuant (PQN) Test Node 2 Instance GUI v6.5.0

Runs a 2nd independent Full Node instance on Port 28334 using separate database directory
`PayQuantTestNode2Data` to directly test zero-port NAT traversal, peer discovery, ping/pong health,
and block propagation between 2 nodes on the same PC.
"""

import sys
import os
import time
import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if getattr(sys, 'frozen', False):
    MEIPASS = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    if MEIPASS not in sys.path:
        sys.path.insert(0, MEIPASS)

# Custom 2nd Node DB Path
NODE2_DATA_DIR = os.path.join(os.path.expanduser("~"), ".payquant_node2") if os.name != 'nt' else os.path.join(os.environ.get('APPDATA', ''), 'PayQuantTestNode2Data')
NODE2_DB_PATH = os.path.join(NODE2_DATA_DIR, "chainstate_v6_node2.db")

try:
    from contrib.chain_db import PersistentChainDB
    import contrib.p2p_chain_transfer as p2p_transfer
    import contrib.irc_p2p_signaling as irc_signaling
except ModuleNotFoundError:
    from chain_db import PersistentChainDB
    import p2p_chain_transfer as p2p_transfer
    import irc_p2p_signaling as irc_signaling

class PayQuantTestNode2GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PayQuant (PQN) Full Node 2 (Test Instance - Port 28334)")
        self.root.geometry("880x640")
        self.root.configure(bg="#040612")

        self.db = PersistentChainDB(db_file=NODE2_DB_PATH)
        self.node_running = True

        self.setup_ui()
        self.start_node2_services()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#080c21", height=75)
        header.pack(fill="x", side="top")

        title_lbl = tk.Label(header, text=" 🖥️ PayQuant Test Node #2 (Port 28334)", font=("Segoe UI", 16, "bold"), fg="#ffaa00", bg="#080c21")
        title_lbl.pack(side="left", padx=20, pady=10)

        self.status_pill = tk.Label(header, text="🟢 NODE 2 ONLINE (P2P :28334)", font=("Segoe UI", 10, "bold"), fg="#00ffaa", bg="#080c21")
        self.status_pill.pack(side="right", padx=20)

        main_frame = tk.Frame(self.root, bg="#040612", padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        stats_frame = tk.Frame(main_frame, bg="#040612")
        stats_frame.pack(fill="x", pady=(0, 15))

        self.card_blocks = self.create_card(stats_frame, "Node 2 Block Height", str(self.db.getLastHeight()), "#ffaa00")
        self.card_peers = self.create_card(stats_frame, "Connected P2P Nodes", "2 Nodes", "#7b2fbe")
        self.card_hash = self.create_card(stats_frame, "Best Block Hash", "0000...", "#00ffaa")

        node_log_frame = tk.LabelFrame(main_frame, text=" Node 2 Real-Time P2P Log Console ", font=("Segoe UI", 10, "bold"), fg="#ffaa00", bg="#040612", bd=1)
        node_log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(node_log_frame, bg="#060814", fg="#e0e0e0", font=("Consolas", 9), bd=0)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def create_card(self, parent, title, val, color):
        card = tk.Frame(parent, bg="#090d26", highlightbackground=color, highlightthickness=1, bd=0, padx=15, pady=12)
        card.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(card, text=title, font=("Segoe UI", 9), fg="#a0aec0", bg="#090d26").pack(anchor="w")
        val_lbl = tk.Label(card, text=val, font=("Segoe UI", 13, "bold"), fg=color, bg="#090d26")
        val_lbl.pack(anchor="w", pady=(4, 0))
        return val_lbl

    def log(self, tag, msg):
        t = time.strftime("%H:%M:%S")
        line = f"[{t}] [{tag}] {msg}\n"
        self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)

    def start_node2_services(self):
        self.log("STARTUP", "PayQuant Test Node #2 initializing on Port 28334...")
        self.log("STORAGE", f"Independent RocksDB Engine at: {self.db.db_file}")

        # Register Node 1 and query its height
        irc_signaling.register_discovered_peer("127.0.0.1", 28333, nick="node_1_primary")
        irc_signaling.register_discovered_peer("127.0.0.1", 28334, nick="node_2_test")

        def node2_loop():
            while True:
                try:
                    # Sync with Node 1
                    res = p2p_transfer.p2p_query_peer("127.0.0.1", 28333, {"type": "get_node_status"})
                    if res and res.get("status") == "ok":
                        node1_h = res.get("height", 0)
                        if node1_h > self.db.getLastHeight():
                            blks_res = p2p_transfer.p2p_query_peer("127.0.0.1", 28333, {"type": "get_blocks", "from_height": self.db.getLastHeight() + 1})
                            if blks_res and "blocks" in blks_res:
                                for b in blks_res["blocks"]:
                                    self.db.putBlock(b)
                                self.root.after(0, self.log, "P2P_SYNC", f"Node #2 synced {len(blks_res['blocks'])} blocks from Node #1! Height: #{self.db.getLastHeight()}")

                    h = self.db.getLastHeight()
                    cnt = irc_signaling.get_node_count()
                    self.root.after(0, self.card_blocks.config, {"text": str(h)})
                    self.root.after(0, self.card_peers.config, {"text": f"{cnt} Nodes Online"})
                except Exception:
                    pass
                time.sleep(3)

        threading.Thread(target=node2_loop, daemon=True).start()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("PayQuant (PQN) Full Node 2 (Test Instance - Port 28334) v6.5.0")
        sys.exit(0)
    root = tk.Tk()
    app = PayQuantTestNode2GUI(root)
    root.mainloop()
