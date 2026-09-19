from logging import getLogger

from tornado.websocket import WebSocketHandler

from pong.api.websocket.connection_manager import ConnectionManager
from pong.api.websocket.serializer import serialize_connection_ack

logger = getLogger(__name__)


class PongWebSocketHandler(WebSocketHandler):
    def initialize(self, connection_manager: ConnectionManager) -> None:
        self._connection_manager = connection_manager

    def check_origin(self, origin: str) -> bool:
        return True

    def open(self, *args: str, **kwargs: str) -> None:
        client_count = self._connection_manager.add(self)
        logger.info("Cliente WebSocket conectado: %s", self.request.remote_ip)
        self.write_message(serialize_connection_ack(client_count))

    def on_close(self) -> None:
        self._connection_manager.remove(self)
        logger.info("Cliente WebSocket desconectado")

    def on_message(self, message: str | bytes) -> None:
        logger.debug("Mensagem WebSocket recebida: %s", message)
