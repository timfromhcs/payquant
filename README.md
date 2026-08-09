# 🚀 PayQuant (PQN) – Quantum-Resistant AI Blockchain (v3.3.0 Ecosystem)

[![Build Status](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml/badge.svg)](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml)
[![Quantum Secure](https://img.shields.io/badge/Post--Quantum-ML--DSA--65-brightgreen)](https://github.com/timfromhcs/payquant)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release v3.3.0](https://img.shields.io/github/v/release/timfromhcs/payquant)](https://github.com/timfromhcs/payquant/releases/tag/v3.3.0-release)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue)](https://timfromhcs.github.io/payquant/)

**PayQuant (PQN) Ecosystem v3.3.0** features a **BitTorrent-style P2P Parallel Data Streaming Protocol**, **Private 1-on-1 IRC Handshakes & Cluster Mesh Auto-Formation**, **Dynamic Failover Protection**, **Pruned Fast-Verify Mode**, and **24-word BIP-39 Quantum Backup Seedphrases**.

---

## ⚡ BitTorrent P2P Streaming & Torrent Cluster Architecture (v3.3.0)

Version 3.3.0 introduces a Torrent-like P2P streaming engine that accelerates block synchronization and protects nodes from chain splits:

### 1. 💬 Private 1-on-1 IRC Handshake (`PRIVMSG` / `NOTICE`)
- **Non-Public Negotiations**: Nodes connect to IRC (`#payquant-mainnet`, `#payquant-nodes`, `#payquant-sync`) and initiate direct private handshakes (`PRIVMSG <nick> :[PQN_TORRENT_REQ]`) without channel flooding.
- **Trust & Speed Scoring**: Handshakes exchange verified block height, DB hash integrity, and available streaming bandwidth.

### 2. 🔀 BitTorrent-Style Piece Partitioning & Parallel Downloads
- **Torrent Piece Chunks**: Block ranges are partitioned into 50-block pieces and streamed concurrently across multiple online cluster peers over TCP sockets.
- **Pruned Fast-Verify Mode**: New nodes instantly verify incoming transactions using Block Headers + UTXO Set state while full historical torrent streams complete in the background.

### 3. 🛡️ Dynamic Failover & Chain Split Protection
- **Automatic Peer Failover**: If a streaming peer drops offline or lags, the cluster detects it instantly and reassigns missing block pieces to backup cluster peers.
- **Furthest-Node Consensus Alignment**: Nodes continuously poll the peer pool to identify the furthest valid chain height, preventing forks and chain splits.

---

## 💻 Standalone Native Applications (v3.3.0)

PayQuant v3.3.0 includes dedicated standalone desktop and mobile applications across all platforms:

- **🖥️ Standalone GUI Node (`payquant-node-gui`)**: Full node with LevelDB persistent chainstate, BitTorrent stream server, live metrics, and 1-click ZIP backup export.
- **⚡ Standalone GUI Miner (`payquant-miner-gui`)**: RinHash ASIC-resistant GPU/CPU solo miner with 1-click payout address input and direct P2P solo rewards.
- **💳 Cross-Platform Light Wallet (`payquant-wallet` / Android APK)**: 24-word BIP-39 quantum seedphrase wallet with QR code payments, camera/file scanner, and invoice request generator.

---

## 🚀 Quick Start & Launch

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
Double-click `start_payquant_mainnet.bat`.

---

## 🔐 Post-Quantum Cryptography & Specs

| Component | Specification / Size |
|-----------|----------------------|
| Signature Scheme | NIST FIPS 204 ML-DSA-65 (Lattice-Based) |
| Public Key | ~1,312 Bytes |
| Private Key Seed | 32 Bytes / 24-Word BIP-39 Seedphrase |
| Signature | ~2,420 Bytes |
| P2P Data Protocol | BitTorrent-Style Piece Streaming over Direct TCP Sockets |
| IRC Handshake | Private 1-on-1 `PRIVMSG` / `NOTICE` Signaling |

---

## 📦 Multi-Platform Releases & Downloads

| Platform | Package | Download Link |
|----------|---------|---------------|
| **Windows 64-bit** | Standalone Executables (`.exe`) | [Releases v3.3.0](https://github.com/timfromhcs/payquant/releases) |
| **Linux x64/arm64** | Standalone AppImages (`.AppImage`) / Binaries | [Releases v3.3.0](https://github.com/timfromhcs/payquant/releases) |
| **macOS Universal** | Standalone Packages (`.dmg`) | [Releases v3.3.0](https://github.com/timfromhcs/payquant/releases) |
| **Android Mobile** | Native Light Wallet APK (`.apk`) | [Releases v3.3.0](https://github.com/timfromhcs/payquant/releases) |

---

## 📜 License

MIT License – see the [LICENSE](LICENSE) file for details.
