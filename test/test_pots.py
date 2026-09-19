import pytest

from pong.cli import pots as pots_module
from pong.domain.pong.state import PongState


def test_render_readings_without_state() -> None:
    table = pots_module.render_readings(None)

    assert table.title == "Diagnóstico dos potenciômetros"
    assert table.row_count == 2


def test_render_readings_with_state(pong_state: PongState) -> None:
    table = pots_module.render_readings(pong_state)

    assert table.row_count == 2


@pytest.mark.asyncio
async def test_run_updates_live_view_and_stops_source(
    settings,
    potentiometers,
    pong_state: PongState,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class StopLoop(Exception):
        pass

    class FakeConsole:
        def __init__(self) -> None:
            self.messages = []

        def print(self, message, **_kwargs) -> None:
            self.messages.append(message)

    class FakeLive:
        def __init__(self, *_args, **_kwargs) -> None:
            self.updates = []

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def update(self, table, refresh: bool) -> None:
            self.updates.append((table, refresh))

    class FakeSource:
        instance = None

        def __init__(self, _settings, potenciomentros, on_update) -> None:
            self.on_update = on_update
            self.start_called = False
            self.stop_called = False
            FakeSource.instance = self

        async def start(self) -> None:
            self.start_called = True
            self.on_update(pong_state)

        async def stop(self) -> None:
            self.stop_called = True

    monkeypatch.setattr(pots_module, "Settings", lambda: settings)
    monkeypatch.setattr(pots_module, "SerialInputSource", FakeSource)
    monkeypatch.setattr(pots_module, "Console", FakeConsole)
    monkeypatch.setattr(pots_module, "Live", FakeLive)

    async def stop_after_one_iteration(_delay: float) -> None:
        raise StopLoop

    monkeypatch.setattr(pots_module.asyncio, "sleep", stop_after_one_iteration)

    with pytest.raises(StopLoop):
        await pots_module.run()

    assert FakeSource.instance is not None
    assert FakeSource.instance.start_called is True
    assert FakeSource.instance.stop_called is True


def test_main_reports_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    messages = []

    class FakeConsole:
        def print(self, message, **_kwargs) -> None:
            messages.append(message)

    async def fake_run() -> None:
        return None

    def fake_asyncio_run(coroutine) -> None:
        coroutine.close()
        raise KeyboardInterrupt

    monkeypatch.setattr(pots_module, "Console", FakeConsole)
    monkeypatch.setattr(pots_module, "run", fake_run)
    monkeypatch.setattr(pots_module.asyncio, "run", fake_asyncio_run)

    pots_module.main()

    assert messages == ["Diagnóstico encerrado"]
