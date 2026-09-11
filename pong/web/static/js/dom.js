function requireElement(id) {
  const element = document.getElementById(id);
  if (!element) throw new Error(`Elemento obrigatório ausente: ${id}`);
  return element;
}

export const DOM = Object.freeze({
  canvas: requireElement('pongCanvas'),
  reset: requireElement('btn-reset'),
  overlay: requireElement('game-overlay'),
  overlayLabel: requireElement('overlay-label'),
  overlayAction: requireElement('overlay-action'),
  indicator: requireElement('ws-indicator'),
  status: requireElement('ws-status-text'),
  source: requireElement('source-text'),
  player1Text: requireElement('p1-percent-text'),
  player1Bar: requireElement('p1-progress-bar'),
  player2Text: requireElement('p2-percent-text'),
  player2Bar: requireElement('p2-progress-bar'),
});
