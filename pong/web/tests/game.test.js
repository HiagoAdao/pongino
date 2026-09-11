import { test } from 'node:test';
import { strict as assert } from 'node:assert';
import { GAME_STATE, PongGameEngine } from '../static/js/game.js';

test('controls clamp both paddles and reject invalid readings', () => {
  const game = new PongGameEngine();
  for (const player of [1, 2]) {
    game.updatePaddleFromPercent(player, 150);
    assert.equal(game.getPaddle(player).percent, 100);
    game.updatePaddleFromPercent(player, NaN);
    assert.equal(game.getPaddle(player).percent, 100);
    game.movePaddleKeyboard(player, -1, 10000, 1);
    assert.equal(game.getPaddle(player).y, 0);
    assert.equal(game.getPaddle(player).percent, 0);
  }
});

test('pause stops ball movement and reset clears the score', () => {
  const game = new PongGameEngine();
  game.toggleStart();
  assert.equal(game.state, GAME_STATE.PLAYING);
  game.toggleStart();
  const position = { ...game.ball };
  game.update(0.02);
  assert.deepEqual(game.ball, position);
  game.score1 = 5;
  game.resetGame();
  assert.equal(game.score1, 0);
  assert.equal(game.state, GAME_STATE.START);
});

test('winning point ends the match and starting again clears scores', () => {
  const game = new PongGameEngine();
  game.toggleStart();
  game.score1 = game.winningScore - 1;
  game.ball.x = game.width + 30;
  game.ball.vx = 100;
  game.update(0.01);
  assert.equal(game.state, GAME_STATE.GAME_OVER);
  game.toggleStart();
  assert.equal(game.score1, 0);
  assert.equal(game.state, GAME_STATE.PLAYING);
});
