export function parsePaddleUpdate(message) {
  let data;
  try {
    data = JSON.parse(message);
  } catch {
    return null;
  }
  if (data?.type !== 'paddle_update') return null;
  const { player1_pct, player2_pct, timestamp } = data;
  if (![player1_pct, player2_pct, timestamp].every(Number.isFinite)) return null;
  if ([player1_pct, player2_pct].some((value) => value < 0 || value > 100)) return null;
  return { player1_pct, player2_pct, timestamp };
}

export class PongWebSocketClient {
  constructor({ onPaddleUpdate = () => {}, onStatusChange = () => {} } = {}) {
    this.onPaddleUpdate = onPaddleUpdate;
    this.onStatusChange = onStatusChange;
    this.socket = null;
    this.retryIntervalMs = 1000;
    this.reconnectTimer = null;
    this.isManuallyClosed = false;
  }

  connect() {
    if (this.socket && this.socket.readyState < WebSocket.CLOSING) return;
    this.isManuallyClosed = false;
    clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
    const url = new URL('/ws', window.location.href);
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    this.onStatusChange({ connected: false, statusText: 'Conectando...' });
    try {
      const socket = new WebSocket(url);
      this.socket = socket;
      socket.addEventListener('open', () => {
        if (this.socket !== socket || this.isManuallyClosed) return;
        this.retryIntervalMs = 1000;
        this.onStatusChange({ connected: true, statusText: 'Conectado' });
        void this.fetchHealthStatus(socket);
      });
      socket.addEventListener('message', ({ data }) => {
        if (this.socket !== socket || this.isManuallyClosed) return;
        const update = parsePaddleUpdate(data);
        if (update) this.onPaddleUpdate(update);
      });
      socket.addEventListener('close', () => {
        if (this.socket !== socket) return;
        this.socket = null;
        this.onStatusChange({ connected: false, statusText: 'Desconectado' });
        this.scheduleReconnect();
      });
      socket.addEventListener('error', () => socket.close());
    } catch (error) {
      console.error('Falha na conexão WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.isManuallyClosed || this.reconnectTimer !== null) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.retryIntervalMs = Math.min(this.retryIntervalMs * 1.5, 8000);
      this.connect();
    }, this.retryIntervalMs);
  }

  async fetchHealthStatus(socket) {
    try {
      const response = await fetch('/health');
      if (!response.ok) return;
      const data = await response.json();
      if (this.isManuallyClosed || this.socket !== socket ||
          socket.readyState !== WebSocket.OPEN) return;
      const sourceName = data.input_source === 'SerialInputSource'
        ? 'Arduino (Serial)' : 'Mock (Simulado)';
      this.onStatusChange({ connected: true, statusText: 'Conectado', sourceName });
    } catch (error) {
      console.debug('Não foi possível obter /health:', error);
    }
  }

  disconnect() {
    this.isManuallyClosed = true;
    clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
    const socket = this.socket;
    this.socket = null;
    socket?.close();
    this.onStatusChange({ connected: false, statusText: 'Desconectado' });
  }
}
