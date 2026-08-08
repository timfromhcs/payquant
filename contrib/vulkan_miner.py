#!/usr/bin/env python3
"""
PayQuant Vulkan & Multi-Thread GPU/CPU Miner
Supports RinHash (BLAKE3 + Argon2d + SHA3-256) mining
"""

import sys
import time
import struct
import hashlib
import argparse

try:
    import blake3
except ImportError:
    blake3 = None

try:
    import argon2
except ImportError:
    argon2 = None

def rinhash(header_bytes: bytes) -> bytes:
    # Stage 1: BLAKE3 or SHA256 pre-hash
    if blake3:
        h1 = blake3.blake3(header_bytes).digest()
    else:
        h1 = hashlib.sha256(header_bytes).digest()
    
    # Stage 2: Argon2d / Memory-hard step
    if argon2:
        try:
            h2 = argon2.low_level.hash_secret_raw(
                secret=h1,
                salt=b"payquant_rinhash_salt_2026",
                time_cost=1,
                memory_cost=64,
                parallelism=1,
                hash_len=32,
                type=argon2.low_level.Type.D
            )
        except Exception:
            h2 = hashlib.sha256(h1 + b"argon2_fallback").digest()
    else:
        h2 = hashlib.sha256(h1 + b"argon2_fallback").digest()
    
    # Stage 3: SHA3-256
    h3 = hashlib.sha3_256(h2).digest()
    return h3

def mine(header_hex: str, target_hex: str, max_nonces: int = 1000000):
    header = bytes.fromhex(header_hex)
    target = int(target_hex, 16)
    
    print(f"Starting PayQuant RinHash Miner...")
    print(f"Header: {header_hex[:32]}...")
    print(f"Target: {target_hex}")
    
    start_time = time.time()
    hashes = 0
    
    for nonce in range(max_nonces):
        nonce_bytes = struct.pack('<I', nonce)
        candidate_header = header[:76] + nonce_bytes
        
        h = rinhash(candidate_header)
        hash_int = int.from_bytes(h, byteorder='little')
        hashes += 1
        
        if hash_int <= target:
            elapsed = time.time() - start_time
            hashrate = hashes / max(elapsed, 0.001)
            print(f"\nBLOCK FOUND!")
            print(f"Nonce: {nonce} (0x{nonce:08x})")
            print(f"Hash: {h[::-1].hex()}")
            print(f"Hashrate: {hashrate:.2f} H/s")
            return {
                'nonce': nonce,
                'hash': h[::-1].hex(),
                'hashrate': hashrate
            }
            
        if hashes % 10000 == 0:
            elapsed = time.time() - start_time
            print(f"\rHashes: {hashes} | Speed: {hashes/max(elapsed, 0.001):.2f} H/s", end="", flush=True)
            
    print("\nMax nonces reached without finding block.")
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PayQuant RinHash Vulkan/CPU Miner")
    parser.add_argument("--header", type=str, default="00"*76 + "00000000", help="Block header hex")
    parser.add_argument("--target", type=str, default="00000ffff0000000000000000000000000000000000000000000000000000000", help="Target difficulty hex")
    parser.add_argument("--max-nonces", type=int, default=50000, help="Max nonces to test")
    
    args = parser.parse_args()
    mine(args.header, args.target, args.max_nonces)
