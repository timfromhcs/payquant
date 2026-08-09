/**
 * PayQuant (PQN) Authentication & Session Manager v3.3.0
 *
 * Replaces the Passkey-only authentication with a mandatory Argon2id-hashed
 * master password.
 *
 *  - Password unlocks the encrypted seed (see seed_manager.js SeedVault).
 *  - Password hash uses Argon2id (memory-hard KDF).
 *  - Recovery ONLY via the 24-word seed - there is no password reset path.
 *  - Keeps an in-memory session (never persisted) so a locked app is truly locked.
 */
'use strict';

const path = require('node:path');
const fs = require('node:fs');
const { SeedVault, generateMnemonic, validateMnemonic } = require('./seed_manager.js');

const SESSION_TIMEOUT_MS = 10 * 60 * 1000; // auto-lock after 10 minutes idle

class MasterPasswordAuth {
  constructor(userDataPath) {
    const dir = path.join(userDataPath || process.cwd(), 'vault');
    fs.mkdirSync(dir, { recursive: true });
    this.vault = new SeedVault(path.join(dir, 'wallet.vault'));
    this.session = null; // { seed, address, unlockedAt }
    this.onLock = null;
  }

  hasWallet() {
    return this.vault.hasWallet();
  }

  /** True when a password (and vault) exists. In-memory only. */
  isUnlocked() {
    if (!this.session) return false;
    const now = Date.now();
    if (now - this.session.unlockedAt > SESSION_TIMEOUT_MS) { this._lock(); return false; }
    return true;
  }

  // Generate a fresh 24-word seed and optionally create the encrypted vault + password.
  async generateSeed() {
    return generateMnemonic(24);
  }

  /**
   * First-time setup: store an Argon2id password hash in the vault and encrypt the seed.
   * @returns {Promise<{mnemonic: string, passwordVerified: boolean, seedWords: string[]}>}
   */
  async setup({ mnemonic, password }) {
    if (!password || String(password).length < 8) {
      throw new Error('Master password must be at least 8 characters.');
    }
    const result = await this.vault.initialize({ mnemonic, password });
    this.session = {
      seed: result.mnemonic,
      unlockedAt: Date.now()
    };
    return { ok: true, mnemonic: result.mnemonic, seedWords: result.mnemonic.split(' ') };
  }

  /** Unlock with the master password -> decrypt seed into memory session. */
  async unlock(password) {
    const seed = await this.vault.unlock(password);
    this.session = { seed, unlockedAt: Date.now() };
    return { mnemonic: seed, seedWords: seed.split(' ') };
  }

  /** Seed-only recovery: re-create vault from a validated seed + new password. */
  async recover({ mnemonic, password }) {
    if (!validateMnemonic(mnemonic).ok) throw new Error('Seed phrase failed validation.');
    if (String(password).length < 8) throw new Error('Master password must be at least 8 characters.');
    await this.vault.recoverFromSeed(mnemonic, password);
    this.session = { seed: mnemonic, unlockedAt: Date.now() };
    return { mnemonic, seedWords: mnemonic.split(' ') };
  }

  /** Change the master password (requires current password). */
  async changePassword(oldPassword, newPassword) {
    if (String(newPassword).length < 8) throw new Error('New master password must be at least 8 characters.');
    const seed = await this.vault.unlock(oldPassword); // throws if wrong
    // Re-encrypt the same seed under the new password by rebuilding the vault.
    await this.vault.initialize({ mnemonic: seed, password: newPassword });
    this.session = { seed, unlockedAt: Date.now() };
    return true;
  }

  verifySeedWords(words) {
    return validateMnemonic(Array.isArray(words) ? words.join(' ') : words).ok;
  }

  lock() { this._lock(); }

  _lock() {
    if (this.session) { this.session = null; if (typeof this.onLock === 'function') try { this.onLock(); } catch {} }
  }
}

module.exports = MasterPasswordAuth;