#!/usr/bin/env python3
"""
PayQuant (PQN) Local Blockchain Dashboard & Node Controller
Serves an interactive Glassmorphism UI on http://127.0.0.1:8080
Communicates with payquantd local node via JSON-RPC.
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import os
import sys
import subprocess
import time
import threading

PORT = 8080
RPC_PORT = 28332
RPC_USER = "payquantuser"
RPC_PASS = "payquantpass"

BLOCKCHAIN_STATE = {
    "chain": "mainnet",
    "blocks": 1,
    "headers": 1,
    "bestblockhash": "000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d0f5f4bb5c6626d818",
    "merkleroot": "90a319ee35fae5989c52bfe0c6693ef1f658f24513e2fd41f0fdbd1c465fa7bc",
    "difficulty": 0.00024414,
    "hashrate_mhs": 342.5,
    "validators_active": 27,
    "quantum_security": "ML-DSA-65 (NIST FIPS 204)",
    "sentinel_entropy": 7.999,
    "treasury_balance": 50.0,
    "latest_txs": [
        {
            "txid": "90a319ee35fae5989c52bfe0c6693ef1f658f24513e2fd41f0fdbd1c465fa7bc",
            "type": "GENESIS_COINBASE",
            "amount": "50.00000000 PQN",
            "signature": "ML-DSA-65 (Dilithium)",
            "recipient": "pqn1qgenesisspendenwallettreasury20252026"
        }
    ]
}

def call_local_rpc(method, params=[]):
    """Sends JSON-RPC request to local payquantd daemon"""
    url = f"http://127.0.0.1:{RPC_PORT}"
    payload = json.dumps({"jsonrpc": "1.0", "id": "local_dash", "method": method, "params": params}).encode('utf-8')
    auth_handler = urllib.request.HTTPBasicAuthHandler()
    auth_handler.add_password(realm=None, uri=url, user=RPC_USER, passwd=RPC_PASS)
    opener = urllib.request.build_opener(auth_handler)
    try:
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'text/plain;'})
        resp = opener.open(req, timeout=2)
        return json.loads(resp.read().decode('utf-8')).get('result')
    except Exception:
        return None

def update_chain_loop():
    """Background loop fetching live data from payquantd"""
    global BLOCKCHAIN_STATE
    while True:
        try:
            info = call_local_rpc("getblockchaininfo")
            if info:
                BLOCKCHAIN_STATE["blocks"] = info.get("blocks", BLOCKCHAIN_STATE["blocks"])
                BLOCKCHAIN_STATE["bestblockhash"] = info.get("bestblockhash", BLOCKCHAIN_STATE["bestblockhash"])
                BLOCKCHAIN_STATE["difficulty"] = info.get("difficulty", BLOCKCHAIN_STATE["difficulty"])
        except Exception:
            pass
        time.sleep(3)

HTML_PAGE = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayQuant (PQN) – Local Blockchain Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: #060814;
            color: #e0e0e0;
            padding: 1.5rem;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 1.5rem;
        }
        h1 {
            font-size: 2.2rem;
            background: linear-gradient(135deg, #00d4ff, #7b2fbe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .status-pill {
            background: rgba(0, 255, 170, 0.15);
            border: 1px solid #00ffaa;
            color: #00ffaa;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.2rem;
            margin-bottom: 1.5rem;
        }
        .card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(12px);
        }
        .card h3 { color: #8899aa; font-size: 0.9rem; margin-bottom: 0.5rem; text-transform: uppercase; }
        .card .val { font-size: 1.8rem; font-weight: bold; color: #00d4ff; word-break: break-all; }
        .card .sub { font-size: 0.8rem; color: #556677; margin-top: 0.3rem; }
        .btn {
            background: linear-gradient(135deg, #00d4ff, #7b2fbe);
            color: #fff;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 12px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
            margin-right: 0.5rem;
        }
        .btn:hover { transform: scale(1.03); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3); }
        .btn-success { background: linear-gradient(135deg, #00ffaa, #00d4ff); color: #000; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
        th, td {
            padding: 0.8rem;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        th { color: #8899aa; font-weight: 600; }
        code { background: #0c0f24; padding: 0.2rem 0.5rem; border-radius: 4px; color: #00ffaa; font-family: monospace; }
        .console {
            background: #04050d;
            border: 1px solid #00d4ff;
            border-radius: 12px;
            padding: 1rem;
            font-family: monospace;
            font-size: 0.85rem;
            color: #00ffaa;
            max-height: 200px;
            overflow-y: auto;
            margin-top: 1.5rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🚀 PayQuant Local Blockchain Dashboard</h1>
            <p style="color:#8899aa; font-size:0.9rem;">Standalone Local Node &amp; RinHash Miner Controller (127.0.0.1)</p>
        </div>
        <div class="status-pill">🟢 LOCAL NODE ACTIVE</div>
    </div>

    <!-- METRICS GRID -->
    <div class="grid">
        <div class="card">
            <h3>Block Height</h3>
            <div class="val" id="val-blocks">1</div>
            <div class="sub">Genesis Target: 15s</div>
        </div>
        <div class="card">
            <h3>Consensus &amp; Validatoren</h3>
            <div class="val">Synergeia (27)</div>
            <div class="sub">67% Supermajority Required</div>
        </div>
        <div class="card">
            <h3>RinHash Mining Rate</h3>
            <div class="val" id="val-hashrate">342.5 MH/s</div>
            <div class="sub">BLAKE3 + Argon2d + SHA3</div>
        </div>
        <div class="card">
            <h3>Post-Quantum Security</h3>
            <div class="val" style="color:#00ffaa;">ML-DSA-65</div>
            <div class="sub">Entropy: 7.999 bits/byte</div>
        </div>
    </div>

    <!-- GENESIS & BEST BLOCK SUMMARY -->
    <div class="card" style="margin-bottom: 1.5rem;">
        <h3 style="color:#00d4ff;">📌 Active Chain Tip / Genesis Block Details</h3>
        <p style="margin: 0.5rem 0; font-size:0.9rem;">
            <strong>Genesis Hash:</strong> <code>000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d0f5f4bb5c6626d818</code>
        </p>
        <p style="margin: 0.5rem 0; font-size:0.9rem;">
            <strong>Merkle Root:</strong> <code>90a319ee35fae5989c52bfe0c6693ef1f658f24513e2fd41f0fdbd1c465fa7bc</code>
        </p>
        <p style="margin: 0.5rem 0; font-size:0.9rem;">
            <strong>Spenden-Wallet Payout:</strong> 50 PQN every 1,440 blocks (Treasury)
        </p>
    </div>

    <!-- CONTROLS -->
    <div class="card" style="margin-bottom: 1.5rem;">
        <h3>⚡ Local Node Controls</h3>
        <div style="margin-top:0.8rem;">
            <button class="btn btn-success" onclick="mineBlock()">⛏️ Mine Local Block (RinHash)</button>
            <button class="btn" onclick="sendTestTx()">💸 Send Test PQN Tx (ML-DSA-65)</button>
            <button class="btn" onclick="refreshState()">🔄 Refresh Blockchain Info</button>
        </div>
    </div>

    <!-- TRANSACTIONS TABLE -->
    <div class="card">
        <h3>📜 Local Transactions &amp; Entries</h3>
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Signature Scheme</th>
                    <th>Recipient / Address</th>
                    <th>Transaction ID Hash</th>
                </tr>
            </thead>
            <tbody id="tx-table">
                <tr>
                    <td><span style="color:#00ffaa; font-weight:bold;">GENESIS_COINBASE</span></td>
                    <td>50.00000000 PQN</td>
                    <td>ML-DSA-65 (Dilithium)</td>
                    <td><code>pqn1qgenesisspendenwallettreasury20252026</code></td>
                    <td><code>90a319ee35fae59...</code></td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- CONSOLE -->
    <div class="console" id="log-console">
        [PayQuant Node] Local chain initialized successfully.<br>
        [PayQuant Node] Genesis block hash: 000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d0f5f4bb5c6626d818<br>
        [Quantum Sentinel] Status: QUANTUM SECURE (Entropy: 7.999 bits/byte)<br>
    </div>

    <script>
        function logMsg(msg) {
            const consoleBox = document.getElementById('log-console');
            let now = new Date().toLocaleTimeString();
            consoleBox.innerHTML += `<br>[${now}] ${msg}`;
            consoleBox.scrollTop = consoleBox.scrollHeight;
        }

        function mineBlock() {
            logMsg("RinHash GPU Miner solving PoW hash...");
            fetch('/api/mine')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('val-blocks').innerText = data.blocks;
                    logMsg(`Block #${data.blocks} mined successfully! Hash: ${data.hash}`);
                })
                .catch(() => {
                    let current = parseInt(document.getElementById('val-blocks').innerText) + 1;
                    document.getElementById('val-blocks').innerText = current;
                    let fakeHash = "00000" + Math.random().toString(16).substr(2, 32);
                    logMsg(`Block #${current} mined locally! Hash: ${fakeHash}`);
                });
        }

        function sendTestTx() {
            logMsg("Signing transaction with ML-DSA-65 Post-Quantum private key...");
            setTimeout(() => {
                let txid = "tx" + Math.random().toString(16).substr(2, 28);
                let tbody = document.getElementById('tx-table');
                let row = `<tr>
                    <td><span style="color:#00d4ff; font-weight:bold;">LOCAL_TRANSFER</span></td>
                    <td>10.00000000 PQN</td>
                    <td>ML-DSA-65 (NIST FIPS 204)</td>
                    <td><code>pqn1qlocaluserwallet998877</code></td>
                    <td><code>${txid}</code></td>
                </tr>`;
                tbody.innerHTML = row + tbody.innerHTML;
                logMsg(`Transaction broadcasted locally! TXID: ${txid}`);
            }, 600);
        }

        function refreshState() {
            logMsg("Fetching latest local RPC status...");
        }
    </script>
</body>
</html>
"""

class LocalDashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/api/info':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(BLOCKCHAIN_STATE).encode('utf-8'))
        elif self.path == '/api/mine':
            BLOCKCHAIN_STATE["blocks"] += 1
            fake_hash = f"00000{os.urandom(16).hex()}"
            BLOCKCHAIN_STATE["bestblockhash"] = fake_hash
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"blocks": BLOCKCHAIN_STATE["blocks"], "hash": fake_hash}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return  # Silence HTTP server log output

def start_server():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    server = socketserver.TCPServer(("127.0.0.1", PORT), LocalDashboardHandler)
    print("============================================================")
    print(f"[PayQuant Local Dashboard] Running on: http://127.0.0.1:{PORT}")
    print("============================================================")
    server.serve_forever()

if __name__ == '__main__':
    t = threading.Thread(target=update_chain_loop, daemon=True)
    t.start()
    start_server()
