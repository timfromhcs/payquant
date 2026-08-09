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


def seed_for_public(block: dict) -> int:
    """Deterministic public seed derived from the block hash (NOT the TRNG seed).

    This makes the gallery reproducible by any node from public headers alone,
    while real mined blocks use a TRNG seed that is never exposed.
    """
    h = hashlib.sha256(f"pqn-public-diamond|{block.get('hash', '')}".encode()).digest()
    return int.from_bytes(h[:4], "big")


def build_gallery(limit: int = 64) -> dict:
    db = get_db()
    last = int(db.getLastHeight() or 0)
    gen = QuantumFootprintGenerator3D()
    blocks = []
    for h in range(max(0, last - limit + 1), last + 1):
        blk = db.getBlockByHeight(h)
        if not blk:
            continue
        block_hash = blk.get("hash", "")
        # public micro-footprint per block (derived from public fields)
        payload = f"{block_hash}|{blk.get('merkle_root', '')}|{blk.get('miner', '')}"
        fp = hashlib.sha256(payload.encode()).hexdigest()
        geom = gen.hash_to_3d(fp)
        light = gen.hash_to_lighting(fp)
        colors = gen.hash_to_colors(fp)
        blocks.append({
            "height": int(h),
            "hash": block_hash,
            "timestamp": blk.get("timestamp", 0),
            "miner": blk.get("miner", ""),
            "quantum_footprint": fp,
            "geometry_3d": geom,
            "lighting": light,
            "colors": colors,
        })
    payload_doc = {
        "engine": "pqn_quantum 2.0.0-quantum",
        "generated_from": "public_block_headers",
        "count": len(blocks),
        "note": "Public-only: geometry derived from block hashes. No seeds committed.",
        "diamonds": blocks,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload_doc, f, indent=1)
    return OUT_FILE


if __name__ == "__main__":
    print("Building public 3D diamond gallery from local block headers...")
    path = build_gallery()
    print(f"Wrote {path}")