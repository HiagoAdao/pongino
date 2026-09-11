from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações declarativas carregadas do ambiente ou de um arquivo .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PONG_",
        extra="ignore",
    )

    serial_port: str | None = Field(
        default=None,
        description="Porta serial USB configurada explicitamente no ambiente",
    )
    serial_baudrate: int = Field(
        default=115200,
        description="Velocidade da porta serial em bps",
        gt=0,
    )
    serial_timeout_seconds: float = Field(
        default=1.0,
        description="Tempo máximo para aguardar uma linha serial",
        gt=0.0,
    )
    serial_startup_delay_seconds: float = Field(
        default=2.0,
        description="Tempo de estabilização após abrir a porta serial",
        ge=0.0,
    )
    serial_reconnect_delay_seconds: float = Field(
        default=2.0,
        description="Intervalo entre tentativas de conexão serial",
        ge=0.0,
    )

    pot1_pin: str = Field(
        default="A0",
        description="Identificador do pino do Potenciômetro 1 (Jogador 1 - Esquerda)",
        min_length=1,
    )
    pot2_pin: str = Field(
        default="A1",
        description="Identificador do pino do Potenciômetro 2 (Jogador 2 - Direita)",
        min_length=1,
    )

    server_host: str = Field(
        default="0.0.0.0",
        description="Endereço de bind do servidor Tornado",
        min_length=1,
    )
    server_port: int = Field(
        default=8888,
        description="Porta TCP para o servidor HTTP/WebSocket",
        ge=1,
        le=65535,
    )
