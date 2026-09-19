from pathlib import Path

from tornado.web import Application, StaticFileHandler

from pong.api.http.index_handler import IndexHandler
from pong.api.websocket.connection_manager import ConnectionManager
from pong.api.websocket.handler import PongWebSocketHandler

WEB_PATH = Path(__file__).resolve().parents[1] / "web"
STATIC_PATH = WEB_PATH / "static"


def make_app(
    connection_manager: ConnectionManager | None = None,
) -> Application:
    manager = connection_manager or ConnectionManager()
    handlers = [
        (r"/", IndexHandler, {"web_path": WEB_PATH}),
        (r"/ws", PongWebSocketHandler, {"connection_manager": manager}),
        (r"/static/(.*)", StaticFileHandler, {"path": str(STATIC_PATH)}),
    ]
    return Application(
        handlers,
        static_path=str(STATIC_PATH),
        debug=False,
    )
