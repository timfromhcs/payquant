#!/usr/bin/env python3
"""
PayQuant (PQN) Quantum Footprint Engine v2.0.0-quantum
======================================================
TRNG-driven, panta-sim accelerated, deterministic-3D block signatures.

Submodules
    trng       : TRNGClient (Outshift / ANU QRNG / os.urandom fallback)
    simulator  : QuantumCircuitBackend (panta-sim primary, NumPy fallback)
    footprints : QuantumFootprintGenerator3D + verify_footprint
"""

from contrib.pqn_quantum.trng import TRNGClient, SEED_SIZE
from contrib.pqn_quantum.simulator import (
    QuantumCircuitBackend, N_QUBITS, SHOTS, PANTASIM_AVAILABLE,
)
from contrib.pqn_quantum.footprints import (
    QuantumFootprintGenerator3D, verify_footprint, sha256_of,
)

__version__ = "2.0.0-quantum"
__all__ = [
    "TRNGClient", "SEED_SIZE",
    "QuantumCircuitBackend", "N_QUBITS", "SHOTS", "PANTASIM_AVAILABLE",
    "QuantumFootprintGenerator3D", "verify_footprint", "sha256_of",
    "__version__",
]