#!/usr/bin/env bash
# ============================================================
# PayQuant (PQN) Backend Bootstrap (Linux/macOS) v6.4.0
# Starts: node daemon -> miner daemon -> API server -> signaling
# ============================================================
set -e
cd "$(dirname "$0")/.."

echo "[PayQuant] Starting backend services in the correct order..."
python3 backend/daemon.py start node
python3 backend/daemon.py start miner
python3 backend/daemon.py start api
python3 backend/daemon.py start signaling

echo "[PayQuant] Waiting for stabilization..."
sleep 4
python3 backend/daemon.py status
echo "[PayQuant] All backend services launched."