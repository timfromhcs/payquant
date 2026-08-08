const $ = (id) => document.getElementById(id);
const consoleEl = $('console');

function log(level, msg) {
  const t = new Date().toLocaleTimeString();
  const line = `[${level}] ${msg}`;
  consoleEl.textContent += `[${t}] ${line}\n`;
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

async function rpc(method, params = []) {
  log('RPC', `${method} ${JSON.stringify(params)}`);
  const res = await window.payquant.rpc(method, params);
  if (!res.ok) throw new Error(res.error);
  return res.result;
}

async function loadSettings() {
  const s = await window.payquant.getSettings();
  $('rpc-host').value = s.host;
  $('rpc-port').value = s.port || 28332;
  $('rpc-user').value = s.user;
  $('rpc-pass').value = s.pass;
}

async function saveSettings() {
  await window.payquant.saveSettings({
    host: $('rpc-host').value,
    port: $('rpc-port').value,
    user: $('rpc-user').value,
    pass: $('rpc-pass').value
  });
}

let walletName = '*';

function setNodeStatus(on) {
  const el = $('node-status');
  el.className = on ? 'pill pill-online' : 'pill pill-offline';
  el.textContent = on ? 'NODE ONLINE' : 'NODE OFFLINE';
  log(on ? 'INFO' : 'WARN', on ? 'Connected to PayQuant node RPC.' : 'Node not reachable.');
}

async function refreshWallet() {
  try {
    const info = await rpc('getblockchaininfo');
    const net = await rpc('getnetworkinfo');
    let balance = '--';
    let pending = '--';
    try {
      const bal = await rpc('getbalance', ['*', 0]);
      balance = bal.toLocaleString('en-US', { minimumFractionDigits: 4 }) + ' PQN';
    } catch (e) {
      balance = '0.0000 PQN (no wallet?)';
    }
    $('balance').textContent = balance;
    $('balance-unconfirmed').textContent = 'Pending: -- PQN';
    $('node-info').textContent =
      `Height ${info.blocks ?? '?'} | Peers ${(net.num_connections ?? 0)} | ${(net.subversion || '').replace(/[\/\\"]/g, '')}`;
    setNodeStatus(true);
  } catch (e) {
    setNodeStatus(false);
    $('node-info').textContent = e.message;
  }
}

async function refreshTransactions() {
  try {
    const txs = await rpc('listtransactions', ['*', 20]);
    const tbody = $('tx-body');
    tbody.innerHTML = '';
    if (!txs || txs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="sub">No transactions yet.</td></tr>';
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
        <td>${tx.confirmations ?? '-'}</td>`;
      tbody.appendChild(tr);
    });
  } catch (e) {
    log('WARN', 'listtransactions: ' + e.message);
  }
}

async function newAddress() {
  try {
    const addr = await rpc('getnewaddress');
    $('receive').textContent = addr;
    log('RECEIVE', 'New address: ' + addr);
  } catch (e) {
    log('WARN', 'getnewaddress: ' + e.message);
  }
}

async function handleSend() {
  const to = $('send-to').value.trim();
  const amount = $('send-amount').value.trim();
  if (!to || !amount) {
    $('send-result').textContent = 'Enter destination and amount.';
    return;
  }
  const btn = $('btn-send');
  btn.disabled = true;
  try {
    const txid = await rpc('sendtoaddress', [to, parseFloat(amount)]);
    $('send-result').textContent = 'Sent. TXID: ' + txid;
    log('SEND', 'TXID ' + txid);
    await refreshWallet();
    await refreshTransactions();
  } catch (e) {
    $('send-result').textContent = 'Send failed: ' + e.message;
    log('WARN', 'sendtoaddress: ' + e.message);
  } finally {
    btn.disabled = false;
  }
}

$('btn-connect').addEventListener('click', async () => {
  await saveSettings();
  await refreshWallet();
  await refreshTransactions();
});
$('btn-new-address').addEventListener('click', newAddress);
$('btn-copy-address').addEventListener('click', async () => {
  const a = $('receive').textContent;
  if (a && a !== 'No address') {
    try { await navigator.clipboard.writeText(a); log('RECEIVE', 'Copied address.'); }
    catch (e) { log('WARN', 'Clipboard unavailable.'); }
  }
});
$('btn-send').addEventListener('click', handleSend);

(async function init() {
  log('PAYQUANT', 'PayQuant Wallet renderer initialised.');
  await loadSettings();
  await refreshWallet();
  await refreshTransactions();
  await newAddress();
  window.setInterval(async () => {
    await refreshWallet();
    await refreshTransactions();
  }, 15000);
})();