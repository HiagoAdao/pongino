import asyncio

from queue import Empty, SimpleQueue

from rich.console import Console
from rich.live import Live
from rich.progress_bar import ProgressBar
from rich.table import Table


from pong.config import Settings
from pong.domain.potenciometro.entity import Potenciometro
from pong.domain.raquete.state import RaqueteState
from pong.infra.input.serial.source import SerialInputSource


def render_readings(state: RaqueteState | None) -> Table:
    table = Table(title="Diagnóstico dos potenciômetros")
    table.add_column("Jogador")
    table.add_column("Posição")
    table.add_column("Percentual", justify="right")

    if not state:
        for _ in range(2):
            table.add_row(
                "—",
                "Aguardando leitura",
                "—",
            )
        return table

    players_data = (
        (state.player1_pos, state.player1_pct),
        (state.player2_pos, state.player2_pct),
    )
    for player, percentage in players_data:
        table.add_row(
            str(player),
            ProgressBar(total=100, completed=percentage, width=24),
            f"{percentage:.1f}%",
        )
    return table

async def run() -> None:
    settings = Settings()
    potenciometros = (
        Potenciometro.config(
            identifier="player1",
            player=1,
            pin=settings.pot1_pin
        ),
        Potenciometro.config(
            identifier="player2",
            player=2,
            pin=settings.pot2_pin
        ),
    )
    samples: SimpleQueue[RaqueteState] = SimpleQueue()
    source = SerialInputSource(
        settings,
        potenciomentros=potenciometros,
        on_update=samples.put,
    )

    console = Console()
    console.print(f"Pinos: {settings.pot1_pin} / {settings.pot2_pin}", markup=False)
    console.print("Pressiona Ctrl+C para encerrar.", style="dim")
    try:
        await source.start()
        with Live(render_readings(None), console=console, auto_refresh=False) as live:
            while True:
                latest: RaqueteState | None = None
                try:
                    while True:
                        latest = samples.get_nowait()
                except Empty:
                    pass
                if latest is not None:
                    live.update(
                        render_readings(latest),
                        refresh=True,
                    )
                await asyncio.sleep(0.1)
    finally:
        await source.stop()


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        Console().print("Diagnóstico encerrado", style="green")


if __name__ == "__main__":
    main()