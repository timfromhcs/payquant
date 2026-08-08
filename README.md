# 🚀 PayQuant (PQN) – Quantensichere KI-Blockchain (v3.0.0 Ecosystem)

[![Build Status](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml/badge.svg)](https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml)
[![Quantum Secure](https://img.shields.io/badge/Quantum-Secure-brightgreen)](https://github.com/timfromhcs/payquant)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release v3.0.0](https://img.shields.io/github/v/release/timfromhcs/payquant)](https://github.com/timfromhcs/payquant/releases/tag/v3.0.0-release)

**PayQuant (PQN) Ecosystem v3.0.0** ist die erste quantensichere, selbstoptimierende KI-Blockchain mit **persistenter LevelDB Blockchain-Datenbank**, **Light Wallet mit SPV-Verifikation (ohne Node-Zwang)**, **QR-Code-Scannern & Zahlungsaufforderungen**, **12-Wort BIP-39 Seedphrase-Wiederherstellung** und **dezentralem P2P Solo-Mining über direkte TCP/IRC-Netzwerkverbindungen**.

---

## ⚡ Multi-Plattform Standalone Applikationen (v3.0.0)

In Version 3.0.0 laufen alle Komponenten als native Standalone-Desktop- und Mobil-Applikationen (vollständig ohne Browser-WebUI):

### 1. 🖥️ Standalone GUI Node (`payquant-node-gui`)
- **Persistente ChainDB**: Speichert alle Blöcke und Transaktionen dauerhaft auf Festplatte (`LevelDB` / SQLite state).
- **Zero-Server P2P**: Entdeckt Peers automatisch über IRC (`#payquant-mainnet` auf Libera/OFTC) und tauscht Blöcke per direktem TCP-Transfer aus.
- **Echtzeit Analytics**: Zeigt Blockhöhe, Peers, Hash-Entropy und visuellen Log-Stream.
- **Backup Export**: 1-Klick-Export der gesamten Blockchain als ZIP-Archiv.

### 2. ⚡ Standalone GUI Miner (`payquant-miner-gui`)
- **Solo P2P Mining**: Keine zentralen Mining-Pools. Der Miner holt Mining-Tasks direkt per P2P und schürft Blöcke auf die eigene Wallet-Adresse.
- **Einfache Bedienung**: Einfach Wallet-Adresse einfügen, Thread-Anzahl wählen und `[▶ START MINING]` klicken.
- **RinHash Acceleration**: Vulkan GPU & CPU Multi-Threading mit Live-Hashrate-Zähler (`24.850 H/s`) und automatischer Payout-Gutschrift.

### 3. 💳 Cross-Platform Light Wallet (`Electron / Android APK`)
- **SPV Light Mode**: Funktioniert auch ohne lokalen Node. Verbindet sich direkt mit P2P-Peers für Headers & UTXO-Sync.
- **QR Code Empfangen & Zahlen**: Integrierter QR-Code Generator und QR Camera/File-Scanner für sekundenschnelle Zahlungen.
- **Zahlungsaufforderungen (Invoices)**: Erstelle wiederverwendbare Zahlungs-QRs mit benutzerdefiniertem PQN-Betrag und Betreff.
- **BIP-39 Quantum Seedphrase**: 12-Wort Wiederherstellungs-Seedphrase beim ersten Start. Inklusive Wiederherstellungs-Funktion bei Passwortverlust.

---

## 🚀 Quick Start & Launch

```bash
# Repository klonen
git clone https://github.com/timfromhcs/payquant.git ~/payquant
cd ~/payquant

# Standalone GUI Node starten
python contrib/node_gui.py

# Standalone GUI Miner starten
python contrib/miner_gui.py

# Cross-Platform Light Wallet starten
cd wallet && npm start
```

### Windows 1-Klick Starter
Doppelklick auf:
```cmd
start_payquant_mainnet.bat
```

---

## 🔐 Post-Quantum-Kryptographie (ML-DSA-65)

PayQuant verwendet **NIST FIPS 204 ML-DSA-65 (Dilithium)** als primären Signaturalgorithmus. Jede Adresse (`pqn1q...`) ist gegen quantenbasierte Angriffe geschützt.

| Komponente | Spezifikation / Größe |
|------------|----------------------|
| Algorithmus | NIST FIPS 204 ML-DSA-65 |
| Public Key | ~1.312 Bytes |
| Private Key Seed | 32 Bytes / 12-Wort BIP-39 Seedphrase |
| Signatur | ~2.420 Bytes |
| Multi-Node Verify | 3-Hop P2P Peer Verification Attestation |

---

## 📦 Multi-Plattform Releases & Artifacts

| Betriebssystem | Applikation | Download Link |
|----------------|-------------|---------------|
| **Windows 64-bit** | Full Node GUI (`.exe`) / Miner GUI (`.exe`) / Wallet (`.exe`) | [Releases v3.0.0](https://github.com/timfromhcs/payquant/releases) |
| **Linux x64/arm64** | Node GUI / Miner GUI / Wallet AppImage (`.AppImage`) | [Releases v3.0.0](https://github.com/timfromhcs/payquant/releases) |
| **macOS Universal** | Node GUI / Miner GUI / Wallet DMG (`.dmg`) | [Releases v3.0.0](https://github.com/timfromhcs/payquant/releases) |
| **Android Mobile** | Light Wallet APK (`.apk`) | [Releases v3.0.0](https://github.com/timfromhcs/payquant/releases) |

---

## 📜 License

MIT License – siehe [LICENSE](LICENSE) Datei.
