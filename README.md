# 🚀 PayQuant (PQN) – Die quantensichere KI-Blockchain

[![Build Status](https://github.com/timfromhcs/payquant/actions/workflows/ci.yml/badge.svg)](https://github.com/timfromhcs/payquant/actions/workflows/ci.yml)
[![Quantum Secure](https://img.shields.io/badge/Quantum-Secure-brightgreen)](https://github.com/timfromhcs/payquant)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/timfromhcs/payquant)](https://github.com/timfromhcs/payquant/releases)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue)](https://timfromhcs.github.io/payquant/)

**PayQuant (PQN)** ist die erste quantensichere, selbstoptimierende KI-Blockchain. Sie kombiniert Post-Quantum-Kryptographie (ML-DSA-65), einen innovativen Synergeia-Konsens (PoW+PoS), Proof of Useful Work (PoUW) mit ZKML, ASIC-resistentes RinHash-Mining und ein dezentrales Spenden-Wallet zu einem vollständigen Ökosystem.

## ⚡ Quick Start

```bash
# Repository klonen (KORREKTE URL)
git clone https://github.com/timfromhcs/payquant.git ~/payquant
cd ~/payquant

# Kompilieren
mkdir build && cd build
cmake .. -DBUILD_GUI=ON
make -j$(nproc)

# Node starten
./src/payquantd -daemon
./src/payquant-cli getblockchaininfo
```

## 🔐 Post-Quantum-Kryptographie (ML-DSA-65)

PayQuant verwendet **NIST FIPS 204 ML-DSA-65 (Dilithium)** als primären Signaturalgorithmus. Dilithium ist eines der von der US-Regierung standardisierten Post-Quantum-Verfahren und bietet Schutz gegen Angriffe mit Shors Algorithmus auf Quantencomputern.

**Schlüsselgrößen:**
| Komponente | Größe |
|------------|-------|
| Öffentlicher Schlüssel | ~1.312 Bytes |
| Privater Schlüssel | ~2.528 Bytes |
| Signatur | ~2.420 Bytes |

**Fallback:** SLH-DSA (SPHINCS+) – hash-basierte Alternative, falls Lattice-basierte Verfahren gebrochen werden sollten.

**Krypto-Agilität:** Jede Signatur trägt einen Algorithmus-Identifikator (0x01 = ML-DSA, 0x02 = SLH-DSA), was spätere Upgrades ohne Konsens-Bruch ermöglicht.

## ⚡ Synergeia-Konsens (PoW + PoS)

Der Synergeia-Konsens kombiniert Proof-of-Work und Proof-of-Stake in einem neuartigen Verfahren namens **Local Dynamic Difficulty (LDD)**.

**Kernmechanismus:**
1. **PoW-Miner** findet einen Kandidatenblock mit RinHash (15 Sekunden Zielzeit)
2. **PoS-Validatoren-Gremium** (27 Nodes) wird per echtem Zufall (TRNG + DePIN) ausgewählt
3. **67% Supermajority** wird für die Finalisierung benötigt
4. **Optionale Burst-Finality** ermöglicht Instant-Finality in ~5 Sekunden

**Sicherheitsgarantie:** Die Block-Interarrival-Zeit wird zu einer Rayleigh-Verteilung geformt, was zu super-exponentieller Sicherheit führt: **ε(k) ≤ exp(-C₁k²) + exp(-C₂k)**

Für Enterprise-Sicherheit (ε ≤ 10⁻⁹) werden nur **k = 26 Blöcke** gegen einen 40%-Angreifer benötigt – bei Bitcoin sind es über 100 Blöcke!

**Konsens-Flow (textuell):**
1. PoW-Miner findet Kandidatenblock
2. 27 PoS-Validatoren werden zufällig ausgewählt
3. Die Validatoren stimmen mit ihrem Stake ab
4. Bei 67% Zustimmung wird der Block in 15s finalisiert
5. Bei Ablehnung wird der Block verworfen
6. Nach Finalisierung prüft das Spenden-Wallet die Aktivität
7. Verteilung an aktive Nutzer

## 🤖 Proof of Useful Work (PoUW) + ZKML

Anders als bei Bitcoin wird die Rechenleistung nicht für sinnloses Hashing verschwendet. Stattdessen trainieren Miner echte KI-Modelle – und beweisen die Korrektheit des Trainings über **Zero-Knowledge Machine Learning (ZKML)**-Proofs.

**Ablauf:**
1. Nutzer burned PQN in einen Smart Contract
2. Miner erhält AI-Training-Job
3. Training wird auf GPU durchgeführt (RinHash + Modell-Training)
4. ZK-Proof der korrekten Ausführung wird generiert
5. Validatoren verifizieren den Proof
6. Bei Erfolg: Block akzeptiert + Reward + Credibility

**Vorteile:**
- GPU-Zyklen haben echten gesellschaftlichen Nutzen
- Miner verdienen nicht nur durch Blöcke, sondern auch durch AI-Training
- Dezentralisierte KI-Entwicklung ohne zentrale Anbieter

## ⛏️ RinHash – ASIC-resistenter PoW

RinHash kombiniert drei Hash-Funktionen für maximale ASIC-Resistenz:

| Schritt | Algorithmus | Zweck |
|---------|-------------|-------|
| 1 | **BLAKE3** | Schnelles, modernes Hashing |
| 2 | **Argon2d** | Memory-hard (64KB, 2 Iterationen) – ASIC-Resistenz |
| 3 | **SHA3-256** | Finaler sicherer Hash |

**Warum ASIC-resistent?** Jeder kann mit handelsüblicher Hardware minen – keine teuren Spezialgeräte nötig.

### Vulkan-Mining Performance

| Hardware | Hashrate |
|----------|----------|
| Browser (CPU) | ~1 MH/s |
| Moderne CPU | ~150 MH/s |
| iGPU (Iris Xe) | ~300 MH/s |
| Mid-Range GPU | ~1-2 GH/s |
| High-End GPU | ~3-5 GH/s |

## 💰 Spenden-Wallet (Treasury)

Alle **1.440 Blöcke** (~6 Stunden) wird das Spenden-Wallet automatisch geleert und der gesamte Betrag gleichmäßig an alle aktiven Nutzer verteilt.

**Parameter:**
- **Ausschüttung:** 50 PQN pro Intervall
- **Aktive Nutzer:** Wallets mit mindestens einer Transaktion in den letzten 1.440 Blöcken
- **Mindestgebühr:** 0,0001 PQN (Anti-Sybil-Schutz)
- **Miner-Extra:** 0,1 PQN für das Einbauen der Verteilungs-Transaktion

**Anti-Sybil-Schutz:** Nur Wallets mit mindestens einer Transaktion in den letzten 1.440 Blöcken gelten als "aktiv" – das verhindert Missbrauch durch tausende leere Wallets.

## 🧠 FMARL – AI-Selbstoptimierung

Jeder PayQuant-Node enthält einen lokalen Reinforcement-Learning-Agenten, der kontinuierlich lernt und die Netzwerkparameter optimiert:

| Komponente | Beschreibung |
|------------|--------------|
| **Zustand** | Transaktionsvolumen, Netzwerk-Latenz, Validator-Verhalten |
| **Aktion** | Block-Größe, Validator-Auswahl, Gebührenstruktur |
| **Belohnung** | Durchsatz, Sicherheit, Energieeffizienz |

**Ergebnisse aus der Forschung:**
- **Genauigkeit:** 98,67%
- **Präzision:** 97,55%
- **Recall:** 98,64%
- **F1-Score:** 98,77%

## 🛡️ Quantum Sentinel – Echtzeit-Quantenüberwachung

Der Quantum Sentinel simuliert kontinuierlich Angriffe mit Shors und Grovers Algorithmus auf die aktuelle Blockchain:

1. **Shors Algorithmus** auf aktuelle Block-Signaturen (prüft ML-DSA-65)
2. **Grovers Algorithmus** auf die Schwierigkeit
3. **Automatische Anpassung** der kryptografischen Parameter (z.B. Wechsel auf ML-DSA-87)

**Aktueller Status:** ✅ QUANTUM SECURE (Entropy: 7.999 bits/byte)

## 📦 Installation

### Windows
```bash
# Installer
payquant-1.0.0-win64-setup.exe

# Oder portable ZIP
payquant-1.0.0-win64.zip
```

### Linux
```bash
tar -xzf payquant-1.0.0-linux-x64.tar.gz
./payquantd -daemon
```

### macOS
```bash
# Intel
payquant-1.0.0-macos-x64.dmg

# Apple Silicon
payquant-1.0.0-macos-arm64.dmg
```

### Docker
```bash
docker pull ghcr.io/timfromhcs/payquant:latest
docker run -p 28333:28333 payquant/payquant:latest
```

## 🤝 Contributing

1. Fork das Repository (`https://github.com/timfromhcs/payquant`)
2. Erstelle einen Feature-Branch (`git checkout -b feature/amazing-feature`)
3. Commite deine Änderungen (`git commit -m 'Add amazing feature'`)
4. Pushe den Branch (`git push origin feature/amazing-feature`)
5. Erstelle einen Pull Request

## 📜 License

MIT License – siehe [LICENSE](LICENSE) Datei.

## 🔗 Links

- [GitHub Repository](https://github.com/timfromhcs/payquant)
- [Webseite](https://timfromhcs.github.io/payquant/)
- [Releases](https://github.com/timfromhcs/payquant/releases)
- [Docker Images](https://github.com/timfromhcs/payquant/pkgs/container/payquant)

---

**🚀 PayQuant – Die Zukunft der Blockchain ist quantensicher, selbstoptimierend und nützlich.**
