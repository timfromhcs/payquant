# 🤖 PayQuant (PQN) AI Agent & Contributor Guidelines

Welcome AI Agent! This document outlines strict operational rules and conventions for AI assistants, automated bots, and human developers contributing to **PayQuant (PQN)**.

---

## 🎯 Project Core Principles

1. **Zero-Breaking Changes**: Never modify core consensus rules, transaction formats, or signature validation logic unless explicitly addressing a security vulnerability.
2. **Intent-Centric UX**: User interfaces must prioritize clarity, large bold balances, passkey biometrics, and clear transaction status indicators over raw hash strings.
3. **Zero-Port NAT Traversal**: P2P transport engines must maintain multi-layer fallback cascades (WebRTC DataChannels -> IRC DCC -> STUN UDP Hole Punch -> Direct TCP -> Encrypted IRC Base64 Relay) so nodes function behind home routers without port forwarding.
4. **Post-Quantum Security**: All wallet keypairs use NIST FIPS 204 ML-DSA-65 (Dilithium) signatures derived from 24-word BIP-39 seedphrases.

---

## 🛠️ Repository Structure

- `contrib/node_gui.py`: Native standalone GUI Full Node application.
- `contrib/miner_gui.py`: Native standalone GUI RinHash PoW Miner application.
- `contrib/explorer_gui.py`: Standalone Public Blockchain Explorer & Address Auditor.
- `contrib/chain_db.py`: Enterprise RocksDB / LevelDB persistent storage engine with UTXO In-Memory LRU Cache.
- `contrib/nat_p2p_transport.py`: Zero-Port NAT Traversal & STUN UDP Hole Punching engine.
- `contrib/irc_dcc_engine.py`: IRC DCC SEND/RESUME & Reverse DCC P2P file transfer engine.
- `contrib/webrtc_p2p_engine.py`: WebRTC DataChannels & ICE SDP Offer/Answer signaling over IRC.
- `contrib/fast_sync_engine.py`: Fast-Sync UTXO Snapshot generator & instant sync importer.
- `wallet/`: Cross-Platform Electron + Capacitor Light Wallet GUI.
- `.github/workflows/build-all.yml`: Multi-platform release build pipeline (Windows, Linux, macOS, Android).

---

## 🧪 Testing & Validation Gate

Before submitting any Pull Request or committing changes:
```bash
# Run full ecosystem test suite
python scripts/local_test_suite.py

# Rebuild local standalone binaries
python contrib/build_local_executables.py

# Build wallet web bundle
cd wallet && npm run build:web
```

All 6 test categories in `scripts/local_test_suite.py` MUST pass with 100% clean output.
