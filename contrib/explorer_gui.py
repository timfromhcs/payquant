#!/usr/bin/env python3
"""
PayQuant (PQN) Standalone Public Blockchain Explorer Application v3.4.0
Zero-Node Required: Connects to global P2P nodes via IRC peer discovery,
queries network metrics, streams live blocks and transactions, and searches wallet balances.
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

try:
    import contrib.p2p_chain_transfer as p2p_transfer
    import contrib.irc_p2p_signaling as irc_signaling
    from contrib.chain_db import get_db
except ModuleNotFoundError:
    import p2p_chain_transfer as p2p_transfer
    import irc_p2p_signaling as irc_signaling
    from chain_db import get_db

class PayQuantExplorerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PayQuant (PQN) Public Blockchain Explorer – v6.1.0")
        self.root.geometry("960x680")
        self.root.configure(bg="#040612")

        self.db = get_db()
        self.setup_ui()
        self.start_explorer_daemon()
        print("[Explorer GUI v6.1.0] Standalone Public Blockchain Explorer & Address Auditor running.")

    def setup_ui(self):
        # Header Banner
        header = tk.Frame(self.root, bg="#0c1024", height=70)
        header.pack(fill="x", side="top")

        title_lbl = tk.Label(header, text="🔍 PayQuant Blockchain Explorer", font=("Segoe UI", 18, "bold"), fg="#00d4ff", bg="#0c1024")
        title_lbl.pack(side="left", padx=20, pady=10)

        sub_lbl = tk.Label(header, text="Zero-Node Standalone P2P Network Explorer & Wallet Auditor", font=("Segoe UI", 9), fg="#94a3b8", bg="#0c1024")
        sub_lbl.pack(side="left", pady=18)

        self.status_pill = tk.Label(header, text="🌐 NETWORK CONNECTED", font=("Segoe UI", 10, "bold"), fg="#00ffaa", bg="#0c1024")
        self.status_pill.pack(side="right", padx=20)

        # Address Search Bar
        search_frame = tk.Frame(self.root, bg="#080d24", padx=15, pady=10)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="Search Address / TX / Hash:", font=("Segoe UI", 10, "bold"), fg="#00d4ff", bg="#080d24").pack(side="left", padx=(0, 10))
        
        self.search_entry = tk.Entry(search_frame, font=("Consolas", 11), bg="#04050d", fg="#00ffaa", insertbackground="white", bd=1)
        self.search_entry.insert(0, "pqn1qgenesisspendenwallettreasury20252026")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_search = tk.Button(search_frame, text="🔍 Search", font=("Segoe UI", 9, "bold"), bg="#00d4ff", fg="#040612", bd=0, padx=15, pady=5, command=self.perform_search)
        btn_search.pack(side="right")

        # Main Layout Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)

        # TAB 1: Network Overview
        self.tab_overview = tk.Frame(self.notebook, bg="#040612", padx=10, pady=10)
        self.notebook.add(self.tab_overview, text="📊 Network Metrics")
        self.setup_overview_tab()

        # TAB 2: Latest Blocks
        self.tab_blocks = tk.Frame(self.notebook, bg="#040612", padx=10, pady=10)
        self.notebook.add(self.tab_blocks, text="📦 Blocks Stream")
        self.setup_blocks_tab()

        # TAB 3: Active P2P Peers Map
        self.tab_peers = tk.Frame(self.notebook, bg="#040612", padx=10, pady=10)
        self.notebook.add(self.tab_peers, text="🌐 Online Peers (IRC)")
        self.setup_peers_tab()

    def setup_overview_tab(self):
        stats_frame = tk.Frame(self.tab_overview, bg="#040612")
        stats_frame.pack(fill="x", pady=(0, 15))

        self.card_height = self.create_card(stats_frame, "Chain Height", "0", "#00d4ff")
        self.card_hashrate = self.create_card(stats_frame, "Est. Network Hashrate", "38,500 H/s", "#00ffaa")
        self.card_peers = self.create_card(stats_frame, "Discovered Peers", "0 Nodes", "#7b2fbe")

        # Result Display Area for Wallet Search
        self.search_result_frame = tk.LabelFrame(self.tab_overview, text=" Address Lookup & UTXO Audit ", font=("Segoe UI", 10, "bold"), fg="#00d4ff", bg="#040612", bd=1, padx=10, pady=10)
        self.search_result_frame.pack(fill="both", expand=True)

        self.search_result_text = tk.Text(self.search_result_frame, bg="#020308", fg="#e0e0e0", font=("Consolas", 10), bd=0)
        self.search_result_text.pack(fill="both", expand=True)

    def setup_blocks_tab(self):
        self.blocks_tree = ttk.Treeview(self.tab_blocks, columns=("height", "hash", "miner", "txs", "time"), show="headings")
        self.blocks_tree.heading("height", text="Height")
        self.blocks_tree.heading("hash", text="Block Hash")
        self.blocks_tree.heading("miner", text="Miner Address")
        self.blocks_tree.heading("txs", text="Transactions")
        self.blocks_tree.heading("time", text="Timestamp")

        self.blocks_tree.column("height", width=80, anchor="center")
        self.blocks_tree.column("hash", width=260)
        self.blocks_tree.column("miner", width=220)
        self.blocks_tree.column("txs", width=100, anchor="center")
        self.blocks_tree.column("time", width=140, anchor="center")

        self.blocks_tree.pack(fill="both", expand=True)

    def setup_peers_tab(self):
        self.peers_tree = ttk.Treeview(self.tab_peers, columns=("ip", "port", "height", "trust", "last_seen"), show="headings")
        self.peers_tree.heading("ip", text="Node IP")
        self.peers_tree.heading("port", text="P2P Port")
        self.peers_tree.heading("height", text="Reported Height")
        self.peers_tree.heading("trust", text="Trust Score")
        self.peers_tree.heading("last_seen", text="Last Active")

        self.peers_tree.column("ip", width=180, anchor="center")
        self.peers_tree.column("port", width=100, anchor="center")
        self.peers_tree.column("height", width=120, anchor="center")
        self.peers_tree.column("trust", width=120, anchor="center")
        self.peers_tree.column("last_seen", width=180, anchor="center")

        self.peers_tree.pack(fill="both", expand=True)

    def create_card(self, parent, title, val, color):
        card = tk.Frame(parent, bg="#0c1024", highlightbackground=color, highlightthickness=1, bd=0, padx=15, pady=12)
        card.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(card, text=title, font=("Segoe UI", 9), fg="#94a3b8", bg="#0c1024").pack(anchor="w")
        val_lbl = tk.Label(card, text=val, font=("Segoe UI", 13, "bold"), fg=color, bg="#0c1024")
        val_lbl.pack(anchor="w", pady=(4, 0))
        return val_lbl

    def perform_search(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        
        self.search_result_text.delete("1.0", tk.END)
        self.search_result_text.insert(tk.END, f"Querying P2P Network for address: {query}...\n\n")

        # Query local DB / P2P UTXOs
        utxos = self.db.getAddressUTXOs(query)
        balance = 0.0
        for tx in utxos:
            if isinstance(tx, dict) and "amount" in tx:
                try:
                    balance += float(str(tx["amount"]).split()[0])
                except ValueError:
                    pass

        res = f"=== PAYQUANT ADDRESS AUDIT RESULT ===\n"
        res += f"Address: {query}\n"
        res += f"Calculated Balance: {balance:,.4f} PQN\n"
        res += f"Recorded Transactions: {len(utxos)}\n\n"
        res += f"--- TRANSACTION HISTORY ---\n"
        for tx in utxos:
            res += f"TXID: {tx.get('txid', '-')} | Amount: {tx.get('amount', '-')} | Type: {tx.get('type', 'TRANSFER')}\n"

        self.search_result_text.insert(tk.END, res)

    def start_explorer_daemon(self):
        irc_signaling.start_background_signaling()
        threading.Thread(target=self.explorer_refresh_loop, daemon=True).start()

    def explorer_refresh_loop(self):
        while True:
            try:
                height = self.db.getLastHeight()
                peers_list = irc_signaling.get_all_peer_infos()
                all_blocks = self.db.getAllBlocks(start_height=max(0, height - 20), limit=20)

                self.root.after(0, self.update_explorer_ui, height, len(peers_list), peers_list, all_blocks)
            except Exception:
                pass
            time.sleep(3)

    def update_explorer_ui(self, height, peer_count, peers_list, blocks):
        self.card_height.config(text=str(height))
        self.card_peers.config(text=f"{peer_count} Nodes")

        # Update Blocks Tree
        for item in self.blocks_tree.get_children():
            self.blocks_tree.delete(item)
        for b in reversed(blocks):
            tx_cnt = len(b.get("transactions", []))
            t_str = time.strftime("%H:%M:%S", time.localtime(b.get("timestamp", time.time())))
            self.blocks_tree.insert("", tk.END, values=(b.get("height"), b.get("hash", "")[:24] + "...", b.get("miner", "")[:24] + "...", tx_cnt, t_str))

        # Update Peers Tree
        for item in self.peers_tree.get_children():
            self.peers_tree.delete(item)
        for p in peers_list:
            t_str = time.strftime("%H:%M:%S", time.localtime(p.get("last_seen", time.time())))
            self.peers_tree.insert("", tk.END, values=(p.get("ip"), p.get("port", 28333), p.get("height", 0), f"{p.get('trust_score', 100)}/100", t_str))

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("PayQuant (PQN) Standalone Public Explorer GUI v6.4.0")
        sys.exit(0)
    root = tk.Tk()
    app = PayQuantExplorerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
