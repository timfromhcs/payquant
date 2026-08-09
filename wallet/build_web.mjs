import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '.');
const www = path.join(root, 'www');

fs.rmSync(www, { recursive: true, force: true });
fs.mkdirSync(www, { recursive: true });

for (const f of ['index.html', 'renderer.js', 'style.css', 'bip39_wordlist.js']) {
  const src = path.join(root, 'renderer', f);
  fs.copyFileSync(src, path.join(www, f));
}

const renderer = String(fs.readFileSync(path.join(www, 'renderer.js'), 'utf-8'));
const webAgnostic = renderer
  .replace(/window\.payquant\.rpc\(/g, 'window.__rpc__(')
  .replace(/window\.payquant\.getSettings\(/g, 'window.__getSettings__(')
  .replace(/window\.payquant\.saveSettings\(/g, 'window.__saveSettings__(');
fs.writeFileSync(path.join(www, 'renderer.js'), webAgnostic, 'utf-8');

const bridge = `// PayQuant Wallet - cross-platform RPC bridge (browser/Capacitor fallback)
window.__rpc__ = async (method, params) => {
  const settings = await window.__getSettings__();
  const enc = btoa(settings.user + ':' + settings.pass);
  try {
    const res = await fetch('http://' + settings.host + ':' + settings.port + '/wallet/' + (settings.wallet || ''), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Basic ' + enc },
      body: JSON.stringify({ jsonrpc: '1.0', id: 'pw-web', method, params })
    });
    const j = await res.json();
    if (j.error) return { ok: false, error: j.error.message || String(j.error) };
    return { ok: true, result: j.result };
  } catch (e) {
    return { ok: false, error: 'RPC error: ' + e.message };
  }
};
window.__getSettings__ = async () => {
  try {
    const s = localStorage.getItem('payquant-wallet-settings');
    return s ? JSON.parse(s) : { host: '127.0.0.1', port: '28332', user: 'payquantuser', pass: 'payquantpass' };
  } catch { return { host: '127.0.0.1', port: '28332', user: 'payquantuser', pass: 'payquantpass' }; }
};
window.__saveSettings__ = async (s) => { localStorage.setItem('payquant-wallet-settings', JSON.stringify(s)); };
if (!window.payquant) {
  window.payquant = {
    rpc: (m, p) => window.__rpc__(m, p),
    getSettings: () => window.__getSettings__(),
    saveSettings: (s) => window.__saveSettings__(s),
    lightSync: async () => {
      const saved = localStorage.getItem('pqn-light-address') || 'pqn1q' + Math.random().toString(36).slice(2, 12);
      localStorage.setItem('pqn-light-address', saved);
      return { online: true, address: saved, balance: 50.0, lastHeight: 1, headersCount: 1, transactions: [] };
    },
    lightSend: async (to, amt) => ({ ok: true, txid: 'tx_web_' + Math.random().toString(36).slice(2, 12) }),
    lightGetAddress: async () => {
      const addr = 'pqn1q' + Math.random().toString(36).slice(2, 12);
      localStorage.setItem('pqn-light-address', addr);
      return addr;
    },
    lightGetBalance: async () => ({ balance: 50.0 }),
    lightList: async () => ({ transactions: [] }),
    lightGetTx: async () => ({ error: 'web fallback has no local tx store' }),
    hasHasWallet: async () => ({ hasWallet: false, unlocked: true }),
    authState: async () => ({ hasWallet: false, unlocked: true }),
    authGenerateSeed: async () => 'abandon ability able about above absent absorb abstract absurd abuse access accident adult advance advice aerobic afford afraid again age agent agree ahead aim',
    authSetup: async () => ({ ok: true, mnemonic: 'demo-session' }),
    authUnlock: async () => ({ ok: true, mnemonic: 'demo-session', seedWords: ['demo'] }),
    authRecover: async () => ({ ok: true, mnemonic: 'demo-session', seedWords: ['demo'] }),
    authChangePassword: async () => ({ ok: true }),
    authLock: async () => ({ ok: true }),
    syncPoll: async () => ({ ok: false, online: false, source: 'web', balance: 50.0, transactions: [] }),
    onSync: () => {},
    explorerBlockcount: async () => 1,
    explorerBlockhash: async () => '000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d0f5f4bb1c6626d818',
    explorerBlock: async () => ({ height: 1, hash: '000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d8f5f4bb5c6626d818', timestamp: 0, txes: [] }),
    explorerBlocktxs: async () => [],
    explorerTx: async () => ({ txid: 'n/a' })
  };
}
`;

const wwwIndex = String(fs.readFileSync(path.join(www, 'index.html'), 'utf-8'));
const withBridge = wwwIndex.replace(
  '<script src="renderer.js"></script>',
  '<script>' + bridge + '</script>\n  <script src="renderer.js"></script>'
);
fs.writeFileSync(path.join(www, 'index.html'), withBridge, 'utf-8');

console.log('[build:web] Web/Android bundle written to www/');