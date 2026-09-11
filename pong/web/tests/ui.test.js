import { test } from 'node:test';
import { strict as assert } from 'node:assert';
import { PongRenderer } from '../static/js/ui.js';

function createElements() {
  return {
    canvas: { width: 800, height: 500, getContext: () => ({}) },
    overlay: { hidden: false },
    overlayLabel: { textContent: '' },
    overlayAction: { textContent: '' },
    indicator: { dataset: {} },
    status: { textContent: '' },
    source: { textContent: '' },
    player1Text: { textContent: '' },
    player2Text: { textContent: '' },
    player1Bar: { style: {} },
    player2Bar: { style: {} },
  };
}

test('overlay exposes pause and start labels through supplied references', () => {
  const dom = Object.freeze(createElements());
  const renderer = new PongRenderer(dom);
  renderer.setOverlayVisible(false);
  assert.equal(dom.overlay.hidden, true);
  renderer.setOverlayVisible(true, true);
  assert.equal(dom.overlay.hidden, false);
  assert.equal(dom.overlayLabel.textContent, 'PARTIDA EM PAUSA');
  assert.equal(dom.overlayAction.textContent, 'CONTINUAR PARTIDA');
  renderer.setOverlayVisible(true);
  assert.equal(dom.overlayAction.textContent, 'INICIAR PARTIDA');
});

test('telemetry bounds both bars and connection updates its data attribute', () => {
  const dom = createElements();
  const renderer = new PongRenderer(dom);
  renderer.updateTelemetry(-10, 110);
  assert.equal(dom.player1Text.textContent, '0.0%');
  assert.equal(dom.player2Bar.style.width, '100%');
  renderer.updateConnectionStatus({ connected: true, statusText: 'Conectado' });
  assert.equal(dom.indicator.dataset.connected, 'true');
});
