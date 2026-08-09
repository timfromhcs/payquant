'use strict';

/**
 * PayAll (PQN) Block Explorer Integration v3.3.0
 *
 * FS-01-05: Integrate a block explorer into the wallet.
 *   - Wraps node RPC: getblockhash, getblock, getrawtransaction (+ getblockcount)
 *   - Decorates blocks/tx with human-readable explorer links
 *   - Works through the injected RPC caller so it runs in both Electron and web builds.
 */
'use strict';

class BlockExplorer {
  constructor({ callRpc } = {}) {
    this.callRpc = callRpc || null;
  }

  _rpc(method, params) {
    if (!this.callRpc) return Promise.reject(new Error('No RPC caller configured for explorer.'));
    return this.callRpc(method, params || []).then((r) => {
      if (r && r.ok) return r.result;
      throw new Error((r && r.error) || `${method} failed`);
    });
  }

  /** Latest block height forwarded by the node. */
  async getBlockCount() {
    return this._rpc('getblockcount', []);
  }

  /** Hash at a given height. */
  async getBlockHash(height) {
    return this._rpc('getblockhash', [height]);
  }

  /** Rich block object (transactions, merkleRoot, nonce, etc.). */
  async getBlock(heightOrHash) {
    let hash = heightOrHash;
    if (typeof heightOrHash === 'number' || /^\d+$/.test(String(heightOrHash))) {
      hash = await this.getBlockHash(heightOrHash);
    }
    const block = await this._rpc('getblock', [hash]);
    return this._decorateBlock(block, hash);
  }

  /** Raw transaction + confirmations + link. */
  async getTransaction(txid) {
    const raw = await this._rpc('getrawtransaction', [txid, true]).catch(async () => {
      return this._rpc('gettransaction', [txid]).then((r) => r.details || r);
    });
    return this._decorateTx(raw, txid);
  }

  /** All transactions inside a given block height. */
  async getBlockTxs(height) {
    const block = await this.getBlock(height);
    return block.txes;
  }

  _decorateBlock(block, hash) {
    const txes = (block.tx || []).map((t) => ({
      txid: t,
      explorerUrl: this._txUrl(t)
    }));
    return {
      height: block.height,
      hash: hash || block.hash,
      timestamp: block.time || block.mediantime || Math.floor(Date.now() / 1000),
      size: block.size,
      numTx: block.nTx || txes.length,
      nonce: block.nonce,
      bits: block.bits,
      difficulty: block.difficulty,
      previousBlockHash: block.previousBlockHash || block.previousBlockhash,
      merkleRoot: block.merkleroot,
      txes
    };
  }

  _decorateTx(tx, txid) {
    return {
      txid: txid || tx.txid,
      amount: tx.amount,
      confirmations: typeof tx.confirmations === 'number' ? tx.confirmations : (tx.confirmations || 0),
      blockHash: tx.blockhash,
      blockHeight: tx.blockheight,
      fee: tx.fee,
      size: tx.size,
      time: typeof tx.time === 'number' ? tx.time : Math.floor(Date.now() / 1000),
      vin: (tx.vin || []).length,
      vout: (tx.vout || []).length,
      explorerUrl: this._txUrl(txid || tx.txid)
    };
  }

  _txUrl(txid) {
    return `https://explorer.payquant.network/tx/${txid}`;
  }
}

module.exports = BlockExplorer;