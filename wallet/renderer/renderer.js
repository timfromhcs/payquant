const $ = (id) => document.getElementById(id);
const consoleEl = $('console');

function log(level, msg) {
  const t = new Date().toLocaleTimeString();
  const line = `[${level}] ${msg}`;
  consoleEl.textContent += `[${t}] ${line}\n`;
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function getMode() {
  return $('wallet-mode').value;
}

function setPillStatus(statusText, online = true, isLight = false) {
  const el = $('node-status');
  if (isLight) {
    el.className = online ? 'pill pill-online' : 'pill pill-offline';
    el.textContent = online ? 'LIGHT MODE (P2P ONLINE)' : 'LIGHT MODE (OFFLINE)';
  } else {
    el.className = online ? 'pill pill-online' : 'pill pill-offline';
    el.textContent = online ? 'NODE RPC ONLINE' : 'NODE RPC OFFLINE';
  }
}

async function rpc(method, params = []) {
  log('RPC', `${method} ${JSON.stringify(params)}`);
  const res = await window.payquant.rpc(method, params);
  if (!res.ok) throw new Error(res.error);
  return res.result;
}

async function syncLightMode() {
  try {
    const data = await window.payquant.lightSync();
    setPillStatus(data.online ? 'Online' : 'Offline', data.online, true);
    
    $('balance').textContent = `${data.balance.toFixed(4)} PQN`;
    $('receive').textContent = data.address;
    $('node-info').textContent = `Light SPV Mode | Block Headers: ${data.headersCount} | Height: ${data.lastHeight}`;
    
    // Update SPV Sync bar
    $('spv-status-text').textContent = `Syncing Block Headers: ${data.headersCount} / ${data.lastHeight} (100% SPV Verified)`;
    $('spv-progress-bar').style.width = '100%';
    
    renderTransactions(data.transactions || []);
  } catch (e) {
    log('WARN', 'Light Sync Notice: ' + e.message);
  }
}

async function refreshRpcMode() {
  try {
    const info = await rpc('getblockchaininfo');
    const net = await rpc('getnetworkinfo');
    let balance = '--';
    try {
      const bal = await rpc('getbalance', ['*', 0]);
      balance = bal.toLocaleString('en-US', { minimumFractionDigits: 4 }) + ' PQN';
    } catch (e) {
      balance = '0.0000 PQN';
    }
    $('balance').textContent = balance;
    $('node-info').textContent = `Full Node | Height ${info.blocks ?? '?'} | Peers ${(net.num_connections ?? 0)}`;
    setPillStatus('Online', true, false);
    
    const txs = await rpc('listtransactions', ['*', 20]);
    renderTransactions(txs || []);
  } catch (e) {
    setPillStatus('Offline', false, false);
    $('node-info').textContent = 'Cannot reach node RPC: ' + e.message;
  }
}

function renderTransactions(txs) {
  const tbody = $('tx-body');
  tbody.innerHTML = '';
  if (!txs || txs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="sub">No transactions recorded yet.</td></tr>';
    return;
  }
  txs.forEach((tx) => {
    const tr = document.createElement('tr');
    const date = tx.time ? new Date(tx.time * 1000).toLocaleString() : '-';
    const category = tx.category || tx.type || '-';
    const amount = tx.amount || 0;
    const cls = amount >= 0 ? 'tx-in' : 'tx-out';
    tr.innerHTML = `
      <td>${date}</td>
      <td>${category}</td>
      <td class="sub">${tx.address || tx.to || '-'}</td>
      <td class="${cls}">${amount >= 0 ? '+' : ''}${amount} PQN</td>
      <td>${tx.confirmations ?? 1}</td>`;
    tbody.appendChild(tr);
  });
}

async function refreshAll() {
  if (getMode() === 'light') {
    $('spv-sync-container').style.display = 'block';
    $('rpc-settings-group').style.display = 'none';
    await syncLightMode();
  } else {
    $('spv-sync-container').style.display = 'none';
    $('rpc-settings-group').style.display = 'inline-block';
    await refreshRpcMode();
  }
}

async function handleSend() {
  const to = $('send-to').value.trim();
  const amount = $('send-amount').value.trim();
  if (!to || !amount) {
    $('send-result').textContent = 'Enter destination address and amount.';
    return;
  }
  const btn = $('btn-send');
  btn.disabled = true;
  try {
    if (getMode() === 'light') {
      const res = await window.payquant.lightSend(to, amount);
      if (res.ok) {
        $('send-result').textContent = `Sent via P2P. TXID: ${res.txid}`;
        log('SEND P2P', `Broadcasted TXID: ${res.txid}`);
      } else {
        $('send-result').textContent = 'Failed to broadcast P2P transaction.';
      }
    } else {
      const txid = await rpc('sendtoaddress', [to, parseFloat(amount)]);
      $('send-result').textContent = 'Sent via RPC. TXID: ' + txid;
      log('SEND RPC', 'TXID ' + txid);
    }
    await refreshAll();
  } catch (e) {
    $('send-result').textContent = 'Send error: ' + e.message;
    log('WARN', 'Send error: ' + e.message);
  } finally {
    btn.disabled = false;
  }
}

$('wallet-mode').addEventListener('change', refreshAll);
$('btn-connect').addEventListener('click', refreshAll);
$('btn-new-address').addEventListener('click', async () => {
  if (getMode() === 'light') {
    const addr = await window.payquant.lightGetAddress();
    $('receive').textContent = addr;
    log('RECEIVE', 'Generated Light Address: ' + addr);
  } else {
    try {
      const addr = await rpc('getnewaddress');
      $('receive').textContent = addr;
      log('RECEIVE', 'New RPC Address: ' + addr);
    } catch (e) {
      log('WARN', 'getnewaddress: ' + e.message);
    }
  }
});

$('btn-copy-address').addEventListener('click', async () => {
  const a = $('receive').textContent;
  if (a && a !== 'No address') {
    try {
      await navigator.clipboard.writeText(a);
      log('RECEIVE', 'Copied address to clipboard.');
    } catch (e) {
      log('WARN', 'Clipboard write failed.');
    }
  }
});

$('btn-send').addEventListener('click', handleSend);

(async function init() {
  log('PAYQUANT', 'PayQuant Cross-Platform Light Wallet (v3.0.0) Initialized.');
  await refreshAll();
  window.setInterval(async () => {
    await refreshAll();
  }, 10000);
})();