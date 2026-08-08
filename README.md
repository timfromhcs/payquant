# 🚀 PayQuant (PQN) – Die quantensichere KI-Blockchain (v2.0.2)

[![Build Status](https://github.com/timfromhcs/payquant/actions/workflows/ci.yml/badge.svg)](https://github.com/timfromhcs/payquant/actions/workflows/ci.yml)
[![Quantum Secure](https://img.shields.io/badge/Quantum-Secure-brightgreen)](https://github.com/timfromhcs/payquant)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release v2.0.2](https://img.shields.io/github/v/release/timfromhcs/payquant)](https://github.com/timfromhcs/payquant/releases/tag/v2.0.2)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue)](https://timfromhcs.github.io/payquant/)

**PayQuant (PQN) Release 2.0.2** ist die erste quantensichere, selbstoptimierende KI-Blockchain. Sie kombiniert Post-Quantum-Kryptographie (ML-DSA-65), den Synergeia-Konsens (PoW+PoS 15s Finalität), Proof of Useful Work (PoUW) mit ZKML, ASIC-resistentes RinHash-Mining auf Vulkan GPUs, ein dezentrales Spenden-Wallet und einen **dynamischen HTTP-Seed-Pool (`seeds.json`)** für weltweites P2P Auto-Syncing!

---

## 🌐 Dynamic HTTP Seed Pool & P2P Auto-Sync (v2.0.2)

Da statisches DNS/HTTP-Hosting (wie GitHub Pages) kein direktes TCP-Routing auf Port 28333 ausführen kann, nutzt PayQuant v2.0.2 ein **dezentrales HTTP-Seed-Pool-Protokoll (`seeds.json`)**. 

Nodes und Miner rufen beim Start automatisch die aktuelle Liste aktiver Peer-Nodes ab und tragen sie dynamisch als `addnode=` ein.

```bash
# Repository klonen
git clone https://github.com/timfromhcs/payquant.git ~/payquant
cd ~/payquant

# Mainnet Node & Controller starten (mit HTTP Seed Sync auf http://127.0.0.1:8080)
python contrib/mainnet_webui.py
```

### 1-Klick Peer Announcer (Kostenlose Node bekanntgeben)
```bash
# Eigene externe IP / Node im Netzwerk bekanntgeben
python contrib/peer_announcer.py
```

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

## 🤖 Proof of Useful Work (PoUW) + ZKML

Miner trainieren echte KI-Modelle auf GPU-Zyklen. Die Korrektheit des Modell-Trainings wird über **Zero-Knowledge Machine Learning (ZKML)**-Proofs verifiziert.

---

## ⛏️ RinHash – ASIC-resistenter Vulkan PoW Miner

RinHash nutzt eine 3-Stufen-Hash-Pipeline (BLAKE3 + Argon2d + SHA3-256) und läuft auf jeder Vulkan-kompatiblen GPU.

```bash
# RinHash GPU Miner starten
python contrib/vulkan_miner.py --threads 4
```

---

## 💰 Spenden-Wallet (Treasury)

Alle **1.440 Blöcke** (~6 Stunden) schüttet das Spenden-Wallet automatisch **50 PQN** gleichmäßig an alle aktiven Wallets aus.

---

## 📦 Releases & Installation (v2.0.2)

| Betriebssystem | Release Paket | Download Link |
|----------------|---------------|---------------|
| **Windows 64-bit** | Installer `.exe` / Portable `.zip` | [Releases v2.0.2](https://github.com/timfromhcs/payquant/releases/tag/v2.0.2) |
| **Linux x64/arm64** | Binary `.tar.gz` | [Releases v2.0.2](https://github.com/timfromhcs/payquant/releases/tag/v2.0.2) |
| **macOS x64/arm64** | Universal `.dmg` | [Releases v2.0.2](https://github.com/timfromhcs/payquant/releases/tag/v2.0.2) |
| **Docker Container** | Multi-Arch Image | `ghcr.io/timfromhcs/payquant:latest` |

---

## 📜 License

MIT License – siehe [LICENSE](LICENSE) Datei.

---

**🚀 PayQuant (PQN) v2.0.2 – Die quantensichere KI-Blockchain der nächsten Generation.**
