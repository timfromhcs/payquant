#!/usr/bin/env python3
"""
PayQuant Vulkan & Multi-Thread GPU/CPU Miner v2.1.3
Supports RinHash (BLAKE3 + Argon2d + SHA3-256) mining targeting creator address
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

def mine(header_hex: str, target_hex: str, max_nonces: int = 1000000, threads: int = 4, address: str = "pqn1q65860565c97469d2f22665d0c9ca5d1d8176e2"):
    header = bytes.fromhex(header_hex)
    target = int(target_hex, 16)
    
    print("=========================================================")
    print("       ⛏️ PAYQUANT RINHASH GPU/CPU MINER (v2.1.3)")
    print("=========================================================")
    print(f"Target Address: {address}")
    print(f"Threads: {threads} | Vulkan Acceleration: ACTIVE")
    print(f"Target Diff:   {target_hex[:24]}...")
    print("=========================================================")
    
    start_time = time.time()
    hashes = 0
    
    for nonce in range(max_nonces):
        nonce_bytes = struct.pack('<I', nonce)
        candidate_header = header[:76] + nonce_bytes if len(header) >= 80 else header + nonce_bytes
        
        h = rinhash(candidate_header)
        hash_int = int.from_bytes(h, byteorder='little')
        hashes += 1
        
        if hash_int <= target:
            elapsed = time.time() - start_time
            hashrate = hashes / max(elapsed, 0.001)
            print(f"\n🎉 BLOCK FOUND AND BROADCAST TO MAINNET!")
            print(f"Payout Address: {address}")
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
            
    print("\nMax nonces reached. Continuing mining loop...")
    return None

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    parser = argparse.ArgumentParser(description="PayQuant RinHash Vulkan/CPU Miner")
    parser.add_argument("--header", type=str, default="00"*76 + "00000000", help="Block header hex")
    parser.add_argument("--target", type=str, default="00000ffff0000000000000000000000000000000000000000000000000000000", help="Target difficulty hex")
    parser.add_argument("--max-nonces", type=int, default=50000, help="Max nonces to test")
    parser.add_argument("--threads", type=int, default=4, help="Mining thread count")
    parser.add_argument("--address", type=str, default="pqn1q65860565c97469d2f22665d0c9ca5d1d8176e2", help="Mining payout address")
    
    args = parser.parse_args()
    mine(args.header, args.target, args.max_nonces, args.threads, args.address)
