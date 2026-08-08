#!/usr/bin/env python3
"""
PayQuant (PQN) Decentralized IRC P2P Signaling Engine v2.1.2
Provides 100% Zero-Single-Point-of-Failure peer discovery across the internet.
Nodes connect to public IRC channels (#payquant-mainnet on Libera/OFTC),
signal their P2P IP/port, and discover all active online nodes worldwide.
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
CHANNEL = "#payquant-mainnet"
P2P_PORT = 28333

DATA_DIR = os.path.join(os.path.expanduser("~"), ".payquant")
if os.name == 'nt':
    DATA_DIR = os.path.join(os.environ.get('APPDATA', ''), 'PayQuantMainnetData')

DISCOVERED_PEERS = set()

def get_external_ip():
    try:
        req = urllib.request.Request("https://api.ipify.org?format=json", headers={'User-Agent': 'PayQuant-IRC-Node/2.1.2'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode('utf-8')).get("ip", "127.0.0.1")
    except Exception:
        return "127.0.0.1"

def add_peer_to_conf(ip, port=28333):
    if not ip or (ip.startswith("127.") and len(DISCOVERED_PEERS) > 0):
        return
    peer_str = f"addnode={ip}:{port}\n"
    if ip not in DISCOVERED_PEERS:
        DISCOVERED_PEERS.add(ip)
        os.makedirs(DATA_DIR, exist_ok=True)
        conf_path = os.path.join(DATA_DIR, "payquant.conf")
        existing = []
        if os.path.exists(conf_path):
            with open(conf_path, "r", encoding="utf-8") as f:
                existing = f.readlines()
        if peer_str not in existing:
            with open(conf_path, "a", encoding="utf-8") as f:
                f.write(peer_str)
            print(f"[IRC P2P Signaling] Discovered online node: {ip}:{port} -> Added to payquant.conf!")

def run_irc_signaling_loop():
    ext_ip = get_external_ip()
    ip_encoded = ext_ip.replace('.', '_')
    
    server_idx = 0
    while True:
        host, port = IRC_SERVERS[server_idx % len(IRC_SERVERS)]
        nick = f"pqn_{ip_encoded}_{int(time.time()) % 10000}"
        sock = None
        try:
            print(f"[IRC P2P Signaling] Connecting to public P2P signaling network ({host}:{port})...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(12)
            sock.connect((host, port))
            
            sock.sendall(f"NICK {nick}\r\n".encode('utf-8'))
            sock.sendall(f"USER {nick} 0 * :PayQuant Mainnet Node\r\n".encode('utf-8'))
            
            time.sleep(2)
            sock.sendall(f"JOIN {CHANNEL}\r\n".encode('utf-8'))
            sock.sendall(f"PRIVMSG {CHANNEL} :[PQN_SIGNAL] ip={ext_ip} port={P2P_PORT}\r\n".encode('utf-8'))
            print(f"[IRC P2P Signaling] Joined {CHANNEL} as {nick}! Signaling node presence: {ext_ip}:{P2P_PORT}")
            
            sock.settimeout(30)
            buf = ""
            last_signal_time = time.time()

            while True:
                # Periodic keep-alive signal every 60s
                if time.time() - last_signal_time > 60:
                    try:
                        sock.sendall(f"PRIVMSG {CHANNEL} :[PQN_SIGNAL] ip={ext_ip} port={P2P_PORT}\r\n".encode('utf-8'))
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
                                for item in sig.split():
                                    if item.startswith("ip="):
                                        node_ip = item.split("=")[1]
                                        add_peer_to_conf(node_ip)
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
    print("[IRC P2P Signaling v2.1.2] Active! Signaling node presence...")
    print("=================================================================")
    while True:
        time.sleep(1)
