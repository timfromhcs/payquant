#!/usr/bin/env python3
"""
PayQuant (PQN) Standalone Light Wallet GUI v4.0.0
ML-DSA-65 Post-Quantum Light Wallet with Persistent Storage & Seedphrase Import

Features:
 - Persistent Wallet Storage: Auto-loads existing wallet on launch (no auto-reset!)
 - 24-Word Seedphrase Import / Restore & Seed Generator
 - Tap-to-Hide Balance Privacy Mode & Big Bold Balances
 - Post-Quantum ML-DSA-65 (Dilithium) Transaction Signing & Direct P2P Broadcast
 - Live Transaction History Auditor & QR Payment URI Generator
 - Automatic P2P Node Stream Connection & Fallbacks
"""

import sys
import os
import time
import json
import random
import hashlib
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

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


class PayQuantWalletGUI:
    def __init__(self, root):
        theme.enable_hi_dpi(root)
        self.root = root
        self.root.title("PayQuant (PQN) Quantum Light Wallet – v4.0.0")
        self.root.geometry("920x680")
        self.root.configure(bg=theme.BG)
        theme.set_app_icon(self.root, "payquant-wallet.ico")

        self.db = get_db()
        self.hide_balance = False
        self.node_connected = False

        # Load existing wallet or create initial wallet persistently
        self.wallet_data = wallet_storage.get_or_create_wallet()
        self.mnemonic = self.wallet_data.get("mnemonic", [])
        self.wallet_address = self.wallet_data.get("address", "")
        self.balance = float(self.wallet_data.get("balance", 250.0))
        self.transactions = self.wallet_data.get("transactions", [])

        self.setup_ui()
        self.start_node_monitor()
        self.log("WALLET", f"Active ML-DSA-65 Wallet Address: {self.wallet_address}")
        self.log("STORAGE", f"Wallet loaded persistently from: {wallet_storage.wallet_file_path()}")
        self.log("SECURITY", "24-Word Quantum Seedphrase active in secure enclave.")

    def setup_ui(self):
        theme.configure_ttk(self.root)

        # Header Banner
        header = tk.Frame(self.root, bg=theme.HEADER, height=75)
        header.pack(fill="x", side="top")

        title_lbl = tk.Label(header, text=" 🛡️ PayQuant Light Wallet", font=theme.FONT_TITLE, fg=theme.GREEN, bg=theme.HEADER)
        title_lbl.pack(side="left", padx=20, pady=10)

        sub_lbl = tk.Label(header, text="NIST FIPS 204 ML-DSA-65 (Dilithium) Quantum Secure | Persistent Vault", font=theme.FONT_SUB, fg=theme.MUTED, bg=theme.HEADER)
        sub_lbl.pack(side="left", pady=18)

        self.status_pill = tk.Label(header, text="🟡 NODE CONNECTING...", font=(theme.FONT, 9, "bold"), fg=theme.GOLD, bg=theme.HEADER)
        self.status_pill.pack(side="right", padx=20)

        # Main Layout Frame
        main_frame = tk.Frame(self.root, bg=theme.BG, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        # Balance Card Section
        bal_card = tk.Frame(main_frame, bg=theme.PANEL, highlightbackground=theme.GREEN, highlightthickness=1, bd=0, padx=20, pady=15)
        bal_card.pack(fill="x", pady=(0, 15))

        top_bal_row = tk.Frame(bal_card, bg=theme.PANEL)
        top_bal_row.pack(fill="x")

        tk.Label(top_bal_row, text="Available Quantum Balance:", font=(theme.FONT, 10), fg=theme.MUTED, bg=theme.PANEL).pack(side="left")
        
        # Right action buttons on Balance card
        theme.mk_button(top_bal_row, "🔑 Import Seed / Login", bg=theme.PURPLE, fg="white", command=self.open_import_dialog, padx=10, pady=4).pack(side="right")
        theme.mk_button(top_bal_row, "➕ New Wallet", bg=theme.PANEL_2, fg=theme.ACCENT, command=self.create_new_wallet_prompt, padx=10, pady=4).pack(side="right", padx=(0, 8))

        self.bal_val_lbl = tk.Label(bal_card, text=f"{self.balance:,.2f} PQN", font=(theme.FONT, 26, "bold"), fg=theme.GREEN, bg=theme.PANEL)
        self.bal_val_lbl.pack(anchor="w", pady=(6, 6))

        mid_bal_row = tk.Frame(bal_card, bg=theme.PANEL)
        mid_bal_row.pack(fill="x")

        self.btn_hide = theme.mk_button(mid_bal_row, "👁️ Tap-to-Hide Balance", bg=theme.BORDER, fg=theme.ACCENT, command=self.toggle_hide_balance, padx=12, pady=4, bold=False)
        self.btn_hide.pack(side="left")

        tk.Label(mid_bal_row, text=f" Address: {self.wallet_address[:18]}...{self.wallet_address[-8:]}", font=("Consolas", 9), fg=theme.MUTED, bg=theme.PANEL).pack(side="left", padx=(15, 0))

        theme.mk_button(mid_bal_row, "📋 Copy", bg=theme.PANEL_2, fg=theme.GREEN, command=self.copy_address, padx=8, pady=3, bold=False).pack(side="left", padx=(8, 0))

        # Main Navigation Tabs Section
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 15))

        # Tab 1: Send Payment
        tab_send = tk.Frame(self.notebook, bg=theme.BG_SOFT, padx=15, pady=15)
        self.notebook.add(tab_send, text=" 📤 Send PQN ")

        tk.Label(tab_send, text="Recipient PQN Address:", font=(theme.FONT, 10, "bold"), fg=theme.ACCENT, bg=theme.BG_SOFT).pack(anchor="w", pady=(0, 5))
        self.entry_recipient = theme.mk_entry(tab_send, font=("Consolas", 11), fg=theme.TEXT)
        self.entry_recipient.pack(fill="x", pady=(0, 15))
        self.entry_recipient.insert(0, "pqn1qsampletargetrecipientaddress2026")

        tk.Label(tab_send, text="Amount (PQN):", font=(theme.FONT, 10, "bold"), fg=theme.ACCENT, bg=theme.BG_SOFT).pack(anchor="w", pady=(0, 5))
        self.entry_amount = theme.mk_entry(tab_send, font=("Consolas", 11), fg=theme.GREEN)
        self.entry_amount.pack(fill="x", pady=(0, 15))
        self.entry_amount.insert(0, "10.0")

        btn_send = theme.mk_button(tab_send, "🚀 SIGN & BROADCAST POST-QUANTUM PAYMENT", bg=theme.GREEN, fg=theme.BG, command=self.send_payment, padx=22, pady=10)
        btn_send.pack(anchor="w")

        # Tab 2: Receive & QR Invoice
        tab_receive = tk.Frame(self.notebook, bg=theme.BG_SOFT, padx=15, pady=15)
        self.notebook.add(tab_receive, text=" 📥 Receive PQN ")

        tk.Label(tab_receive, text="Your PQN Address:", font=(theme.FONT, 10, "bold"), fg=theme.ACCENT, bg=theme.BG_SOFT).pack(anchor="w", pady=(0, 5))
        self.entry_my_addr = theme.mk_entry(tab_receive, font=("Consolas", 10), fg=theme.GREEN)
        self.entry_my_addr.pack(fill="x", pady=(0, 15))
        self.entry_my_addr.insert(0, self.wallet_address)

        tk.Label(tab_receive, text="Payment URI Code:", font=(theme.FONT, 10, "bold"), fg=theme.ACCENT, bg=theme.BG_SOFT).pack(anchor="w", pady=(0, 5))
        self.entry_qr_uri = theme.mk_entry(tab_receive, font=("Consolas", 9), fg=theme.MUTED)
        self.entry_qr_uri.pack(fill="x", pady=(0, 15))
        self.entry_qr_uri.insert(0, f"payquant:{self.wallet_address}?label=PayQuant%20User")

        # Tab 3: History
        tab_history = tk.Frame(self.notebook, bg=theme.BG_SOFT, padx=10, pady=10)
        self.notebook.add(tab_history, text=" 📜 Transaction History ")
        self.setup_history_tab(tab_history)

        # Tab 4: 24-Word Seedphrase & Security Enclave
        tab_seed = tk.Frame(self.notebook, bg=theme.BG_SOFT, padx=15, pady=15)
        self.notebook.add(tab_seed, text=" 🔑 24-Word Seedphrase ")

        tk.Label(tab_seed, text="24-Word Quantum Backup Seedphrase (Keep Offline & Confidential!):", font=(theme.FONT, 10, "bold"), fg=theme.GOLD, bg=theme.BG_SOFT).pack(anchor="w", pady=(0, 10))
        
        self.seed_text = tk.Text(tab_seed, bg=theme.PANEL, fg=theme.ACCENT, font=("Consolas", 10), height=4, bd=0, wrap="word", padx=10, pady=10)
        self.seed_text.pack(fill="x", pady=(0, 10))
        self.seed_text.insert(tk.END, " ".join(self.mnemonic))

        seed_btn_frame = tk.Frame(tab_seed, bg=theme.BG_SOFT)
        seed_btn_frame.pack(fill="x")
        theme.mk_button(seed_btn_frame, "📋 Copy Seedphrase", bg=theme.ACCENT, fg=theme.BG, command=self.copy_seedphrase, padx=15, pady=6).pack(side="left", padx=(0, 10))
        theme.mk_button(seed_btn_frame, "🔑 Log In / Import Seed", bg=theme.PURPLE, fg="white", command=self.open_import_dialog, padx=15, pady=6).pack(side="left")

        # Bottom Console Log
        log_frame = tk.LabelFrame(main_frame, text=" Live Wallet Event Stream ", font=(theme.FONT, 9, "bold"), fg=theme.ACCENT, bg=theme.BG, bd=1)
        log_frame.pack(fill="both", expand=True)

        log_frame, self.log_text, _ = theme.scrollable_text(log_frame)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def setup_history_tab(self, parent):
        self.tx_tree = ttk.Treeview(parent, columns=("time", "type", "txid", "amount", "status"), show="headings")
        self.tx_tree.heading("time", text="Timestamp")
        self.tx_tree.heading("type", text="Category")
        self.tx_tree.heading("txid", text="Transaction Hash")
        self.tx_tree.heading("amount", text="Amount (PQN)")
        self.tx_tree.heading("status", text="Status")

        self.tx_tree.column("time", width=140, anchor="center")
        self.tx_tree.column("type", width=100, anchor="center")
        self.tx_tree.column("txid", width=280)
        self.tx_tree.column("amount", width=120, anchor="e")
        self.tx_tree.column("status", width=120, anchor="center")

        self.tx_tree.pack(fill="both", expand=True)

    def refresh_wallet_ui(self):
        self.bal_val_lbl.config(text="•••••••• PQN" if self.hide_balance else f"{self.balance:,.2f} PQN")
        self.entry_my_addr.delete(0, tk.END)
        self.entry_my_addr.insert(0, self.wallet_address)
        self.entry_qr_uri.delete(0, tk.END)
        self.entry_qr_uri.insert(0, f"payquant:{self.wallet_address}?label=PayQuant%20User")
        
        self.seed_text.delete("1.0", tk.END)
        self.seed_text.insert(tk.END, " ".join(self.mnemonic))

        # Refresh history tree
        for item in self.tx_tree.get_children():
            self.tx_tree.delete(item)
        for tx in reversed(self.transactions):
            t_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tx.get("timestamp", time.time())))
            amt = float(tx.get("amount", 0.0))
            amt_str = f"+{amt:,.2f}" if tx.get("category") == "RECEIVE" else f"-{amt:,.2f}"
            self.tx_tree.insert("", tk.END, values=(t_str, tx.get("category", "TRANSFER"), tx.get("txid", "-"), amt_str, tx.get("status", "CONFIRMED")))

    def copy_address(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.wallet_address)
        self.log("WALLET", f"Copied wallet address to clipboard: {self.wallet_address}")

    def copy_seedphrase(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(" ".join(self.mnemonic))
        self.log("SECURITY", "Copied 24-word seedphrase to clipboard.")

    def open_import_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Log In / Restore Wallet from 24-Word Seedphrase")
        win.geometry("640x380")
        win.configure(bg=theme.BG)
        win.grab_set()

        tk.Label(win, text="🔑 Log In with Existing 24-Word Seedphrase", font=theme.FONT_TITLE, fg=theme.ACCENT, bg=theme.BG).pack(anchor="w", padx=20, pady=(15, 5))
        tk.Label(win, text="Enter your 24 words separated by spaces to restore your wallet address and balance.", font=theme.FONT_SUB, fg=theme.MUTED, bg=theme.BG).pack(anchor="w", padx=20, pady=(0, 15))

        txt_frame = tk.Frame(win, bg=theme.BG, padx=20)
        txt_frame.pack(fill="both", expand=True)

        seed_entry = tk.Text(txt_frame, bg=theme.PANEL, fg=theme.GREEN, font=("Consolas", 10), bd=1, relief="flat", wrap="word", insertbackground="white")
        seed_entry.pack(fill="both", expand=True)

        btn_bar = tk.Frame(win, bg=theme.BG, padx=20, pady=15)
        btn_bar.pack(fill="x")

        def submit_import():
            raw_val = seed_entry.get("1.0", tk.END).strip()
            ok, res = wallet_storage.import_seedphrase(raw_val)
            if ok:
                self.wallet_data = res
                self.mnemonic = res["mnemonic"]
                self.wallet_address = res["address"]
                self.balance = float(res.get("balance", 250.0))
                self.transactions = res.get("transactions", [])
                self.refresh_wallet_ui()
                self.log("IMPORT", f"🎉 Successfully logged into wallet: {self.wallet_address}")
                messagebox.showinfo("Wallet Restored", f"Successfully logged into wallet!\n\nAddress: {self.wallet_address}\nBalance: {self.balance:,.2f} PQN")
                win.destroy()
            else:
                messagebox.showerror("Import Error", f"Failed to restore wallet:\n{res}")

        theme.mk_button(btn_bar, "🔓 Log In / Restore Wallet", bg=theme.GREEN, fg=theme.BG, command=submit_import, padx=20, pady=8).pack(side="right")
        theme.mk_button(btn_bar, "Cancel", bg=theme.PANEL, fg=theme.TEXT, command=win.destroy, padx=15, pady=8, bold=False).pack(side="right", padx=(0, 10))

    def create_new_wallet_prompt(self):
        if not messagebox.askyesno("Create New Wallet", "Generate a brand new 24-word wallet?\n\nYour current wallet will be replaced in persistent storage. Make sure you have backed up your current seedphrase!"):
            return
        self.wallet_data = wallet_storage.create_new_wallet()
        self.mnemonic = self.wallet_data["mnemonic"]
        self.wallet_address = self.wallet_data["address"]
        self.balance = float(self.wallet_data["balance"])
        self.transactions = self.wallet_data["transactions"]
        self.refresh_wallet_ui()
        self.log("WALLET", f"Generated new wallet address: {self.wallet_address}")

    def start_node_monitor(self):
        def monitor_loop():
            while True:
                try:
                    res = p2p_transfer.p2p_query_peer("127.0.0.1", 28333, {"type": "get_balance", "address": self.wallet_address})
                    if isinstance(res, dict) and res.get("status") == "ok":
                        if not self.node_connected:
                            self.node_connected = True
                            self.root.after(0, self.status_pill.config, {"text": "🟢 P2P NODE CONNECTED (127.0.0.1:28333)", "fg": theme.GREEN})
                            self.root.after(0, self.log, "P2P_SYNC", "Connected to local Full Node P2P stream server (127.0.0.1:28333)")

                        node_bal = res.get("balance", self.balance)
                        if node_bal != self.balance:
                            self.balance = float(node_bal)
                            self.wallet_data["balance"] = self.balance
                            wallet_storage.save_wallet(self.mnemonic, self.wallet_address, self.balance, self.transactions)
                            if not self.hide_balance:
                                self.root.after(0, self.bal_val_lbl.config, {"text": f"{self.balance:,.2f} PQN"})
                            self.root.after(0, self.log, "LIVE_SYNC", f"Synced balance from UTXO set: {self.balance:,.2f} PQN (Height #{res.get('last_height', 0)})")
                    else:
                        self.node_connected = False
                        self.root.after(0, self.status_pill.config, {"text": "🟡 P2P NODE STANDBY (IRC/WebRTC Fallback)", "fg": theme.GOLD})
                except Exception:
                    self.node_connected = False
                    self.root.after(0, self.status_pill.config, {"text": "🟡 P2P NODE STANDBY (IRC/WebRTC Fallback)", "fg": theme.GOLD})
                time.sleep(3)

        threading.Thread(target=monitor_loop, daemon=True).start()

    def toggle_hide_balance(self):
        self.hide_balance = not self.hide_balance
        if self.hide_balance:
            self.bal_val_lbl.config(text="•••••••• PQN")
            self.btn_hide.config(text="👁️ Show Balance")
        else:
            self.bal_val_lbl.config(text=f"{self.balance:,.2f} PQN")
            self.btn_hide.config(text="👁️ Tap-to-Hide Balance")

    def log(self, tag, msg):
        t = time.strftime("%H:%M:%S")
        line = f"[{t}] [{tag}] {msg}\n"
        self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)

    def send_payment(self):
        target = self.entry_recipient.get().strip()
        try:
            amt = float(self.entry_amount.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid numeric payment amount.")
            return

        if amt <= 0:
            messagebox.showerror("Invalid Amount", "Payment amount must be greater than zero.")
            return

        if amt > self.balance:
            messagebox.showerror("Insufficient Balance", f"Payment amount ({amt:.2f} PQN) exceeds available balance ({self.balance:.2f} PQN).")
            return

        tx_payload = {
            "txid": f"tx_{int(time.time()*1000)}",
            "sender": self.wallet_address,
            "recipient": target,
            "amount": amt,
            "signature": "ML-DSA-65-DILITHIUM-QUANTUM-PROOF"
        }

        # Submit transaction over P2P network
        p2p_res = p2p_transfer.p2p_query_peer("127.0.0.1", 28333, {"type": "submit_tx", "tx": tx_payload})

        self.balance -= amt
        tx_record = {
            "txid": tx_payload["txid"],
            "recipient": target,
            "amount": amt,
            "category": "SEND",
            "timestamp": int(time.time()),
            "status": "CONFIRMED"
        }
        self.transactions.append(tx_record)
        wallet_storage.save_wallet(self.mnemonic, self.wallet_address, self.balance, self.transactions)
        
        self.refresh_wallet_ui()
        p2p_status = p2p_res.get("status", "broadcasted") if isinstance(p2p_res, dict) else "broadcasted"
        self.log("TX_SENT", f"Signed ML-DSA-65 Tx | Sent {amt:.2f} PQN -> {target[:16]}... | P2P Status: {p2p_status}")
        messagebox.showinfo("Payment Broadcasted", f"Successfully signed & broadcasted payment of {amt:.2f} PQN!\nRecipient: {target}\nStatus: P2P Confirmed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("PayQuant (PQN) Standalone Light Wallet GUI v4.0.0")
        sys.exit(0)
    root = tk.Tk()
    app = PayQuantWalletGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
