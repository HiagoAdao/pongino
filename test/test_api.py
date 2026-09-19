import json
import socket

import pytest
import pytest_asyncio
from tornado.httpclient import AsyncHTTPClient
from tornado.httpserver import HTTPServer
from tornado.netutil import bind_sockets
from tornado.websocket import websocket_connect

import pong.api.app as app_module
from pong.api.app import make_app
from pong.api.websocket.connection_manager import ConnectionManager
from pong.api.websocket.handler import PongWebSocketHandler


@pytest_asyncio.fixture
async def running_app():
    manager = ConnectionManager()
    app = make_app(manager)
    sockets = bind_sockets(0, address="127.0.0.1", family=socket.AF_INET)
    server = HTTPServer(app)
    server.add_sockets(sockets)
    port = sockets[0].getsockname()[1]

    yield f"http://127.0.0.1:{port}", manager

    server.stop()
    await server.close_all_connections()


@pytest_asyncio.fixture
async def running_app_without_index(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(app_module, "WEB_PATH", tmp_path)
    monkeypatch.setattr(app_module, "STATIC_PATH", tmp_path)
    app = make_app()
    sockets = bind_sockets(0, address="127.0.0.1", family=socket.AF_INET)
    server = HTTPServer(app)
    server.add_sockets(sockets)
    port = sockets[0].getsockname()[1]

    yield f"http://127.0.0.1:{port}"

    server.stop()
    await server.close_all_connections()


@pytest.mark.asyncio
async def test_index_and_static_routes_are_served(running_app) -> None:
    base_url, _manager = running_app
    client = AsyncHTTPClient(force_instance=True)

    try:
        index_response = await client.fetch(base_url)
        favicon_response = await client.fetch(f"{base_url}/static/favicon.svg")
    finally:
        client.close()

    assert index_response.code == 200
    assert b"DISTRIBUTED PONG" in index_response.body
    assert favicon_response.code == 200
    assert b"<svg" in favicon_response.body


@pytest.mark.asyncio
async def test_index_route_has_fallback_when_file_is_missing(running_app_without_index) -> None:
    client = AsyncHTTPClient(force_instance=True)

    try:
        response = await client.fetch(running_app_without_index)
    finally:
        client.close()

    assert response.code == 200
    assert b"Frontend em carregamento" in response.body


@pytest.mark.asyncio
async def test_websocket_sends_connection_ack(running_app) -> None:
    base_url, manager = running_app
    websocket_url = base_url.replace("http://", "ws://") + "/ws"

    connection = await websocket_connect(websocket_url)
    message = await connection.read_message()
    connection.close()

    assert isinstance(message, str)
    assert json.loads(message) == {
        "type": "connection_ack",
        "message": "Conectado ao servidor Pong Tornado WebSocket",
        "clients_count": 1,
    }
    assert manager.client_count == 1


def test_websocket_handler_accepts_origin_and_logs_messages(caplog) -> None:
    handler = PongWebSocketHandler.__new__(PongWebSocketHandler)

    assert handler.check_origin("https://example.test") is True
    with caplog.at_level("DEBUG", logger="pong.api.websocket.handler"):
        handler.on_message("ping")

    assert "Mensagem WebSocket recebida: ping" in caplog.text
