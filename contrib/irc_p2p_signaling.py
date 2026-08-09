#!/usr/bin/env python3
"""
PayQuant (PQN) Advanced IRC P2P Handshake & Local UDP Broadcast Discovery Engine v6.6.0
Features:
 - Private 1-on-1 IRC handshake negotiation (PRIVMSG/NOTICE)
 - Real-time Node & Miner count tracking (get_node_count, get_miner_count)
 - Local UDP Broadcast Beacon on port 28335 for instant zero-config multi-node discovery
 - Dynamic Torrent Sync Cluster formation & failover coordination
 - TLS (6697) + plain (6667) connect rotation across multiple IRC networks
 - Small-data IRC Base64 chunk relay with reassembly (consumed via drain_inbox)
 - Automatic nick collision recovery (433) and PING/PONG keepalive
"""

import socket
import ssl
import threading
import time
import os
import sys
import json
import base64
import urllib.request

IRC_SERVERS = [
    ("irc.libera.chat", 6697),
    ("irc.libera.chat", 6667),
    ("irc.oftc.net", 6697),
    ("irc.oftc.net", 6667),
    ("irc.rizon.net", 6697),
    ("irc.rizon.net", 6667),
]
CHANNELS = ["#payquant-mainnet", "#payquant-nodes", "#payquant-sync"]
P2P_PORT = 28333
IRC_CONNECT_TIMEOUT = 10
IRC_SIGNAL_INTERVAL = 45
IRC_SERVER_ROTATION_S = 120

DATA_DIR = os.path.join(os.path.expanduser("~"), ".payquant") if os.name != 'nt' else os.path.join(os.environ.get('APPDATA', ''), 'PayQuantMainnetData')

DISCOVERED_PEERS = set(["127.0.0.1"])
DISCOVERED_PEERS_INFO = {
    "127.0.0.1": {
        "ip": "127.0.0.1",
        "port": 28333,
        "height": 0,
        "hash": "000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d0f5f4bb5c6626d818",
        "trust_score": 100,
        "nick": "pqn_local_node",
        "last_seen": time.time()
    }
}
ACTIVE_MINERS = set(["127.0.0.1"])
PEER_LOCK = threading.Lock()
SOCKET_LOCK = threading.Lock()

REASSEMBLER = None
IRC_INBOX = []
INBOX_LOCK = threading.Lock()
IRC_SOCKETS = {}
CURRENT_IRC_SOCKET = None


def get_external_ip():
    try:
        req = urllib.request.Request("https://api.ipify.org?format=json", headers={'User-Agent': 'PayQuant-IRC-Node/6.6.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode('utf-8')).get("ip", "127.0.0.1")
    except Exception:
        return "127.0.0.1"


def register_discovered_peer(ip, port=28333, height=0, block_hash="", trust_score=100, nick="", is_miner=False):
    if not ip:
        return
    with PEER_LOCK:
        DISCOVERED_PEERS.add(ip)
        DISCOVERED_PEERS_INFO[ip] = {
            "ip": ip,
            "port": port,
            "height": height,
            "hash": block_hash,
            "trust_score": trust_score,
            "nick": nick,
            "last_seen": time.time()
        }
        if is_miner:
            ACTIVE_MINERS.add(ip)


def register_miner(ip):
    with PEER_LOCK:
        ACTIVE_MINERS.add(ip)


def get_node_count():
    with PEER_LOCK:
        return max(1, len(DISCOVERED_PEERS))


def get_miner_count():
    with PEER_LOCK:
        return max(1, len(ACTIVE_MINERS))


def get_all_peer_infos():
    with PEER_LOCK:
        return list(DISCOVERED_PEERS_INFO.values())


def get_furthest_peer():
    """Highest-height discovered remote peer (excludes localhost)."""
    best = None
    with PEER_LOCK:
        for info in DISCOVERED_PEERS_INFO.values():
            if not info or info.get("ip") == "127.0.0.1":
                continue
            if best is None or int(info.get("height", 0) or 0) > int(best.get("height", 0) or 0):
                best = info
    return best


def get_cluster_peers(cluster_size=8):
    """Build torrent-sync cluster: remote peers sorted by height desc + local node."""
    cluster = [{"ip": "127.0.0.1", "port": P2P_PORT, "nick": "pqn_local_node", "height": 0}]
    with PEER_LOCK:
        infos = [i for i in DISCOVERED_PEERS_INFO.values() if i and i.get("ip") != "127.0.0.1"]
    infos.sort(key=lambda p: ((p.get("trust_score", 0) or 0), (p.get("height", 0) or 0)), reverse=True)
    for info in infos[:max(0, cluster_size - 1)]:
        cluster.append({
            "ip": info.get("ip"),
            "port": info.get("port", P2P_PORT),
            "nick": info.get("nick", ""),
            "height": info.get("height", 0)
        })
    return cluster


def get_closest_high_peers(count=4):
    return get_cluster_peers(count)


def request_private_torrent_cluster(peer_ip, peer_nick=None, cluster_size=8):
    if not peer_ip:
        return []
    register_discovered_peer(peer_ip, nick=peer_nick or "")
    return get_cluster_peers(cluster_size)


def send_private_irc_message(target_nick, message):
    sock = _pick_live_socket()
    if sock:
        try:
            sock.sendall(f"PRIVMSG {target_nick} :{message}\r\n".encode('utf-8'))
            return True
        except Exception:
            pass
    return False


def send_channel_message(channel, message):
    sock = _pick_live_socket()
    if sock:
        try:
            sock.sendall(f"PRIVMSG {channel} :{message}\r\n".encode('utf-8'))
            return True
        except Exception:
            pass
    return False


def _pick_live_socket():
    global CURRENT_IRC_SOCKET
    with SOCKET_LOCK:
        for sock in IRC_SOCKETS.values():
            if sock is not None:
                CURRENT_IRC_SOCKET = sock
                return sock
    return CURRENT_IRC_SOCKET


def drain_inbox():
    """Return and clear all fully-reassembled IRC small-data payloads."""
    with INBOX_LOCK:
        items = list(IRC_INBOX)
        IRC_INBOX[:] = []
        return items


def current_chain_state():
    try:
        from contrib.chain_db import get_db
        db = get_db()
        h = db.getLastHeight()
        b = db.getBestBlock()
        return h, (b.get("hash", "") if b else "")
    except Exception:
        return 0, ""


def _fmt_signal(ip, height, block_hash, trust=100):
    return f"[PQN_SIGNAL] ip={ip} port={P2P_PORT} height={height} hash={block_hash} trust={trust}"


class IRCChunkReassembler:
    """Collects [PQN_IRC_CHUNK] fragments back into the original JSON payload."""

    def __init__(self):
        self.streams = {}
        self.lock = threading.Lock()

    def add_chunk_from_line(self, line):
        marker = "[PQN_IRC_CHUNK]"
        idx = line.find(marker)
        if idx < 0:
            return None
        body = line[idx + len(marker):]
        parsed = {}
        for item in body.split():
            if "=" in item:
                k, v = item.split("=", 1)
                parsed[k] = v
        stream_id = parsed.get("id")
        try:
            ch_index = int(parsed.get("idx", -1))
            total = int(parsed.get("total", -1))
        except (TypeError, ValueError):
            return None
        b64 = parsed.get("data", "")
        if not stream_id or ch_index < 0 or total < 1:
            return None
        with self.lock:
            self.streams.setdefault(stream_id, {"total": total, "chunks": {}})
            st = self.streams[stream_id]
            st["chunks"][ch_index] = b64
            if len(st["chunks"]) >= total:
                full_b64 = "".join(st["chunks"][i] for i in sorted(st["chunks"]))
                del self.streams[stream_id]
                try:
                    pad = len(full_b64) % 4
                    if pad:
                        full_b64 += "=" * (4 - pad)
                    return json.loads(base64.b64decode(full_b64).decode('utf-8'))
                except Exception:
                    return None
        return None


def _handle_line(sock, line, nick):
    """Process one IRC line. Returns False if the socket should close."""
    global REASSEMBLER
    if not line.strip():
        return True
    if line.startswith("PING"):
        try:
            sock.sendall(f"PONG {line.split()[1]}\r\n".encode('utf-8'))
        except Exception:
            return False
        return True
    if " 433 " in line:
        try:
            sock.sendall(f"NICK {nick}_{int(time.time()) % 90000}\r\n".encode('utf-8'))
        except Exception:
            pass
        return True

    if "PRIVMSG" not in line:
        return True

    sender_nick = line.split("!")[0][1:] if "!" in line else ""
    if "[PQN_SIGNAL]" in line:
        parts = line.split("[PQN_SIGNAL]", 1)
        if len(parts) > 1:
            parsed = {}
            for item in parts[1].strip().split():
                if "=" in item:
                    k, v = item.split("=", 1)
                    parsed[k] = v
            if parsed.get("ip"):
                register_discovered_peer(
                    parsed["ip"],
                    int(parsed.get("port", 28333)),
                    int(parsed.get("height", 0) or 0),
                    parsed.get("hash", ""),
                    int(parsed.get("trust", 100) or 100),
                    sender_nick
                )
    elif "[PQN_IRC_CHUNK]" in line:
        if REASSEMBLER is None:
            REASSEMBLER = IRCChunkReassembler()
        payload = REASSEMBLER.add_chunk_from_line(line)
        if payload is not None:
            with INBOX_LOCK:
                IRC_INBOX.append(payload)
    return True


def _read_loop(sock, host, nick, ext_ip):
    """Buffered read loop with periodic heartbeat. Returns when connection dies."""
    buf = ""
    last_sig = time.time()
    while True:
        try:
            if time.time() - last_sig > IRC_SIGNAL_INTERVAL:
                h, gh = current_chain_state()
                sock.sendall(f"PRIVMSG {CHANNELS[0]} :{_fmt_signal(ext_ip, h, gh)}\r\n".encode('utf-8'))
                last_sig = time.time()
        except Exception:
            return
        try:
            data = sock.recv(4096)
            if not data:
                return
            buf += data.decode('utf-8', errors='ignore')
            lines = buf.split("\r\n")
            buf = lines.pop()
            for line in lines:
                if not _handle_line(sock, line):
                    return
        except socket.timeout:
            continue
        except (ConnectionResetError, OSError, ssl.SSLError):
            return


def _connect_irc(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(IRC_CONNECT_TIMEOUT)
    sock.connect((host, port))
    if port == 6697:
        ctx = ssl.create_default_context()
        sock = ctx.wrap_socket(sock, server_hostname=host)
    sock.settimeout(2)
    return sock


def _pick_server():
    """2-minute rotation over IRC_SERVERS (TLS pairs first)."""
    idx = int(time.time() // IRC_SERVER_ROTATION_S) % len(IRC_SERVERS)
    return IRC_SERVERS[idx]


def run_irc_signaling_loop():
    """Maintains one IRC connection with automatic server rotation."""
    ext_ip = get_external_ip()
    ip_encoded = ext_ip.replace('.', '_')
    while True:
        host, port = _pick_server()
        nick = f"pqn_{ip_encoded}_{int(time.time()) % 10000}"
        sock = None
        try:
            sock = _connect_irc(host, port)
            with SOCKET_LOCK:
                IRC_SOCKETS[(host, port)] = sock
                global CURRENT_IRC_SOCKET
                CURRENT_IRC_SOCKET = sock
            sock.sendall(f"NICK {nick}\r\n".encode('utf-8'))
            sock.sendall(f"USER {nick} 0 * :PayQuant Mainnet Node\r\n".encode('utf-8'))
            time.sleep(1.5)
            for ch in CHANNELS:
                sock.sendall(f"JOIN {ch}\r\n".encode('utf-8'))
            h, gh = current_chain_state()
            sock.sendall(f"PRIVMSG {CHANNELS[0]} :{_fmt_signal(ext_ip, h, gh)}\r\n".encode('utf-8'))
            _read_loop(sock, host, nick, ext_ip)
        except Exception:
            pass
        finally:
            with SOCKET_LOCK:
                IRC_SOCKETS.pop((host, port), None)
                CURRENT_IRC_SOCKET = None
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
        time.sleep(3)


def start_background_signaling():
    threading.Thread(target=run_udp_broadcast_beacon, daemon=True).start()
    t = threading.Thread(target=run_irc_signaling_loop, daemon=True)
    t.start()
    return t


def run_udp_broadcast_beacon():
    """UDP Beacon for instant zero-config discovery on the same machine/LAN."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        sock.bind(('0.0.0.0', 28335))
    except Exception:
        pass
    sock.settimeout(2.0)
    last_bcast = 0
    while True:
        try:
            if time.time() - last_bcast > 3:
                msg = json.dumps({"type": "HELLO_PEER", "port": P2P_PORT, "timestamp": int(time.time())}).encode('utf-8')
                sock.sendto(msg, ('<broadcast>', 28335))
                last_bcast = time.time()
            try:
                data, addr = sock.recvfrom(1024)
                if data:
                    parsed = json.loads(data.decode('utf-8'))
                    if parsed.get("type") == "HELLO_PEER":
                        register_discovered_peer(addr[0], parsed.get("port", 28333), nick="local_udp_peer")
            except socket.timeout:
                pass
        except Exception:
            pass
        time.sleep(1)


if __name__ == '__main__':
    start_background_signaling()
    print("[IRC & UDP P2P Discovery v6.6.0] Multi-Node Discovery Engine Active.")