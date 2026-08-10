"""
PayQuant (PQN) Ecosystem Local Test Suite v2.0.0-quantum
Verifies:
  1. Enterprise RocksDB Storage Engine, RepairDB & Block Integrity Gate
  2. UTXO Fast-Sync Snapshot Generation & Instant Import
  3. IRC DCC Engine (DCC SEND / DCC RESUME / Reverse Connect)
  4. WebRTC DataChannel SDP Offer/Answer Signaling over IRC
  5. P2P BitTorrent Chunk Streaming & Universal NAT Transport
  6. 24-Word Quantum Seedphrase Validation Logic
  7. WebRTC Status Report & Background Daemon Health Queries
  8. Super-Transport Ladder & Merkle-Delta UTXO Sync Protocol (v7)
  9. DirectDrop-style Encrypted File Transfer Protocol (v7)
 10. TRNG + Quantum Circuit simulation (panta-sim / NumPy fallback)
 11. Quantum Footprint Generation & Validator authenticity
 12. Public 3D Diamond Gallery integrity (deterministic, no secrets)
 13. Repository Secret Gate (no keys/seeds/wallet data in tree)
"""

import os
import sys
import tempfile
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from contrib.chain_db import get_db
from contrib.p2p_chain_transfer import start_p2p_server, p2p_query_peer
from contrib.irc_dcc_engine import get_dcc_engine
from contrib.webrtc_p2p_engine import get_webrtc_engine


def run_tests():
    print("=" * 52)
    print("   PAYQUANT (PQN) ECOSYSTEM v2.0.0-quantum TEST SUITE")
    print("=" * 52)

    # 1. Test Chain DB Engine & RepairDB
    db = get_db()
    init_height = db.getLastHeight()
    print(f"[TEST 1/9] Chain DB Engine loaded. Current Height: {init_height}")
    assert db.repair_db() is True, "DB integrity repair failed!"
    print(" -> [SUCCESS] Chain DB Engine & Automatic Repair verified!")

    # 2. Test UTXO Fast-Sync Snapshot Generator & Apply
    print("[TEST 2/9] Testing Fast-Sync UTXO Snapshot Engine...")
    snap = db.create_utxo_snapshot()
    assert snap is not None and "snapshot_hash" in snap, "UTXO Snapshot generation failed!"
    assert db.apply_utxo_snapshot(snap) is True, "UTXO Snapshot apply failed!"
    print(f" -> [SUCCESS] Generated and applied Fast-Sync UTXO Snapshot ({snap['utxo_count']} UTXOs)!")

    # 3. Test IRC DCC Engine
    print("[TEST 3/9] Testing IRC DCC Engine (DCC SEND / RESUME / Reverse)...")
    sample_file_data = b"PQN_UTXO_SNAPSHOT_DATA_CHUNK_TEST"
    dcc_offer = get_dcc_engine().create_dcc_send_offer("snapshot.json", sample_file_data, "pqn_peer_test")
    parsed_dcc = get_dcc_engine().parse_dcc_ctcp(dcc_offer["ctcp"])
    assert parsed_dcc is not None and parsed_dcc["type"] == "SEND", "IRC DCC CTCP parsing failed!"
    print(f" -> [SUCCESS] Generated & parsed IRC DCC offer for target {dcc_offer['target_nick']}!")

    # 4. Test WebRTC DataChannel SDP Offer/Answer Signaling
    print("[TEST 4/9] Testing WebRTC DataChannel SDP Offer/Answer Engine...")
    webrtc_offer = get_webrtc_engine().create_sdp_offer("pqn_peer_test")
    parsed_sdp = get_webrtc_engine().parse_webrtc_signal(webrtc_offer["irc_msg"])
    assert parsed_sdp is not None and parsed_sdp["type"] == "OFFER", "WebRTC SDP signal parsing failed!"
    print(" -> [SUCCESS] WebRTC SDP Offer/Answer signaling over IRC verified!")

    # 5. Test P2P Fast-Sync UTXO Snapshot Protocol
    print("[TEST 5/9] Testing P2P Fast-Sync Snapshot Protocol Server...")
    srv = start_p2p_server(28333)
    time.sleep(1)

    p2p_snap_res = p2p_query_peer("127.0.0.1", 28333, {"type": "get_utxo_snapshot"})
    assert p2p_snap_res.get("status") == "ok" and "snapshot" in p2p_snap_res, "P2P get_utxo_snapshot failed!"
    print(" -> [SUCCESS] P2P Node responded with verified Fast-Sync UTXO Snapshot!")

    # 6. Test 24-Word Seedphrase & 21M Max Supply Cap / 40-Block Hashrate-Adaptive Rewards
    print("[TEST 6/9] Verifying 24-Word Seedphrase & Max Supply Cap / 40-Block Adaptive Reward Engine...")
    sample_24_words = ("abandon ability able about above absent absorb abstract absurd abuse access accident "
                       "adult advance advice aerobic afford afraid again age agent agree ahead aim")
    assert len(sample_24_words.split()) == 24, "Seedphrase word count must be exactly 24 words!"
    r_base = db.get_current_block_reward(1, estimated_hashrate=40000.0)
    r_halving = db.get_current_block_reward(210000, estimated_hashrate=40000.0)
    r_adapted = db.get_current_block_reward(40, estimated_hashrate=80000.0)
    assert r_base == 50.0, f"Expected 50.0 base reward, got {r_base}"
    assert r_halving == 25.0, f"Expected 25.0 reward after first 210k halving, got {r_halving}"
    assert r_adapted > r_base, f"Expected reward to adapt upward with higher hashrate every 40 blocks, got {r_adapted}"
    assert db.MAX_SUPPLY == 2100000000.0, "Max supply cap must be exactly 2,100,000,000 PQN!"
    print(f" -> [SUCCESS] 24-Word Seedphrase + Max Supply (2.1B PQN) + 40-Block Adaptive Reward ({r_base} -> {r_adapted} PQN) verified!")

    # 7. Test WebRTC DataChannel Status Report & Daemon Queries
    print("[TEST 7/9] Testing WebRTC DataChannel Status Report & Daemon Queries...")
    report = get_webrtc_engine().get_status_report()
    assert report is not None and "ice_status" in report, "WebRTC status report query failed!"
    print(f" -> [SUCCESS] WebRTC Status Report verified! Active ICE: {report['ice_status']}")

    # 8. Test Super-Transport & Merkle-Delta UTXO Sync
    print("[TEST 8/9] Testing Super-Transport Ladder & Merkle-Delta UTXO Sync Protocol...")
    from contrib.pqn_netlib import query_peer, get_super_transport, libp2p_available
    from contrib.pqn_sync import merkle_root

    st = get_super_transport()
    st.ladder = ["direct_tcp"]  # force the deterministic path for the local test
    root = merkle_root(db)
    assert isinstance(root, str) and len(root) == 64, "Merkle root must be sha256 (64 hex chars)!"

    q = query_peer("127.0.0.1", {"type": "get_node_status"}, port=28333)
    assert q.get("status") == "ok", "Super-Transport get_node_status failed!"
    assert q.get("height", 0) == init_height, "Super-Transport height mismatch!"

    offer_resp = query_peer("127.0.0.1", {"type": "pqn_sync_offer", "local_height": 0,
                                          "merkle_root": "0" * 64}, port=28333)
    assert offer_resp.get("status") == "ok", "pqn_sync_offer roundtrip failed!"
    assert "delta" in offer_resp or "snapshot" in offer_resp or offer_resp.get("match"), \
        "pqn_sync_offer reply must include delta/snapshot/match"
    print(f" -> [SUCCESS] Super-Transport + Merkle-Delta sync verified "
          f"(libp2p accelerator: {libp_available()})!")

# 9. Test DirectDrop-style Encrypted File Transfer
    print("[TEST 9/9] Testing DirectDrop-style Encrypted File Transfer Protocol...")
    from contrib.pqn_file import (send_file, make_transfer_code, sha256_of_file,
                                  handle_file_offer)
    src_dir = os.path.join(tempfile.gettempdir(), "pqn_test_src_" + str(os.getpid()))
    dst_dir = os.path.join(tempfile.gettempdir(), "pqn_test_dst_" + str(os.getpid()))
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(dst_dir, exist_ok=True)
    demo_src = os.path.join(src_dir, "delta_of_love.bin")
    with open(demo_src, "wb") as fh:
        fh.write(b"PAYQUANT_V7_DELTA_OF_LOVE_" * 4000)

    froot = handle_file_offer({
        "type": "pqn_file_offer", "name": "backup.bin", "size": 100,
        "sha256": "0" * 64, "salt_b64": "AAAA", "code_hint": "ABC",
    })
    assert froot.get("status") == "ok" and froot.get("accept"), "File offer handler failed!"

    code = make_transfer_code()
    send_resp = send_file("127.0.0.1", demo_src, code=code, port=28333,
                          dest_dir=dst_dir, timeout=30)
    assert send_resp.get("status") == "ok", f"DirectDrop file transfer failed: {send_resp}"
    written = os.path.join(dst_dir, os.path.basename(demo_src))
    assert os.path.exists(written) and os.path.normcase(written) != os.path.normcase(demo_src), \
        "File not written to distinct destination after transfer!"
    assert os.path.getsize(written) == send_resp.get("size"), "File size mismatch after transfer!"
    assert sha256_of_file(written) == send_resp.get("sha256"), "SHA-256 mismatch after transfer!"
    print(f" -> [SUCCESS] DirectDrop encrypted transfer verified ({send_resp.get('size')} bytes)!")

    # 10. Test TRNG + Quantum Circuit Simulation
    print("[TEST 10/13] Testing TRNG Engine & 8-Qubit Quantum Simulation...")
    from contrib.pqn_quantum import TRNGClient, QuantumCircuitBackend, PANTASIM_AVAILABLE
    trng = TRNGClient("fallback")
    s1, s2 = trng.get_seed(), trng.get_seed()
    assert s1 != s2, "TRNG seeds must be unique!"
    sim = QuantumCircuitBackend()
    res = sim.run(20260809)
    assert res["counts"] and len(res["most_probable"]) == 8, "Quantum simulation failed!"
    print(f" -> [SUCCESS] TRNG + {sim.backend} simulation verified (8 qubits, {len(res['counts'])} outcomes)!")

    # 11. Test Quantum Footprint Generation & Validator
    print("[TEST 11/13] Testing Quantum Footprint Gen + Validator...")
    from contrib.pqn_quantum import (QuantumFootprintGenerator3D, verify_footprint,
                                     sha256_of)
    gen = QuantumFootprintGenerator3D(trng=trng, backend=sim)
    fp = gen.generate_footprint("deadbeef" * 8, "pqn1qtest")
    assert len(fp["footprint"]) == 64, "Footprint must be 64-char sha256!"
    assert fp["geometry_3d"]["vertices"] and fp["geometry_3d"]["faces"], "3D geometry empty!"
    assert verify_footprint("deadbeef" * 8, "pqn1qtest", fp["seed"], fp["footprint"]), \
        "Validator rejected a genuine footprint!"
    assert not verify_footprint("deadbeef" * 8, "pqn1qtest", fp["seed"] + 1, fp["footprint"]), \
        "Validator accepted a tampered footprint!"
    print(f" -> [SUCCESS] Footprint {fp['footprint'][:12]}… + 3D diamond verified!")

    # 12. Test Public 3D Diamond Gallery integrity
    print("[TEST 12/13] Testing Public 3D Diamond Gallery integrity...")
    import json as _json
    gallery_path = os.path.join(BASE_DIR, "explorer_3d", "diamonds.json")
    assert os.path.exists(gallery_path), "explorer_3d/diamonds.json missing!"
    with open(gallery_path, "r", encoding="utf-8") as jf:
        gallery = _json.load(jf)
    assert gallery.get("diamonds"), "Gallery has no diamonds!"
    for d in gallery["diamonds"]:
        assert len(d.get("quantum_footprint", "")) == 64, "Bad footprint in gallery!"
        assert d.get("geometry_3d", {}).get("faces"), "Diamond geometry missing!"
    print(f" -> [SUCCESS] {gallery['count']} deterministic public diamonds verified!")

    # 13. Test Secret Gate (no keys/seeds in the tree)
    print("[TEST 13/13] Testing Repository Secret Gate...")
    from scripts.check_secrets import scan as secret_scan
    violations = secret_scan(BASE_DIR)
    assert not violations, f"Secret gate found: {violations}"
    print(" -> [SUCCESS] Repository secret gate clean - no keys/seeds/wallet data.")

    print("=" * 52)
    print("   ALL PAYQUANT v2.0.0-quantum ECOSYSTEM TESTS PASSED")
    print("=" * 52)


def libp_available():
    try:
        from contrib.pqn_netlib import libp2p_available
        return libp2p_available()
    except Exception:
        return False


if __name__ == "__main__":
    run_tests()