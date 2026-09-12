from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PotenciometroReading:
    potenciomentro_id: str
    player: int
    raw_value: float | None
    percentage: float
    timestamp: float
