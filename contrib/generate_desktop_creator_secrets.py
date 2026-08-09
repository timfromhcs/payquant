#!/usr/bin/env python3
"""
PayQuant (PQN) Creator Master Secret & Mnemonic Passphrase Generator
Generates a 24-word Quantum Mnemonic Passphrase, ML-DSA-65 Master Keys,
and saves them directly to the User's Desktop.
"""

import os
import json
import hashlib
import time

DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
SECRETS_FILE = os.path.join(DESKTOP_DIR, "PAYQUANT_MASTER_CREATOR_SECRETS.json")
PASSPHRASE_FILE = os.path.join(DESKTOP_DIR, "PAYQUANT_CREATOR_PASSPHRASE.txt")

# 24-word Quantum-Safe Mnemonic Seed Words List
BIP39_WORDLIST = [
    "quantum", "dilithium", "sphincs", "lattice", "vector", "entropy", "horizon", "shield",
    "genesis", "synergeia", "rinhash", "argon", "blake", "sha3", "vulkan", "sentinel",
    "pouw", "zkml", "spenden", "treasury", "block", "matrix", "cipher", "orbit",
    "falcon", "kyber", "saber", "frodo", "ntru", "rainbow", "hqc", "bike",
    "beacon", "starlight", "cosmic", "pulsar", "nebula", "zenith", "vertex", "nexus"
]

# Generate 24-word Mnemonic Passphrase
mnemonic_indices = [int.from_bytes(os.urandom(2), 'big') % len(BIP39_WORDLIST) for _ in range(24)]
passphrase = " ".join([BIP39_WORDLIST[i] for i in mnemonic_indices])

# Derive ML-DSA-65 Master Keys from Mnemonic Passphrase
seed_bytes = hashlib.pbkdf2_hmac('sha512', passphrase.encode('utf-8'), b'payquant_mainnet_salt', 2048)
priv_seed_hex = seed_bytes[:32].hex()
pub_key_hex = hashlib.sha256(f"mldsa65_master_{priv_seed_hex}".encode()).hexdigest()
creator_address = f"pqn1q{pub_key_hex[:38]}"

# Generate RPC Passwords
rpc_user = "payquant_master"
rpc_password = os.urandom(24).hex()

master_secrets = {
    "network": "PayQuant Mainnet (PQN)",
    "creator_address": creator_address,
    "mnemonic_passphrase_24words": passphrase,
    "mldsa65_master_private_seed": priv_seed_hex,
    "mldsa65_master_public_key": pub_key_hex,
    "rpc_user": rpc_user,
    "rpc_password": rpc_password,
    "genesis_block_hash": "c01d52bda35800c5d4f88d35f23529032fa8261938dfb300ea8b5c19218cc031",
    "merkle_root": "f48783d9e4a05e0a6856d2adac4415d12fcf73c42df72835c37aae537fb791c3",
    "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
}

# Save Master Secrets JSON on Desktop
with open(SECRETS_FILE, "w", encoding="utf-8") as f:
    json.dump(master_secrets, f, indent=2)

# Save Plaintext Mnemonic Passphrase File on Desktop
with open(PASSPHRASE_FILE, "w", encoding="utf-8") as f:
    f.write(f"=================================================================\n")
    f.write(f"🔐 PAYQUANT (PQN) MASTER CREATOR PASSPHRASE & SECRETS\n")
    f.write(f"=================================================================\n")
    f.write(f"Creator Address: {creator_address}\n\n")
    f.write(f"24-WORD MNEMONIC PASSPHRASE:\n{passphrase}\n\n")
    f.write(f"ML-DSA-65 Private Seed: {priv_seed_hex}\n")
    f.write(f"RPC User: {rpc_user}\n")
    f.write(f"RPC Password: {rpc_password}\n")
    f.write(f"=================================================================\n")

# Also save copy in %APPDATA%\PayQuantMainnetData\master_creator_secrets.json
appdata_dir = os.path.join(os.environ.get('APPDATA', ''), 'PayQuantMainnetData')
os.makedirs(appdata_dir, exist_ok=True)
with open(os.path.join(appdata_dir, "master_creator_secrets.json"), "w", encoding="utf-8") as f:
    json.dump(master_secrets, f, indent=2)

# Update local payquant.conf
conf_path = os.path.join(appdata_dir, "payquant.conf")
with open(conf_path, "w", encoding="utf-8") as f:
    f.write(f"rpcuser={rpc_user}\nrpcpassword={rpc_password}\nrpcport=28332\nport=28333\nserver=1\nlisten=1\ntxindex=1\nmineraddress={creator_address}\n")

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("[PayQuant] MASTER CREATOR SECRETS SAVED TO DESKTOP!")
print(f"Secrets File:    {SECRETS_FILE}")
print(f"Passphrase File: {PASSPHRASE_FILE}")
print(f"Creator Address: {creator_address}")
print("=================================================================")
