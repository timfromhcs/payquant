#!/usr/bin/env python3
"""
PayQuant (PQN) WebRTC DataChannel & ICE Signaling Engine v6.0.0

Provides high-speed DataChannel P2P streaming for blocks and UTXO snapshots over WebRTC ICE framework.
Uses IRC as the signaling channel for SDP Offer/Answer and ICE candidate exchange.
"""

import socket
import threading
import time
import os
import sys
import json
import base64

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

class PayQuantWebRTCEngine:
    def __init__(self):
        self.active_sessions = {}
        self.lock = threading.Lock()

    def create_sdp_offer(self, peer_nick):
        """Generates a WebRTC SDP Offer object for IRC signaling"""
        from contrib.nat_p2p_transport import query_stun_server, get_external_ip
        stun_res = query_stun_server()
        ip_addr = stun_res["ip"] if stun_res else get_external_ip()
        udp_port = stun_res["port"] if stun_res else 28333

        session_id = f"sdp_{int(time.time()*1000)}"
        sdp_offer = {
            "version": "v6.0.0",
            "type": "offer",
            "session_id": session_id,
            "ice_candidate": {
                "ip": ip_addr,
                "port": udp_port,
                "protocol": "udp",
                "type": "srflx",
                "stun_server": "stun.l.google.com:19302"
            },
            "datachannel": "payquant_utxo_stream"
        }
        
        with self.lock:
            self.active_sessions[session_id] = sdp_offer

        b64_sdp = base64.b64encode(json.dumps(sdp_offer).encode('utf-8')).decode('utf-8')
        irc_msg = f"[PQN_WEBRTC_OFFER] sid={session_id} sdp={b64_sdp}"
        return {"session_id": session_id, "irc_msg": irc_msg, "target_nick": peer_nick}

    def create_sdp_answer(self, session_id, offer_sdp, peer_nick):
        """Generates a WebRTC SDP Answer responding to an Offer"""
        from contrib.nat_p2p_transport import query_stun_server, get_external_ip
        stun_res = query_stun_server()
        ip_addr = stun_res["ip"] if stun_res else get_external_ip()
        udp_port = stun_res["port"] if stun_res else 28333

        sdp_answer = {
            "version": "v6.0.0",
            "type": "answer",
            "session_id": session_id,
            "ice_candidate": {
                "ip": ip_addr,
                "port": udp_port,
                "protocol": "udp",
                "type": "srflx"
            },
            "status": "accepted"
        }

        b64_sdp = base64.b64encode(json.dumps(sdp_answer).encode('utf-8')).decode('utf-8')
        irc_msg = f"[PQN_WEBRTC_ANSWER] sid={session_id} sdp={b64_sdp}"
        return {"session_id": session_id, "irc_msg": irc_msg, "target_nick": peer_nick}

    def parse_webrtc_signal(self, irc_line):
        """Parses WebRTC SDP Offer / Answer from IRC message"""
        try:
            if "[PQN_WEBRTC_OFFER]" in irc_line:
                parts = irc_line.split("[PQN_WEBRTC_OFFER]")[1].strip().split()
                p_dict = {item.split("=")[0]: item.split("=")[1] for item in parts if "=" in item}
                b64_sdp = p_dict.get("sdp", "")
                missing_pad = len(b64_sdp) % 4
                if missing_pad:
                    b64_sdp += "=" * (4 - missing_pad)
                sdp_json = json.loads(base64.b64decode(b64_sdp).decode('utf-8'))
                return {"type": "OFFER", "session_id": p_dict.get("sid"), "sdp": sdp_json}
            
            elif "[PQN_WEBRTC_ANSWER]" in irc_line:
                parts = irc_line.split("[PQN_WEBRTC_ANSWER]")[1].strip().split()
                p_dict = {item.split("=")[0]: item.split("=")[1] for item in parts if "=" in item}
                b64_sdp = p_dict.get("sdp", "")
                missing_pad = len(b64_sdp) % 4
                if missing_pad:
                    b64_sdp += "=" * (4 - missing_pad)
                sdp_json = json.loads(base64.b64decode(b64_sdp).decode('utf-8'))
                return {"type": "ANSWER", "session_id": p_dict.get("sid"), "sdp": sdp_json}
        except Exception as e:
            print(f"[WebRTC Signal Error] {e}")
        return None

WEBRTC_ENGINE = PayQuantWebRTCEngine()

def get_webrtc_engine():
    return WEBRTC_ENGINE

if __name__ == '__main__':
    print("==================================================")
    print("      PAYQUANT WEBRTC ICE ENGINE DIAGNOSTICS      ")
    print("==================================================")
    offer = get_webrtc_engine().create_sdp_offer("pqn_peer_node")
    print(f"Generated WebRTC SDP Offer Signal: {offer['irc_msg']}")
    print("==================================================")
