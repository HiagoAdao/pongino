from json import dumps

from pong.domain.pong.state import PongState


def serialize_connection_ack(client_count: int) -> str:
    return dumps(
        {
            "type": "connection_ack",
            "message": "Conectado ao servidor Pong Tornado WebSocket",
            "clients_count": client_count,
        }
    )


def serialize_paddle_update(state: PongState) -> str:
    return dumps(
        {
            "type": "paddle_update",
            "player1_pct": round(state.player1_pct, 2),
            "player2_pct": round(state.player2_pct, 2),
            "timestamp": state.timestamp,
        }
    )
