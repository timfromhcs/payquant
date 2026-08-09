# 🚀 PayQuant (PQN) – Quantum-Resistant AI Blockchain Platform (v6.4.0 Master Release)

<p align="center">
  <img src="doc/payquant-logo.svg" alt="PayQuant Logo" width="220" />
</p>

<p align="center">
  <b>The World's First Post-Quantum Self-Optimizing Blockchain Ecosystem</b><br>
  <i>Powered by NIST FIPS 204 ML-DSA-65 Signatures, Zero-Port-Forwarding P2P Streaming, and Enterprise RocksDB Storage</i>
</p>

<p align="center">
  <a href="https://github.com/timfromhcs/payquant/actions/workflows/build-all-platforms.yml"><img src="https://img.shields.io/github/actions/workflow/status/timfromhcs/payquant/build-all-platforms.yml?branch=main&style=for-the-badge&logo=github" alt="Build Status" /></a>
  <a href="https://github.com/timfromhcs/payquant"><img src="https://img.shields.io/badge/Post--Quantum-ML--DSA--65-brightgreen?style=for-the-badge&logo=shield" alt="Quantum Secure" /></a>
  <a href="https://github.com/timfromhcs/payquant/releases"><img src="https://img.shields.io/github/v/release/timfromhcs/payquant?style=for-the-badge&color=blue" alt="Release v6.4.0" /></a>
  <a href="https://timfromhcs.github.io/payquant/"><img src="https://img.shields.io/badge/GitHub-Pages-purple?style=for-the-badge&logo=github" alt="GitHub Pages" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge" alt="License" /></a>
</p>

---

## 🌟 Executive Overview

**PayQuant (PQN) v6.4.0** is the ultimate release featuring native **Platform Setup Installers** for Windows, Linux, macOS, and Android. It introduces:
- **Payout Wallet Address Entry**: Configure your PQN wallet payout address before mining. Mined block rewards (50 PQN) are automatically credited and broadcasted across the network.
- **Background Daemon Loops**: Non-blocking Node and Miner daemon threads for real-time job distribution (`get_mining_job` & `submit_block`), peer requests, and WebRTC status reporting.
- **WebRTC & IRC-DCC Zero-Port P2P Streaming**: 5-layer NAT traversal cascade.
- **Enterprise RocksDB Engine**: RocksDB Column Families with automatic database repair.
- **Quantum Backup**: 24-word BIP-39 seedphrases with ML-DSA-65 Dilithium signature validation.

---

## 📦 Multi-Platform Setup Installers (v6.4.0)

| Platform | Installer Package | Suite / Application | Download Link |
|----------|-------------------|---------------------|---------------|
| **Windows x64** | `PayQuant-Node-Miner-Suite-Setup-v6.3.0.exe` | Combined Full Node + Solo Miner Setup | [Releases v6.4.0](https://github.com/timfromhcs/payquant/releases) |
| **Windows x64** | `PayQuant-Wallet-Setup-v6.3.0.exe` | Standalone Light Wallet Setup | [Releases v6.4.0](https://github.com/timfromhcs/payquant/releases) |
| **Windows x64** | `PayQuant-Explorer-Setup-v6.3.0.exe` | Standalone Public Explorer Setup | [Releases v6.4.0](https://github.com/timfromhcs/payquant/releases) |
| **Linux x64** | `PayQuant-Node-Miner-Linux.AppImage` | Portable Linux Desktop Suite | [Releases v6.4.0](https://github.com/timfromhcs/payquant/releases) |
| **macOS Universal** | `PayQuant-Ecosystem-macOS.dmg` | macOS App Installer Package | [Releases v6.4.0](https://github.com/timfromhcs/payquant/releases) |
| **Android Mobile** | `PayQuant-Wallet-arm64-v8a.apk` | Native Light Wallet Mobile APK | [Releases v6.4.0](https://github.com/timfromhcs/payquant/releases) |

---

## 🏛️ Ecosystem Architecture

```mermaid
graph TD
    A[PayQuant P2P Client Node] --> B{Layer 1: WebRTC DataChannels}
    B -- Success --> C[High-Speed WebRTC P2P Stream]
    B -- Fallback --> D{Layer 2: IRC DCC SEND/RESUME}
    D -- Success --> E[Direct DCC P2P File Link]
    D -- Fallback --> F{Layer 3: STUN UDP Hole Punch}
    F -- Success --> G[Bilateral UDP Socket Link]
    F -- Fallback --> H{Layer 4: Direct TCP Socket}
    H -- Success --> I[Standard TCP P2P Connection]
    H -- Fallback --> J[Layer 5: Encrypted IRC Base64 Relay Stream]
```

---

## ⚡ Quick Start

### 1. Build Executables & Run Local Diagnostics
```bash
# Execute Win32 Ecosystem Test Suite (7 Categories)
python scripts/local_test_suite.py

# Build Native Desktop Installers & PyInstaller Binaries
python contrib/build_local_executables.py
```

### 2. Launch Unified Desktop Suite
```bash
# Launch Combined Full Node & Solo Miner Desktop App
python contrib/node_miner_gui.py
```

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more details.
