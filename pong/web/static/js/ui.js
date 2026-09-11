import { GAME_STATE } from './game.js';

export class PongRenderer {
  constructor(dom) {
    this.dom = dom;
    this.ctx = dom.canvas.getContext('2d');
    if (!this.ctx) throw new Error('Canvas 2D indisponível.');
    this.width = dom.canvas.width;
    this.height = dom.canvas.height;
    this.telemetry = [
      { text: dom.player1Text, bar: dom.player1Bar },
      { text: dom.player2Text, bar: dom.player2Bar },
    ];
  }

  updateTelemetry(...percentages) {
    this.telemetry.forEach(({ text, bar }, index) => {
      const percentage = Math.max(0, Math.min(100, percentages[index]));
      text.textContent = `${percentage.toFixed(1)}%`;
      bar.style.width = `${percentage}%`;
    });
  }

  updateConnectionStatus({ connected, statusText, sourceName }) {
    this.dom.status.textContent = statusText;
    this.dom.indicator.dataset.connected = String(connected);
    if (sourceName) this.dom.source.textContent = sourceName;
  }

  setOverlayVisible(visible, paused = false) {
    this.dom.overlay.hidden = !visible;
    this.dom.overlayLabel.textContent = paused ? 'PARTIDA EM PAUSA' : 'PRONTO PARA JOGAR?';
    this.dom.overlayAction.textContent = paused ? 'CONTINUAR PARTIDA' : 'INICIAR PARTIDA';
  }

  render(game) {
    const ctx = this.ctx;

    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, this.width, this.height);

    ctx.fillStyle = '#ffffff';
    const segWidth = 4;
    const segHeight = 10;
    const gap = 30;
    const centerX = this.width / 2 - segWidth / 2;

    for (let y = 10; y < this.height; y += segHeight + gap) {
      ctx.fillRect(centerX, y, segWidth, segHeight);
    }

    ctx.fillStyle = '#f5f5f5';
    ctx.font = 'bold 52px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(String(game.score1), this.width / 4, 30);
    ctx.fillText(String(game.score2), (3 * this.width) / 4, 30);

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(game.paddle1.x, game.paddle1.y, game.paddleWidth, game.paddleHeight);

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(game.paddle2.x, game.paddle2.y, game.paddleWidth, game.paddleHeight);

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(game.ball.x, game.ball.y, game.ballSize, game.ballSize);

    if (game.state === GAME_STATE.GAME_OVER) {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
      ctx.fillRect(0, 0, this.width, this.height);

      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 24px Arial';
      const winner = game.score1 >= game.winningScore ? 'JOGADOR 1 VENCEU!' : 'JOGADOR 2 VENCEU!';
      ctx.fillText(winner, this.width / 2, this.height / 2 - 20);

      ctx.fillStyle = '#f5f5f5';
      ctx.font = '14px monospace';
      ctx.fillText('PRESSIONE ESPAÇO PARA REINICIAR', this.width / 2, this.height / 2 + 30);
    }
  }
}
