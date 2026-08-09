#!/usr/bin/env python3
"""
PayQuant (PQN) Public 3D Diamond Gallery Builder v2.0.0-quantum
==============================================================
Reads the local chain DB (block headers only = public data) and produces a
PUBLIC gallery of each block's quantum 3D diamond representation.

Design principle: the 3D diamond geometry is derived only from PUBLIC data
(footprint, which itself is the SHA-256 of public block fields + most
probable quantum outcome). No TRNG seed, private key, or wallet content is
exported. The seed used at mint time is never written here.

Output: explorer_3d/diamonds.json  (public, safe to commit)
"""

import hashlib
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from contrib.chain_db import get_db
from contrib.pqn_quantum.footprints import QuantumFootprintGenerator3D

OUT_DIR = os.path.join(BASE_DIR, "explorer_3d")
OUT_FILE = os.path.join(OUT_DIR, "diamonds.json")


def build_gallery(limit: int = 64) -> dict:
    db = get_db()
    last = int(db.getLastHeight() or 0)
    gen = QuantumFootprintGenerator3D()
    blocks = [genesis_entry(gen)]
    for h in range(max(1, last - limit + 2), last + 1):
        blk = db.getBlockByHeight(h)
        if not blk:
            continue
        block_hash = blk.get("hash", "")
        # public micro-footprint per block (derived from public fields)
        payload = f"{block_hash}|{blk.get('merkle_root', '')}|{blk.get('miner', '')}"
        fp = hashlib.sha256(payload.encode()).hexdigest()
        blocks.append(block_entry(blk, fp, gen))
    payload_doc = {
        "engine": "pqn_quantum 2.0.0-quantum",
        "generated_from": "public_block_headers + canonical mainnet genesis",
        "count": len(blocks),
        "note": "Public-only: geometry derived from public hashes. No seeds committed.",
        "diamonds": blocks,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload_doc, f, indent=1)
    return OUT_FILE


def genesis_entry(gen: QuantumFootprintGenerator3D) -> dict:
    """The canonical mainnet genesis (height 0) as a public gallery diamond."""
    from contrib.chain_db import GENESIS_BLOCK
    gb = GENESIS_BLOCK
    fp = gb["quantum_footprint"]
    return {
        "height": 0,
        "hash": gb["hash"],
        "timestamp": gb.get("timestamp", 0),
        "miner": gb.get("miner", ""),
        "quantum_footprint": fp,
        "geometry_3d": gen.hash_to_3d(fp),
        "lighting": gen.hash_to_lighting(fp),
        "colors": gen.hash_to_colors(fp),
    }


def block_entry(blk: dict, fp: str, gen) -> dict:
    return {
        "height": int(blk.get("height", 0)),
        "hash": blk.get("hash", ""),
        "timestamp": blk.get("timestamp", 0),
        "miner": blk.get("miner", ""),
        "quantum_footprint": fp,
        "geometry_3d": gen.hash_to_3d(fp),
        "lighting": gen.hash_to_lighting(fp),
        "colors": gen.hash_to_colors(fp),
    }


if __name__ == "__main__":
    print("Building public 3D diamond gallery from local block headers...")
    path = build_gallery()
    print(f"Wrote {path}")