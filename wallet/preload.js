const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('payquant', {
  rpc: (method, params = []) => ipcRenderer.invoke('rpc:call', method, params),
  getSettings: () => ipcRenderer.invoke('settings:get'),
  saveSettings: (s) => ipcRenderer.invoke('settings:save', s),
  lightSync: () => ipcRenderer.invoke('light:sync'),
  lightSend: (to, amt) => ipcRenderer.invoke('light:send', to, amt),
  lightGetAddress: () => ipcRenderer.invoke('light:getaddress'),
  lightGetBalance: () => ipcRenderer.invoke('light:getbalance'),
  lightList: () => ipcRenderer.invoke('light:listtransactions'),
  lightGetTx: (txid) => ipcRenderer.invoke('light:gettransaction', txid),

  /* --- Auth & seed vault (FS-01-01 / FS-01-02) --- */
  authState: () => ipcRenderer.invoke('auth:hasWallet'),
  hasHasWallet: () => ipcRenderer.invoke('auth:hasWallet'),
  authGenerateSeed: () => ipcRenderer.invoke('auth:generateSeed'),
  authSetup: (mnemonic, password) => ipcRenderer.invoke('auth:setup', { mnemonic, password }),
  authUnlock: (password) => ipcRenderer.invoke('auth:unlock', password),
  authRecover: (mnemonic, password) => ipcRenderer.invoke('auth:recover', { mnemonic, password }),
  authLock: () => ipcRenderer.invoke('auth:lock'),

  /* --- Live sync (FS-01-03) --- */
  syncPoll: () => ipcRenderer.invoke('sync:poll'),
  onSync: (cb) => { ipcRenderer.on('sync:update', (_e, payload) => cb(payload)); },

  /* --- Block explorer (FS-01-05) --- */
  explorerBlockcount: () => ipcRenderer.invoke('explorer:blockcount'),
  explorerBlockhash: (h) => ipcRenderer.invoke('explorer:blockhash', h),
  explorerBlock: (h) => ipcRenderer.invoke('explorer:block', h),
  explorerBlocktxs: (h) => ipcRenderer.invoke('explorer:blocktxs', h),
  explorerTx: (txid) => ipcRenderer.invoke('explorer:tx', txid)
});