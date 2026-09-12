from dataclasses import dataclass

from pong.domain.potenciometro.reading import PotenciometroReading


@dataclass(frozen=True, slots=True)
class PaddleState:
    player_1: PotenciometroReading
    player_2: PotenciometroReading
    timestamp: float

    @property
    def player1_pct(self) -> float:
        return self.player_1.percentage

    @property
    def player2_pct(self) -> float:
        return self.player_2.percentage
