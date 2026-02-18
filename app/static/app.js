const logEl = document.getElementById('log');
const ordersBody = document.getElementById('ordersBody');

function log(data) {
  const stamp = new Date().toISOString();
  const txt = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
  logEl.textContent = `[${stamp}] ${txt}\n\n` + logEl.textContent;
}

async function api(path, options = {}) {
  const resp = await fetch(path, {
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const payload = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(payload.detail || `Erro ${resp.status}`);
  }
  return payload;
}

function orderRow(order) {
  return `<tr>
    <td>${order.id}</td>
    <td>${order.symbol}</td>
    <td>${order.side}</td>
    <td>${order.status}</td>
    <td>
      <button onclick="monitorOrder('${order.id}')">Monitorar</button>
      <button class="secondary" onclick="cancelOrder('${order.id}')">Cancelar</button>
    </td>
  </tr>`;
}

async function refreshOrders() {
  try {
    const orders = await api('/orders', { method: 'GET' });
    ordersBody.innerHTML = orders.map(orderRow).join('');
    log({ message: 'lista de ordens atualizada', total: orders.length });
  } catch (err) {
    log(`Erro ao listar ordens: ${err.message}`);
  }
}

async function connect() {
  const gmail = document.getElementById('gmail').value;
  const senha = document.getElementById('senha').value;
  try {
    const data = await api('/connect', {
      method: 'POST',
      body: JSON.stringify({ gmail, senha }),
    });
    log({ message: 'conectado com sucesso', data });
  } catch (err) {
    log(`Falha na conexão: ${err.message}`);
  }
}

async function disconnect() {
  try {
    const data = await api('/disconnect', { method: 'POST', body: '{}' });
    log({ message: 'desconectado', data });
  } catch (err) {
    log(`Falha ao desconectar: ${err.message}`);
  }
}

async function analyze() {
  const symbol = document.getElementById('symbol').value;
  try {
    const data = await api(`/market/${symbol}`, { method: 'GET' });
    log({ message: 'análise de mercado', symbol, trend: data.trend, signal: data.signal, current_price: data.current_price });
  } catch (err) {
    log(`Falha na análise: ${err.message}`);
  }
}

async function createOrder() {
  const symbol = document.getElementById('symbol').value;
  const side = document.getElementById('side').value;
  const amount = Number(document.getElementById('amount').value);

  try {
    const data = await api('/orders', {
      method: 'POST',
      body: JSON.stringify({ symbol, side, amount, expiration_seconds: 60 }),
    });
    log({ message: 'ordem criada', order: data.order });
    await refreshOrders();
  } catch (err) {
    log(`Falha ao criar ordem: ${err.message}`);
  }
}

async function monitorOrder(orderId) {
  try {
    const data = await api(`/orders/${orderId}/monitor`, { method: 'POST', body: '{}' });
    log({ message: 'ordem monitorada', order: data.order });
    await refreshOrders();
  } catch (err) {
    log(`Falha ao monitorar ordem: ${err.message}`);
  }
}

async function cancelOrder(orderId) {
  try {
    const data = await api(`/orders/${orderId}/cancel`, { method: 'POST', body: '{}' });
    log({ message: 'ordem cancelada', order: data.order });
    await refreshOrders();
  } catch (err) {
    log(`Falha ao cancelar ordem: ${err.message}`);
  }
}

window.monitorOrder = monitorOrder;
window.cancelOrder = cancelOrder;

document.getElementById('btnConnect').addEventListener('click', connect);
document.getElementById('btnDisconnect').addEventListener('click', disconnect);
document.getElementById('btnMarket').addEventListener('click', analyze);
document.getElementById('btnCreate').addEventListener('click', createOrder);
document.getElementById('btnList').addEventListener('click', refreshOrders);

refreshOrders();
