#!/usr/bin/env bash
# ============================================================
# PayQuant (PQN) Backend Shutdown (Linux/macOS) v6.4.0
# ============================================================
cd "$(dirname "$0")/.."

echo "[PayQuant] Stopping all backend services..."
python3 backend/daemon.py stop signaling
python3 backend/daemon.py stop api
python3 backend/daemon.py stop miner
python3 backend/daemon.py stop node

echo "[PayQuant] All backend services stopped cleanly."