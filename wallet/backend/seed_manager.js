/**
 * PayQuant (PQN) Encrypted Seed Manager v3.3.0
 *
 * Responsibilities:
 *  1. Standards-compliant BIP-39 24-word seed generation (full 2048-word list + checksum validation)
 *  2. Local encrypted vault storage (AES-256-GCM) whose key is derived from the master password
 *     via Argon2id (memory-hard KDF). Never stores the seed in plaintext.
 *  3. Password unlock + seed-only recovery (no password reset path - recovery is seed-only).
 *
 * Security notes:
 *   - The seed is never written to localStorage or to disk in plaintext.
 *   - A dedicated Argon2id hash of the master password is persisted for password verification.
 *   - If the native `argon2` module is unavailable the implementation degrades to
 *     Node built-in scrypt (same role: memory-hard KDF) so the app never crashes.
 */
'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

let argon2 = null;
try { argon2 = require('argon2'); } catch { /* optional native dep */ }

const WORDLIST = require('../renderer/bip39_wordlist.js');

/* ------------------------------------------------------------------ */
/*  BIP-39 primitives                                                  */
/* ------------------------------------------------------------------ */

const VALID_WORD_COUNTS = [12, 15, 18, 21, 24];

function csBitsFor(entropy) {
  const checksum = crypto.createHash('sha256').update(entropy).digest();
  const count = (entropy.length * 8) / 32;
  const bits = [];
  for (let i = 0; i < count; i++) bits.push((checksum[Math.floor(i / 8)] >> (7 - (i % 8))) & 1);
  return bits;
}

function bufToBits(buf) {
  const bits = [];
  for (const b of buf) for (let i = 7; i >= 0; i--) bits.push((b >> i) & 1);
  return bits;
}

function bitsToBuf(bits) {
  const bytes = [];
  for (let i = 0; i < bits.length; i += 8) {
    let v = 0;
    for (let j = 0; j < 8; j++) v = (v << 1) | (bits[i + j] || 0);
    bytes.push(v);
  }
  return Buffer.from(bytes);
}

function entropyForWords(wordCount) {
  if (VALID_WORD_COUNTS.indexOf(wordCount) === -1) wordCount = 24;
  const entropyBits = (wordCount * 11 * 32) / 33;  // e.g. 24 words -> 256 entropy bits
  return crypto.randomBytes(Math.round(entropyBits / 8));
}

function entropyToMnemonic(entropy) {
  const bits = bufToBits(entropy).concat(csBitsFor(entropy));
  const words = [];
  for (let i = 0; i < bits.length; i += 11) {
    let idx = 0;
    for (let j = 0; j < 11; j++) idx = (idx << 1) | (bits[i + j] || 0);
    words.push(WORDS[idx]);
  }
  return words.join(' ');
}

function indexOfWord(word) {
  for (let i = 0; i < WORDLIST.length; i++) if (WORDLIST[i] === word) return i;
  return -1;
}

function generateMnemonic(wordCount = 24) {
  return entropyToMnemonic(entropyForWords(wordCount));
}

function validateMnemonic(mnemonic) {
  if (typeof mnemonic !== 'string') return { ok: false, reason: 'not_a_string' };
  const parts = mnemonic.trim().split(/\s+/);
  if (VALID_WORD_COUNTS.indexOf(parts.length) === -1) {
    return { ok: false, reason: 'unexpected word count (' + parts.length + '); expected 24' };
  }
  const indices = [];
  for (const w of parts) {
    const idx = indexOfWord(w);
    if (idx === -1) return { ok: false, reason: 'word not in BIP-39 list: ' + w };
    indices.push(idx);
  }
  const csLen = parts.length / 3;   // 24 words -> 8 checksum bits
  const bits = [];
  for (const idx of indices) for (let i = 10; i >= 0; i--) bits.push((idx >> i) & 1);
  const entropyBits = bits.slice(0, bits.length - csLen);
  const csBitsActual = bits.slice(bits.length - csLen);
  const entropy = bitsToBuf(entropyBits);
  const csExpected = csBitsFor(entropy);
  for (let i = 0; i < csLen; i++) {
    if (csBitsActual[i] !== csExpected[i]) return { ok: false, reason: 'checksum_failed' };
  }
  return { ok: true, wordCount: parts.length };
}

/* ------------------------------------------------------------------ */
/*  Password KDF helpers                                               */
/* ------------------------------------------------------------------ */

const ARGON2_MEM = 64 * 1024;

function argon2Available() { return argon2 !== null; }

/* Argon2id raw output (32-byte key) or scrypt fallback */
async function deriveKey(password, salt, length = 32) {
  if (!length) length = 32;
  const pass = Buffer.isBuffer(password) ? password : Buffer.from(String(password));
  if (argon2) {
    const raw = await argon2.hash(pass, {
      type: argon2.argon2id,
      salt,
      saltLength: 16,
      raw: true,
      length,
      memoryCost: ARGON2_MEM,
      timeCost: 3,
      parallelism: 1
    });
    return Buffer.from(raw);
  }
  return crypto.scryptSync(pass, salt, length, { N: 1 << 17, r: 8, p: 1 });
}

async function hashPassword(password, salt) {
  const pass = Buffer.from(String(password));
  if (argon2) {
    return argon2.hash(pass, {
      type: argon2.argon2id,
      salt,
      saltLength: 16,
      memoryCost: ARGON2_MEM,
      timeCost: 3,
      parallelism: 1
    });
  }
  return fallbackPasswordHash(password, salt);
}

async function fallbackPasswordHash(password, salt) {
  const key = crypto.scryptSync(Buffer.from(String(password)), salt, 32, { N: 1 << 17, r: 8, p: 1 });
  return '$argon2n-fallback$v=19$' + salt.toString('base64') + '$' + key.toString('base64');
}

async function fallbackPasswordVerify(hashStr, password) {
  const parts = hashStr.split('$');
  if (parts.length !== 4) return false;
  try {
    const salt = Buffer.from(parts[2], 'base64');
    const expected = Buffer.from(parts[3], 'base64');
    const key = crypto.scryptSync(Buffer.from(String(password)), salt, 32, { N: 1 << 17, r: 8, p: 1 });
    return key.length === expected.length && crypto.timingSafeEqual(key, expected);
  } catch { return false; }
}

async function verifyPasswordHash(hashStr, password) {
  if (!hashStr) return false;
  if (hashStr.indexOf('$argon2id$') === 0 && argon2) {
    try { return await argon2.verify(hashStr, String(password)); } catch { return false; }
  }
  if (hashStr.indexOf('$argon2n-fallback$') === 0) return fallbackPasswordVerify(hashStr, password);
  return false;
}

/* ------------------------------------------------------------------ */
/*  Encrypted vault                                                    */
/* ------------------------------------------------------------------ */

const VAULT_VERSION = 1;

class SeedVault {
  constructor(vaultPath) {
    this.vaultPath = vaultPath;
  }

  vaultExists() {
    return !!(this.vaultPath && fs.existsSync(this.vaultPath));
  }

  loadVault() {
    if (!this.vaultExists()) return null;
    try { return JSON.parse(fs.readFileSync(this.vaultPath, 'utf-8')); } catch { return null; }
  }

  /** Create a brand-new encrypted vault from a validated seed + master password. */
  async initialize({ mnemonic, password }) {
    const valid = validateMnemonic(mnemonic);
    if (!valid.ok) throw new Error('Seed phrase failed validation: ' + valid.reason);

    const salt = crypto.randomBytes(16);
    const iv = crypto.randomBytes(12);
    const key = await deriveKey(password, salt);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    const enc = Buffer.concat([cipher.update(Buffer.from(mnemonic, 'utf-8')), cipher.final()]);
    const tag = cipher.getAuthTag();
    const authHash = await hashPassword(password, salt);

    const vault = {
      version: VAULT_VERSION,
      kdf: argon2 ? 'argon2id' : 'scrypt-fallback',
      authHash,
      salt: salt.toString('base64'),
      iv: iv.toString('base64'),
      tag: tag.toString('base64'),
      data: enc.toString('base64')
    };
    this._writeVault(vault);
    return { mnemonic, passwordVerified: true };
  }

  _writeVault(vault) {
    const dir = path.dirname(this.vaultPath);
    if (dir) fs.mkdirSync(dir, { recursive: true });
    // 0600 on POSIX; best-effort on Windows
    fs.writeFileSync(this.vaultPath, JSON.stringify(vault, null, 2), { encoding: 'utf-8', mode: 0o600 });
  }

  /** Unlock: verify password against stored Argon2id hash, then derive key & decrypt seed. */
  async unlock(password) {
    const vault = this.loadVault();
    if (!vault) throw new Error('No wallet vault found - initialize a wallet first.');
    const salt = Buffer.from(vault.salt, 'base64');
    const passwordOk = await verifyPasswordHash(vault.authHash || '', password);
    if (!passwordOk) throw new Error('Incorrect master password.');
    const key = await deriveKey(password, salt);
    return this._decrypt(vault, key);
  }

  _decrypt(vault, key) {
    const iv = Buffer.from(vault.iv, 'base64');
    const tag = Buffer.from(vault.tag, 'base64');
    const data = Buffer.from(vault.data, 'base64');
    const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAuthTag(tag);
    return Buffer.concat([decipher.update(data), decipher.final()]).toString('utf-8');
  }

  /** Recovery is seed-only: overwrite vault with a fresh one built from a validated seed. */
  async recoverFromSeed(mnemonic, newPassword) {
    return this.initialize({ mnemonic, password: newPassword });
  }

  hasWallet() {
    return this.vaultExists();
  }
}

const WORDS = WORDLIST;

module.exports = {
  generateMnemonic,
  validateMnemonic,
  entropyToMnemonic,
  SeedVault,
  deriveKey,
  hashPassword,
  verifyPasswordHash,
  argon2Available
};