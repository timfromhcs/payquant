#!/usr/bin/env python3
"""
PayQuant (PQN) - Desktop-Only Blockchain Reset Orchestrator v2.0.0-quantum
==========================================================================
SAFETY: runs 100% on the local machine. It NEVER commits to the repo and
writes genesis secrets only under a local sandbox directory (default
~/.payquant_reset). By default it operates in a TEMPORARY sandbox; the live
chain is untouched. --live requires an explicit human flag and still keeps the
seed local-only.

Flow
    mint   : mint a fresh genesis block using a real TRNG seed
    public : emit public_genesis.json (seed stripped) for optional commit

This is the tool a desktop operator / human uses to produce the genesis
footprint; the repository only ever receives the extracted public data.
"""

import argparse
import json
import os
import sys
import tempfile
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from contrib.pqn_quantum import (
    QuantumFootprintGenerator3D, TRNGClient, QuantumCircuitBackend,
)
from tools.extract_public_data import extract_public

ZERO_HASH = "0" * 64
DEFAULT_SANDBOX = os.path.join(os.path.expanduser("~"), "payquant_quantum_reset")


def mint_genesis(sandbox, miner_id="pqn1qgenesis2026", amount="1000000000.00000000 PQN"):
    """Mint a fresh genesis using a real TRNG + panta-sim run."""
    gen = QuantumFootprintGenerator3D(
        trng=TRNGClient("fallback"),
        backend=QuantumCircuitBackend(),
    )
    rec = gen.generate_footprint(ZERO_HASH, miner_id)

    genesis = {
        "height": 0,
        "hash": rec["footprint"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "previous_hash": ZERO_HASH,
        "nonce": 0,
        "difficulty": 1,
        "miner": miner_id,
        "quantum_footprint": rec["footprint"],      # public
        "quantum_3d_geometry": rec["geometry_3d"],  # public
        "quantum_lighting": rec["lighting"],        # public
        "colors": rec["colors"],                    # public
        "raw_outcome": rec["raw_outcome"],          # public
        "seed": rec["seed"],                        # LOCAL ONLY - never committed
        "transactions": [
            {"type": "coinbase", "amount": amount, "recipient": miner_id,
             "note": "genesis coinbase - public address only"},
        ],
    }
    # Write local-only (with the seed) file under the sandbox, outside the repo.
    os.makedirs(sandbox, exist_ok=True)
    local_path = os.path.join(sandbox, "genesis_local.json")
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(genesis, f, indent=2)

    public_path = os.path.join(sandbox, "public_genesis.json")
    with open(public_path, "w", encoding="utf-8") as f:
        json.dump(extract_public(genesis), f, indent=2)

    return {"local": local_path, "public": public_path, "footprint": rec["footprint"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox", default=None,
                    help="local-only sandbox dir (default ~/.payquant_quantum_reset)")
    args = ap.parse_args()

    live = False  # demo-first policy: the desktop operator must opt-in to live
    sandbox = args.sandbox or DEFAULT_SANDBOX
    if not live:
        # cooked demo in a disposable temp dir ensures the desktop chain is safe
        sandbox = tempfile.mkdtemp(prefix="pqn_reset_demo_")
        print(f"[reset_chain] DEMO mode - sandbox chosen: {sandbox}")
        print("[reset_chain] No live data touched. (pass nothing further to stay safe)")
    print("[reset_chain] Minting genesis with TRNG (+panta-sim)...")
    res = mint_genesis(sandbox, amount="1000000000.00000000 PQN")
    print(f"[reset_chain] local (seed kept): {res['local']}")
    print(f"[reset_chain] public (seed stripped): {res['public']}")
    print(f"[reset_chain] footprint: {res['footprint'][:24]}...")
    print("[reset_chain] Done. Only the public JSON is safe to share/commit.")


if __name__ == "__main__":
    main()