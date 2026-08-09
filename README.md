# 🚀 PayQuant (PQN) – Quantum-Resistant AI Blockchain (v6.0.0 Ultimate Release)

[![Build Status](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml/badge.svg)](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml)
[![Quantum Secure](https://img.shields.io/badge/Post--Quantum-ML--DSA--65-brightgreen)](https://github.com/timfromhcs/payquant)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release v6.0.0](https://img.shields.io/github/v/release/timfromhcs/payquant)](https://github.com/timfromhcs/payquant/releases/tag/v6.0.0-release)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue)](https://timfromhcs.github.io/payquant/)

**PayQuant (PQN) Ecosystem v6.0.0** is the ultimate release featuring **WebRTC DataChannel Streaming**, **IRC DCC (Direct Client-to-Client) Transfers**, **Enterprise RocksDB Storage Engine**, **Fast-Sync UTXO Snapshots**, and **24-word BIP-39 Quantum Backup Seedphrases**.

---

## 🌐 Hybrid P2P Architecture without Port Forwarding (v6.0.0)

Nodes establish direct peer-to-peer connections behind any NAT, firewall, or CGNAT network through a 5-layer transport fallback matrix:

```text
               [ PayQuant P2P Network Engine ]
                              │
     ┌────────────────────────┼────────────────────────┐
     ▼                        ▼                        ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ WebRTC Data  │      │   IRC DCC    │      │  STUN UDP    │
│ Channels/ICE │─────►│ SEND/RESUME  │─────►│ Hole Punch   │
└──────────────┘      └──────────────┘      └──────────────┘
     │                        │                        │
     ▼                        ▼                        ▼
┌──────────────┐      ┌──────────────┐
│ Direct TCP   │─────►│ Encrypted    │
│ Socket       │      │ IRC Base64   │
└──────────────┘      └──────────────┘
```

### Protocol Mechanics:
1. **WebRTC DataChannels & ICE**: High-throughput DataChannel P2P streaming with SDP Offer/Answer signaling over IRC and STUN candidate discovery (`stun.l.google.com:19302`).
2. **IRC DCC (Direct Client-to-Client)**: Direct DCC SEND, DCC RESUME, and Reverse DCC P2P file transfers for firewalled nodes.
3. **STUN UDP Hole Punching**: Bilateral UDP pinhole punching between NATed nodes.
4. **Encrypted IRC Base64 Relay**: 100% guaranteed fallback relaying Base64 payload chunks over private IRC channels (`PRIVMSG`).

---

## 💾 Enterprise RocksDB Storage & UTXO Fast-Sync (v6.0.0)

- **Enterprise RocksDB Engine**: High-performance Column Families (`blocks`, `utxo_set`, `snapshots`) with enterprise buffer tuning (`write_buffer_size=64MB`, `block_size=4096`, `cache_size=256MB`).
- **In-Memory LRU UTXO Cache & Bloom Filters**: High-speed transaction verification and instant UTXO lookups.
- **Fast-Sync Engine**: New nodes load verified periodic UTXO Snapshots, reducing initial network synchronization time from hours to minutes!
- **Automatic DB Repair**: Auto-recovery mode restores corrupted databases seamlessly.

---

## 💻 Standalone Native Applications Suite (v6.0.0)

1. **🔍 Standalone Public Explorer (`payquant-explorer`)**: Zero-node standalone blockchain auditor and address lookup.
2. **🖥️ Standalone GUI Node (`payquant-node-gui`)**: Full node with RocksDB persistent storage, WebRTC P2P stream server, and Fast-Sync engine.
3. **⚡ Standalone GUI Miner (`payquant-miner-gui`)**: One-click RinHash ASIC-resistant GPU/CPU solo miner with direct P2P payouts.
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
| **Windows 64-bit** | Standalone Executables (`.exe`) | [Releases v6.0.0](https://github.com/timfromhcs/payquant/releases) |
| **Linux x64/arm64** | Standalone AppImages (`.AppImage`) / Binaries | [Releases v6.0.0](https://github.com/timfromhcs/payquant/releases) |
| **macOS Universal** | Standalone Packages (`.dmg`) | [Releases v6.0.0](https://github.com/timfromhcs/payquant/releases) |
| **Android Mobile** | Native Light Wallet APK (`.apk`) | [Releases v6.0.0](https://github.com/timfromhcs/payquant/releases) |

---

## 📜 License

MIT License – see the [LICENSE](LICENSE) file for details.
