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
