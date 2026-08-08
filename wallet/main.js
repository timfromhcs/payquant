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

let settingsFile = path.join(app.getPath('userData'), 'payquant-wallet-settings.json');
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
}

const LightWalletManager = require('./src/light_wallet');
let lightWallet = null;

ipcMain.handle('rpc:call', async (_e, method, params) => callRpc(method, params || []));
ipcMain.handle('settings:get', () => ({ ...settings }));
ipcMain.handle('settings:save', (_e, next) => {
  saveSettings(next);
  return { ...settings };
});
ipcMain.handle('light:sync', async () => {
  if (!lightWallet) lightWallet = new LightWalletManager(app.getPath('userData'));
  return await lightWallet.syncLightWallet();
});
ipcMain.handle('light:send', async (_e, to, amt) => {
  if (!lightWallet) lightWallet = new LightWalletManager(app.getPath('userData'));
  return await lightWallet.sendTransactionP2P(to, amt);
});
ipcMain.handle('light:getaddress', () => {
  if (!lightWallet) lightWallet = new LightWalletManager(app.getPath('userData'));
  return lightWallet.generateNewAddress();
});

app.whenReady().then(() => {
  loadSettings();
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});