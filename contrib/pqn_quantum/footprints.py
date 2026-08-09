#!/usr/bin/env python3
"""
PayQuant (PQN) Quantum Footprint Generator + Validator v2.0.0-quantum
====================================================================
Transforms quantum simulation results into a block footprint (public,
256-bit SHA-256 hex) and a 3D diamond-like geometry (public, derived from
the footprint hash).

    footprint = SHA256(prev_hash | most_probable_outcome | miner_id | seed)

TRNG seed itself is used as a local-only factor at mint time; it is NEVER
stored in blocks or committed to the repository (a validator re-runs the
simulation using the seed embedded in the block header, exactly as panta-sim
reproduces it deterministically).

Public outputs
    footprint        : 64-char hex (public, verifiable)
    raw_outcome      : most probable 8-qbit bitstring (public)
    geometry_3d      : {vertices, faces, type} diamond facets (public)
    lighting         : primary/secondary/ambient params (public)
    colors           : facet color palette (public)
"""

import hashlib
import json
import math
from typing import Any, Dict, List

from contrib.pqn_quantum.simulator import QuantumCircuitBackend
from contrib.pqn_quantum.trng import TRNGClient

OUTCOME_TOKENS = 4        # segments used for vertex generation
VERTEX_OCANTS = 8         # one facet-vertex per hash segment


def sha256_of(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8"))
    return h.hexdigest()


def fill_byte(entry: str) -> int:
    """Interpret first 2 hex chars of a hash segment as an int 0..255."""
    try:
        return int(entry[:2], 16)
    except (TypeError, ValueError):
        return 0


def segments_of(hash_hex: str, count: int = 8) -> List[str]:
    return [hash_hex[i:i+8] for i in range(0, min(len(hash_hex), count*8), 8)]


class QuantumFootprintGenerator3D:
    """Mints footprints and their companion 3D diamond data from seeds."""

    def __init__(self, trng: TRNGClient = None, backend=None):
        self.trng = trng or TRNGClient("fallback")
        self.backend = backend or QuantumCircuitBackend()

    # ------------------------------------------------------------------ mint
    def generate_footprint(self, previous_hash: str, miner_id: str) -> Dict[str, Any]:
        """Full minting pipeline. Returns public record (seed kept transient)."""
        seed = int(self.trng.get_seed())   # secret, local-only lifetime
        result = self.backend.run(seed)
        most = result["most_probable"]

        payload = f"{previous_hash}|{most}|{miner_id}|{seed}"
        footprint = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        # Public representations only:
        geometry = self.hash_to_3d(footprint)
        lighting = self.hash_to_lighting(footprint)
        colors = self.hash_to_colors(footprint)

        return {
            "seed": seed,                       # transient — never committed
            "footprint": footprint,             # public
            "raw_outcome": most,                # public
            "backend": result.get("backend"),
            "geometry_3d": geometry,
            "lighting": lighting,
            "colors": colors,
        }

    # ------------------------------------------------------------------ public geometry
    def hash_to_3d(self, footprint: str) -> Dict[str, Any]:
        """Deterministic 3D diamond-like faceted geometry from the hash."""
        segments = segments_of(footprint, 8)
        vertices: List[Any] = []
        facets: List[Any] = []

        # crown & pavilion caps
        peak = [0.0, 1.0, 0.0]
        nadir = [0.0, -1.0, 0.0]
        vertices.append(peak)
        vertices.append(nadir)
        rim = []

        for i, seg in enumerate(segments):
            theta = (int(seg[:4], 16) / 65535.0) * 2 * math.pi
            phi = (int(seg[4:], 16) / 65535.0) * math.pi
            radius = 0.55 + 0.45 * (int(seg, 16) / 65535.0)
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.cos(phi)
            z = radius * math.sin(phi) * math.sin(theta)
            idx = len(vertices)
            vertices.append([x, y, z])
            rim.append(idx)

        n = len(vertices)
        # crown facets
        for k in range(1, 8):
            a, b = rim[k - 1], rim[k % 8]
            facets.append([0, a, b])
        # girdle facets (pairs)
        for k in range(0, 8, 1):
            a, b = rim[k], rim[(k + 2) % 8]
            facets.append([1, b, a])
        # base triangle fans from nadir to adjacent rim pairs
        for k in range(8):
            a, b = rim[k], rim[(k + 1) % 8]
            facets.append([1, a, b])

        return {"vertices": vertices, "faces": facets, "type": "diamond"}

    def hash_to_lighting(self, footprint: str) -> Dict[str, Any]:
        seg = segments_of(footprint, 4)
        theta = (int(seg[0][:4], 16) / 65535.0) * 2 * math.pi
        phi = (int(seg[0][4:], 16) / 65535.0) * math.pi
        p1 = [math.sin(phi) * math.cos(theta), math.sin(phi) * math.sin(theta),
              math.cos(phi)]
        theta2 = (int(seg[1][:4], 16) / 65535.0) * 2 * math.pi
        phi2 = (int(seg[1][4:], 16) / 65535.0) * math.pi
        p2 = [math.sin(phi2) * math.cos(theta2), math.sin(phi2) * math.sin(theta2),
              math.cos(phi2)]
        color1 = [fill_byte(seg[2][0:2]) / 255.0, fill_byte(seg[2][2:4]) / 255.0,
                  fill_byte(seg[2][4:6]) / 255.0]
        intens1 = 0.7 + 0.4 * (fill_byte(seg[3][:2]) / 255.0)
        intens2 = 0.4 + 0.4 * (fill_byte(seg[3][2:4]) / 255.0)
        return {
            "primary": {"position": p1, "color": color1, "intensity": round(intens1, 3)},
            "secondary": {"position": p2,
                          "color": [1.0 - color1[0], 1.0 - color1[1], 1.0 - color1[2]],
                          "intensity": round(intens2, 3)},
            "ambient": {"intensity": 0.2 + 0.2 * (fill_byte(seg[3][4:6]) / 255.0)},
        }

    def hash_to_colors(self, footprint: str) -> List[str]:
        seg = segments_of(footprint, 8)
        out = []
        for i in range(0, 8, 2):
            r = fill_byte(seg[i][0:2])
            g = fill_byte(seg[i + 1][0:2])
            b = fill_byte(seg[i][2:4])
            out.append(f"#{r:02x}{g:02x}{b:02x}")
        return out


def verify_footprint(prev_hash: str, miner_id: str, seed: int,
                                 block_footprint: str) -> bool:
    """Deterministically re-mint and compare (validator core)."""
    result = QuantumCircuitBackend().run(int(seed))
    most = result["most_probable"]
    payload = f"{prev_hash}|{most}|{miner_id}|{seed}"
    recomputed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return recomputed == block_footprint


__all__ = ["QuantumFootprintGenerator3D", "verify_footprint", "sha256_of",
           "segments_of", "fill_byte"]