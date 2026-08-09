# 🚀 PayQuant (PQN) – Quantum-Resistant AI Blockchain (v3.1.0 Ecosystem)

[![Build Status](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml/badge.svg)](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml)
[![Quantum Secure](https://img.shields.io/badge/Post--Quantum-ML--DSA--65-brightgreen)](https://github.com/timfromhcs/payquant)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release v3.1.0](https://img.shields.io/github/v/release/timfromhcs/payquant)](https://github.com/timfromhcs/payquant/releases/tag/v3.1.0-release)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue)](https://timfromhcs.github.io/payquant/)

**PayQuant (PQN) Ecosystem v3.1.0** is the world's first post-quantum, self-optimizing AI blockchain platform combining **NIST FIPS 204 ML-DSA-65 digital signatures**, **LevelDB persistent chainstate**, **SPV Light Wallet (Zero-Node Required)** with **24-word BIP-39 seedphrase security**, **QR code invoice payment requests**, and **decentralized P2P solo mining with dynamic furthest-node consensus alignment**.

---

## ⚡ Standalone Native Applications (v3.1.0)

PayQuant v3.1.0 features dedicated standalone desktop and mobile applications across all major operating systems (no web-browser dependencies):

### 1. 🖥️ Standalone GUI Node (`payquant-node-gui`)
- **Persistent ChainDB**: Saves all blocks, UTXOs, and transaction indexes to persistent disk storage (`LevelDB` / SQLite state).
- **Furthest-Node Querying & Auto-Sync**: Continuously polls online P2P peers to identify the furthest valid node height and automatically synchronizes the chain, protecting the network from chain splits and fork manipulation.
- **Zero-Server IRC P2P Engine**: Discovers global peers dynamically across public IRC channels (`#payquant-mainnet`, `#payquant-nodes`, `#payquant-sync`).
- **Live Metrics & Backup Export**: Displays real-time block height, active peers, entropy, visual log stream, and features a 1-click ZIP database backup exporter.

### 2. ⚡ Standalone GUI Miner (`payquant-miner-gui`)
- **Solo P2P Mining (No Central Pools)**: Retrieves candidate block templates directly from local/P2P nodes (`get_mining_job`) and pays block rewards (50.0 PQN) directly to the miner's address.
- **One-Click Operation**: Paste your PQN wallet address, select CPU/GPU mining threads, and click `[▶ START MINING]`.
- **RinHash Acceleration**: ASIC-resistant RinHash PoW with real-time hashrate monitoring (`24,850 H/s`) and instant block payout validation.

### 3. 💳 Cross-Platform Light Wallet (`payquant-wallet` / Android APK)
- **SPV Light Mode**: Runs independently without requiring a local node process. Connects directly to P2P peers to verify headers and balance UTXOs.
- **QR Code Payments & Scanner**: Integrated QR code renderer and camera/file QR scanner for friction-free payments.
- **Payment Request Invoices**: Generate custom payment request QR codes with specific PQN amounts and notes.
- **24-Word BIP-39 Quantum Backup Seedphrase**: Generates a 24-word seedphrase backed by cryptographically secure PRNG and quantum sentinel entropy. Includes 1-click wallet restoration.

---

## 🚀 Quick Start & Launch

### Run Standalone Applications (Python / Native):

```bash
# Clone repository
git clone https://github.com/timfromhcs/payquant.git ~/payquant
cd ~/payquant

# Launch Native GUI Node
python contrib/node_gui.py

# Launch Native GUI Miner
python contrib/miner_gui.py

# Launch Cross-Platform GUI Light Wallet
cd wallet && npm start
```

### Windows 1-Click Launchers:
Double-click:
```cmd
start_payquant_mainnet.bat
```

---

## 🔐 Post-Quantum Cryptography (NIST FIPS 204 ML-DSA-65)

PayQuant utilizes **NIST FIPS 204 ML-DSA-65 (Dilithium)** as its primary digital signature algorithm. Every PQN address (`pqn1q...`) is cryptographically protected against quantum attacks using Shor's algorithm.

| Component | Specification / Size |
|-----------|----------------------|
| Signature Scheme | NIST FIPS 204 ML-DSA-65 |
| Public Key | ~1,312 Bytes |
| Private Key Seed | 32 Bytes / 24-Word BIP-39 Seedphrase |
| Signature | ~2,420 Bytes |
| Multi-Node Attestation | 3-Hop Peer Verification Routing |

---

## 🌐 Synergeia Consensus & P2P Routing

1. **Wallet -> Node**: Transactions broadcast directly to active P2P nodes.
2. **Multi-Node Attestation**: Nodes append peer signature attestations (`verifications`) before entering block templates.
3. **Node -> Miner Solo P2P**: Miners retrieve candidate block templates via `get_mining_job` with coinbase rewards allocated to the miner's address.
4. **Dynamic Consensus Sync**: Nodes query the network every 12 seconds for the furthest valid height, preventing chain splits.

---

## 📦 Multi-Platform Releases & Downloads

| Platform | Component | Package |
|----------|-----------|---------|
| **Windows 64-bit** | GUI Node / GUI Miner / GUI Wallet | Standalone Executables (`.exe`) |
| **Linux x64/arm64** | GUI Node / GUI Miner / GUI Wallet | Standalone AppImages (`.AppImage`) / Binaries |
| **macOS Universal** | GUI Node / GUI Miner / GUI Wallet | Standalone Packages (`.dmg`) |
| **Android Mobile** | GUI Light Wallet | Native Debug/Release APK (`.apk`) |

Visit the [GitHub Releases](https://github.com/timfromhcs/payquant/releases) page to download pre-compiled binaries.

---

## 📜 License

MIT License – see the [LICENSE](LICENSE) file for details.
