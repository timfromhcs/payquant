#!/usr/bin/env bash
# ============================================================
# PayQuant (PQN) Backend Service Status (Linux/macOS) v6.4.0
# ============================================================
cd "$(dirname "$0")/.."

python3 backend/daemon.py status

echo
echo "[PayQuant] API health check:"
curl -s --max-time 4 http://127.0.0.1:28377/api/health || echo "API: unreachable (is api daemon running?)"