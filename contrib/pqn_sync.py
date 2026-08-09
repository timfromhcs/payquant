#!/usr/bin/env python3
"""
PayQuant (PQN) Merkle-Delta UTXO Synchronization Engine v7.0.0
=============================================================

Upgrade over the v6 blob "get_utxo_snapshot" protocol:
  - Compute a canonical Merkle root of the UTXO set so peers compare fingerprints
    BEFORE shipping data (O(1) check vs O(n) transfer).
  - Transfer only the *delta* (UTXOs changed since the peer's recorded height),
    unless the height gap is large (then exchange the full verified snapshot).
  - Payloads can be AES-256-GCM sealed via contrib.pqn_netlib.

Protocol messages (JSON over the Super-Transport):
  request  {"type":"pqn_sync_offer","local_height":H,"merkle_root":R}
  reply    {"type":"pqn_sync_delta","status":"ok","remote_height":H2,
            "merkle_root":R2,"match":bool,"gap":int,
            "delta":[utxo dicts...]|"snapshot":{...}}
"""

import hashlib
import json
import os
import sys
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from contrib.chain_db import get_db
    from contrib.pqn_netlib import query_peer
except Exception:
    from chain_db import get_db
    from pqn_netlib import query_peer

FULL_SNAPSHOT_GAP = 200       # beyond this height gap, exchange the full snapshot
MAX_DELTA = 20000             # cap on delta rows shipped per reply
EMPTY_ROOT = hashlib.sha256(b"pqn-empty-utxo-set").hexdigest()

_sync_lock = threading.Lock()


# ------------------------------------------------------------------ merkle helpers
def canonical_utxo_hash(utxo):
    """Deterministic single-UTXO digest (recipient, amount, txid, height)."""
    recipient = str(utxo.get("recipient", ""))
    try:
        amount = float(str(utxo.get("amount", "0")).split()[0])
    except (TypeError, ValueError):
        amount = 0.0
    txid = str(utxo.get("txid", utxo.get("utxo_id", "")))
    try:
        height = int(utxo.get("height", utxo.get("block_height", 0)) or 0)
    except (TypeError, ValueError):
        height = 0
    payload = f"{recipient}|{amount:.8f}|{txid}|{height}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def utxo_set_merkle_root(utxos):
    """Canonical Merkle tree root over a sorted list of UTXO hashes."""
    leaves = sorted(canonical_utxo_hash(u) for u in utxos or [])
    if not leaves:
        return EMPTY_ROOT
    level = leaves
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [hashlib.sha256(f"{a}{b}".encode("utf-8")).hexdigest()
                 for a, b in zip(level[0::2], level[1::2])]
    return level[0]


# ------------------------------------------------------------------ db access
def _conn(db):
    return db._get_connection()


def _height(db):
    try:
        return int(db.getLastHeight())
    except Exception:
        return 0


def _all_utxos(db):
    with _sync_lock:
        try:
            return db.getAllUTXOs()
        except Exception:
            return []


def _utxos_since(db, since_height):
    with _sync_lock:
        try:
            return db.getUTXOsSince(since_height)
        except Exception:
            return []


def merkle_root(db=None):
    db = db or get_db()
    return db.merkleRootOfUTXOs()


# ------------------------------------------------------------------ server side
def handle_sync_offer(msg):
    """Server side: answer a pqn_sync_offer request with a delta reply."""
    db = get_db()
    local_height = _height(db)
    req_height = int(msg.get("local_height", 0) or 0)
    req_root = str(msg.get("merkle_root", ""))
    root = merkle_root(db)

    reply = {
        "type": "pqn_sync_delta",
        "status": "ok",
        "remote_height": local_height,
        "merkle_root": root,
        "match": False,
        "gap": max(0, local_height - req_height),
        "delta": [],
    }

    if root == req_root and local_height == req_height:
        reply["match"] = True
        return reply

    gap = local_height - req_height
    if gap > FULL_SNAPSHOT_GAP or gap < 0:
        try:
            snap = db.create_utxo_snapshot()
            reply["snapshot"] = snap
        except Exception as e:
            reply["error"] = f"snapshot_unavailable: {e}"
        return reply

    reply["delta"] = _utxos_since(db, req_height)[:MAX_DELTA]
    reply["match"] = True
    return reply


# ------------------------------------------------------------------ client side
def sync_utxos_from_peer(peer_ip, port=28333, peer_nick=None, db=None):
    """Pull UTXO delta from a peer over the Super-Transport and apply locally.

    Returns a report dict:
      {status, mode: 'synced'|'delta'|'snapshot'|'noop'|'error', ...}
    """
    db = db or get_db()
    my_height = _height(db)
    my_root = merkle_root(db)
    req = {"type": "pqn_sync_offer", "local_height": my_height, "merkle_root": my_root}

    res = query_peer(peer_ip, req, port=port, peer_nick=peer_nick)
    if not isinstance(res, dict) or res.get("status") != "ok":
        return {"status": "error", "error": (res or {}).get("error", "no_response")}

    if res.get("match") and not res.get("delta") and not res.get("snapshot"):
        return {"status": "ok", "mode": "synced", "remote": res.get("remote_height")}

    if res.get("snapshot"):
        ok = db.apply_utxo_snapshot(res["snapshot"])
        return {"status": "ok" if ok else "error", "mode": "snapshot",
                "applied": ok, "remote": res.get("remote_height")}

    delta = res.get("delta", [])
    if delta:
        _apply_delta(db, delta)
    return {"status": "ok", "mode": "delta", "delta_applied": len(delta),
            "remote": res.get("remote_height")}


def _apply_delta(db, delta_rows):
    db.applyUTXODelta(delta_rows)


if __name__ == "__main__":
    print("=" * 52)
    print("  PAYQUANT MERKLE-DELTA UTXO SYNC DIAGNOSTICS v7.0.0")
    print("=" * 52)
    db = get_db()
    print(f"Local height        : {_height(db)}")
    print(f"UTXO count          : {len(_all_utxos(db))}")
    print(f"Merkle root         : {merkle_root(db)[:24]}...")
    print(f"FULL_SNAPSHOT_GAP   : {FULL_SNAPSHOT_GAP}")
    print("=" * 52)