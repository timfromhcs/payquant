#!/usr/bin/env python3
"""
PayQuant (PQN) Persistent Blockchain Database Engine v3.0.0
Location: src/db/ / contrib/chain_db.py
Provides persistent SQLite / File block & transaction storage with LevelDB interface compatibility.
Features:
 - getBlock(hash)
 - getBlockByHeight(height)
 - putBlock(block)
 - getBestBlock()
 - getLastHeight()
 - exportChainZip(zipPath)
 - importChainZip(zipPath)
"""

import os
import sys
import json
import sqlite3
import zipfile
import threading
import time

DATA_DIR = os.path.join(os.expanduser("~"), ".payquant") if os.name != 'nt' else os.path.join(os.environ.get('APPDATA', ''), 'PayQuantMainnetData')
DB_PATH = os.path.join(DATA_DIR, "chainstate.db")

GENESIS_BLOCK = {
    "height": 0,
    "hash": "000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d0f5f4bb5c6626d818",
    "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
    "merkle_root": "90a319ee35fae5989c52bfe0c6693ef1f658f24513e2fd41f0fdbd1c465fa7bc",
    "timestamp": 1770000000,
    "nonce": 1048576,
    "miner": "pqn1qgenesisspendenwallettreasury20252026",
    "transactions": [
        {
            "txid": "90a319ee35fae5989c52bfe0c6693ef1f658f24513e2fd41f0fdbd1c465fa7bc",
            "type": "GENESIS_COINBASE",
            "amount": "50.00000000 PQN",
            "signature": "ML-DSA-65 (Dilithium)",
            "recipient": "pqn1qgenesisspendenwallettreasury20252026"
        }
    ]
}

class PersistentChainDB:
    def __init__(self, db_file=None):
        self.db_file = db_file or DB_PATH
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self.lock = threading.Lock()
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blocks (
                    height INTEGER PRIMARY KEY,
                    hash TEXT UNIQUE NOT NULL,
                    prev_hash TEXT NOT NULL,
                    merkle_root TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    nonce INTEGER NOT NULL,
                    miner TEXT NOT NULL,
                    data_json TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    txid TEXT PRIMARY KEY,
                    height INTEGER NOT NULL,
                    recipient TEXT NOT NULL,
                    amount REAL NOT NULL,
                    data_json TEXT NOT NULL,
                    FOREIGN KEY(height) REFERENCES blocks(height)
                )
            """)
            conn.commit()

            # Ensure Genesis Block exists
            cur.execute("SELECT COUNT(*) FROM blocks")
            if cur.fetchone()[0] == 0:
                self._put_block_unlocked(conn, GENESIS_BLOCK)

            conn.close()

    def _put_block_unlocked(self, conn, block):
        cur = conn.cursor()
        txs = block.get("transactions", [])
        data_json = json.dumps(block)
        cur.execute("""
            INSERT OR REPLACE INTO blocks (height, hash, prev_hash, merkle_root, timestamp, nonce, miner, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            block["height"],
            block["hash"],
            block["prev_hash"],
            block["merkle_root"],
            block["timestamp"],
            block["nonce"],
            block.get("miner", ""),
            data_json
        ))

        for tx in txs:
            if isinstance(tx, dict):
                txid = tx.get("txid", "")
                recipient = tx.get("recipient", "")
                amount_str = str(tx.get("amount", "0")).split()[0]
                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 0.0
                cur.execute("""
                    INSERT OR REPLACE INTO transactions (txid, height, recipient, amount, data_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (txid, block["height"], recipient, amount, json.dumps(tx)))
        conn.commit()

    def validate_block_integrity(self, block):
        """Sanity and attack protection checks for incoming block structure"""
        if not block or not isinstance(block, dict):
            return False
        height = block.get("height")
        block_hash = block.get("hash", "")
        prev_hash = block.get("prev_hash", "")
        if height is None or not isinstance(height, int) or height < 0:
            return False
        if not block_hash or len(block_hash) < 10:
            return False
        if height > 0 and not block_hash.startswith("0000"):
            return False
        return True

    def putBlock(self, block):
        if not self.validate_block_integrity(block):
            print(f"[ChainDB Security Warning] Rejected malformed/invalid block structure!")
            return False
        with self.lock:
            conn = self._get_connection()
            try:
                self._put_block_unlocked(conn, block)
                return True
            except Exception as e:
                print(f"[ChainDB Error] putBlock failed: {e}")
                return False
            finally:
                conn.close()

    def getBlock(self, block_hash):
        with self.lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("SELECT data_json FROM blocks WHERE hash = ?", (block_hash,))
            row = cur.fetchone()
            conn.close()
            if row:
                return json.loads(row["data_json"])
            return None

    def getBlockByHeight(self, height):
        with self.lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("SELECT data_json FROM blocks WHERE height = ?", (height,))
            row = cur.fetchone()
            conn.close()
            if row:
                return json.loads(row["data_json"])
            return None

    def getBestBlock(self):
        with self.lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("SELECT data_json FROM blocks ORDER BY height DESC LIMIT 1")
            row = cur.fetchone()
            conn.close()
            if row:
                return json.loads(row["data_json"])
            return GENESIS_BLOCK

    def getLastHeight(self):
        with self.lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("SELECT MAX(height) FROM blocks")
            res = cur.fetchone()[0]
            conn.close()
            return res if res is not None else 0

    def getAllBlocks(self, start_height=0, limit=1000):
        with self.lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("SELECT data_json FROM blocks WHERE height >= ? ORDER BY height ASC LIMIT ?", (start_height, limit))
            rows = cur.fetchall()
            conn.close()
            return [json.loads(r["data_json"]) for r in rows]

    def getAddressUTXOs(self, address):
        """Calculates UTXOs / transactions for given PQN address"""
        with self.lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("SELECT data_json FROM transactions WHERE recipient = ?", (address,))
            rows = cur.fetchall()
            conn.close()
            return [json.loads(r["data_json"]) for r in rows]

    def exportChainZip(self, zip_path=None):
        if not zip_path:
            zip_path = os.path.join(DATA_DIR, "payquant_chain_backup.zip")
        with self.lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("SELECT data_json FROM blocks ORDER BY height ASC")
            all_blocks = [json.loads(r["data_json"]) for r in cur.fetchall()]
            conn.close()

        export_data = {
            "version": "3.0.0",
            "exported_at": time.time(),
            "height": len(all_blocks) - 1,
            "blocks": all_blocks
        }

        temp_json = os.path.join(DATA_DIR, "export_chain_temp.json")
        with open(temp_json, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(temp_json, arcname="payquant_blockchain.json")

        if os.path.exists(temp_json):
            os.remove(temp_json)

        print(f"[ChainDB] Persistent Chain exported to ZIP: {zip_path}")
        return zip_path

    def importChainZip(self, zip_path):
        if not os.path.exists(zip_path):
            return False
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                content = zf.read("payquant_blockchain.json").decode('utf-8')
                data = json.loads(content)
                blocks = data.get("blocks", [])
                for block in blocks:
                    self.putBlock(block)
            print(f"[ChainDB] Successfully imported {len(blocks)} blocks from ZIP!")
            return True
        except Exception as e:
            print(f"[ChainDB Import Error] {e}")
            return False

# Global instance singleton
db_instance = PersistentChainDB()

def get_db():
    return db_instance

if __name__ == '__main__':
    db = get_db()
    print("==================================================")
    print("      PAYQUANT PERSISTENT DB DIAGNOSTIC          ")
    print("==================================================")
    print(f"Database File: {db.db_file}")
    print(f"Current Last Height: {db.getLastHeight()}")
    best = db.getBestBlock()
    print(f"Best Block Hash: {best['hash']}")
    print("==================================================")
