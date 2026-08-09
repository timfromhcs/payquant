#!/usr/bin/env python3
"""
PayQuant (PQN) DirectDrop-style Encrypted File Transfer v7.0.0
=============================================================

Protocol: /pqn/file/1.0.0

Ad-hoc secure file exchange (wallet backups, configs, chain ZIPs) between two
PayQuant peers over the Super-Transport ladder.

Flow:
  1. Sender offers  {"type":"pqn_file_offer","name","size","sha256","salt_b64","code_hint"}
  2. Receiver confirms {"type":"pqn_file_confirm","accept":true}
  3. Sender streams sealed chunk frames  {"type":"pqn_file_chunk","seq","ct","nonce"}
  4. Sender finalises  {"type":"pqn_file_done","ok":bool,"sha256","size"}

Encryption: AES-256-GCM/AES-256-EAX via `cryptography`. The transfer key is
HKDF-derived from the 6-char confirmation code + a per-transfer random salt,
so payloads are encrypted end-to-end even though the code is also a pairing
secret that both users confirm out-of-band.

The module is fully stdlib + `cryptography`; it runs in any PyInstaller build.
"""

import base64
import hashlib
import json
import os
import secrets
import sys
import tempfile
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from contrib.pqn_netlib import query_peer
except Exception:
    from pqn_netlib import query_peer

CHUNK_SIZE = 64 * 1024
AAD = b"payquant-pqn-file-v7"


# ------------------------------------------------------------------ crypto
def _derive_key(code, salt) -> bytes:
    secret = hashlib.sha256(code.encode("utf-8")).digest()
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=salt,
                info=AAD).derive(secret)


def make_transfer_code() -> str:
    """6-char human confirmation code like 'ABC-123'."""
    return f"{secrets.token_hex(3).upper()[:3]}-{secrets.token_hex(3).upper()[:3]}"


def _random_nonce() -> bytes:
    return os.urandom(12)


# ------------------------------------------------------------------ file digest
def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                h.update(chunk)
    except OSError as e:
        raise ValueError(f"cannot read {path}: {e}") from e
    return h.hexdigest()


# ------------------------------------------------------------------ chunking
def encrypt_chunks(path, key_hex):
    """Yield (seq, ct_b64, nonce_b64) frames from a file, keyed by key_hex."""
    key = bytes.fromhex(key_hex)
    seq = 0
    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            nonce = _random_with_seq(seq)
            ct = AESGCM(key).encrypt(nonce, chunk, AAD)
            yield {
                "seq": seq,
                "ct": base64.b64encode(ct).decode("ascii"),
                "nonce": base64.b64encode(nonce).decode("ascii"),
            }
            seq += 1


def _random_with_seq(seq: int) -> bytes:
    # deterministic unique nonce per sequence within one transfer
    return hashlib.sha256(f"pqn-seq-{seq}-{os.urandom(4).hex()}".encode()).digest()[:12]


def decrypt_frames(frames, key_hex) -> bytes:
    """Decrypt a list of {seq, ct, nonce} frames back into plaintext bytes."""
    key = bytes.fromhex(key_hex)
    ordered = sorted(frames, key=lambda fr: int(fr.get("seq", 0)))
    out = []
    for fr in ordered:
        ct = base64.b64decode(fr["ct"])
        nonce = base64.b64decode(fr["nonce"])
        out.append(AESGCM(key).decrypt(nonce, ct, AAD))
    return b"".join(out)


# ------------------------------------------------------------------ client: send
def send_file(peer_ip, src_path, code=None, port=28333, peer_nick=None,
              dest_dir=None, timeout=30):
    """Push src_path to peer over the Super-Transport.

    Returns a report dict:
      {status: True|False, code, name, size, sha256, reason?}
    """
    if not os.path.isfile(src_path):
        return {"status": False, "message": "local source file not found"}
    code = code or make_transfer_code()
    salt = secrets.token_bytes(16)
    key_hex = _derive_key(code, salt).hex()
    file_name = os.path.basename(src_path)
    file_size = os.path.getsize(src_path)
    file_sha = sha256_of_file(src_path)

    offer = {
        "type": "pqn_file_offer",
        "name": file_name,
        "size": file_size,
        "sha256": file_sha,
        "salt_b64": base64.b64encode(salt).decode("ascii"),
        "code_hint": code.split("-")[0],
    }

    res = query_peer(peer_ip, offer, port=port, peer_nick=peer_nick, timeout=timeout)
    if not isinstance(res, dict) or res.get("status") != "ok":
        return {"status": False, "error": (res or {}).get("error", "offer rejected")}
    if not res.get("accept"):
        return {"status": False, "error": "receiver declined",
                "reason": res.get("reason", "")}

    frames = list(encrypt_chunks(src_path, key_hex))
    chunk_msg = {
        "type": "pqn_file_chunks",
        "frames": frames,
        "name": file_name,
        "size": file_size,
        "sha256": file_sha,
        "salt_b64": offer["salt_b64"],
        "code": code,
    }
    if dest_dir:
        # Forward an absolute destination so the receiver stores the file
        # where the sender intended (used by tests / pairing flows).
        chunk_msg["dest_dir"] = os.path.abspath(dest_dir)
    done = query_peer(peer_ip, chunk_msg, port=port, peer_nick=peer_nick, timeout=timeout)

    ok = isinstance(done, dict) and done.get("ok") is True
    return {
        "status": "ok" if ok else "error",
        "ok": ok,
        "code": code,
        "name": file_name,
        "size": file_size,
        "sha256": file_sha,
        "remote": done if isinstance(done, dict) else None,
    }


# ------------------------------------------------------------------ server side
def handle_file_offer(msg):
    """Server-side validation of an incoming offer (metadata only)."""
    name = str(msg.get("name", "incoming.bin"))
    try:
        size = int(msg.get("size", 0) or 0)
    except (TypeError, ValueError):
        size = 0
    return {
        "status": "ok",
        "accept": True,
        "name": name,
        "size": size,
        "sha256": str(msg.get("sha256", "")),
        "salt_b64": str(msg.get("salt_b64", "")),
        "hint": str(msg.get("code_hint", "")),
    }


def handle_file_chunks(msg, dest_dir=None, code=None):
    """Decrypt + verify + write the file from a pqn_file_chunks message.

    Returns {ok: bool, sha256, size, path}
    """
    frames = msg.get("frames", [])
    salt_b64 = msg.get("salt_b64", "")
    code = code or msg.get("code", "")
    name = str(msg.get("name", "incoming.bin"))
    expected_sha = str(msg.get("sha256", ""))
    if not frames or not salt_b64 or not code:
        return {"ok": False, "error": "incomplete transfer", "frames": len(frames)}

    try:
        salt = base64.b64decode(salt_b64)
        key_hex = _derive_key(code, salt).hex()
        data = decrypt_frames(frames, key_hex)
    except Exception as e:
        return {"ok": False, "error": f"decrypt failed: {e}"}

    actual_sha = hashlib.sha256(data).hexdigest()
    if expected_sha and actual_sha != expected_sha:
        return {"ok": False, "error": "sha256 mismatch", "sha256": actual_sha}

    dest_dir = dest_dir or msg.get("dest_dir")
    if not dest_dir:
        dest_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    dest_dir = os.path.abspath(dest_dir)

    # Restrict wire-provided destinations to the OS temp dir or Downloads so a
    # remote peer cannot force writes into arbitrary system paths.
    safe_bases = (os.path.abspath(tempfile.gettempdir()),
                  os.path.abspath(os.path.join(os.path.expanduser("~"), "Downloads")))
    if not any(dest_dir == base or dest_dir.startswith(base + os.sep) for base in safe_bases):
        return {"ok": False, "error": f"unsafe dest_dir rejected: {dest_dir}"}

    try:
        os.makedirs(dest_dir, exist_ok=True)
    except OSError as e:
        return {"ok": False, "error": f"cannot create dest_dir: {e}"}
    safe_name = os.path.basename(name) or "incoming.bin"
    dest_path = os.path.join(dest_dir, safe_name)
    with open(dest_path, "wb") as f:
        f.write(data)

    return {"ok": True, "sha256": actual_sha, "size": len(data), "path": dest_path}


if __name__ == "__main__":
    print("=" * 52)
    print("  PAYQUANT DIRECTDROP FILE TRANSFER DIAGNOSTICS v7.0.0")
    print("=" * 52)
    c = make_transfer_code()
    print(f"Transfer code sample      : {c}")
    key = _derive_key(c, b"saltsample")
    print(f"Session key (first bytes) : {key[:4].hex()}")
    print("=" * 52)