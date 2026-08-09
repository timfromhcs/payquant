#!/usr/bin/env python3
"""
PayQuant (PQN) - Public Data Extraction Tool v2.0.0-quantum
==========================================================
Extracts ONLY public-facing data from a genesis block / footprint run so the
repository never receives seeds, private keys, or wallet internals.

Usage (local desktop only):
    python tools/extract_public_data.py --in genesis_local.json --out public_genesis.json

Input may be either a raw footprint record produced by the local genesis
minter OR a chain block dict. Any 'seed' key is always stripped.
"""

import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

PRIVATE_FIELDS = (
    "seed", "private_key", "private", "secret", "mnemonic", "words",
    "api_key", "key", "signature_raw", "wallet_priv",
)


def _strip_secrets(obj):
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if str(k).lower() in PRIVATE_FIELDS or "priv" in str(k).lower():
                continue
            cleaned[k] = _strip_secrets(v)
        return cleaned
    if isinstance(obj, list):
        return [_strip_secrets(v) for v in obj]
    return obj


def extract_public(block: dict) -> dict:
    """Return a public-only view of a genesis/block dict (seeds removed)."""
    public = _strip_secrets(block)
    # keep explicit public transaction summary
    if "transactions" in public:
        public["transactions"] = [
            {k: v for k, v in (t.items() if isinstance(t, dict) else ())
             if str(k).lower() in ("type", "amount", "recipient")}
            for t in block.get("transactions", [])
            if isinstance(t, dict)
        ]
    return public


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", required=True, help="Local/private genesis block JSON")
    ap.add_argument("--out", required=True, help="Public output JSON (safe to commit)")
    args = ap.parse_args()

    with open(args.inp, "r", encoding="utf-8") as f:
        block = json.load(f)
    public = extract_public(block)

    # hard safety: refuse to publish a file that still carries secret fields
    serialized = json.dumps(public).lower()
    forbidden = ('"seed"', '"api_key"', "private_keys", "mnemonic", "wallet_priv")
    for s in forbidden:
        if s in serialized:
            raise SystemExit(f"REFUSED: private field {s!r} survived extraction; aborting")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(public, f, indent=2)
    print(f"[extract_public_data] Wrote public genesis: {args.out}")
    print("[extract_public_data] Seeds/keys stripped. Only public data written.")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(public, f, indent=2)
    print(f"[extract_public_data] Wrote public genesis: {args.out}")


if __name__ == "__main__":
    main()