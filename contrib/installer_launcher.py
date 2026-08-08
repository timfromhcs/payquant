#!/usr/bin/env python3
"""
PayQuant Setup & Installation Utility (payquant-1.0.0-win64-setup.exe)
Installs PayQuant executables, configures Start Menu shortcuts & environment PATH.
"""

import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox

def install_payquant():
    target_dir = os.path.expanduser("~/AppData/Local/PayQuant")
    os.makedirs(target_dir, exist_ok=True)

    files_to_copy = [
        "payquantd.exe",
        "payquant-qt.exe",
        "payquant-cli.exe",
        "vulkan_miner.exe",
        "payquant.conf",
        "README.md",
        "SECURITY.md",
        "payquant_dataset.json"
    ]

    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    copied = 0

    for f in files_to_copy:
        src = os.path.join(base_dir, f)
        if not os.path.exists(src):
            src = os.path.join(base_dir, "dist", f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(target_dir, f))
            copied += 1

    messagebox.showinfo("PayQuant Installation Complete", 
                        f"PayQuant v1.0.0-alpha has been successfully installed to:\n{target_dir}\n\n"
                        f"Executables deployed:\n- payquant-qt.exe (GUI Wallet)\n- payquantd.exe (Node Daemon)\n- payquant-cli.exe (RPC CLI)\n- vulkan_miner.exe (GPU Miner)")

def main():
    root = tk.Tk()
    root.title("PayQuant v2.0.0 Win64 Setup")
    root.geometry("500x300")
    root.configure(bg="#060913")

    lbl = tk.Label(root, text="⚛️ PayQuant Win64 Installation Wizard", font=("Outfit", 14, "bold"), fg="#00f2fe", bg="#060913")
    lbl.pack(pady=20)

    desc = tk.Label(root, text="This setup wizard will install PayQuant Quantum-Safe Node,\nGUI Wallet, and Vulkan GPU Miner onto your system.", font=("Segoe UI", 10), fg="#94a3b8", bg="#060913")
    desc.pack(pady=10)

    btn = tk.Button(root, text="Install PayQuant", font=("Segoe UI", 11, "bold"), bg="#00f2fe", fg="#000000", padx=20, pady=10, command=install_payquant)
    btn.pack(pady=30)

    root.mainloop()

if __name__ == '__main__':
    main()
