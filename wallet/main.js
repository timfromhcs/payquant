const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');

const RPC_DEFAULTS = {
  host: '127.0.0.1',
  port: 28332,
  user: 'payquantuser',
  pass: 'payquantpass'
};

let settingsFile = path.join(app.getPath('userData'), 'payquant-ux.json');
let settings = { ...RPC_DEFAULTS };

function loadSettings() {
  try {
    if (fs.existsSync(settingsFile)) {
      const s = JSON.parse(fs.readFileSync(settingsFile, 'utf-8'));
      settings = { ...RPC_DEFAULTS, ...s };
    }
  } catch (e) {
    console.warn('[PayQuant Wallet] Could not load settings:', e.message);
  }
}

function saveSettings(next) {
  settings = { ...RPC_DEFAULTS, ...next };
  try {
    fs.writeFileSync(settingsFile, JSON.stringify(settings, null, 2), 'utf-8');
  } catch (e) {
    console.warn('[PayQuant Wallet] Could not save settings:', e.message);
  }
}

function callRpc(method, params = []) {
  return new Promise((resolve) => {
    const payload = JSON.stringify({
      jsonrpc: '1.0',
      id: 'payquant-wallet',
      method,
      params
    });
    const auth = 'Basic ' + Buffer.from(`${settings.user}:${settings.pass}`).toString('base64');
    const req = http.request({
      host: settings.host,
      port: settings.port,
      path: '/wallet/' + encodeURIComponent(settings.wallet || ''),
      method: 'POST',
      headers: {
        'Authorization': auth,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      },
      timeout: 10000
    }, (res) => {
      let body = '';
      res.on('data', (c) => (body += c));
      res.on('end', () => {
        try {
          const j = JSON.parse(body);
          if (j.error) return resolve({ ok: false, error: j.error.message || String(j.error) });
          resolve({ ok: true, result: j.result });
        } catch (e) {
          resolve({ ok: false, error: 'Invalid RPC response: ' + body.slice(0, 120) });
        }
      });
    });
    req.on('timeout', () => {
      req.destroy();
      resolve({ ok: false, error: 'RPC timeout - is the PayQuant node running?' });
    });
    req.on('error', (e) => resolve({ ok: false, error: `Cannot reach node RPC on ${settings.host}:${settings.port}. Start the node first. (${e.code || e.message})` }));
    req.write(payload);
    req.end();
  });
}

const MasterPasswordAuth = require('./backend/auth.js');
const SyncService = require('./backend/sync_service.js');
const BlockExplorer = require('./backend/explorer.js');

const LightWalletManager = require('./src/light_wallet');

function createWindow() {
  const win = new BrowserWindow({
    width: 1080,
    height: 760,
    minWidth: 860,
    minHeight: 620,
    backgroundColor: '#060814',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });
  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
  return win;
}

app.whenReady().then(() => {
  loadSettings();

  const auth = new MasterPasswordAuth(app.getPath('userData'));
  const sync = new SyncService({ callRpc });
  const explorer = new BlockExplorer({ callRpc });
  let lightWallet = null;
  if (!lightWallet) lightWallet = new LightWalletManager(app.getPath('userData'));

  /* ---------- Seed & password (FS-01-01 / FS-01-02) ---------- */
  ipcMain.handle('auth:hasWallet', () => ({ hasWallet: auth.hasWallet(), unlocked: auth.isUnlocked() }));
  ipcMain.handle('auth:generateSeed', () => auth.generateSeed());
  ipcMain.handle('auth:setup', async (_e, { mnemonic, password }) => {
    try { return await auth.setup({ mnemonic, password }); }
    catch (e) { return { ok: false, error: e.message }; }
  });
  ipcMain.handle('auth:unlock', async (_e, password) => {
    try { return { ok: true, ...(await auth.unlock(password)) }; }
    catch (e) { return { ok: false, error: e.message }; }
  });
  ipcMain.handle('auth:recover', async (_e, { mnemonic, password }) => {
    try { return { ok: true, ...(await auth.recover({ mnemonic, password })) }; }
    catch (e) { return { ok: false, error: e.message }; }
  });
  ipcMain.handle('auth:changePassword', async (_e, oldPw, newPw) => {
    try { await auth.changePassword(oldPw, newPw); return { ok: true }; }
    catch (e) { return { ok: false, error: e.message }; }
  });
  ipcMain.handle('auth:lock', () => { auth.lock(); return { ok: true }; });
  ipcMain.handle('auth:isLocked', () => ({ locked: !auth.isUnlocked() }));

  /* ---------- RPC / settings ---------- */
  ipcMain.handle('rpc:call', async (_e, method, params) => callRpc(method, params || []));
  ipcMain.handle('settings:get', () => ({ ...settings }));
  ipcMain.handle('settings:save', (_e, next) => {
    saveSettings(next);
    return { ...settings };
  });

  /* ---------- Light wallet ---------- */
  ipcMain.handle('light:sync', async () => await lightWallet.syncLightWallet());
  ipcMain.handle('light:send', async (_e, to, amt) => await lightWallet.sendTransactionP2P(to, amt));
  ipcMain.handle('light:getaddress', () => lightWallet.generateNewAddress());
  ipcMain.handle('light:getbalance', () => ({ balance: lightWallet.walletData.balance }));
  ipcMain.handle('light:listtransactions', () => ({ transactions: lightWallet.walletData.transactions }));
  ipcMain.handle('light:gettransaction', async (_e, txid) => {
    const tx = (lightWallet.walletData.transactions || []).find((t) => t.txid === txid);
    return tx || { error: 'tx not found' };
  });

  /* ---------- Live sync + explorer (FS-01-03 / FS-01-05) ---------- */
  sync.onUpdate((payload) => {
    for (const w of BrowserWindow.getAllWindows()) {
      w.webContents.send('sync:update', payload);
    }
  });
  ipcMain.handle('sync:poll', () => sync.poll());
  sync.start();

  ipcMain.handle('explorer:blockcount', () => explorer.getBlockCount());
  ipcMain.handle('explorer:blockhash', (_e, h) => explorer.getBlockHash(h));
  ipcMain.handle('explorer:block', (_e, h) => explorer.getBlock(h));
  ipcMain.handle('explorer:blocktxs', (_e, h) => explorer.getBlockTxs(h));
  ipcMain.handle('explorer:tx', (_e, txid) => explorer.getTransaction(txid));

  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});