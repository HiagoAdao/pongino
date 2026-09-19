import asyncio
import logging
import signal

from pong.api.app import make_app
from pong.api.websocket.connection_manager import ConnectionManager
from pong.config import Settings
from pong.domain.pong.state import PongState
from pong.domain.potenciometro.entity import Potenciometro
from pong.infra.input.serial.source import SerialInputSource

logger = logging.getLogger(__name__)


async def run_server() -> None:
    settings = Settings()
    potenciometros = (
        Potenciometro.config(identifier="player1", player=1, pin=settings.pot1_pin),
        Potenciometro.config(identifier="player2", player=2, pin=settings.pot2_pin),
    )
    connection_manager = ConnectionManager()
    stop_event = asyncio.Event()
    event_loop = asyncio.get_running_loop()

    def on_paddle_update(state: PongState) -> None:
        connection_manager.broadcast_state(state)

    input_source = SerialInputSource(
        settings=settings,
        potenciomentros=potenciometros,
        on_update=on_paddle_update,
    )

    app = make_app(connection_manager=connection_manager)
    http_server = app.listen(settings.server_port, address=settings.server_host)

    logger.info("=" * 70)
    logger.info("Pong Retrô Distribuído (Arduino + Tornado WebSockets)")
    logger.info("Servidor HTTP/WebSocket: %s:%s", settings.server_host, settings.server_port)
    logger.info("Potenciômetro 1: %s | Potenciômetro 2: %s", settings.pot1_pin, settings.pot2_pin)
    logger.info("Fonte de entrada: %s", type(input_source).__name__)
    logger.info("Acesse http://localhost:%s no navegador.", settings.server_port)
    logger.info("Pressione Ctrl+C para encerrar.")
    logger.info("=" * 70)

    signals = (signal.SIGINT, signal.SIGTERM)
    installed_signals: list[signal.Signals] = []
    try:
        for sig in signals:
            event_loop.add_signal_handler(sig, stop_event.set)
            installed_signals.append(sig)
        await input_source.start()
        await stop_event.wait()
    finally:
        try:
            http_server.stop()
            await input_source.stop()
        finally:
            await http_server.close_all_connections()
            for sig in installed_signals:
                event_loop.remove_signal_handler(sig)
        logger.info("Servidor finalizado.")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
