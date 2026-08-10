#!/usr/bin/env python3
"""
PayQuant (PQN) Persistent Wallet Storage & Seedphrase Manager v4.0.0

Manages Light Wallet persistence:
 - Auto-loads saved 24-word seedphrase and address on startup.
 - Prevents creating a new wallet every launch.
 - Supports importing / logging into existing wallets via 24-word seedphrase.
 - Cross-platform APPDATA/XDG storage.
"""

import os
import sys
import json
import time
import hashlib
import random

BIP39_WORDLIST = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse",
    "access", "accident", "account", "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act",
    "action", "actor", "actress", "actual", "adapt", "add", "addict", "address", "adjust", "admit",
    "adult", "advance", "advice", "aerobic", "afford", "afraid", "again", "age", "agent", "agree",
    "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol", "alert", "alien",
    "all", "alley", "allow", "almost", "alone", "alpha", "already", "also", "alter", "always",
    "amateur", "amazing", "among", "amount", "amused", "analyst", "anchor", "ancient", "anger", "angle",
    "angry", "animal", "ankle", "announce", "annual", "another", "answer", "antenna", "antique", "anxiety",
    "any", "apart", "apology", "appear", "apple", "approve", "april", "arch", "arctic", "area",
    "arena", "argue", "arm", "armed", "armor", "army", "around", "arrange", "arrest", "arrive",
    "arrow", "art", "artefact", "artist", "artwork", "ask", "aspect", "assault", "asset", "assist",
    "assume", "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction", "audit",
    "august", "aunt", "author", "auto", "autumn", "average", "avocado", "avoid", "awake", "aware",
    "away", "awesome", "awful", "awkward", "axis", "baby", "bachelor", "bacon", "badge", "bag"
]

def user_data_dir():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "PayQuant")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/PayQuant")
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return os.path.join(xdg, "payquant")
    return os.path.join(os.path.expanduser("~"), ".config", "payquant")

def wallet_file_path():
    env = os.environ.get("PAYQUANT_WALLET_FILE")
    if env:
        return env
    return os.path.join(user_data_dir(), "wallet.json")

def derive_address_from_mnemonic(mnemonic_words):
    if isinstance(mnemonic_words, list):
        clean_words = [w.strip().lower() for w in mnemonic_words if w.strip()]
        mnemonic_str = " ".join(clean_words)
    else:
        mnemonic_str = " ".join(str(mnemonic_words).strip().lower().split())
    raw_hash = hashlib.sha256(mnemonic_str.encode("utf-8")).hexdigest()
    return f"pqn1q{raw_hash[:38]}"

def load_wallet():
    """Load persistent wallet from disk. Returns wallet dict or None if missing/corrupt."""
    path = wallet_file_path()
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "mnemonic" in data and "address" in data:
                    return data
    except Exception as e:
        sys.stderr.write(f"[WalletStorage] warning loading wallet: {e}\n")
    return None

def save_wallet(mnemonic, address=None, balance=None, transactions=None):
    """Save wallet data persistently to disk."""
    if isinstance(mnemonic, str):
        mnemonic = mnemonic.strip().lower().split()
    mnemonic_str = " ".join(mnemonic)
    if not address:
        address = derive_address_from_mnemonic(mnemonic_str)

    existing = load_wallet() or {}
    data = {
        "mnemonic": mnemonic,
        "mnemonic_str": mnemonic_str,
        "address": address,
        "balance": balance if balance is not None else existing.get("balance", 250.0),
        "transactions": transactions if transactions is not None else existing.get("transactions", []),
        "updated_at": int(time.time()),
        "created_at": existing.get("created_at", int(time.time()))
    }

    try:
        path = wallet_file_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        return data
    except Exception as e:
        sys.stderr.write(f"[WalletStorage] error saving wallet: {e}\n")
        return None

def create_new_wallet():
    """Generate a brand new random 24-word wallet and save it."""
    words = [random.choice(BIP39_WORDLIST) for _ in range(24)]
    addr = derive_address_from_mnemonic(words)
    return save_wallet(words, addr, balance=250.0, transactions=[])

def import_seedphrase(seedphrase_text):
    """
    Import/log in using an existing 24-word seedphrase.
    Returns (True, wallet_dict) on success or (False, error_message) on failure.
    """
    clean_text = " ".join(str(seedphrase_text).strip().lower().split())
    words = clean_text.split()
    if len(words) != 24:
        return False, f"Invalid seedphrase length: expected 24 words, got {len(words)}."
    
    addr = derive_address_from_mnemonic(words)
    wallet_data = save_wallet(words, addr)
    if wallet_data:
        return True, wallet_data
    return False, "Failed to save imported wallet to disk."

def get_or_create_wallet():
    """Returns saved wallet if exists, otherwise creates and returns a new wallet."""
    existing = load_wallet()
    if existing:
        return existing
    return create_new_wallet()
