export const GAME_STATE = Object.freeze({ START: 'START', PLAYING: 'PLAYING', GAME_OVER: 'GAME_OVER' });

export class PongGameEngine {
  constructor({ width = 800, height = 500 } = {}) {
    this.width = width;
    this.height = height;

    this.paddleWidth = 14;
    this.paddleHeight = 85;
    this.paddleOffset = 25;

    this.paddle1 = {
      x: this.paddleOffset,
      y: (this.height - this.paddleHeight) / 2,
      targetY: (this.height - this.paddleHeight) / 2,
      percent: 50.0,
    };

    this.paddle2 = {
      x: this.width - this.paddleOffset - this.paddleWidth,
      y: (this.height - this.paddleHeight) / 2,
      targetY: (this.height - this.paddleHeight) / 2,
      percent: 50.0,
    };

    this.ballSize = 12;
    this.initialSpeed = 360;
    this.speed = this.initialSpeed;
    this.maxSpeed = 750;
    this.ball = {
      x: this.width / 2,
      y: this.height / 2,
      vx: this.initialSpeed,
      vy: 0,
    };

    this.score1 = 0;
    this.score2 = 0;
    this.winningScore = 11;
    this.state = GAME_STATE.START;

    this.resetBall(1);
  }

  percentToY(pct) {
    const clamped = Math.max(0.0, Math.min(100.0, pct));
    const maxY = this.height - this.paddleHeight;
    return (clamped / 100.0) * maxY;
  }

  yToPercent(y) {
    const maxY = this.height - this.paddleHeight;
    if (maxY <= 0) return 50.0;
    const clamped = Math.max(0, Math.min(maxY, y));
    return (clamped / maxY) * 100.0;
  }

  getPaddle(player) {
    return player === 1 ? this.paddle1 : player === 2 ? this.paddle2 : null;
  }

  updatePaddleFromPercent(player, percent) {
    const paddle = this.getPaddle(player);
    if (!paddle || !Number.isFinite(percent)) return;
    paddle.percent = Math.max(0, Math.min(100, percent));
    paddle.targetY = this.percentToY(paddle.percent);
  }

  movePaddleKeyboard(player, direction, speedPixels = 400, dt = 0.016) {
    const paddle = this.getPaddle(player);
    if (!paddle) return;
    paddle.y = Math.max(0, Math.min(this.height - this.paddleHeight,
      paddle.y + direction * speedPixels * dt));
    paddle.targetY = paddle.y;
    paddle.percent = this.yToPercent(paddle.y);
  }

  toggleStart() {
    if (this.state === GAME_STATE.START || this.state === GAME_STATE.GAME_OVER) {
      if (this.state === GAME_STATE.GAME_OVER) {
        this.score1 = 0;
        this.score2 = 0;
      }
      this.state = GAME_STATE.PLAYING;
      this.resetBall(Math.random() > 0.5 ? 1 : -1);
    } else if (this.state === GAME_STATE.PLAYING) {
      this.state = GAME_STATE.START;
    }
  }

  resetGame() {
    this.score1 = 0;
    this.score2 = 0;
    this.state = GAME_STATE.START;
    this.resetBall(1);
  }

  resetBall(direction = 1) {
    this.ball.x = this.width / 2;
    this.ball.y = this.height / 2;
    this.speed = this.initialSpeed;

    const angle = (Math.random() * 70 - 35) * (Math.PI / 180);
    this.ball.vx = direction * this.speed * Math.cos(angle);
    this.ball.vy = this.speed * Math.sin(angle);
  }

  update(dt) {
    const lerpFactor = 0.35;
    this.paddle1.y += (this.paddle1.targetY - this.paddle1.y) * lerpFactor;
    this.paddle2.y += (this.paddle2.targetY - this.paddle2.y) * lerpFactor;

    if (this.state !== GAME_STATE.PLAYING) {
      return;
    }

    this.ball.x += this.ball.vx * dt;
    this.ball.y += this.ball.vy * dt;

    if (this.ball.y <= 0) {
      this.ball.y = 0;
      this.ball.vy = Math.abs(this.ball.vy);
    }

    if (this.ball.y + this.ballSize >= this.height) {
      this.ball.y = this.height - this.ballSize;
      this.ball.vy = -Math.abs(this.ball.vy);
    }

    if (
      this.ball.vx < 0 &&
      this.ball.x <= this.paddle1.x + this.paddleWidth &&
      this.ball.x + this.ballSize >= this.paddle1.x &&
      this.ball.y + this.ballSize >= this.paddle1.y &&
      this.ball.y <= this.paddle1.y + this.paddleHeight
    ) {
      this.handlePaddleBounce(this.paddle1, 1);
    }

    if (
      this.ball.vx > 0 &&
      this.ball.x + this.ballSize >= this.paddle2.x &&
      this.ball.x <= this.paddle2.x + this.paddleWidth &&
      this.ball.y + this.ballSize >= this.paddle2.y &&
      this.ball.y <= this.paddle2.y + this.paddleHeight
    ) {
      this.handlePaddleBounce(this.paddle2, -1);
    }

    if (this.ball.x < -20) {
      this.score2 += 1;
      if (this.score2 >= this.winningScore) {
        this.state = GAME_STATE.GAME_OVER;
      } else {
        this.resetBall(1);
      }
    }

    if (this.ball.x > this.width + 20) {
      this.score1 += 1;
      if (this.score1 >= this.winningScore) {
        this.state = GAME_STATE.GAME_OVER;
      } else {
        this.resetBall(-1);
      }
    }
  }

  handlePaddleBounce(paddle, direction) {
    const paddleCenter = paddle.y + this.paddleHeight / 2;
    const ballCenter = this.ball.y + this.ballSize / 2;
    const relativeImpact = (ballCenter - paddleCenter) / (this.paddleHeight / 2);
    const clampedImpact = Math.max(-1.0, Math.min(1.0, relativeImpact));

    this.speed = Math.min(this.maxSpeed, this.speed + 25);

    const bounceAngle = clampedImpact * (55 * (Math.PI / 180));
    this.ball.vx = direction * this.speed * Math.cos(bounceAngle);
    this.ball.vy = this.speed * Math.sin(bounceAngle);

    if (direction === 1) {
      this.ball.x = paddle.x + this.paddleWidth + 1;
    } else {
      this.ball.x = paddle.x - this.ballSize - 1;
    }

  }
}
