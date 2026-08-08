const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('payquant', {
  rpc: (method, params = []) => ipcRenderer.invoke('rpc:call', method, params),
  getSettings: () => ipcRenderer.invoke('settings:get'),
  saveSettings: (s) => ipcRenderer.invoke('settings:save', s)
});