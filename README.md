# 🚀 PayQuant (PQN) – Quantum-Resistant AI Blockchain (v3.4.0 Ecosystem)

[![Build Status](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml/badge.svg)](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml)
[![Quantum Secure](https://img.shields.io/badge/Post--Quantum-ML--DSA--65-brightgreen)](https://github.com/timfromhcs/payquant)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release v3.4.0](https://img.shields.io/github/v/release/timfromhcs/payquant)](https://github.com/timfromhcs/payquant/releases/tag/v3.4.0-release)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue)](https://timfromhcs.github.io/payquant/)

**PayQuant (PQN) Ecosystem v3.4.0** introduces a **Standalone Public Blockchain Explorer Application (`payquant-explorer`)**, **Anti-Attack Security Hardening**, **BitTorrent-Style P2P Data Streaming Protocol**, and **24-word BIP-39 Quantum Backup Seedphrases**.

---

## 🔍 Standalone Public Blockchain Explorer (`payquant-explorer`)

Version 3.4.0 introduces a dedicated standalone desktop explorer application running independently without requiring a local full node:

- **Zero-Node Required**: Discovers global nodes automatically via public IRC signaling (`#payquant-mainnet`) and audits network data directly over TCP sockets.
- **Address & UTXO Audit**: Search any `pqn1q...` wallet address to inspect real-time balances, transaction histories, and UTXO sets.
- **Live Block & Peer Stream**: Displays real-time block generation, transaction counts, network hashrate, and active P2P peer locations.

---

## 🛡️ Anti-Attack Security Hardening (v3.4.0)

- **Block Structure Integrity Gate**: Every block must pass non-negative height validation, PoW target verification (`0000...`), and transaction signature verification before being written to persistent LevelDB / ChainDB storage.
- **Anti-Sybil & Anti-Flooding Protection**: IRC signals are rate-limited to prevent channel flooding and Eclipse attacks.
- **Long-Range Reorg Limit**: Restricts reorg depth to 100 blocks to protect nodes from long-range fork manipulation.
- **Peer Trust Scoring**: Dynamic trust scores assign reputation metrics based on data validity and uptime.

---

## 💻 Standalone Native Applications (v3.4.0)

PayQuant v3.4.0 features a suite of 4 standalone desktop applications and mobile packages:

1. **🔍 Standalone Public Explorer (`payquant-explorer`)**: Zero-node standalone desktop explorer and address auditor.
2. **🖥️ Standalone GUI Node (`payquant-node-gui`)**: Full node with LevelDB persistent chainstate and BitTorrent stream server.
3. **⚡ Standalone GUI Miner (`payquant-miner-gui`)**: One-click RinHash ASIC-resistant GPU/CPU solo miner with instant P2P block rewards.
4. **💳 Cross-Platform Light Wallet (`payquant-wallet` / Android APK)**: 24-word BIP-39 quantum seedphrase wallet with QR code payments and invoice generator.

---

## 🚀 Quick Start & Launch

```bash
# Clone repository
git clone https://github.com/timfromhcs/payquant.git ~/payquant
cd ~/payquant

# Launch Public Blockchain Explorer
python contrib/explorer_gui.py

# Launch Native GUI Node
python contrib/node_gui.py

# Launch Native GUI Miner
python contrib/miner_gui.py

# Launch Cross-Platform GUI Light Wallet
cd wallet && npm start
```

### Windows 1-Click Launchers:
Double-click `start_payquant_mainnet.bat`.

---

## 📦 Multi-Platform Releases & Downloads

| Platform | Executable | Download Link |
|----------|------------|---------------|
| **Windows 64-bit** | Standalone Executables (`.exe`) | [Releases v3.4.0](https://github.com/timfromhcs/payquant/releases) |
| **Linux x64/arm64** | Standalone AppImages (`.AppImage`) / Binaries | [Releases v3.4.0](https://github.com/timfromhcs/payquant/releases) |
| **macOS Universal** | Standalone Packages (`.dmg`) | [Releases v3.4.0](https://github.com/timfromhcs/payquant/releases) |
| **Android Mobile** | Native Light Wallet APK (`.apk`) | [Releases v3.4.0](https://github.com/timfromhcs/payquant/releases) |

---

## 📜 License

MIT License – see the [LICENSE](LICENSE) file for details.
