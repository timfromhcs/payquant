#!/usr/bin/env python3
"""
PayQuant (PQN) - UTXO Rebuild + Wallet Restore Orchestrator v2.0.0-quantum
=========================================================================
Rebuilds the UTXO set from a genesis block and restores/verifies wallet data
after a quantum chain reset. Local-only: no repository writes, seeds and
private metadata never leave the desktop.

Usage:
    python tools/utxo_wallet.py --genesis <sandbox>/public_genesis.json
"""

import argparse
import json
import os
import shutil
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from contrib.chain_db import get_db


def gen_to_utxo_rows(genesis: dict) -> list:
    """Model a genesis block's coinbase transactions as UTXO rows."""
    rows = []
    for t in genesis.get("transactions", []) or []:
        amount = t.get("amount", "")
        try:
            amt = float(str(amount).split()[0])
        except (TypeError, ValueError):
            amt = 0.0
        rows.append({
            "recipient": t.get("recipient", ""),
            "amount": amt,
            "height": int(genesis.get("height", 0) or 0),
            "txid": str(t.get("type", "coinbase")),
        })
    return rows


def rebuild_utxo_from_genesis(genesis: dict, db=None) -> int:
    db = db or get_db()
    rows = gen_to_utxo_rows(genesis)
    return db.applyUTXODelta(rows)


def backup_wallet(db=None) -> str:
    """Copy the local wallet artefact to a timestamped backup (local only)."""
    db = db or get_db()
    wallet_file = os.path.join(os.path.dirname(os.path.abspath(db.db_file)), "wallet.dat")
    backup_dir = os.path.join(os.path.expanduser("~"), "payquant_wallet_backups")
    os.makedirs(backup_dir, exist_ok=True)
    dest = os.path.join(backup_dir, f"wallet_backup_{int(time.time())}.dat")
    if os.path.exists(wallet_file):
        shutil.copy2(wallet_file, dest)
        return dest
    return ""


def verify_wallet(db=None) -> dict:
    """Local-only verification report: UTXO count and total balance."""
    db = db or get_db()
    utxos = db.getAllUTXOs()
    total = sum(float(str(u.get("amount", "0")).split()[0]) for u in utxos) \
        if isinstance(utxos, list) else 0.0
    report = {"utxo_count": len(utxos or []), "total_pqn": total,
              "note": "local-only verification report"}
    report_dir = os.path.join(os.path.expanduser("~"), "payquant_quantum_reset")
    os.makedirs(report_dir, exist_ok=True)
    with open(os.path.join(report_dir, "wallet_restore_report.json"), "w",
              encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--genesis", default=None,
                    help="path to a (public) genesis JSON")
    args = ap.parse_args()

    if args.genesis:
        with open(args.genesis, "r", encoding="utf-8") as f:
            genesis = json.load(f)
    else:
        # demo-only synthetic genesis (public fields only)
        genesis = {"height": 0, "transactions": [
            {"type": "coinbase", "amount": "1000000000.00000000 PQN",
             "recipient": "pqn1qdemo2026"}]}

    print("[utxo_wallet] Rebuilding UTXO set from genesis (local-only)...", flush=True)
    n = rebuild_utxo_from_genesis(genesis)
    print(f"[utxo_wallet] Applied {n} coinbase UTXO row(s).", flush=True)
    bk = backup_wallet()
    print(f"[utxo_wallet] Wallet backup: {bk or '(none present)'}", flush=True)
    rep = verify_wallet()
    print(f"[utxo_wallet] Restore check: {rep['utxo_count']} UTXOs, "
          f"{rep['total_pqn']:.4f} PQN.", flush=True)
    print("[utxo_wallet] Done. No repository writes performed.", flush=True)


if __name__ == "__main__":
    main()