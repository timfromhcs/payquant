#!/usr/bin/env python3
"""
PayQuant (PQN) True Random Number Generator Client v2.0.0-quantum
===============================================================
Fetches true-random seeds for the Quantum Footprint engine from external
TRNG sources. API keys are read from the local environment (.env) and are
NEVER committed to the repository.

Sources in priority order:
  1. Outshift (Cisco) QRNG  - REST, API key via OUTSHIFT_API_KEY (env-only)
  2. ANU QRNG               - REST, public endpoint, no auth required
  3. os.urandom fallback    - cryptographically secure, local-only

The class maintains a warm pool of pre-fetched seeds so block production
never blocks on a slow network round-trip.
"""

import logging
import os
import random
import threading
import time
from typing import List, Optional

logger = logging.getLogger("pqn.trng")

try:
    import requests
except Exception:  # pragma: no cover - degraded environments
    requests = None

OUTSHIFT_URL = "https://api.outshift.ai/quantum-random/v1/random"
ANU_URL = "https://qrng.anu.edu.au/API/jsonI.php"


class TRNGClient:
    """Fetches true random seeds with multi-source fallback + seed pool."""

    SEED_SIZE = 32        # default genuine-random bytes per footprint
    POOL_SIZE = 100       # pre-fetched seeds kept warm locally
    NET_TIMEOUT = 5.0

    def __init__(self, source: str = "anu", api_key: Optional[str] = None,
                 pool_size: int = POOL_SIZE):
        self._source = source if source in ("outshift", "anu", "fallback") else "anu"
        # API key consumed from the environment ONCE; stored in-memory only.
        self._api_key = api_key or os.getenv("OUTSHIFT_API_KEY") or ""
        self._pool: List[int] = []
        self._lock = threading.Lock()
        self._pool_size = max(4, min(int(pool_size), 500))
        self._stats = {"fetched": 0, "fallback": 0, "failures": 0}

    # ------------------------------------------------------------------ public
    def get_seed(self, size: int = SEED_SIZE) -> int:  # noqa: F821 -> SEED_SIZE is a class const
        """Return a non-negative big-endian integer seed of `size` random bytes."""
        with self._lock:
            if self._pool:
                return self._pool.pop()
        seed_bytes = self._fetch_random_bytes(size)
        return int.from_bytes(seed_bytes, byteorder="big")

    def pre_fetch_pool(self):
        """Warm the local seed pool (best-effort; never blocks callers)."""
        if len(self._pool) >= self._pool_size:
            return
        wanted = self._pool_size - len(self._pool)
        for _ in range(wanted):
            try:
                blob = self._fetch_random_bytes(self.SEED_SIZE)
                with self._lock:
                    self._pool.append(int.from_bytes(blob, byteorder="big"))
            except Exception:
                break

    def stats(self) -> dict:
        return dict(self._stats)

    # ------------------------------------------------------------------ internals
    def _fetch_random_bytes(self, size: int) -> bytes:
        attempts = []
        if self._source == "outshift":
            attempts.append(self._fetch_outshift)
            attempts.append(self._fetch_anu)
        elif self._source == "anu":
            attempts.append(self._fetch_anu)
            attempts.append(self._fetch_outshift)
        for fetcher in attempts:
            try:
                blob = fetcher(size)
                if blob and len(blob) == size:
                    self._stats["fetched"] += 1
                    return blob
            except Exception as e:
                self._stats["failures"] += 1
                logger.debug("TRNG source unavailable: %s", e)
        # Last-resort crypto-secure local entropy
        self._stats["fallback"] += 1
        return self._fallback(size)

    def _fetch_anu(self, size: int) -> bytes:
        """ANU QRNG public endpoint (uint16 stream)."""
        if requests is None:
            raise RuntimeError("requests library unavailable")
        from urllib.parse import urlencode
        url = ANU_URL + "?" + urlencode({"length": size, "type": "uint16"})
        resp = requests.get(url, timeout=self.NET_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        numbers = data.get("data")
        if not numbers:
            raise RuntimeError("ANU replied without data")
        chunks = b"".join(int(n).to_bytes(2, "big") for n in numbers[:max(size, 1)])
        return self._normalize(chunks, size)

    def _fetch_outshift(self, size: int) -> bytes:
        """Outshift (Cisco) QRNG REST endpoint, API key from env only."""
        if requests is None:
            raise RuntimeError("requests library unavailable")
        if not self._api_key:
            raise RuntimeError("OUTSHIFT_API_KEY not present; skipping")
        resp = requests.get(
            OUTSHIFT_URL,
            params={"length": size},
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=self.NET_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        numbers = data.get("data") or data.get("random") or []
        if not numbers:
            raise RuntimeError("Outshift replied without data")
        chunks = b"".join(int(n).to_bytes(2, "big") for n in numbers[:max(size, 1)])
        return self._normalize(chunks, size)

    @staticmethod
    def _fallback(size: int) -> bytes:
        return os.urandom(size)

    @staticmethod
    def _normalize(blob: bytes, size: int) -> bytes:
        if len(blob) >= size:
            return blob[:size]
        # pad deterministically from local entropy if the remote returned short
        extra = os.urandom(size - len(blob))
        return blob + extra


SEED_LEN = TRNGClient.SEED_SIZE
SEED_SIZE = SEED_LEN  # canonical exported constant (quantum engine)
__all__ = ["TRNGClient", "SEED_SIZE", "SEED_LEN"]