const net = require('net');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class LightWalletManager {
  constructor(userDataPath) {
    this.storageFile = path.join(userDataPath || process.cwd(), 'payquant-light-wallet.json');
    this.peers = ['127.0.0.1'];
    this.p2pPort = 28333;
    this.walletData = {
      address: null,
      privateKey: null,
      balance: 50.0000,
      unconfirmed: 0.0000,
      headersCount: 1,
      lastHeight: 1,
      mode: 'light',
      transactions: [],
      utxos: []
    };
    this.initWallet();
  }

  initWallet() {
    try {
      if (fs.existsSync(this.storageFile)) {
        const raw = fs.readFileSync(this.storageFile, 'utf-8');
        const parsed = JSON.parse(raw);
        this.walletData = { ...this.walletData, ...parsed };
      }
    } catch (e) {
      console.warn('[Light Wallet] Storage load warning:', e.message);
    }

    if (!this.walletData.address) {
      this.generateNewAddress();
    }
    this.saveWallet();
  }

  saveWallet() {
    try {
      fs.writeFileSync(this.storageFile, JSON.stringify(this.walletData, null, 2), 'utf-8');
    } catch (e) {
      console.warn('[Light Wallet] Storage save warning:', e.message);
    }
  }

  generateNewAddress() {
    const randomBuf = crypto.randomBytes(20).toString('hex');
    this.walletData.privateKey = 'pqn_priv_' + crypto.randomBytes(32).toString('hex');
    this.walletData.address = 'pqn1q' + randomBuf;
    this.saveWallet();
    return this.walletData.address;
  }

  queryPeer(peerIp, requestPayload, timeout = 5000) {
    return new Promise((resolve) => {
      const socket = new net.Socket();
      let responseData = '';
      let timer = setTimeout(() => {
        socket.destroy();
        resolve({ status: 'error', error: 'P2P timeout' });
      }, timeout);

      socket.connect(this.p2pPort, peerIp, () => {
        socket.write(JSON.stringify(requestPayload));
      });

      socket.on('data', (data) => {
        responseData += data.toString();
      });

      socket.on('end', () => {
        clearTimeout(timer);
        try {
          const parsed = JSON.parse(responseData);
          resolve(parsed);
        } catch (e) {
          resolve({ status: 'error', error: 'Invalid P2P payload' });
        }
      });

      socket.on('error', (err) => {
        clearTimeout(timer);
        resolve({ status: 'error', error: err.message });
      });
    });
  }

  async syncLightWallet() {
    let synced = false;
    for (const peer of this.peers) {
      const res = await this.queryPeer(peer, {
        type: 'get_headers',
        from_height: 0
      });

      if (res.status === 'ok') {
        const headers = res.headers || [];
        this.walletData.lastHeight = res.last_height || headers.length;
        this.walletData.headersCount = Math.max(this.walletData.headersCount || 1, headers.length);
        synced = true;

        // Query UTXOs & balance for address
        const utxoRes = await this.queryPeer(peer, {
          type: 'get_utxos',
          address: this.walletData.address
        });

        if (utxoRes.status === 'ok' && utxoRes.utxos) {
          this.walletData.utxos = utxoRes.utxos;
          let calculatedBal = 0.0;
          utxoRes.utxos.forEach(tx => {
            if (typeof tx.amount === 'number') calculatedBal += tx.amount;
          });
          this.walletData.balance = calculatedBal;
        }

        // Pull mempool / node txs for this address so tx list & balance stay live
        const txRes = await this.queryPeer(peer, {
          type: 'get_txs',
          limit: 50
        });
        if (txRes.status === 'ok' && Array.isArray(txRes.txs)) {
          const mine = txRes.txs.filter(t => String(t.address || '') === this.walletData.address);
          for (const t of mine) {
            if (!this.walletData.transactions.some(x => x.txid === t.txid)) {
              this.walletData.transactions.unshift(t);
            }
          }
          this.walletData.transactions = this.walletData.transactions.slice(0, 60);
        }

        break;
      }
    }

    this.saveWallet();
    return {
      synced,
      online: synced,
      address: this.walletData.address,
      balance: this.walletData.balance,
      lastHeight: this.walletData.lastHeight,
      headersCount: this.walletData.headersCount,
      transactions: this.walletData.transactions
    };
  }

  async sendTransactionP2P(destination, amount) {
    const tx = {
      txid: 'tx_p2p_' + crypto.randomBytes(16).toString('hex'),
      from: this.walletData.address,
      recipient: destination,
      amount: parseFloat(amount),
      timestamp: Math.floor(Date.now() / 1000),
      signature: 'ML-DSA-65-SPV-SIGNATURE-' + crypto.randomBytes(16).toString('hex')
    };

    let sent = false;
    for (const peer of this.peers) {
      const res = await this.queryPeer(peer, {
        type: 'submit_tx',
        tx
      });
      if (res.status === 'ok') {
        sent = true;
        break;
      }
    }

    // Always record locally in Light Wallet history
    this.walletData.balance = Math.max(0, this.walletData.balance - parseFloat(amount));
    this.walletData.transactions.unshift({
      time: tx.timestamp,
      category: 'send',
      address: destination,
      amount: -parseFloat(amount),
      confirmations: 1,
      txid: tx.txid
    });

    this.saveWallet();
    return { ok: true, txid: tx.txid, broadcasted: sent };
  }
}

module.exports = LightWalletManager;
