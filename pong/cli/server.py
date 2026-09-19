from asyncio import get_event_loop
from signal import SIGINT, SIGTERM, signal
from types import FrameType

from tornado.ioloop import IOLoop

from pong.api.app import make_app
from pong.api.websocket.connection_manager import ConnectionManager
from pong.config import Settings
from pong.domain.potenciometro.entity import Potenciometro
from pong.domain.raquete.state import RaqueteState
from pong.infra.input.serial.source import SerialInputSource


def run_server() -> None:
    """Inicializa a aplicação e aguarda um sinal de encerramento."""
    settings = Settings()
    potenciometros = (
        Potenciometro.config(identifier="player1", player=1, pin=settings.pot1_pin),
        Potenciometro.config(identifier="player2", player=2, pin=settings.pot2_pin),
    )
    connection_manager = ConnectionManager()
    loop = IOLoop.current()
    event_loop = get_event_loop()

    def on_paddle_update(state: RaqueteState) -> None:
        connection_manager.broadcast_state(state)

    def handle_signal(_signal_number: int, _frame: FrameType | None) -> None:
        event_loop.call_soon_threadsafe(loop.stop)

    input_source = SerialInputSource(
        settings=settings,
        potenciomentros=potenciometros,
        on_update=on_paddle_update,
    )

    app = make_app(connection_manager=connection_manager)
    http_server = app.listen(settings.server_port, address=settings.server_host)

    print("=" * 70)
    print("Pong Retrô Distribuído (Arduino + Tornado WebSockets)")
    print(f"Servidor HTTP/WebSocket: http://{settings.server_host}:{settings.server_port}")
    print(f"Potenciômetro 1: {settings.pot1_pin} | Potenciômetro 2: {settings.pot2_pin}")
    print(f"Fonte de entrada: {type(input_source).__name__}")
    print(f"Acesse http://localhost:{settings.server_port} no navegador.")
    print("Pressione Ctrl+C para encerrar.")
    print("=" * 70)

    previous_sigint = signal(SIGINT, handle_signal)
    previous_sigterm = signal(SIGTERM, handle_signal)
    try:
        event_loop.run_until_complete(input_source.start())
        loop.start()
    finally:
        try:
            event_loop.run_until_complete(input_source.stop())
        finally:
            http_server.stop()
            event_loop.run_until_complete(http_server.close_all_connections())
            signal(SIGINT, previous_sigint)
            signal(SIGTERM, previous_sigterm)
        print("Servidor finalizado.")


def main() -> None:
    run_server()


if __name__ == "__main__":
    main()
