# PayQuant (PQN) - Quantum-Safe, Self-Optimizing AI Blockchain

[![PayQuant CI](https://github.com/payquant/payquant/actions/workflows/ci.yml/badge.svg)](https://github.com/payquant/payquant/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](COPYING)
[![Version](https://img.shields.io/badge/version-1.0.0--alpha-purple.svg)](https://github.com/payquant/payquant)

**PayQuant (PQN)** is a next-generation, post-quantum, AI-driven blockchain built upon the foundations of Bitcoin Knots. It combines NIST FIPS 204 ML-DSA-65 post-quantum cryptography, Synergeia Hybrid Consensus (PoW + PoS), Proof of Useful Work (PoUW) with ZKML verification, ASIC-resistant RinHash GPU mining, dynamic Spenden-Wallet treasury allocation, and FMARL self-optimization.

---

## 🌟 Core Features

- ⚛️ **ML-DSA-65 Post-Quantum Cryptography**: NIST-standardized Dilithium signatures protecting transaction outputs against quantum computer attacks.
- ⚡ **Synergeia Consensus**: Hybrid PoW + PoS consensus engine achieving **15-second block finality** with 27 active validator slots.
- 🧠 **Proof of Useful Work (PoUW) + ZKML**: Zero-Knowledge Machine Learning computation proofs powering decentralized AI inference & model training.
- ⛏️ **RinHash Algorithm & Vulkan GPU Miner**: Multi-stage hashing combining BLAKE3, Argon2d, and SHA3-256 for ASIC resistance.
- 🎁 **Spenden-Wallet (Treasury)**: Automated 50 PQN donation payouts every 1,440 blocks (~6 hours) with Anti-Sybil identity validation.
- 🤖 **FMARL AI Agent**: Federated Multi-Agent Reinforcement Learning self-tuning mempool fee targets, dynamic block sizes, and peer routing.
- 🛡️ **Security Sentinel & Warmup**: First 10,000 blocks initial warmup protection phase and Qiskit quantum circuit entropy monitoring.

---

## 🚀 Quick Start

### 1. Installation & Dependencies

```bash
# Clone PayQuant Repository
git clone https://github.com/payquant/payquant.git ~/payquant
cd ~/payquant

# Install Python Requirements
pip install blake3 argon2-cffi qiskit pycryptodome
```

### 2. Mining & Quantum Audit

```bash
# Run RinHash Vulkan GPU/CPU Miner
python contrib/vulkan_miner.py

# Execute Quantum Sentinel Entropy Audit
python contrib/quantum_sentinel.py

# Run Test Suite
python test/functional/payquant_tests.py
```

---

## 📄 License & Copyright

PayQuant is released under the terms of the MIT license. See [COPYING](COPYING) for more information.
