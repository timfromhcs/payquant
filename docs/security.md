# 🛡️ PayQuant (PQN) Post-Quantum Cryptography & Security Whitepaper

PayQuant (PQN) is engineered to remain 100% secure against future quantum computers capable of executing Shor's algorithm.

---

## 🔐 1. NIST FIPS 204 ML-DSA-65 Digital Signatures

- **Lattice Cryptography**: PayQuant utilizes ML-DSA-65 (Dilithium), a lattice-based post-quantum signature scheme standardized by NIST in FIPS 204.
- **Key Specifications**:
  - Public Key Size: ~1,312 Bytes
  - Signature Size: ~2,420 Bytes
  - Private Seed: 32 Bytes (256-bit CSPRNG entropy)
- **Quantum Immune**: Unlike classical secp256k1 (Bitcoin/Ethereum) or RSA signatures, ML-DSA-65 cannot be broken by Shor's quantum factoring algorithm.

---

## 🔑 2. 24-Word BIP-39 Quantum Backup Seedphrase

- **High Entropy**: Every PayQuant wallet generates a 24-word seedphrase providing 256 bits of cryptographic entropy.
- **1-Click Restoration**: Allows users to recover public keypairs, private keys, and transaction history seamlessly on any device.

---

## 🛡️ 3. Anti-Attack Security Hardening

- **Block Structure Integrity Gate**: Every incoming block must pass PoW target verification (`0000...`), height sequence sanity, and ML-DSA-65 signature checks before writing to persistent storage.
- **Reorg Depth Limit**: Enforces a strict 100-block reorg limit to protect nodes from long-range fork attacks.
- **IRC Anti-Flooding & Peer Trust Scoring**: Rate-limits discovery signals to prevent Eclipse attacks and Sybil flooding.
