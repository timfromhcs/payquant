import struct
import hashlib
import time

def sha256d(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def create_coinbase(psz_timestamp, genesis_reward=5000000000):
    pubkey = bytes.fromhex("04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f")
    
    script_sig = (
        b'\x04\xff\xff\x00\x1d' +
        b'\x01\x04' +
        bytes([len(psz_timestamp)]) + psz_timestamp.encode('ascii')
    )
    
    tx_in = (
        b'\x00' * 32 +
        b'\xff\xff\xff\xff' +
        bytes([len(script_sig)]) + script_sig +
        b'\xff\xff\xff\xff'
    )
    
    script_pubkey = b'\x41' + pubkey + b'\xac'
    
    tx_out = (
        struct.pack('<Q', genesis_reward) +
        bytes([len(script_pubkey)]) + script_pubkey
    )
    
    tx = (
        struct.pack('<I', 1) +
        b'\x01' + tx_in +
        b'\x01' + tx_out +
        struct.pack('<I', 0)
    )
    
    return tx

def calculate_merkle_root(tx_bytes):
    return sha256d(tx_bytes)

def generate_genesis(psz_timestamp, n_time, n_bits, n_version=1, genesis_reward=5000000000):
    tx = create_coinbase(psz_timestamp, genesis_reward)
    merkle_root = calculate_merkle_root(tx)
    
    target = (n_bits & 0x00ffffff) * 2**(8 * ((n_bits >> 24) - 3))
    
    print(f"Mining Genesis Block for timestamp: '{psz_timestamp}'...")
    print(f"Time: {n_time}, Bits: 0x{n_bits:08x}, Target: 0x{target:064x}")
    print(f"Merkle Root: {merkle_root[::-1].hex()}")
    
    nonce = 0
    start = time.time()
    
    while nonce < 0xffffffff:
        header = (
            struct.pack('<i', n_version) +
            b'\x00' * 32 +
            merkle_root +
            struct.pack('<I', n_time) +
            struct.pack('<I', n_bits) +
            struct.pack('<I', nonce)
        )
        hash_result = sha256d(header)
        hash_int = int.from_bytes(hash_result, byteorder='little')
        
        if hash_int <= target:
            elapsed = time.time() - start
            block_hash = hash_result[::-1].hex()
            print(f"Genesis block found in {elapsed:.2f}s!")
            print(f"Nonce: {nonce} (0x{nonce:08x})")
            print(f"Hash: {block_hash}")
            return {
                'psz_timestamp': psz_timestamp,
                'n_time': n_time,
                'n_nonce': nonce,
                'n_bits': f"0x{n_bits:08x}",
                'merkle_root': merkle_root[::-1].hex(),
                'hash': block_hash
            }
        nonce += 1
    
    raise RuntimeError("Failed to find genesis nonce within range")

if __name__ == '__main__':
    timestamp_msg = "PayQuant Genesis 2026: Post-Quantum Self-Optimizing AI Blockchain Launched"
    n_time = 1770000000
    bits = 0x1e0ffff0
    res = generate_genesis(timestamp_msg, n_time, bits)
    print("\nC++ Chainparams Snippet:")
    print(f'const char* pszTimestamp = "{res["psz_timestamp"]}";')
    print(f'genesis = CreateGenesisBlock(pszTimestamp, genesisOutputScript, {res["n_time"]}, {res["n_nonce"]}, {res["n_bits"]}, 1, 50 * COIN);')
    print(f'consensus.hashGenesisBlock = genesis.GetHash();')
    print(f'assert(consensus.hashGenesisBlock == uint256{{"{res["hash"]}"}});')
    print(f'assert(genesis.hashMerkleRoot == uint256{{"{res["merkle_root"]}"}});')
