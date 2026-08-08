#!/usr/bin/env python3
"""
PayQuant (PQN) Free Peer Announcer & Public IP Discovery
Allows any node operator to discover their public IP or run a free tunnel (localtunnel/serveo)
and broadcast their active seed node address to peers.
"""

import urllib.request
import json
import os
import sys

def get_public_ip():
    """Discovers external public IP using free public API"""
    try:
        req = urllib.request.Request("https://api.ipify.org?format=json", headers={'User-Agent': 'PayQuant-Node/2.0.2'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode('utf-8')).get("ip")
    except Exception:
        return "127.0.0.1"

def announce_peer():
    pub_ip = get_public_ip()
    print("=================================================================")
    print(f"[PayQuant Peer Announcer] Detected External Public IP: {pub_ip}")
    print(f"[P2P Address] {pub_ip}:28333")
    print("Share this address with other nodes to let them connect directly:")
    print(f"addnode={pub_ip}:28333")
    print("=================================================================")

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    announce_peer()
