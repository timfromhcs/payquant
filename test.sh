#!/usr/bin/env bash
# PayQuant (PQN) - local test workflow
# Runs the ecosystem unit suite + Docker/compose validation.
# Usage: ./test.sh [unit|docker|all]    (default: all)
set -uo pipefail
cd "$(dirname "$0")"

TARGET="${1:-all}"

run_unit() {
  echo "[test.sh] Running ecosystem unit test suite..."
  python scripts/local_test_suite.py
}

run_docker() {
  echo "[test.sh] Validating docker-compose configuration..."
  docker compose -f docker-compose.yml config --quiet
  docker compose -f docker-compose.yml -f docker-compose.publish.yml config --quiet
  echo "[test.sh] Docker compose configuration is valid."
}

case "${TARGET}" in
  unit)   run_unit ;;
  docker) run_docker ;;
  all)    run_unit; run_docker ;;
  *)      echo "Unknown target '${TARGET}'. Use: unit | docker | all" >&2; exit 2 ;;
esac

echo "ALL TESTS PASSED"