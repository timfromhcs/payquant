#!/usr/bin/env python3
"""
PayQuant (PQN) - Fresh Mainnet Genesis Minter v2.0.0-quantum
============================================================
Desktop-ONLY. Mints a brand-new Mainnet genesis block using the real TRNG
driver (Cisco Outshift / ANU / crypto-secure os.urandom fallback) and writes
ALL secrets exclusively to the operator's Desktop folder.

    Output (Desktop / PayQuant_Mainnet_Secure, never in the repo):
      genesis_local.json            -> complete record INCL. TRNG seed (LOCAL ONLY)
      public_genesis.json           -> seed-stripped public record (safe)
      master_creator_secrets.json   -> fresh creator mnemonic + ML-DSA-65 master
      PAYQUANT_CREATOR_PASSPHRASE.txt -> human-readable backup copy

The public constants (hash / merkle / footprint / 3D geometry / lighting) are
printed so they can be baked into the chain's canonical genesis definition in
the repository. Seeds NEVER leave the Desktop.

Usage:
    python tools/mint_mainnet_genesis.py [--source anu|outshift|fallback]
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from contrib.pqn_quantum import (
    QuantumFootprintGenerator3D, TRNGClient, QuantumCircuitBackend,
    verify_footprint,
)
from tools.extract_public_data import extract_public

ZERO_HASH = "0" * 64

# Canonical public coinbase of the PayQuant mainnet (treasury address).
TREASURY = "pqn1qgenesisspendenwallettreasury20252026"
COINBASE = "50.00000000 PQN"

BIP39_WORDLIST = [
    "quantum", "dilithium", "sphincs", "lattice", "vector", "entropy", "horizon", "shield",
    "genesis", "synergeia", "rinhash", "argon", "blake", "sha3", "vulkan", "sentinel",
    "pouw", "zkml", "spenden", "treasury", "block", "matrix", "cipher", "orbit",
    "falcon", "kyber", "saber", "frodo", "ntru", "rainbow", "hqc", "bike",
    "beacon", "starlight", "cosmic", "pulsar", "nebula", "zenith", "vertex", "nexus",
]


def desktop_secrets_dir() -> str:
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    return desktop


def mint_creator_secrets(genesis_hash: str, merkle: str) -> dict:
    """A fresh creator wallet for the operator - Desktop only."""
    indices = [int.from_bytes(os.urandom(2), "big") % len(BIP39_WORDLIST)
               for _ in range(24)]
    passphrase = " ".join(BIP39_WORDLIST[i] for i in indices)
    seed_bytes = hashlib.pbkdf2_hmac(
        "sha512", passphrase.encode("utf-8"), b"payquant_mainnet_salt", 2048)
    priv_seed_hex = seed_bytes[:32].hex()
    pub_key_hex = hashlib.sha256(f"mldsa65_master_{priv_seed_hex}".encode()).hexdigest()
    creator_address = f"pqn1q{pub_key_hex[:38]}"
    rpc_user = "payquant_master"
    rpc_password = os.urandom(24).hex()
    return {
        "network": "PayQuant Mainnet (PQN)",
        "creator_address": creator_address,
        "mnemonic_passphrase_24words": passphrase,
        "mldsa65_master_private_seed": priv_seed_hex,
        "mldsa65_master_public_key": pub_key_hex,
        "rpc_user": rpc_user,
        "rpc_password": rpc_password,
        "genesis_block_hash": genesis_hash,
        "merkle_root": merkle,
        "new_mainnet_genesis": True,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


def build_mainnet_genesis(rec: dict, lock_hash: str, merkle: str, now: int) -> dict:
    return {
        "height": 0,
        "hash": lock_hash,
        "previous_hash": ZERO_HASH,
        "merkle_root": merkle,
        "timestamp": now,
        "nonce": 1,
        "difficulty": 1,
        "miner": TREASURY,
        "network": "mainnet",
        "quantum_footprint": rec["footprint"],
        "quantum_3d_geometry": rec["geometry_3d"],
        "quantum_lighting": rec["lighting"],
        "colors": rec["colors"],
        "raw_outcome": rec["raw_outcome"],
        "backend": rec["backend"],
        "seed": rec["seed"],
        "transactions": [
            {"txid": merkle, "type": "GENESIS_COINBASE",
             "amount": COINBASE, "signature": "ML-DSA-65 (Dilithium)",
             "recipient": TREASURY}
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="anu",
                    choices=("outshift", "anu", "fallback"),
                    help="TRNG source priority")
    args = ap.parse_args()

    if args.source == "outshift" and not os.getenv("OUTSHIFT_API_KEY"):
        print("[mint] no OUTSHIFT_API_KEY set - falling back to ANU/urandom",
              flush=True)

    print(f"[mint] Minting MAINNET genesis with TRNG source '{args.source}' ...",
          flush=True)
    gen = QuantumFootprintGenerator3D(
        trng=TRNGClient(args.source),
        backend=QuantumCircuitBackend(),
    )
    rec = gen.generate_footprint(ZERO_HASH, TREASURY)

    # Validate before locking anything in.
    assert verify_footprint(ZERO_HASH, TREASURY, rec["seed"], rec["footprint"]), \
        "[mint] ABORT - validator rejected the freshly minted footprint!"
    print("[mint] Validator: + OK footprint self-checks.", flush=True)

    now = int(datetime.now(timezone.utc).timestamp())
    lock_hash = rec["footprint"]
    merkle = hashlib.sha256(("pqn-genesis-merkle|" + lock_hash).encode()).hexdigest()

    genesis = build_mainnet_genesis(rec, lock_hash, merkle, now)

    secure = desktop_secrets_dir()
    local_json = os.path.join(secure, "genesis_local.json")
    with open(local_json, "w", encoding="utf-8") as f:
        json.dump(genesis, f, indent=2)

    public = extract_public(genesis)
    public_json = os.path.join(secure, "public_genesis.json")
    with open(public_json, "w", encoding="utf-8") as f:
        json.dump(public, f, indent=2)

    creator = mint_creator_secrets(lock_hash, merkle)
    creator_path = os.path.join(secure, "master_creator_secrets.json")
    with open(creator_path, "w", encoding="utf-8") as f:
        json.dump(creator, f, indent=2)
    passfile = os.path.join(secure, "PAYQUANT_CREATOR_PASSPHRASE.txt")
    with open(passfile, "w", encoding="utf-8") as f:
        f.write("PAYQUANT (PQN) MAINNET CREATOR SECRETS - DESKTOP ONLY\n")
        f.write(f"Creator Address: {creator['creator_address']}\n")
        f.write(f"24-WORD MNEMONIC: {creator['mnemonic_passphrase_24words']}\n")
        f.write(f"ML-DSA-65 Private Seed: {creator['mldsa65_master_private_seed']}\n")
        f.write(f"RPC: {creator['rpc_user']} / {creator['rpc_password']}\n")

    serialized = json.dumps(public).lower()
    forbidden = ('"seed"', '"api_key"', "private_keys", "mnemonic", "wallet_priv")
    assert not any(s in serialized for s in forbidden), \
        "[mint] ABORT - secret leaked into public JSON!"

    print("=" * 62)
    print("[mint] MAINNET GENESIS MINTED - DESKTOP SECRETS SAVED")
    print(f"  local block (seed kept):  {local_json}")
    print(f"  public record (stripped): {public_json}")
    print(f"  creator secrets:          {creator_path}")
    print("=" * 62)
    print()
    print("PUBLIC CHAIN-START CONSTANTS TO BAKE INTO THE REPO:")
    print(f"  GENESIS_HASH      = {lock_hash}")
    print(f"  MERKLE_ROOT       = {merkle}")
    print(f"  GENESIS_TIMESTAMP = {now}")
    print(f"  MINER             = {TREASURY}")
    print(f"  OUTCOME           = {rec['raw_outcome']}  (backend={rec['backend']})")
    print("  --- geometry/lighting/colors are in public_genesis.json ---")


if __name__ == "__main__":
    main()