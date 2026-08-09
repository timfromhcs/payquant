'use strict';

/**
 * PayAll (PQN) LIVE Node/Blockchain Sync Service v3.3.0
 *
 * FS-01-03: Live balance synchronization with the node backend.
 *   - REST/HTTP (JSON-RPC) polling against the local payquantd node
 *   - getbalance + listtransactions + gettransaction (confirmation counts)
 *   - Lightweight P2P fallback when RPC is unreachable (redeems via contrib node)
 *   - Push-style event delivery for the renderer (subscribe via onUpdate).
 */
'use strict';

const net = require('node:net');
const http = require('node:http');

class SyncService {
  /**
   * @param {object} opts
   * @param {function(method, params):Promise<{ok:boolean,result?:any}>} [opts.callRpc]
   * @param {number} [opts.pollInterval] ms
   */
  constructor(opts = {}) {
    this.opts = opts;
    this.callRpc = opts.callRpc || null;
    this.rpcHost = opts.rpcHost || '127.0.0.1';
    this.rpcPort = opts.rpcPort || 28332;
    this.rpcUser = opts.rpcUser || 'payquantuser';
    this.rpcPass = opts.rpcPass || 'payquantpass';
    this.rpcWallet = opts.rpcWallet || '';
    this.pollInterval = opts.pollInterval || 5000;
    this.p2pPort = opts.p2pPort || 28333;
    this._timer = null;
    this._stopped = false;
    this.listeners = [];
    this.last = null;
  }

  onUpdate(fn) { this.listeners.push(fn); }

  _broadcast(payload) {
    this.last = payload;
    for (const fn of this.listeners) { try { fn(payload); } catch {} }
  }

  /* Direct JSON-RPC against the local node (used when no injected callRpc). */
  _rpcDefault(method, params) {
    return new Promise((resolve) => {
      const body = JSON.stringify({ jsonrpc: '1.0', id: 'pqn-sync', method, params: params || [] });
      const auth = 'Basic ' + Buffer.from(`${this.rpcUser}:${this.rpcPass}`).toString('base64');
      const req = http.request({
        host: this.rpcHost,
        port: this.rpcPort,
        path: '/wallet/' + encodeURIComponent(this.rpcWallet || ''),
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: auth },
        timeout: 8000
      }, (res) => {
        let b = '';
        res.on('data', (c) => (b += c));
        res.on('end', () => {
          try {
            const j = JSON.parse(b);
            resolve(j.error ? { ok: false, error: j.error.message || String(j.error) } : { ok: true, result: j.result });
          } catch { resolve({ ok: false, error: 'invalid_rpc_response' }); }
        });
      });
      req.on('timeout', () => { req.destroy(); resolve({ ok: false, error: 'timeout' }); });
      req.on('error', (e) => resolve({ ok: false, error: (e && e.code) || 'unreachable' }));
      req.write(body);
      req.end();
    });
  }

  async _query(method, params) {
    return this.callRpc ? this.callRpc(method, params || []) : this._rpcDefault(method, params);
  }

  async _safeQuery(method, params) {
    try { return await this._query(method, params); } catch { return { ok: false }; }
  }

  /** One full sync pass. */
  async poll() {
    const out = {
      ok: false,
      online: false,
      syncState: 'offline',
      source: 'rpc',
      balance: 0,
      unconfirmed: 0,
      height: 0,
      headers: 0,
      transactions: []
    };

    if (this.callRpc) {
      const chain = await this._safeQuery('getblockchaininfo', []);
      if (chain.ok) {
        const bal = await this._safeQuery('getbalance', ['*', 0]);
        const txsRaw = await this._safeQuery('listtransactions', ['*', 50]);
        let txs = [];
        if (txsRaw.ok && Array.isArray(txsRaw.result)) txs = await this._decorate(txsRaw.result);

        out.balance = bal.ok ? Number(bal.result) : 0;
        out.transactions = txs;
        out.height = (chain.result && chain.result.blocks) || 0;
        out.headers = (chain.result && chain.result.headers) || out.height;
        out.online = true;
        out.sync = out.height > 0 && out.headers >= out.height ? 'synced' : 'syncing';
        out.syncState = out.sync;
        out.ok = true;
        this._broadcast(out);
        return out;
      }
      out.error = 'node_rpc_unreachable';
    }

    // P2P light-wallet fallback
    try {
      const res = await this._queryP2P({ type: 'get_headers', from_height: 0 });
      if (res.status === 'ok') {
        out.source = 'p2p';
        out.online = true;
        out.height = res.last_height || (res.headers || []).length;
        out.headers = res.last_height || out.height;
        const utxo = await this._queryP2P({ type: 'get_utxos', address: (this.opts.address || '') });
        if (utxo.status === 'ok') {
          out.balance = (utxo.utxos || []).reduce((s, u) => s + (typeof u.amount === 'number' ? u.amount : 0), 0);
        }
        const txs = await this._queryP2P({ type: 'get_txs' });
        out.transactions = Array.isArray(txs.txs) ? txs.txs : [];
        out.sync = out.height > 0 ? 'synced' : 'syncing';
        out.syncState = out.sync;
        out.ok = true;
      }
    } catch {}

    this._broadcast(out);
    return out;
  }

  async _decorate(txs) {
    const out = [];
    for (const t of txs) {
      let confirmations = typeof t.confirmations === 'number' ? t.confirmations : 1;
      if (!t.txid) { out.push(t); continue; }
      const detail = await this._safeQuery('gettransaction', [t.txid]);
      if (detail.ok && typeof detail.result.confirmations === 'number') confirmations = detail.result.confirmations;
      out.push({ ...t, confirmations, date: t.time || Date.now() / 1000, amount: t.amount || 0 });
    }
    return out;
  }

  _queryP2P(payload) {
    return new Promise((resolve) => {
      const s = new net.Socket();
      let buf = '';
      const timer = setTimeout(() => { s.destroy(); resolve({ status: 'error', error: 'timeout' }); }, 5000);
      s.connect(this.p2pPort, '127.0.0.1', () => s.write(JSON.stringify(payload)));
      s.on('data', (c) => (buf += c.toString()));
      s.on('end', () => { clearTimeout(timer); try { resolve(JSON.parse(buf)); } catch { resolve({ status: 'error', error: 'bad_payload' }); } });
      s.on('error', (e) => { clearTimeout(timer); resolve({ status: 'error', error: (e && e.message) || 'connect' }); });
    });
  }

  start() {
    if (this._timer) return;
    this._stopped = false;
    const run = async () => { if (this._stopped) return; await this._safePoll(); };
    run();
    this._timer = setInterval(run, this.pollInterval);
    if (this._timer.unref) this._timer.unref();
  }

  stop() { this._stopped = true; if (this._timer) clearInterval(this._timer); this._timer = null; }

  async _safePoll() { try { await this.poll(); } catch {} }

  getLast() { return this.last; }
}

module.exports = SyncService;