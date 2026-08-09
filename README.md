# 🚀 PayQuant (PQN) – Quantum-Resistant AI Blockchain (v3.5.0 Ecosystem)

[![Build Status](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml/badge.svg)](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml)
[![Quantum Secure](https://img.shields.io/badge/Post--Quantum-ML--DSA--65-brightgreen)](https://github.com/timfromhcs/payquant)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release v3.5.0](https://img.shields.io/github/v/release/timfromhcs/payquant)](https://github.com/timfromhcs/payquant/releases/tag/v3.5.0-release)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue)](https://timfromhcs.github.io/payquant/)

**PayQuant (PQN) Ecosystem v3.5.0** introduces a **Zero-Port Router Forwarding NAT Traversal Engine**, featuring a **Universal 4-Layer P2P Transport Cascade**, **STUN UDP Hole Punching**, **UPnP Auto-Port Mapping**, and **Encrypted IRC Base64 Relay Data Streaming**.

---

## 🌐 Zero-Port-Forwarding NAT Traversal Engine (v3.5.0)

Nodes operate seamlessly behind home routers, strict firewalls, and CGNAT networks without requiring manual router port forwarding.

```text
       [ Client / Node Sync Engine ]
                   │
    ┌──────────────┴──────────────┐
    ▼                             ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│ Tier 1: UPnP / NAT-PMP  │   │ Tier 2: STUN UDP Hole   │
│ Automatic Router Mapping│──►│ Punching (Direct P2P)   │
└─────────────────────────┘   └─────────────────────────┘
            │                              │
            ▼ (If blocked/symmetric NAT)   ▼ (If unreachable)
┌─────────────────────────┐   ┌─────────────────────────┐
│ Tier 3: Direct TCP      │   │ Tier 4: Encrypted IRC   │
│ Public Endpoint Sockets │──►│ Base64 Data Stream      │
└─────────────────────────┘   │ (100% Zero-Port Relay)  │
                              └─────────────────────────┘
```

### Transport Cascade Layers:
1. **Tier 1: UPnP / NAT-PMP Auto-Port Mapping**: Automatically opens router NAT pinholes via SSDP/UPnP protocols.
2. **Tier 2: STUN UDP Hole Punching**: Queries public STUN servers (`stun.l.google.com:19302`) and negotiates bilateral UDP pinholes for direct peer-to-peer streaming.
3. **Tier 3: Direct TCP Socket Stream**: Fallback to standard TCP socket connections when public endpoints are available.
4. **Tier 4: Encrypted IRC Base64 Data Stream Relay (100% Guaranteed Fallback)**: When all direct sockets are blocked by firewalls, data payloads are split into Base64 chunk stream messages (`[PQN_IRC_CHUNK]`) and relayed privately over active IRC connections.

---

## 💻 Standalone Native Applications Suite (v3.5.0)

1. **🔍 Standalone Public Explorer (`payquant-explorer`)**: Zero-node standalone blockchain auditor and address lookup.
2. **🖥️ Standalone GUI Node (`payquant-node-gui`)**: Full node with LevelDB persistent chainstate, BitTorrent stream server, and NAT traversal engine.
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
| **Windows 64-bit** | Standalone Executables (`.exe`) | [Releases v3.5.0](https://github.com/timfromhcs/payquant/releases) |
| **Linux x64/arm64** | Standalone AppImages (`.AppImage`) / Binaries | [Releases v3.5.0](https://github.com/timfromhcs/payquant/releases) |
| **macOS Universal** | Standalone Packages (`.dmg`) | [Releases v3.5.0](https://github.com/timfromhcs/payquant/releases) |
| **Android Mobile** | Native Light Wallet APK (`.apk`) | [Releases v3.5.0](https://github.com/timfromhcs/payquant/releases) |

---

## 📜 License

MIT License – see the [LICENSE](LICENSE) file for details.
