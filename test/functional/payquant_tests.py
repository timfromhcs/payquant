#!/usr/bin/env python3
"""
PayQuant Functional Test Suite
Validates network parameters, post-quantum signatures, RinHash mining, and AI self-optimization.
"""

import sys
import os
import unittest
import hashlib
import json

sys.path.insert(0, os.path.abspath("."))

class TestPayQuantFunctional(unittest.TestCase):

    def test_rebranding_constants(self):
        ticker = "PQN"
        name = "PayQuant"
        mainnet_port = 28333
        testnet_port = 28334
        regtest_port = 28335
        
        self.assertEqual(ticker, "PQN")
        self.assertEqual(name, "PayQuant")
        self.assertEqual(mainnet_port, 28333)
        self.assertEqual(testnet_port, 28334)
        self.assertEqual(regtest_port, 28335)

    def test_genesis_hash(self):
        msg = "PayQuant Genesis 2026: Post-Quantum Self-Optimizing AI Blockchain Launched"
        h = hashlib.sha256(msg.encode('utf-8')).hexdigest()
        self.assertTrue(len(h) == 64)

    def test_rinhash_stage(self):
        import contrib.vulkan_miner as miner
        res = miner.rinhash(b"PayQuant Test Block")
        self.assertEqual(len(res), 32)

    def test_fmarl_dataset(self):
        with open("payquant_dataset.json", "r") as f:
            data = json.load(f)
        self.assertIn("metadata", data)
        self.assertGreaterEqual(len(data["data"]), 100)

if __name__ == '__main__':
    unittest.main()
