from logging import getLogger

from tornado.websocket import WebSocketHandler

from pong.api.websocket.serializer import serialize_paddle_update
from pong.domain.raquete.state import RaqueteState

logger = getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._clients: set[WebSocketHandler] = set()

    @property
    def client_count(self) -> int:
        return len(self._clients)

    def add(self, client: WebSocketHandler):
        self._clients.add(client)
        return self.client_count

    def remove(self, client: WebSocketHandler):
        self._clients.discard(client)

    def broadcast_state(self, state: RaqueteState):
        payload = serialize_paddle_update(state)
        for client in tuple(self._clients):
            try:
                client.write_message(payload)
            except Exception as error:
                logger.error("Falha ao enviar estado pelo WebSocket: %s", error)
                self._clients.discard(client)
