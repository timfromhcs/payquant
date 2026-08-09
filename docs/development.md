# 🛠️ PayQuant (PQN) Developer Setup & Testing Guide

Welcome developers! This document explains how to set up your local environment, run tests, and build standalone applications for PayQuant v6.0.0.

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
