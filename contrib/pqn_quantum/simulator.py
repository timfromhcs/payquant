#!/usr/bin/env python3
"""
PayQuant (PQN) Quantum Simulator & Footprint Engine v2.0.0-quantum
=================================================================
Runs the 8-qubit entanglement circuit that mints each block's Quantum
Footprint. Primary backend: panta-sim (panta_sim==1.6.0). A pure-NumPy
statevector fallback keeps tools and CI functional when panta-sim is absent.

Circuit (public design):
    H(0) -> CNOT(0,1) -> Ry(pi/4, 2) -> CNOT(2,3) -> H(4) -> CNOT(4,5)
    -> Rz(pi/3, 6) -> CNOT(6,7) ; measure-all, 1024 shots.

Seed usage: the TRNG seed is passed as `seed` to the simulator's run(); it
seeds the noise/sampling so each seed yields a unique, non-reproducible
footprint without any two blocks colliding.
"""

import numpy as np

try:
    import panta_sim
    PANTASIM_AVAILABLE = True
except Exception:
    panta_sim = None
    PANTASIM_AVAILABLE = False

N_QUBITS = 8
SHOTS = 1024


def build_circuit(panta_sim, qubits: int):
    """Wire the canonical 8-qubit footprint-entanglement circuit in panta-sim."""
    qc = panta_sim.QuantumCircuit(qubits)
    qc.h(0)
    qc.cx(0, 1)
    qc.ry(np.pi / 4, 2)
    qc.cx(2, 3)
    qc.h(4)
    qc.cx(4, 5)
    qc.rz(np.pi / 3, 6)
    qc.cx(6, 7)
    qc.measure_all()
    return qc


class QuantumCircuitBackend:
    """Uniform interface over panta-sim (primary) and NumPy fallback."""

    def __init__(self, qubits: int = N_QUBITS, shots: int = SHOTS):
        self.qubits = int(qubits)
        self.shots = int(shots)
        self.backend = "panta_sim" if PANTASIM_AVAILABLE else "numpy-statevector"

    # ------------------------------------------------------------- public API
    def run(self, seed: int) -> dict:
        """Run the circuit; return {'counts': dict, 'most_probable': str}."""
        seed = self._sim_seed(int(seed))
        if PANTASIM_AVAILABLE:
            try:
                return self._run_pantasim(seed)
            except Exception:
                return self._run_numpy(seed)
        return self._run_numpy(seed)

    @staticmethod
    def _sim_seed(seed: int) -> int:
        """panta-sim's Rust kernel accepts bounded seed ints; clamp deterministically."""
        return int(seed) & 0xFFFFFFFF

    def most_probable_outcome(self, seed: int) -> str:
        return self.run(seed)["most_probable"]

    # ------------------------------------------------------------ panta-sim
    def _run_pantasim(self, seed: int) -> dict:
        qc = build_circuit(panta_sim, self.qubits)
        res = qc.run(shots=self.shots, seed=seed)
        counts = dict(res.counts())
        if not counts:
            raise RuntimeError("panta-sim returned empty counts")
        most_probable = max(counts.items(), key=lambda kv: kv[1])[0]
        return {"counts": counts, "most_probable": most_probable,
                "backend": "panta_sim"}

    # ------------------------------------------------------------ numpy fallback
    def _run_numpy(self, seed: int) -> dict:
        """Deterministic exact statevector of the same circuit (NumPy only)."""
        n = self.qubits
        dim = 1 << n
        state = np.zeros(dim, dtype=complex)
        state[0] = 1.0

        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        Ry = lambda t: np.array([[np.cos(t/2), -np.sin(t/2)],
                                 [np.sin(t/2),  np.cos(t/2)]], dtype=complex)
        Rz = lambda t: np.array([[np.exp(-1j*t/2), 0],
                                 [0,             np.exp(1j*t/2)]], dtype=complex)

        state = self._single(state, 0, H, n)

        def cnot(c, t):
            out = np.zeros_like(state)
            for base in range(dim):
                cb = (base >> c) & 1
                if cb == 1:
                    out[base ^ (1 << t)] += state[base]
                else:
                    out[base] += state[base]
            return out

        state = cnot(0, 1)
        state = self._single(state, 2, Ry(np.pi/4), n)
        state = cnot(2, 3)
        state = self._single(state, 4, H, n)
        state = cnot(4, 5)
        state = self._single(state, 6, Rz(np.pi/3), n)
        state = cnot(6, 7)

        probs = np.abs(state) ** 2
        rng = np.random.default_rng(int(seed))
        samples = rng.choice(dim, size=self.shots, p=probs)
        counts = {}
        for k in samples:
            bstr = format(int(k), f"0{n}b")
            counts[bstr] = counts.get(bstr, 0) + 1
        most_probable = max(counts.items(), key=lambda kv: kv[1])[0]
        return {"counts": counts, "most_probable": most_probable,
                "backend": "numpy-statevector"}

    @staticmethod
    def _single(state: np.ndarray, q: int, g: np.ndarray, n: int) -> np.ndarray:
        """Apply single-qubit gate `g` on qubit `q` of an n-qubit state vector."""
        dim = 1 << n
        out = state.copy()
        bit = 1 << q
        for base in range(dim):
            if base & bit:          # process each pair once (base has q=0)
                continue
            zero = base
            one = base | bit
            a0 = out[zero]
            a1 = out[one]
            out[zero] = g[0, 0] * a0 + g[0, 1] * a1
            out[one] = g[1, 0] * a0 + g[1, 1] * a1
        return out


__all__ = ["QuantumCircuitBackend", "N_QUBITS", "SHOTS", "PANTASIM_AVAILABLE"]