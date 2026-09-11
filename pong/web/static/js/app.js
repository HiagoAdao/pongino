import { DOM } from './dom.js';
import { GAME_STATE, PongGameEngine } from './game.js';
import { PongRenderer } from './ui.js';
import { PongWebSocketClient } from './websocket.js';

const CONTROLS = Object.freeze([
  Object.freeze({ player: 1, up: 'KeyA', down: 'KeyD' }),
  Object.freeze({ player: 2, up: 'ArrowUp', down: 'ArrowDown' }),
]);
const activeKeys = new Set();
const renderer = new PongRenderer(DOM);
const game = new PongGameEngine({
  width: DOM.canvas.width,
  height: DOM.canvas.height,
});
const client = new PongWebSocketClient({
  onPaddleUpdate: ({ player1_pct, player2_pct }) => {
    game.updatePaddleFromPercent(1, player1_pct);
    game.updatePaddleFromPercent(2, player2_pct);
    renderer.updateTelemetry(player1_pct, player2_pct);
  },
  onStatusChange: (status) => renderer.updateConnectionStatus(status),
});
let lastTimestamp = null;
let frame = null;

function toggleGame() {
  game.toggleStart();
  renderer.setOverlayVisible(game.state !== GAME_STATE.PLAYING, true);
}

function handleKeyDown(event) {
  if (event.target instanceof Element &&
      event.target.closest('button, a, input, textarea, select, [contenteditable="true"]')) {
    return;
  }
  if (['ArrowUp', 'ArrowDown', 'Space'].includes(event.code)) event.preventDefault();
  activeKeys.add(event.code);
  if (event.code === 'Space' && !event.repeat) toggleGame();
}

function updateControls(dt) {
  let moved = false;
  for (const { player, up, down } of CONTROLS) {
    const direction = Number(activeKeys.has(down)) - Number(activeKeys.has(up));
    if (!direction) continue;
    game.movePaddleKeyboard(player, direction, 450, dt);
    moved = true;
  }
  if (moved) renderer.updateTelemetry(game.paddle1.percent, game.paddle2.percent);
}

function gameLoop(timestamp) {
  const dt = lastTimestamp === null ? 0 : Math.min(0.05, (timestamp - lastTimestamp) / 1000);
  lastTimestamp = timestamp;
  updateControls(dt);
  game.update(dt);
  renderer.render(game);
  frame = requestAnimationFrame(gameLoop);
}

function start() {
  if (frame !== null) return;
  lastTimestamp = null;
  client.connect();
  frame = requestAnimationFrame(gameLoop);
}

window.addEventListener('keydown', handleKeyDown);
window.addEventListener('keyup', ({ code }) => activeKeys.delete(code));
window.addEventListener('blur', () => activeKeys.clear());
DOM.overlay.addEventListener('click', toggleGame);
DOM.reset.addEventListener('click', () => {
  game.resetGame();
  renderer.setOverlayVisible(true);
});
window.addEventListener('pagehide', () => {
  cancelAnimationFrame(frame);
  frame = null;
  activeKeys.clear();
  client.disconnect();
});
window.addEventListener('pageshow', start);
start();
