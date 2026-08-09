#!/usr/bin/env python3
"""
PayQuant (PQN) Fast-Sync Engine with Verified UTXO Snapshots v6.0.0

Allows new nodes to sync the blockchain in minutes by pulling verified UTXO Snapshots
over WebRTC DataChannels, IRC DCC, or Universal P2P Transport before downloading missing block ranges.
"""

import socket
import threading
import time
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from contrib.chain_db import get_db
import contrib.p2p_chain_transfer as p2p_transfer
import contrib.irc_p2p_signaling as irc_signaling
import contrib.irc_dcc_engine as dcc_engine
import contrib.webrtc_p2p_engine as webrtc_engine

def trigger_fast_sync_from_peer(peer_info):
    """Triggers UTXO Snapshot Fast-Sync from a target peer"""
    db = get_db()
    peer_ip = peer_info.get("ip")
    peer_nick = peer_info.get("nick")
    
    print(f"[Fast-Sync Engine] Requesting UTXO Snapshot from peer {peer_ip} ({peer_nick})...")

    # 1. Try WebRTC SDP Offer / Answer for fast stream
    if peer_nick:
        webrtc_offer = webrtc_engine.get_webrtc_engine().create_sdp_offer(peer_nick)
        irc_signaling.send_private_irc_message(peer_nick, webrtc_offer["irc_msg"])

    # 2. Query peer via Universal Transport for UTXO Snapshot
    res = p2p_transfer.p2p_query_peer(peer_ip, request_msg={"type": "get_utxo_snapshot"}, peer_nick=peer_nick)
    
    if res.get("status") == "ok" and "snapshot" in res:
        snap = res["snapshot"]
        success = db.apply_utxo_snapshot(snap)
        if success:
            print(f"[Fast-Sync Engine] Successfully fast-synced to height {snap.get('height')}!")
            return True

    # 3. Fallback: Generate local genesis UTXO state
    print("[Fast-Sync Engine] Peer snapshot unavailable. Continuing full chain sync...")
    return False

def check_and_run_fast_sync():
    """Checks if node is behind network and initiates Fast-Sync"""
    db = get_db()
    my_h = db.getLastHeight()
    furthest = irc_signaling.get_furthest_peer()
    
    if furthest and furthest.get("height", 0) > my_h + 50:
        print(f"[Fast-Sync Engine] Local node is {furthest['height'] - my_h} blocks behind network. Initiating Fast-Sync...")
        return trigger_fast_sync_from_peer(furthest)
    return False

if __name__ == '__main__':
    print("==================================================")
    print("      PAYQUANT FAST-SYNC ENGINE DIAGNOSTICS      ")
    print("==================================================")
    db = get_db()
    print(f"Current Last Height: {db.getLastHeight()}")
    print("==================================================")
