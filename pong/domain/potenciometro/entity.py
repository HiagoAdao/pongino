from dataclasses import dataclass
from typing import Self

from pong.domain.potenciometro.normalization import clamp, normalize_raw_value
from pong.domain.potenciometro.reading import PotenciometroReading


@dataclass(frozen=True, slots=True)
class Potenciometro:
    identifier: str
    player: int
    pin: str
    raw_min: int = 0
    raw_max: int = 1023

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("O identificador do potenciômetro não pode ser vazio")
        if self.player < 1:
            raise ValueError("O jogador do potenciômetro deve ser positivo")
        if not self.pin.strip():
            raise ValueError("O pino do potenciômetro não pode ser vazio")
        if self.raw_min >= self.raw_max:
            raise ValueError("raw_min deve ser menor que raw_max")

    @classmethod
    def config(
        cls,
        *,
        identifier: str,
        player: int,
        pin: str,
        raw_min: int = 0,
        raw_max: int = 1023,
    ) -> Self:
        return cls(
            identifier=identifier,
            player=player,
            pin=pin,
            raw_min=raw_min,
            raw_max=raw_max,
        )

    def normalize(self, raw_value: int | float) -> float:
        return normalize_raw_value(raw_value, self.raw_min, self.raw_max)

    def reading_from_raw(self, raw_value: int | float, timestamp: float) -> PotenciometroReading:
        return PotenciometroReading(
            potenciomentro_id=self.identifier,
            player=self.player,
            raw_value=float(raw_value),
            percentage=self.normalize(raw_value),
            timestamp=timestamp,
        )

    def reading_from_percentage(
        self,
        percentage: float,
        timestamp: float,
    ) -> PotenciometroReading:
        return PotenciometroReading(
            potenciomentro_id=self.identifier,
            player=self.player,
            raw_value=None,
            percentage=clamp(percentage),
            timestamp=timestamp,
        )
