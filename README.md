# 🚀 PayQuant (PQN) – Post-Quantum Self-Optimizing AI Blockchain

<p align="center">
  <img src="doc/payquant-logo.svg" alt="PayQuant Logo" width="220" />
</p>

<p align="center">
  <b>The World's First Post-Quantum, Self-Optimizing Blockchain Ecosystem</b><br>
  <i>NIST FIPS 204 ML-DSA-65 Signatures · Zero-Port-Forwarding P2P Streaming · 3D Quantum Diamonds · Merkle-Delta UTXO Sync</i>
</p>

<p align="center">
  <a href="https://github.com/timfromhcs/payquant/actions/workflows/build-all.yml"><img src="https://img.shields.io/github/actions/workflow/status/timfromhcs/payquant/build-all.yml?branch=main&style=for-the-badge&logo=github" alt="Build Status" /></a>
  <a href="https://github.com/timfromhcs/payquant"><img src="https://img.shields.io/badge/Post--Quantum-ML--DSA--65-brightgreen?style=for-the-badge&logo=shield" alt="Quantum Secure" /></a>
  <a href="https://github.com/timfromhcs/payquant/releases"><img src="https://img.shields.io/github/v/release/timfromhcs/payquant?style=for-the-badge&color=blue" alt="Release" /></a>
  <a href="https://timfromhcs.github.io/payquant/"><img src="https://img.shields.io/badge/GitHub--Pages-Online-purple?style=for-the-badge&logo=github" alt="GitHub Pages" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge" alt="License" /></a>
</p>

<p align="center">
  <a href="https://timfromhcs.github.io/payquant/">🌐 Website</a> ·
  <a href="https://timfromhcs.github.io/payquant/download.html">⬇️ Download</a> ·
  <a href="https://timfromhcs.github.io/payquant/docs.html">📖 Docs</a> ·
  <a href="https://timfromhcs.github.io/payquant/architecture.html">🏗 Architecture</a> ·
  <a href="https://timfromhcs.github.io/payquant/security.html">🔐 Security</a>
</p>

---

## 🌟 What is PayQuant?

**PayQuant (PQN)** is a post-quantum, self-optimizing blockchain ecosystem designed to stay
private and functional no matter where it runs — from your home PC behind a router to a
cloud server. It combines:

| Pillar | What it gives you |
| --- | --- |
| 🛡️ **ML-DSA-65 (Dilithium)** | NIST FIPS 204 lattice signatures — quantum-attack resistant *today* |
| 🔀 **Zero-Port P2P** | 5-layer transport cascade (WebRTC → IRC DCC → STUN → TCP → encrypted relay). No port forwarding needed |
| 🗄️ **RocksDB Engine** | Column-family storage, UTXO LRU cache, Bloom filters, auto-repair on startup |
| 🧮 **Merkle-Delta Sync** | Canonical fingerprint compare → ships only UTXO deltas, not whole blobs |
| 📦 **DirectDrop Files** | AES-256-GCM sealed, love-code exchanged peer-to-peer file transfer |
| ⚡ **Fast-Sync** | Verified UTXO snapshots cut initial sync from hours to minutes |
| ⚡ **RinHash PoW** | ASIC-resistant memory-hard mining with 50 PQN block rewards |
| 💳 **Quantum Wallet** | 24-word BIP-39 seed encrypted with Argon2id master password |
| 🤖 **Self-Healing Daemons** | Background orchestration with health checks and ordered lifecycle |
| 🎲 **TRNG Quantum Core** | True-random seeds from Cisco Outshift / ANU QRNG (desktop-only) drive the 8-qubit simulator |
| 💎 **3D Quantum Diamonds** | Every block mints a unique, publicly verifiable 3D diamond derived from its quantum footprint |

---

## ✨ Features

- **Unified Node + Miner desktop suite** (`node_miner_gui.py`) and standalone GUIs for Node, Miner, Wallet and Explorer.
- **Payout wallet address persistence** – miners define a payout address before mining; settings are auto-loaded on every launch (`miner/backend/config_manager.py`).
- **Live WebSocket status & mining jobs** – `/ws/events` status stream, `get_mining_job` / `submit_block` over the signaling server.
- **Background daemon orchestration** – `backend/daemon.py` starts/status/stops node, miner, API and signaling as real processes, with `start_backend.bat/.sh` one-shot helpers.
- **Argon2id-encrypted wallet vault** – 24-word BIP-39 seeds, AES-256-GCM vault, seed-only recovery, auto-lock.
- **Built-in block explorer** – chain, address auditor and transaction viewer (desktop + light wallet).
- **Fast-sync UTXO snapshots** – verified snapshot generation & instant import via `contrib/fast_sync_engine.py`.
- **Merkle-delta UTXO sync** – `contrib/pqn_sync.py` compares canonical Merkle roots before transferring only changed UTXOs.
- **Super-Transport layer** – `contrib/pqn_netlib.py` unifies WebRTC/IRC-DCC/STUN/TCP/relay under one retryable ladder, optionally accelerated by libp2p/Noise.
- **DirectDrop peer-to-peer files** – 4-char transfer codes, AES-256-GCM sealed frames via `contrib/pqn_file.py`.
- **Cross-platform release pipeline** – `.github/workflows/build-all.yml` produces Windows `.exe`, Linux `.AppImage`, macOS `.dmg` and Android `.apk` on every release.
- **Quantum footprints** – `contrib/pqn_quantum/` ties each block to a true-random seed via the 8-qubit panta-sim simulator and mints a public SHA-256 footprint (`footprints.py`); `TRNGClient` falls back to OS entropy when the QRNG endpoints are unreachable.
- **3D Quantum Diamond explorer** – a Three.js WebGL gallery (`explorer_3d/`) renders one deterministic 3D diamond per block from the public footprint only; `tools/build_gallery3d.py` regenerates the public dataset from local chain headers.

---

## 🏛️ Ecosystem Architecture

```mermaid
graph TD
    A[PayQuant P2P Node] --> B{Transport Layer 1: WebRTC DataChannels}
    B -- Success --> C[High-Speed WebRTC P2P Stream]
    B -- Fallback --> D{Layer 2: IRC DCC SEND / RESUME}
    D -- Success --> E[Direct DCC P2P File Link]
    D -- Fallback --> F{Layer 3: STUN UDP Hole Punch}
    F -- Success --> G[Bilateral UDP Socket]
    F -- Fallback --> H{Layer 4: Direct TCP}
    H -- Success --> I[TK2 Standard TCP P2P Connection]
    H -- Fallback --> J[Layer 5: Encrypted IRC Base64 Relay]
```

---

## ⚡ Quick Start

### From source

```bash
# 1. Clone
git clone https://github.com/timfromhcs/payquant.git
cd payquant

# 2. Run the 9-category ecosystem test suite
python scripts/local_test_suite.py

# 3. Launch the unified desktop suite (Full Node + Solo Miner)
python contrib/node_miner_gui.py
```

### Start the backend stack (node, miner, API, signaling)

```bash
# Linux / macOS
./scripts/start_backend.sh
# Windows
scripts\start_backend.bat

# Or manual control
python backend/daemon.py start all      # start node + miner + api + signaling
python backend/daemon.py status
python backend/daemon.py stop all
```

### Mining

```bash
python contrib/miner_gui.py                 # GUI solo miner (uses saved payout addr)
python backend/daemon.py start miner       # headless miner daemon
```

### API Server (REST + JSON-RPC)

The unified API server (`backend/api_server.py`) boots in any environment
(FastAPI/uvicorn when installed, pure-stdlib fallback otherwise) and exposes:

| Endpoint | Port | Purpose |
| --- | --- | --- |
| `GET /api/status` | `28377` | Real node height, balance, peers, hashrate, sync state |
| `GET /api/balance` | `28377` | Wallet balance |
| `GET /api/transactions` | `28377` | Wallet transaction history |
| `GET /api/mining/status` | `28377` | Live miner hashrate + active state |
| `GET /api/health` | `28377` | Liveness probe (daemon/scripts) |
| `WS /ws/events` | `28377` | Live status push stream |
| `POST /` (JSON-RPC) | `28332` | `getblockchaininfo`, `getbalance`, `listtransactions`, `gettransaction`, `getblockcount`, `getmininginfo` — consumed by the Electron light wallet |

```bash
python backend/api_server.py                # starts both :28377 (REST/WS) and :28332 (JSON-RPC)
```

---

## 🔮 Quantum Footprint Live

Every PayQuant block is tied to a **true-random seed** captured at mint time.

```bash
# OPTIONAL deps for the 8-qubit simulator + luminance helpers
pip install numpy panta-sim requests
```

- **Sources** — Cisco (Outshift) QRNG REST or ANU QRNG (desktop-only keys in
  `.env`, see `.env.example`). No key = OS `os.urandom` fallback, so mining works
  offline everywhere.
- **Simulation** — the seed drives an 8-qubit quantum circuit (panta-sim when
  installed, pure-Python fallback otherwise).
- **Footprint** — `SHA-256(prev_hash | outcome | miner | seed)` produces the
  public 64-hex fingerprint `contrib/pqn_quantum/footprints.py`;
  `quantum_tools.py` prints the interpretable qubit schedule.
- **3D signature** — each footprint becomes a unique diamond-like crystal
  (facet geometry, lighting & color palette) in `contrib/pqn_quantum/diamond.py`;
  explore every block in `explorer_3d/` (see `docs/explorer-3d.md`).

> **Secure by default:** the seed is generated once, stored only on the signer,
> and never leaves the desktop. Diamonds are reproducible from public headers
> alone — no key in the repo, no seed in git.

---

## 🧬 Chain Start & Mainnet Genesis

The PayQuant mainnet was launched with a **TRNG-minted genesis block** — the
only block whose hash is a direct quantum footprint (no previous hash). The
seed was generated on the desktop of the chain creator and has never been
committed to the repository; only public constants ship in code.

| Chain-start constant | Value |
| --- | --- |
| **Genesis hash** | `c01d52bda35800c5d4f88d35f23529032fa8261938dfb300ea8b5c19218cc031` |
| **Merkle root** | `f48783d9e4a05e0a6856d2adac4415d12fcf73c42df72835c37aae537fb791c3` |
| **Timestamp** | `1786283877` (UTC) |
| **Backend** | `panta_sim` · 8-qubit · outcome `00000011` |
| **Coinbase** | `50.00000000 PQN` → `pqn1qgenesisspendenwallettreasury20252026` |

The exact public record is reproduced by `contrib/chain_db.py` (`GENESIS_BLOCK`)
and rendered as the height-0 diamond in the 3D gallery. Nodes varify every
subsequent block against this chain start — no trust required, only
deterministic geometry and the public SHA-256 footprint.

---

## 🧪 Testing & Validation Gate

```bash
python scripts/local_test_suite.py          # 13 categories, MUST pass 100% clean
python scripts/test_loop.py                 # self-healing loop → DEPLOY READY
python tools/check_secrets.py               # secret gate (no keys/seeds in tree)
python contrib/build_local_executables.py   # rebuild local standalone binaries
cd wallet && npm run build:web              # wallet web/Android bundle
```

All commit/push-request PRs must pass the full suite.

---

## 📦 Releases

| Platform | Package |
|---|---|
| **Windows x64** | `PayQuant-Node-Miner-Suite-Setup.exe`, `PayQuant-Wallet-Setup.exe`, `PayQuant-Explorer-Setup.exe` |
| **Linux x64** | `PayQuant-Node-Miner-Linux.AppImage`, `payquantd` headless daemon |
| **macOS Universal** | `PayQuant-Ecosystem-macOS.dmg` |
| **Android** | `PayQuant-Wallet-arm64-v8a.apk` |

Every Tag `v*` triggers the full cross-platform build & release pipeline automatically.

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more details.