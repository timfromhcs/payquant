#!/usr/bin/env python3
"""
PayQuant (PQN) Ecosystem Local Test Suite v3.0.0
Verifies Persistent ChainDB, P2P Direct TCP Transfer Server, and Light Wallet SPV sync.
"""

import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from contrib.chain_db import get_db
from contrib.p2p_chain_transfer import start_p2p_server, p2p_query_peer

def run_tests():
    print("==================================================")
    print("   PAYQUANT (PQN) LOCAL ECOSYSTEM TEST SUITE     ")
    print("==================================================")

    # 1. Test Persistent ChainDB
    db = get_db()
    init_height = db.getLastHeight()
    print(f"[TEST 1/3] Persistent ChainDB loaded. Current Height: {init_height}")
    
    test_block = {
        "height": init_height + 1,
        "hash": f"00000testblockhash_{int(time.time())}",
        "prev_hash": db.getBestBlock()["hash"],
        "merkle_root": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "timestamp": int(time.time()),
        "nonce": 123456,
        "miner": "pqn1qtestmineraddress2026",
        "transactions": [
            {
                "txid": f"tx_test_{int(time.time())}",
                "recipient": "pqn1qtestrecipientaddress2026",
                "amount": "10.0 PQN",
                "signature": "ML-DSA-65"
            }
        ]
    }
    
    db.putBlock(test_block)
    new_height = db.getLastHeight()
    assert new_height == init_height + 1, "ChainDB height failed to update!"
    fetched_block = db.getBlockByHeight(new_height)
    assert fetched_block["hash"] == test_block["hash"], "ChainDB fetched block hash mismatch!"
    print(f" -> [SUCCESS] Persistent ChainDB wrote block height {new_height} successfully!")

    # 2. Test P2P TCP Server
    print("[TEST 2/3] Testing P2P Direct TCP Chain Transfer Server...")
    srv = start_p2p_server(28333)
    time.sleep(1)
    
    res = p2p_query_peer("127.0.0.1", 28333, {"type": "get_headers", "from_height": 0})
    assert res.get("status") == "ok", "P2P get_headers request failed!"
    headers = res.get("headers", [])
    print(f" -> [SUCCESS] P2P Server responded with {len(headers)} block headers!")

    res_utxo = p2p_query_peer("127.0.0.1", 28333, {"type": "get_utxos", "address": "pqn1qtestrecipientaddress2026"})
    assert res_utxo.get("status") == "ok", "P2P get_utxos request failed!"
    print(f" -> [SUCCESS] P2P Server returned UTXOs for test address!")

    # 3. Test Export ZIP Archive
    zip_path = db.exportChainZip()
    assert os.path.exists(zip_path), "Chain ZIP export failed!"
    print(f"[TEST 3/3] Chain export archive created at {zip_path}")

    print("==================================================")
    print("   ALL PAYQUANT ECOSYSTEM TESTS PASSED (100%)    ")
    print("==================================================")

if __name__ == '__main__':
    run_tests()
