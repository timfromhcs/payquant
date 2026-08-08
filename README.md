# 🚀 PayQuant (PQN) – Die quantensichere KI-Blockchain (v2.1.2)

[![Build Status](https://github.com/timfromhcs/payquant/actions/workflows/ci.yml/badge.svg)](https://github.com/timfromhcs/payquant/actions/workflows/ci.yml)
[![Quantum Secure](https://img.shields.io/badge/Quantum-Secure-brightgreen)](https://github.com/timfromhcs/payquant)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release v2.1.2](https://img.shields.io/github/v/release/timfromhcs/payquant)](https://github.com/timfromhcs/payquant/releases/tag/v2.1.2)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue)](https://timfromhcs.github.io/payquant/)

**PayQuant (PQN) Release 2.1.2** ist die erste quantensichere, selbstoptimierende KI-Blockchain mit **Zero-Server P2P-Signalisierung über das gesamte Internet** und einem interaktiven **WebUI Mainnet Controller mit Live System Log Visualizer**.

---

## ⚡ Quick Start & WebUI Mainnet Controller (v2.1.2)

```bash
# Repository klonen
git clone https://github.com/timfromhcs/payquant.git ~/payquant
cd ~/payquant

# Mainnet Node, RinHash GPU Miner & WebUI starten (http://127.0.0.1:8080)
python contrib/mainnet_webui.py
```

### Windows 1-Klick Starter
Doppelklick auf:
```cmd
start_payquant_mainnet.bat
```

---

## 💻 Lokale Windows Executables (`dist/`)

In Release 2.1.2 sind vorkompilierte Standalone Executables direkt im `dist/`-Verzeichnis enthalten:
- `dist/payquantd.exe` – PayQuant Mainnet Node Daemon Service
- `dist/vulkan_miner.exe` – RinHash ASIC-Resistenter Vulkan GPU/CPU Miner
- `dist/payquant-qt.exe` – Post-Quantum Core Desktop GUI Wallet

---

## 🌐 Zero-Server Internet P2P Signaling & Peer Discovery

In PayQuant gibt es **keinen zentralen Hauptserver und keinen Single Point of Failure**. 

Jede Node signalisiert ihre Online-Präsenz automatisch auf einem öffentlich sichtbaren Internet-Kanal (`#payquant-mainnet` auf Libera.Chat & OFTC) und entdeckt weltweite Online-Nodes in Echtzeit.

---

## 📜 WebUI Live System Log Visualizer (`http://127.0.0.1:8080`)

Das WebUI bietet volle Kontrolle über Node & RinHash GPU/CPU Miner mit einem echten Live System Log Visualizer:
- **`▶️ Start Mainnet Node`** → Emittiert `[NODE]` Log-Badge im Feed.
- **`⏹️ Stop Mainnet Node`** → Emittiert `[NODE]` Stop-Badge.
- **`⛏️ Start RinHash Miner`** → Emittiert `[MINER]` Badge auf Creator-Wallet `pqn1q65860565c97469d2f22665d0c9ca5d1d8176e2`.
- **`⏹️ Stop RinHash Miner`** → Stoppt Miner & protokolliert Hashrate.
- **`🌐 P2P Internet Signaling`** → Zeigt gefundene Online-Peers im `[P2P]` Feed an.

---

## 🔐 Post-Quantum-Kryptographie (ML-DSA-65)

PayQuant verwendet **NIST FIPS 204 ML-DSA-65 (Dilithium)** als primären Signaturalgorithmus. Jede Adresse (`pqn1q...`) ist gegen Angriffe mit Shors Algorithmus geschützt.

| Komponente | Spezifikation / Größe |
|------------|----------------------|
| Algorithmus | NIST FIPS 204 ML-DSA-65 |
| Public Key | ~1.312 Bytes |
| Private Key Seed | 32 Bytes |
| Signatur | ~2.420 Bytes |
| Fallback | SLH-DSA (SPHINCS+) |

---

## ⚡ Synergeia-Konsens (PoW + PoS 15s)

Der Synergeia-Konsens vereint Proof-of-Work und Proof-of-Stake für maximale Sicherheit und 15-Sekunden-Block-Finalität.

- **PoW-Miner**: Findet Kandidatenblock mit RinHash.
- **PoS-Validatoren**: 27 zufällig ausgewählte Nodes stimmen ab.
- **67% Supermajority**: Block-Finalisierung in 15 Sekunden.
- **Super-exponentielle Sicherheit**: $\varepsilon(k) \le \exp(-C_1 k^2) + \exp(-C_2 k)$ ($k = 26$ für $\varepsilon \le 10^{-9}$).

---

## ⛏️ RinHash – ASIC-resistenter Vulkan PoW Miner

RinHash nutzt eine 3-Stufen-Hash-Pipeline (BLAKE3 + Argon2d + SHA3-256) und läuft auf jeder Vulkan-kompatiblen GPU.

```bash
python contrib/vulkan_miner.py --threads 4 --address pqn1q65860565c97469d2f22665d0c9ca5d1d8176e2
```

---

## 💰 Spenden-Wallet (Treasury)

Alle **1.440 Blöcke** (~6 Stunden) schüttet das Spenden-Wallet automatisch **50 PQN** gleichmäßig an alle aktiven Wallets aus.

---

## 📦 Releases & Installation (v2.1.2)

| Betriebssystem | Release Paket | Download Link |
|----------------|---------------|---------------|
| **Windows 64-bit** | Installer `.exe` / Portable `.zip` | [Releases v2.1.2](https://github.com/timfromhcs/payquant/releases/tag/v2.1.2) |
| **Linux x64/arm64** | Binary `.tar.gz` | [Releases v2.1.2](https://github.com/timfromhcs/payquant/releases/tag/v2.1.2) |
| **macOS x64/arm64** | Universal `.dmg` | [Releases v2.1.2](https://github.com/timfromhcs/payquant/releases/tag/v2.1.2) |
| **Docker Container** | Multi-Arch Image | `ghcr.io/timfromhcs/payquant:latest` |

---

## 📜 License

MIT License – siehe [LICENSE](LICENSE) Datei.

---

**🚀 PayQuant (PQN) v2.1.2 – Die quantensichere KI-Blockchain der nächsten Generation.**
