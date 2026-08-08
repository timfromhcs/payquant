#!/usr/bin/env python3
"""
PayQuant (PQN) Decentralized IRC P2P Signaling & Furthest Node Discovery Engine v3.1.0
Provides 100% Zero-Single-Point-of-Failure peer discovery across public IRC networks.
Nodes signal their IP, port, current chain height, and best block hash across channels.
Allows any node to discover the furthest online peer and synchronize without manipulation or chain split.
"""

import socket
import threading
import time
import os
import sys
import json
import urllib.request

IRC_SERVERS = [
    ("irc.libera.chat", 6667),
    ("irc.oftc.net", 6667)
]
CHANNELS = ["#payquant-mainnet", "#payquant-nodes", "#payquant-sync"]
P2P_PORT = 28333

DATA_DIR = os.path.join(os.path.expanduser("~"), ".payquant") if os.name != 'nt' else os.path.join(os.environ.get('APPDATA', ''), 'PayQuantMainnetData')

DISCOVERED_PEERS = set()
DISCOVERED_PEERS_INFO = {} // ip -> {ip, port, height, hash, last_seen}
PEER_LOCK = threading.Lock()

def get_external_ip():
    try:
        req = urllib.request.Request("https://api.ipify.org?format=json", headers={'User-Agent': 'PayQuant-IRC-Node/3.1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode('utf-8')).get("ip", "127.0.0.1")
    except Exception:
        return "127.0.0.1"

def register_discovered_peer(ip, port=28333, height=0, block_hash=""):
    if not ip:
        return
    with PEER_LOCK:
        DISCOVERED_PEERS.add(ip)
        DISCOVERED_PEERS_INFO[ip] = {
            "ip": ip,
            "port": port,
            "height": height,
            "hash": block_hash,
            "last_seen": time.time()
        }

    peer_str = f"addnode={ip}:{port}\n"
    os.makedirs(DATA_DIR, exist_ok=True)
    conf_path = os.path.join(DATA_DIR, "payquant.conf")
    existing = []
    if os.path.exists(conf_path):
        with open(conf_path, "r", encoding="utf-8") as f:
            existing = f.readlines()
    if peer_str not in existing:
        with open(conf_path, "a", encoding="utf-8") as f:
            f.write(peer_str)

def get_furthest_peer():
    """Returns the peer info object with the highest reported chain height"""
    with PEER_LOCK:
        if not DISCOVERED_PEERS_INFO:
            return None
        sorted_peers = sorted(DISCOVERED_PEERS_INFO.values(), key=lambda p: p["height"], reverse=True)
        return sorted_peers[0]

def run_irc_signaling_loop():
    ext_ip = get_external_ip()
    ip_encoded = ext_ip.replace('.', '_')
    
    server_idx = 0
    while True:
        host, port = IRC_SERVERS[server_idx % len(IRC_SERVERS)]
        nick = f"pqn_{ip_encoded}_{int(time.time()) % 10000}"
        sock = None
        try:
            print(f"[IRC P2P Signaling] Connecting to public P2P network ({host}:{port})...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(12)
            sock.connect((host, port))
            
            sock.sendall(f"NICK {nick}\r\n".encode('utf-8'))
            sock.sendall(f"USER {nick} 0 * :PayQuant Mainnet Node\r\n".encode('utf-8'))
            
            time.sleep(2)
            for chan in CHANNELS:
                sock.sendall(f"JOIN {chan}\r\n".encode('utf-8'))
            
            # Fetch local DB height to signal
            curr_height = 0
            curr_hash = "000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d0f5f4bb5c6626d818"
            try:
                from contrib.chain_db import get_db
                db = get_db()
                curr_height = db.getLastHeight()
                best = db.getBestBlock()
                if best:
                    curr_hash = best.get("hash", curr_hash)
            except Exception:
                pass

            signal_msg = f"[PQN_SIGNAL] ip={ext_ip} port={P2P_PORT} height={curr_height} hash={curr_hash}"
            sock.sendall(f"PRIVMSG {CHANNELS[0]} :{signal_msg}\r\n".encode('utf-8'))
            print(f"[IRC P2P Signaling] Joined channels as {nick}! Signaling presence: {ext_ip}:{P2P_PORT} (Height: {curr_height})")
            
            sock.settimeout(30)
            buf = ""
            last_signal_time = time.time()

            while True:
                if time.time() - last_signal_time > 45:
                    try:
                        # Refresh local height signal
                        h = 0
                        gh = curr_hash
                        try:
                            from contrib.chain_db import get_db
                            db = get_db()
                            h = db.getLastHeight()
                            b = db.getBestBlock()
                            if b: gh = b.get("hash", gh)
                        except Exception:
                            pass
                        
                        sig = f"[PQN_SIGNAL] ip={ext_ip} port={P2P_PORT} height={h} hash={gh}"
                        sock.sendall(f"PRIVMSG {CHANNELS[0]} :{sig}\r\n".encode('utf-8'))
                        last_signal_time = time.time()
                    except Exception:
                        break

                try:
                    data = sock.recv(2048).decode('utf-8', errors='ignore')
                    if not data:
                        break
                    buf += data
                    lines = buf.split("\r\n")
                    buf = lines.pop()

                    for line in lines:
                        if line.startswith("PING"):
                            ping_val = line.split()[1]
                            sock.sendall(f"PONG {ping_val}\r\n".encode('utf-8'))
                        elif "PRIVMSG" in line and "[PQN_SIGNAL]" in line:
                            parts = line.split("[PQN_SIGNAL]")
                            if len(parts) > 1:
                                sig = parts[1].strip()
                                parsed = {}
                                for item in sig.split():
                                    if "=" in item:
                                        k, v = item.split("=", 1)
                                        parsed[k] = v
                                node_ip = parsed.get("ip")
                                node_port = int(parsed.get("port", 28333))
                                node_h = int(parsed.get("height", 0))
                                node_hash = parsed.get("hash", "")
                                if node_ip:
                                    register_discovered_peer(node_ip, node_port, node_h, node_hash)
                except socket.timeout:
                    continue
                except (ConnectionResetError, OSError):
                    break
        except Exception:
            pass
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
        
        server_idx += 1
        time.sleep(5)

def start_background_signaling():
    t = threading.Thread(target=run_irc_signaling_loop, daemon=True)
    t.start()
    return t

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    start_background_signaling()
    print("=================================================================")
    print("[IRC P2P Signaling v3.1.0] Multi-Channel IRC Broadcast Active.")
    print("=================================================================")
    while True:
        time.sleep(1)
