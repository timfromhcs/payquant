#!/usr/bin/env python3
"""
PayQuant (PQN) Fast-Sync Engine with Verified UTXO Snapshots v7.0.0

Allows new nodes to sync the blockchain in minutes by pulling verified UTXO Snapshots
over WebRTC DataChannels, IRC DCC, or Universal P2P Transport before downloading missing block ranges.

v7 upgrade: reconciliation now attempts the Merkle-Delta protocol (contrib.pqn_sync)
over the Super-Transport ladder first (O(1) fingerprint compare, delta-only transfer),
falling back to the v6 verified UTXO snapshot blob when the peer is legacy or far behind.
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
import contrib.pqn_sync as pqn_sync

def trigger_fast_sync_from_peer(peer_info):
    """Triggers UTXO Snapshot Fast-Sync from a target peer.

    v7: prefers Merkle-Delta sync over the Super-Transport, then falls back to
    the v6 verified snapshot protocol.
    """
    db = get_db()
    peer_ip = peer_info.get("ip")
    peer_port = peer_info.get("port", 28333)
    peer_nick = peer_info.get("nick")

    print(f"[Fast-Sync Engine] Reconciliating UTXO state with peer {peer_ip} ({peer_nick})...")

    # 1. Preferred: Merkle-Delta sync over the Super-Transport ladder
    try:
        report = pqn_sync.sync_utxos_from_peer(
            peer_ip, port=peer_port, peer_nick=peer_nick, db=db
        )
        if report.get("status") == "ok":
            mode = report.get("mode", "synced")
            if mode != "synced":
                print(f"[Fast-Sync Engine] Merkle-Delta sync succeeded "
                      f"(mode={mode}, applied={report.get('delta_applied', 'n/a')}).")
            else:
                print("[Fast-Sync Engine] Already in sync with peer (Merkle root match).")
            return True
    except Exception as e:
        print(f"[Fast-Sync Engine] Merkle-Delta path unavailable ({e}); falling back...")

    # 2. Legacy fallback: WebRTC SDP Offer / Answer for fast stream
    if peer_nick:
        try:
            webrtc_offer = webrtc_engine.get_webrtc_engine().create_sdp_offer(peer_nick)
            irc_signaling.send_private_irc_message(peer_nick, webrtc_offer["irc_msg"])
        except Exception:
            pass

    # 3. Legacy fallback: full UTXO snapshot over universal transport
    res = p2p_transfer.p2p_query_peer(peer_ip, request_msg={"type": "get_utxo_snapshot"}, peer_nick=peer_nick)
    
    if res.get("status") == "ok" and "snapshot" in res:
        snap = res["snapshot"]
        success = db.apply_utxo_snapshot(snap)
        if success:
            print(f"[Fast-Sync Engine] Successfully fast-synced to height {snap.get('height')}!")
            return True

    # 4. Fallback: Generate local genesis UTXO state
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
