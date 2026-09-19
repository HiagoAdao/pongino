import pytest

from pong.domain.pong.state import PongState
from pong.domain.potenciometro.entity import Potenciometro
from pong.domain.potenciometro.normalization import adc_to_percent, clamp, normalize_raw_value


@pytest.mark.parametrize(
    ("value", "expected"),
    [(-10.0, 0.0), (0.0, 0.0), (42.5, 42.5), (100.0, 100.0), (110.0, 100.0)],
)
def test_clamp_limits_values(value: float, expected: float) -> None:
    assert clamp(value) == expected


def test_clamp_rejects_an_invalid_range() -> None:
    with pytest.raises(ValueError, match="mínimo deve ser menor"):
        clamp(10.0, 20.0, 10.0)


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [(0, 0.0), (512, 50.0488758553), (1023, 100.0)],
)
def test_adc_to_percent_normalizes_arduino_values(raw_value: int, expected: float) -> None:
    assert adc_to_percent(raw_value) == pytest.approx(expected)


@pytest.mark.parametrize("raw_value", [-1, 1024])
def test_normalization_rejects_values_outside_adc_range(raw_value: int) -> None:
    with pytest.raises(ValueError, match="fora da faixa"):
        normalize_raw_value(raw_value, 0, 1023)


@pytest.mark.parametrize(
    ("minimum", "maximum"),
    [(10, 10), (20, 10)],
)
def test_normalization_rejects_invalid_ranges(minimum: int, maximum: int) -> None:
    with pytest.raises(ValueError, match="mínimo deve ser menor"):
        normalize_raw_value(10, minimum, maximum)


def test_potentiometer_builds_readings() -> None:
    potentiometer = Potenciometro.config(
        identifier="player1",
        player=1,
        pin="A0",
    )

    raw_reading = potentiometer.reading_from_raw(512, 10.0)
    percentage_reading = potentiometer.reading_from_percentage(120.0, 11.0)

    assert raw_reading.raw_value == 512.0
    assert raw_reading.percentage == pytest.approx(50.0488758553)
    assert raw_reading.timestamp == 10.0
    assert percentage_reading.raw_value is None
    assert percentage_reading.percentage == 100.0


def test_pong_state_exposes_player_values(pong_state: PongState) -> None:
    assert pong_state.player1_pos == 1
    assert pong_state.player2_pos == 2
    assert pong_state.player1_pct == 25.0
    assert pong_state.player2_pct == 75.0
