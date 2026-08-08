#!/usr/bin/env python3
"""
PayQuant (PQN) Dynamic HTTP Seed & Peer Discovery Engine
Fetches active seeds from raw GitHub JSON repository and injects them
into payquant.conf for automatic P2P sync across nodes worldwide.
"""

import urllib.request
import json
import os
import sys

RAW_SEEDS_URL = "https://raw.githubusercontent.com/timfromhcs/payquant/main/seeds.json"
DATA_DIR = os.path.join(os.path.expanduser("~"), ".payquant")
if os.name == 'nt':
    DATA_DIR = os.path.join(os.environ.get('APPDATA', ''), 'PayQuantMainnetData')

def fetch_online_seeds():
    """Fetches active seeds from GitHub HTTP raw JSON endpoint"""
    print(f"[Seed Fetcher] Connecting to HTTP Seed Pool ({RAW_SEEDS_URL})...")
    try:
        req = urllib.request.Request(RAW_SEEDS_URL, headers={'User-Agent': 'PayQuant-Seed-Fetcher/2.0.2'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            seeds = data.get("seeds", [])
            print(f"[Seed Fetcher] Successfully fetched {len(seeds)} seed nodes from network pool!")
            return seeds
    except Exception as e:
        print(f"[Seed Fetcher Warning] HTTP fetch fallback: {str(e)}")
        return [
            {"host": "127.0.0.1", "port": 28333},
            {"host": "payquant-seed-node.fly.dev", "port": 28333},
            {"host": "payquant-mainnet-node.onrender.com", "port": 28333}
        ]

def inject_seeds_into_conf():
    """Appends addnode entries to payquant.conf"""
    seeds = fetch_online_seeds()
    os.makedirs(DATA_DIR, exist_ok=True)
    conf_path = os.path.join(DATA_DIR, "payquant.conf")
    
    existing_lines = []
    if os.path.exists(conf_path):
        with open(conf_path, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()
    
    addnodes = set()
    for s in seeds:
        host = s.get("host")
        port = s.get("port", 28333)
        if host:
            addnodes.add(f"addnode={host}:{port}\n")
    
    new_lines = [l for l in existing_lines if not l.startswith("addnode=")]
    for an in addnodes:
        new_lines.append(an)
    
    with open(conf_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print(f"[Seed Fetcher] Updated {conf_path} with {len(addnodes)} P2P peer nodes.")
    return list(addnodes)

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    inject_seeds_into_conf()
