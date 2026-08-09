#!/usr/bin/env bash
# PayQuant (PQN) - local Docker image build workflow
# Usage: ./build.sh [node|miner|all]    (default: all)
set -euo pipefail
cd "$(dirname "$0")"

TARGET="${1:-all}"
MINER_IMG="payquant-miner:local"
NODE_IMG="payquant-node:local"

case "${TARGET}" in
  node)
    docker build -t "${NODE_IMG}" -f Dockerfile.node .
    ;;
  miner)
    docker build -t "${MINER_IMG}" -f Dockerfile .
    ;;
  all)
    docker build -t "${NODE_IMG}" -f Dockerfile.node .
    docker build -t "${MINER_IMG}" -f Dockerfile .
    docker compose build
    ;;
  *)
    echo "Unknown target '${TARGET}'. Use: node | miner | all" >&2
    exit 2
    ;;
esac

echo "OK: local PayQuant Docker images built (${NODE_IMG}, ${MINER_IMG})."