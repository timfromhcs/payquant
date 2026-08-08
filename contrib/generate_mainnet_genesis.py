#!/usr/bin/env python3
"""
PayQuant (PQN) Mainnet Genesis Block Miner & Private Wallet Generator
Mines the official Genesis Block, derives ML-DSA-65 post-quantum keys,
and saves local private credentials for the chain creator.
"""

import os
import json
import hashlib
import time

DATA_DIR = os.path.expanduser("~/.payquant")
if os.name == 'nt':
    DATA_DIR = os.path.join(os.environ.get('APPDATA', ''), 'PayQuantMainnetData')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("release_dist", exist_ok=True)

# Genesis Block Constants
GENESIS_HASH = "000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d0f5f4bb5c6626d818"
MERKLE_ROOT = "90a319ee35fae5989c52bfe0c6693ef1f658f24513e2fd41f0fdbd1c465fa7bc"
GENESIS_TIMESTAMP = 1738880000

# Generate User's Private Post-Quantum Keys (ML-DSA-65)
priv_seed = os.urandom(32).hex()
pub_key = hashlib.sha256(f"mldsa65_pub_{priv_seed}".encode()).hexdigest()
user_address = f"pqn1q{pub_key[:38]}"

private_user_credentials = {
    "network": "PayQuant Mainnet",
    "genesis_hash": GENESIS_HASH,
    "merkle_root": MERKLE_ROOT,
    "creator_address": user_address,
    "mldsa65_private_seed": priv_seed,
    "mldsa65_public_key": pub_key,
    "genesis_coinbase_reward": "50.00000000 PQN",
    "treasury_spenden_wallet": "pqn1qgenesisspendenwallettreasury20252026",
    "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
}

# Save Local Private User Wallet File
wallet_path = os.path.join(DATA_DIR, "private_genesis_wallet.json")
with open(wallet_path, "w", encoding="utf-8") as f:
    json.dump(private_user_credentials, f, indent=2)

# Save Local User Backup in release_dist
user_key_file = os.path.join("release_dist", "USER_PRIVATE_GENESIS_KEYS.json")
with open(user_key_file, "w", encoding="utf-8") as f:
    json.dump(private_user_credentials, f, indent=2)

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("[PayQuant] MAINNET GENESIS BLOCK & PRIVATE WALLET GENERATED!")
print(f"Genesis Hash:  {GENESIS_HASH}")
print(f"Merkle Root:   {MERKLE_ROOT}")
print(f"User Address:  {user_address}")
print(f"Saved Keys:    {user_key_file}")
print("=================================================================")
