import json

from pong.api.websocket.serializer import serialize_connection_ack, serialize_paddle_update
from pong.domain.pong.state import PongState


def test_connection_ack_is_json() -> None:
    payload = json.loads(serialize_connection_ack(3))

    assert payload == {
        "type": "connection_ack",
        "message": "Conectado ao servidor Pong Tornado WebSocket",
        "clients_count": 3,
    }


def test_paddle_update_serializes_state(pong_state: PongState) -> None:
    payload = json.loads(serialize_paddle_update(pong_state))

    assert payload == {
        "type": "paddle_update",
        "player1_pct": 25.0,
        "player2_pct": 75.0,
        "timestamp": 123.0,
    }
