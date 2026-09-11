import { test } from 'node:test';
import { strict as assert } from 'node:assert';
import { parsePaddleUpdate, PongWebSocketClient } from '../static/js/websocket.js';

test('only valid paddle messages reach the game', () => {
  const update = { type: 'paddle_update', player1_pct: 20, player2_pct: 90, timestamp: 1 };
  assert.deepEqual(parsePaddleUpdate(JSON.stringify(update)),
    { player1_pct: 20, player2_pct: 90, timestamp: 1 });
  for (const message of ['{', 'null', '{}', JSON.stringify({ ...update, player1_pct: '20' }),
    JSON.stringify({ ...update, player2_pct: 101 })]) {
    assert.equal(parsePaddleUpdate(message), null);
  }
});

test('late health response cannot restore disconnected status', async (context) => {
  let resolveHealth;
  context.mock.method(globalThis, 'fetch', () => new Promise((resolve) => {
    resolveHealth = resolve;
  }));
  const statuses = [];
  const client = new PongWebSocketClient({ onStatusChange: (status) => statuses.push(status) });
  const socket = { close() {} };
  client.socket = socket;
  const pending = client.fetchHealthStatus(socket);
  client.disconnect();
  resolveHealth({ ok: true, json: async () => ({ input_source: 'MockInputSource' }) });
  await pending;
  assert.equal(statuses.length, 1);
  assert.equal(statuses[0].connected, false);
});

test('reconnect schedules once and disconnect cancels it', (context) => {
  context.mock.timers.enable({ apis: ['setTimeout'] });
  const client = new PongWebSocketClient();
  let attempts = 0;
  client.connect = () => { attempts += 1; };
  client.scheduleReconnect();
  client.scheduleReconnect();
  context.mock.timers.tick(1000);
  assert.equal(attempts, 1);
  client.scheduleReconnect();
  client.disconnect();
  context.mock.timers.tick(8000);
  assert.equal(attempts, 1);
});
