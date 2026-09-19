from pathlib import Path

import pytest

from pong.config import Settings
from pong.domain.pong.state import PongState
from pong.domain.potenciometro.entity import Potenciometro


@pytest.fixture
def isolated_settings_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / ".env").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    for field_name in Settings.model_fields:
        monkeypatch.delenv(f"PONG_{field_name.upper()}", raising=False)


@pytest.fixture
def settings(isolated_settings_environment: None) -> Settings:
    return Settings(
        serial_port="/dev/test-pong",
        serial_baudrate=115200,
        serial_timeout_seconds=0.01,
        serial_startup_delay_seconds=0.0,
        serial_reconnect_delay_seconds=0.01,
        pot1_pin="A0",
        pot2_pin="A1",
        server_host="127.0.0.1",
        server_port=8888,
    )


@pytest.fixture
def potentiometers() -> tuple[Potenciometro, Potenciometro]:
    return (
        Potenciometro.config(identifier="player1", player=1, pin="A0"),
        Potenciometro.config(identifier="player2", player=2, pin="A1"),
    )


@pytest.fixture
def pong_state(potentiometers: tuple[Potenciometro, Potenciometro]) -> PongState:
    player_1, player_2 = potentiometers
    return PongState(
        player_1=player_1.reading_from_percentage(25.0, 123.0),
        player_2=player_2.reading_from_percentage(75.0, 123.0),
        timestamp=123.0,
    )
