# 🛠️ PayQuant (PQN) Developer Setup & Testing Guide

Welcome developers! This document explains how to set up your local environment, run tests, and build standalone applications for PayQuant v2.0.0-quantum-genesis.

---

## 🚀 Environment Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/timfromhcs/payquant.git
cd payquant

# Install Wallet dependencies
cd wallet && npm install && cd ..
```

---

## 🧪 Running Local Test Suite

Run the full ecosystem diagnostic suite:
```bash
python scripts/local_test_suite.py
```
This tests:
1. Enterprise RocksDB Engine & RepairDB
2. UTXO Fast-Sync Snapshot Generator
3. IRC DCC Engine (DCC SEND/RESUME)
4. WebRTC DataChannel SDP Offer/Answer Signaling
5. P2P BitTorrent Chunk Server & Universal Transport
6. 24-Word Quantum Seedphrase Generation & Validation
7. TRNG + 8-Qubit Quantum Simulation
8. Quantum Footprint Generation & Validator
9. Public 3D Diamond Gallery integrity
10. Repository Secret Gate (no keys/seeds in tree)

### Chain start (mainnet genesis)

The canonical mainnet genesis block is **TRNG-minted** — its hash is a quantum
footprint, not a mined nonce. To mint a fresh genesis locally (secrets stay on
the Desktop, the repo receives only public data):

```bash
python tools/mint_mainnet_genesis.py --source anu   # or outshift / fallback
```

The public constants baked into the repo are defined in
`contrib/chain_db.py` (`GENESIS_BLOCK`) and shown in `README.md`.

---

## 📦 Building Standalone Executables

Compile local native binaries:
```bash
python contrib/build_local_executables.py
```
Outputs binaries in `dist/`:
- `payquant-node-gui.exe` (GUI Full Node)
- `payquant-miner-gui.exe` (GUI Solo Miner)
- `payquant-explorer.exe` (Public Explorer App)
- `payquantd.exe` (Command-Line Daemon)
- `payquant-qt.exe` (QT Wallet Interface)
