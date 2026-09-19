import pytest
from pydantic import ValidationError

from pong.config import Settings


def test_settings_use_declared_defaults(isolated_settings_environment: None) -> None:
    settings = Settings()

    assert settings.serial_baudrate == 115200
    assert settings.serial_timeout_seconds == 1.0
    assert settings.pot1_pin == "A0"
    assert settings.pot2_pin == "A1"
    assert settings.server_host == "0.0.0.0"
    assert settings.server_port == 8888


@pytest.mark.parametrize(
    ("environment_name", "environment_value", "attribute", "expected"),
    [
        ("PONG_SERIAL_BAUDRATE", "9600", "serial_baudrate", 9600),
        ("PONG_POT1_PIN", "A2", "pot1_pin", "A2"),
        ("PONG_SERVER_PORT", "9000", "server_port", 9000),
    ],
)
def test_settings_read_prefixed_environment(
    isolated_settings_environment: None,
    monkeypatch: pytest.MonkeyPatch,
    environment_name: str,
    environment_value: str,
    attribute: str,
    expected: object,
) -> None:
    monkeypatch.setenv(environment_name, environment_value)

    settings = Settings()

    assert getattr(settings, attribute) == expected


@pytest.mark.parametrize("field", ["server_port", "serial_baudrate"])
def test_settings_reject_non_positive_values(
    isolated_settings_environment: None,
    field: str,
) -> None:
    with pytest.raises(ValidationError):
        Settings(**{field: 0})
