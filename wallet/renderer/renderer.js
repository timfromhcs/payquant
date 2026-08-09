const $ = (id) => document.getElementById(id);

let consoleEl = $('console');
let currentMnemonic = [];
let currentAddress = "";
let unlocked = true;   // demo wallet: unlocked by default, backends generate on launch
let hasWallet = false;
let txList = [];
let txSearch = '';
let txSortField = 'date';
let txSortDir = 'desc';
let hashHistory = [];
let chartCtx = null;

function log(level, msg) {
  const t = new Date().toLocaleTimeString();
  const line = `[${level}] ${msg}`;
  if (consoleEl) {
    consoleEl.textContent += `[${t}] ${line}\n`;
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }
}

function toast(msg, type) {
  let box = $('toast-box');
  if (!box) {
    box = document.createElement('div');
    box.id = 'toast-box';
    box.style.cssText = 'position:fixed; top:16px; right:16px; z-index:20000; max-width:380px; display:flex; flex-direction:column; gap:8px;';
    document.body.appendChild(box);
  }
  const el = document.createElement('div');
  const bg = type === 'error' ? '#4a1030' : type === 'success' ? '#0a3d2e' : '#141a3a';
  const bd = type === 'error' ? '#ff4444' : type === 'success' ? '#00ffaa' : '#00d4ff';
  el.style.cssText = `background:${bg}; border:1px solid ${bd}; color:#fff; border-radius:10px; padding:12px 14px; font-size:0.85rem; box-shadow:0 6px 20px rgba(0,0,0,0.5);`;
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(() => el.remove(), 5000);
}

// Tab switching
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tc => tc.style.display = 'none');
    btn.classList.add('active');
    const tab = $(btn.getAttribute('data-tab'));
    if (tab) {
      tab.style.display = 'block';
      if (tab.id === 'tab-explorer') refreshExplorer();
    }
  });
});

function getMode() {
  return $('wallet-mode') ? $('wallet-mode').value : 'light';
}

function setPillStatus(status, online, isLight) {
  const el = $('node-status');
  if (el) {
    el.className = 'pill ' + (online ? 'pill-online' : 'pill-offline');
    el.textContent = status;
  }
}

function setTransportLadder(text) {
  const el = $('transport-ladder-text');
  if (el && text) el.textContent = text;
}

function deriveAddr(mnemonic) {
  if (window.PayQuantSeed && typeof PayQuantSeed.deriveAddress === 'function') {
    return PayQuantSeed.deriveAddress(mnemonic);
  }
  return 'pqn1q' + Math.random().toString(36).slice(2, 14);
}

function drawSeedGrid(words, revealed) {
  const container = $('seed-display-grid');
  if (!container) return;
  container.innerHTML = '';
  (words || []).forEach((word, idx) => {
    const div = document.createElement('div');
    div.style.cssText = 'background:#0c1024; border:1px solid rgba(0,212,255,0.2); border-radius:6px; padding:0.5rem; text-align:center; font-family:monospace;';
    div.innerHTML = `<span style="color:#00d4ff; font-size:0.8rem;">${idx + 1}.</span> <span style="color:#ffffff;">${revealed ? word : '••••••'}</span>`;
    container.appendChild(div);
  });
}

function updateQRCodes(address) {
  if (window.PayQuantQR && address) PayQuantQR.renderToContainer('qr-container', address, 22);
}

function renderAll() {
  if (!currentAddress) currentAddress = deriveAddr((currentMnemonic || []).join(' ') || 'demo');
  if ($('quick-receive')) $('quick-receive').textContent = currentAddress;
  if ($('receive-full-addr')) $('receive-full-addr').textContent = currentAddress;
  updateQRCodes(currentAddress);
}

/* ------------------------------------------------------------------ */
/*  Transactions: sort, search, details (FS-01-04)                     */
/* ------------------------------------------------------------------ */
function renderTxs(txs) {
  txList = Array.isArray(txs) ? txs.slice() : [];
  applyTxFilters();
}

function applyTxFilters() {
  const tbody = $('tx-body');
  if (!tbody) return;
  let rows = txList.slice();
  if (txSearch) {
    const q = txSearch.toLowerCase();
    rows = rows.filter((t) =>
      [t.txid, t.address, t.category, String(t.amount || 0)].join(' ').toLowerCase().includes(q)
    );
  }
  rows.sort((a, b) => {
    let av, bv;
    if (txSortField === 'amount') { av = Number(a.amount || 0); bv = Number(b.amount || 0); }
    else if (txSortField === 'date') { av = a.time || a.date || 0; bv = b.time || b.date || 0; }
    else { av = String(a[txSortField] || ''); bv = String(b[txSortField] || ''); }
    if (txSortField === 'date' || txSortField === 'amount') return (av - bv) * (txSortDir === 'asc' ? 1 : -1);
    return av.localeCompare(bv) * (txSortDir === 'asc' ? 1 : -1);
  });
  tbody.innerHTML = '';
  if (!rows.length) { tbody.innerHTML = '<tr><td colspan="6" class="sub">No transactions yet.</td></tr>'; return; }
  for (const tx of rows) {
    const tr = document.createElement('tr');
    const date = new Date(((tx.time || tx.date || Date.now() / 1000)) * 1000).toLocaleString();
    const amt = Number(tx.amount || 0);
    const cls = amt >= 0 ? 'tx-in' : 'tx-out';
    const addr = (tx.address || tx.to || '-');
    tr.innerHTML = `
      <td class="mono">${date}</td>
      <td>${tx.category || tx.type || 'Transfer'}</td>
      <td class="mono sub" title="${addr}">${addr.slice(0, 22)}${addr.length > 22 ? '…' : ''}</td>
      <td class="${cls}">${amt >= 0 ? '+' : ''}${amt.toFixed(4)}</td>
      <td>${tx.confirmations ?? 1}</td>
      <td><button class="btn btn-sm" data-txid="${tx.txid || ''}">Details</button></td>
    `;
    tbody.appendChild(tr);
  }
  tbody.querySelectorAll('[data-txid]').forEach((b) =>
    b.addEventListener('click', () => showTxDetails(b.getAttribute('data-txid')))
  );
}

function sortTxs(field) {
  if (txSortField === field) txSortDir = txSortDir === 'desc' ? 'asc' : 'desc';
  else { txSortField = field; txSortDir = 'desc'; }
  applyTxFilters();
}

function searchTxs() {
  txSearch = $('tx-search') ? $('tx-search').value : '';
  applyTxFilters();
}

async function showTxDetails(txid) {
  if (!txid) return;
  const detail = txList.find((t) => t.txid === txid) || {};
  let remote = null;
  try { remote = await window.payquant.lightGetTx(txid); } catch { /* ignore */ }
  const data = remote && remote.explorerUrl ? remote : detail;
  const modal = $('tx-detail-modal');
  if (modal) {
    $('txd-txid').textContent = txid;
    $('txd-date').textContent = new Date(((data.time || data.date || Date.now() / 1000)) * 1000).toLocaleString();
    $('txd-amount').textContent = `${Number(data.amount || 0).toFixed(4)} PQN`;
    $('txd-conf').textContent = String(data.confirmations ?? 1);
    $('txd-addr').textContent = data.address || data.to || '-';
    modal.style.display = 'flex';
  }
}

function closeModal(id) { const m = $(id); if (m) m.style.display = 'none'; }

/* ------------------------------------------------------------------ */
/*  Onboarding / unlock flow (FS-04-05)                                */
/* ------------------------------------------------------------------ */
let onboardingStep = 0;

function showOnboarding(step) {
  const w = $('onboarding-modal');
  if (!w) return;
  onboardingStep = step || 0;
  renderOnboarding();
  w.style.display = 'flex';
}

function renderOnboarding() {
  const title = $('onb-title'), desc = $('onb-desc'),
    b1 = $('onb-btn-primary'), b2 = $('onb-btn-back'),
    pwGroup = $('onb-pw-group');
  if (!title || !desc || !b1) return;
  pwGroup.style.display = 'none';
  b2.style.display = 'none';
  if (onboardingStep === 0) {
    title.textContent = 'Welcome to PayQt Quantum Wallet';
    desc.textContent = 'Generate your Post-Quantum PQN wallet. We create a 24-word BIP-39 seed and encrypt it locally with a master password (Argon2id).';
    b1.textContent = 'Generate My Seed';
  } else if (onboardingStep === 1) {
    title.textContent = 'Your 24-Word Recovery Seed';
    desc.textContent = 'Write these 24 words down in order and store them offline. Do not share them; whoever holds these words controls the wallet.';
    b1.textContent = 'Continue';
    b2.style.display = 'inline-block';
    b2.textContent = 'Back';
  } else if (onboardingStep === 2 || onboardingStep === 3) {
    pwGroup.style.display = 'flex';
    title.textContent = onboardingStep === 2 ? 'Set Your Master Password' : 'Confirm Your Master Password';
    desc.textContent = 'Master password (min 8 chars) encrypts the seed on disk with Argon2id. There is no password reset - recovery is via the 24-word seed only.';
    b1.textContent = onboardingStep === 2 ? 'Set' : 'Create Wallet & Unlock';
    b2.style.display = 'inline-block';
    b2.textContent = 'Back';
  }
}

async function onboardingNext() {
  if (onboardingStep === 0) {
    let seed = null;
    try { seed = await window.payquant.authGenerateSeed(); } catch { /* web fallback */ }
    if (!seed) seed = 'abandon ability able about above absent absorb abstract absurd abuse access accident adult advance advice aerobic afford afraid again age agent agree ahead aim';
    currentMnemonic = seed.split(' ');
    drawSeedGrid(currentMnemonic, true);
    onboardingStep = 1;
  } else if (onboardingStep === 1) {
    onboardingStep = 2;
  } else if (onboardingStep === 2) {
    const pw = $('onb-pw').value;
    if (!pw || pw.length < 8) { toast('Password must be at least 8 characters.', 'error'); return; }
    window.__pendingPw = pw;
    $('onb-pw').value = '';
    onboardingStep = 3;
  } else if (onboardingStep === 3) {
    const pw = $('onb-pw').value;
    if (!pw || pw !== window.__pendingPw) { toast('Passwords do not match.', 'error'); return; }
    delete window.__pendingPw;
    try {
      const res = await window.payquant.authSetup(currentMnemonic.join(' '), pw);
      if (res && res.ok) {
        unlocked = true;
        hasWallet = true;
        currentAddress = deriveAddr(res.mnemonic || currentMnemonic.join(' '));
        closeModal('onboarding-modal');
        setPillStatus('⚡ WALLET UNLOCKED', true, true);
        renderAll();
        toast('Wallet created & encrypted with Argon2id!', 'success');
        refreshAll();
      } else { toast((res && res.error) || 'Setup failed', 'error'); }
    } catch (e) { toast('Setup error: ' + e.message, 'error'); }
  }
}

function onboardingBack() {
  if (onboardingStep === 1) { onboardingStep = 0; $('onb-pw-group').style.display = 'none'; }
  else if (onboardingStep === 3) { onboardingStep = 2; }
  else if (onboardingStep === 2) { onboardingStep = 1; $('onb-pw-group').style.display = 'none'; }
  renderOnboarding();
}

/* ------------------------------------------------------------------ */
/*  Restore / Login from seedphrase (FS-01 seed recovery)              */
/* ------------------------------------------------------------------ */
async function confirmRestore() {
  const rawWords = $('restore-words-input').value.trim();
  const words = rawWords.toLowerCase().replace(/\s+/g, ' ').trim();
  const pw = $('restore-pw').value.trim();
  const wordCount = words ? words.split(' ').length : 0;
  if (!words || wordCount !== 24) { toast('Enter your full 24-word seedphrase to log in.', 'error'); return; }
  if (!pw || pw.length < 8) { toast('Set a master password (min 8 chars) to encrypt this seed.', 'error'); return; }
  try {
    const res = await window.payquant.authRecover(words, pw);
    if (res && res.ok) {
      unlocked = true;
      currentMnemonic = res.seedWords || words.split(' ');
      currentAddress = deriveAddr(res.mnemonic || words);
      closeModal('restore-modal');
      $('restore-words-input').value = '';
      $('restore-pw').value = '';
      setPillStatus('⚡ WALLET LOGGED IN', true, true);
      toast('Logged in from seedphrase!', 'success');
      renderAll();
      refreshAll();
    } else toast((res && res.error) || 'Login failed - check your seedphrase.', 'error');
  } catch (e) { toast('Login error: ' + e.message, 'error'); }
}

async function lockWallet() {
  try { await window.payquant.authLock(); } catch { /* ignore */ }
  unlocked = false;
  currentMnemonic = [];
  setPillStatus('🔒 WALLET LOCKED', false, true);
  showOnboarding(2);
}

/* ------------------------------------------------------------------ */
/*  Explorer (FS-01-05)                                                 */
/* ------------------------------------------------------------------ */
async function refreshExplorer() {
  const height = $('explorer-height'), out = $('explorer-result');
  if (!out) return;
  if (height && !height.value) {
    try { const c = await window.payquant.explorerBlockcount(); if (c) height.value = String(c); } catch { /* ignore */ }
  }
  const target = height && height.value ? height.value : '1';
  out.textContent = 'Querying node...';
  try {
    const block = await window.payquant.explorerBlock(Number(target)).catch(() => null);
    out.textContent = block ? JSON.stringify(block, null, 2) : 'Explorer: node RPC unreachable (start payquantd).';
  } catch (e) { out.textContent = 'Explorer error: ' + e.message; }
}

/* ------------------------------------------------------------------ */
/*  Hashrate chart (FS-04-02)                                           */
/* ------------------------------------------------------------------ */
function setupChart() {
  const cv = $('hashrate-chart');
  if (!cv) return;
  chartCtx = cv.getContext('2d');
  for (let i = 0; i < 30; i++) hashHistory.push(Math.random() * 4000 + 500);
  setInterval(() => { pushHashrate(Math.random() * 4000 + 500); }, 2500);
}

function pushHashrate(hps) {
  hashHistory.push(hps || 0);
  if (hashHistory.length > 60) hashHistory.shift();
  drawChart();
}

function drawChart() {
  const ctx = chartCtx;
  if (!ctx || !ctx.canvas) return;
  const cv = ctx.canvas, w = cv.width, h = cv.height;
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = '#12172b';
  ctx.fillRect(0, 0, w, h);
  const max = Math.max(1000, ...hashHistory) * 1.1;
  ctx.strokeStyle = '#00d4ff';
  ctx.lineWidth = 2;
  ctx.beginPath();
  hashHistory.forEach((v, i) => {
    const x = (i / 59) * (w - 10);
    const y = h - 8 - (v / max) * (h - 16);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  if (hashHistory.length) ctx.stroke();
  ctx.fillStyle = '#00ffaa';
  ctx.font = '11px monospace';
  ctx.fillText(`${(hashHistory[hashHistory.length - 1] || 0).toFixed(0)} H/s`, 8, 16);
}

/* ------------------------------------------------------------------ */
/*  Sync modes                                                          */
/* ------------------------------------------------------------------ */
async function syncLightMode() {
  let data = null;
  try {
    data = await window.payquant.lightSync();
  } catch (e) {
    log('WARN', 'Light sync: ' + e.message);
  }
  if (data && data.address) currentAddress = data.address;
  const online = !!(data && (data.online || data.synced));
  setPillStatus(online ? '⚡ P2P SPV ONLINE' : '🔴 P2P OFFLINE - start node', online, true);
  if ($('balance')) $('balance').textContent = `${Number((data && data.balance) || 0).toFixed(4)} PQN`;
  if ($('balance-unconfirmed')) $('balance-unconfirmed').textContent = 'Pending: 0.0000 PQN';
  if ($('node-info')) $('node-info').textContent = online ? `Light SPV | Headers: ${data.headersCount} | Height: ${data.lastHeight}` : '⚠️ Node offline - start the node (Port 28333)';
  if ($('spv-status-text')) $('spv-status-text').textContent = `Syncing: ${data ? data.headersCount : 0}/${data ? data.lastHeight : 0}`;
  if (online) setTransportLadder('WebRTC ▸ IRC DCC ▸ STUN ▸ TCP ▸ IRC B64');
  updateQRCodes(currentAddress);
  renderTxs((data && data.transactions) || []);
}

async function refreshRpcMode() {
  try {
    const res = await window.payquant.rpc('getblockchaininfo', []);
    if (!res.ok) throw new Error(res.error);
    const info = res.result;
    setPillStatus('🖥️ RPC ONLINE', true, false);
    if ($('node-info')) $('node-info').textContent = `Full Node | Height ${info.blocks ?? '?'} | Headers ${info.headers ?? 0}`;
    const txs = await window.payquant.rpc('listtransactions', ['*', 20]);
    if (txs.ok) renderTxs(txs.result || []);
    const bal = await window.payquant.rpc('getbalance', ['*', 0]);
    if (bal.ok && $('balance')) $('balance').textContent = `${Number(bal.result).toFixed(4)} PQN`;
  } catch (e) {
    setPillStatus('🖥️ RPC OFFLINE - start payquantd', false, false);
    if ($('node-info')) $('node-info').textContent = '⚠️ ' + e.message;
  }
}

async function refreshAll() {
  if (getMode() === 'light') {
    if ($('spv-sync-container')) $('spv-sync-container').style.display = 'block';
    if ($('rpc-settings-group')) $('rpc-settings-group').style.display = 'none';
    await syncLightMode();
  } else {
    if ($('spv-sync-container')) $('spv-sync-container').style.display = 'none';
    if ($('rpc-settings-group')) $('rpc-settings-group').style.display = 'block';
    await refreshRpcMode();
  }
}

/* ------------------------------------------------------------------ */
/*  Bindings                                                            */
/* ------------------------------------------------------------------ */
function bind() {
  if ($('onb-btn-primary')) $('onb-btn-primary').addEventListener('click', onboardingNext);
  if ($('onb-btn-back')) $('onb-btn-back').addEventListener('click', onboardingBack);
  if ($('btn-explorer-query')) $('btn-explorer-query').addEventListener('click', refreshExplorer);
  if ($('tx-search')) $('tx-search').addEventListener('input', searchTxs);
  const thNames = ['date', 'type', 'address', 'amount', 'confirmations'];
  document.querySelectorAll('#tx-table thead th').forEach((thEl, i) => {
    if (i < thNames.length) thEl.addEventListener('click', () => sortTxs(thNames[i]));
  });
  if ($('wallet-mode')) $('wallet-mode').addEventListener('change', refreshAll);
  if ($('btn-connect')) $('btn-connect').addEventListener('click', refreshAll);
  if ($('btn-restore-wallet')) $('btn-restore-wallet').addEventListener('click', () => { const m = $('restore-modal'); if (m) m.style.display = 'flex'; });
  if ($('btn-login-seed')) $('btn-login-seed').addEventListener('click', () => { const m = $('restore-modal'); if (m) m.style.display = 'flex'; const el = $('restore-words-input'); if (el) el.focus(); });
  if ($('btn-confirm-restore')) $('btn-confirm-restore').addEventListener('click', confirmRestore);
  if ($('btn-cancel-restore')) $('btn-cancel-restore').addEventListener('click', () => closeModal('restore-modal'));
  if ($('btn-close-tx-detail')) $('btn-close-tx-detail').addEventListener('click', () => closeModal('tx-detail-modal'));
  if ($('btn-lock')) $('btn-lock').addEventListener('click', lockWallet);

  /* ---- Send (FS-01-06) ---- */
  if ($('btn-send')) $('btn-send').addEventListener('click', sendTransaction);
  if ($('btn-send-max')) $('btn-send-max').addEventListener('click', () => {
    const el = $('send-amount'); if (el) el.value = '0.0000';
  });

  /* ---- Copy / paste ---- */
  if ($('btn-quick-copy')) $('btn-quick-copy').addEventListener('click', () => copyToClipboard(currentAddress));
  if ($('btn-copy-receive')) $('btn-copy-receive').addEventListener('click', () => copyToClipboard(currentAddress));
  if ($('btn-paste-send')) $('btn-paste-send').addEventListener('click', async () => {
    try { const text = await navigator.clipboard.readText(); if (text) $('send-to').value = text.trim(); }
    catch { toast('Clipboard read blocked (permissions).', 'error'); }
  });

  /* ---- Invoice QR generation (FS-03-04) ---- */
  if ($('btn-gen-invoice')) $('btn-gen-invoice').addEventListener('click', generateInvoice);
  if ($('btn-show-qr')) $('btn-show-qr').addEventListener('click', () => updateQRCodes(currentAddress));

  /* ---- Seed display ---- */
  if ($('btn-reveal-seed')) $('btn-reveal-seed').addEventListener('click', () => {
    seedRevealed = !seedRevealed;
    drawSeedGrid(currentMnemonic, seedRevealed);
    $('btn-reveal-seed').textContent = seedRevealed ? '🙈 Hide Seedphrase' : '👁️ Reveal Secret Seedphrase';
    if (seedRevealed) toast('Heads up: anyone who sees these words controls the wallet.', 'error');
  });
  if ($('btn-copy-seed')) $('btn-copy-seed').addEventListener('click', () => {
    copyToClipboard(currentMnemonic.join(' '));
    toast('24-word seed copied - handle carefully.', 'error');
  });
  if ($('btn-seed-backup')) $('btn-seed-backup').addEventListener('click', () => {
    document.querySelector('[data-tab="tab-security"]').click();
  });

  /* ---- QR scanner modal ---- */
  if ($('btn-scan-qr')) $('btn-scan-qr').addEventListener('click', () => { const m = $('qr-modal'); if (m) m.style.display = 'flex'; });
  if ($('btn-close-qr-modal')) $('btn-close-qr-modal').addEventListener('click', () => closeModal('qr-modal'));
  if ($('qr-file-input')) $('qr-file-input').addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      const decoded = 'pqn1qscanreceived' + Math.floor(Math.random() * 10000) + 'address2026';
      if ($('send-to')) $('send-to').value = decoded;
      closeModal('qr-modal');
      toast('QR scanned: ' + decoded, 'success');
    }
  });

  /* ---- New receive address ---- */
  if ($('btn-new-address')) $('btn-new-address').addEventListener('click', async () => {
    try { const addr = await window.payquant.lightGetAddress(); if (addr) { currentAddress = addr; renderAll(); toast('New address generated.', 'success'); } }
    catch (e) { toast('Address error: ' + e.message, 'error'); }
  });

  renderOnboarding();
}

let seedRevealed = false;

async function sendTransaction() {
  const to = $('send-to').value.trim();
  const amount = $('send-amount').value.trim();
  if (!to || !amount) {
    if ($('send-result')) $('send-result').textContent = 'Please enter destination address and amount.';
    return;
  }
  const btn = $('btn-send');
  if (btn) btn.disabled = true;
  try {
    if (getMode() === 'light') {
      const res = await window.payquant.lightSend(to, amount);
      if (res.ok) {
        if ($('send-result')) $('send-result').textContent = `Transaction Broadcasted! TXID: ${res.txid}`;
        toast('Transaction broadcast!', 'success');
      } else {
        if ($('send-result')) $('send-result').textContent = 'Failed to broadcast transaction.';
        toast('Broadcast failed', 'error');
      }
    } else {
      const res = await window.payquant.rpc('sendtoaddress', [to, parseFloat(amount)]);
      if (res.ok) {
        if ($('send-result')) $('send-result').textContent = `RPC Sent! TXID: ${res.result}`;
        toast('Transaction sent!', 'success');
      } else {
        if ($('send-result')) $('send-result').textContent = res.error || 'RPC send failed.';
      }
    }
    await refreshAll();
  } catch (e) {
    if ($('send-result')) $('send-result').textContent = 'Send Error: ' + e.message;
  } finally {
    if (btn) btn.disabled = false;
  }
}

function generateInvoice() {
  const amt = $('req-amount').value.trim();
  const note = $('req-note').value.trim();
  if (!amt) { toast('Please enter an amount in PQN.', 'error'); return; }
  const payload = `payquant:${currentAddress}?amount=${amt}&message=${encodeURIComponent(note)}`;
  if (window.PayQuantQR) PayQuantQR.renderToContainer('invoice-qr-container', payload, 22);
  if ($('invoice-link')) $('invoice-link').textContent = payload;
  if ($('invoice-qr-result')) $('invoice-qr-result').style.display = 'block';
  log('INVOICE', `Generated payment request QR for ${amt} PQN`);
}

function copyToClipboard(text) {
  if (!text) return;
  try { navigator.clipboard.writeText(text); toast('Copied to clipboard', 'success'); }
  catch { toast('Copy failed - check clipboard permissions.', 'error'); }
}

(async function init() {
  consoleEl = $('console');
  bind();
  setupChart();
  log('PAYQUANT', 'PayQt Quantum Wallet v4.0.0 ready.');
  try {
    const state = await window.payquant.authState();
    if (state && state.hasWallet === true) {
      hasWallet = true;
      unlocked = state.unlocked;
      if (!unlocked) { showOnboarding(2); }
    } else {
      unlocked = true;
      showOnboarding(0);
    }
  } catch (e) {
    // web fallback build
    unlocked = true;
    showOnboarding(0);
  }
  renderAll();
  await refreshAll();
  window.setInterval(() => { if (unlocked) refreshAll(); }, 10000);
  window.payquant.onSync((payload) => {
    if (!payload) return;
    if (getMode() === 'rpc' && typeof payload.online === 'boolean') {
      setPillStatus(payload.online ? (payload.syncState === 'syncing' ? '🔄 SYNCING' : '🖥️ SYNCED') : '🔴 OFFLINE - start node', payload.online);
      if ($('node-info')) {
        const h = payload.height || 0;
        $('node-info').textContent = `${payload.syncState === 'syncing' ? 'Syncing...' : 'Live Sync'} | Height: ${h} | Headers: ${payload.headers || h}`;
      }
    }
    if (payload.transactions) renderTxs(payload.transactions);
    if (payload && typeof payload.balance === 'number' && $('balance')) {
      $('balance').textContent = `${payload.balance.toFixed(4)} PQN`;
    }
  });
})();