from pong.domain.potenciometro.normalization import adc_to_percent


class PotStreamParser:
    def __init__(self) -> None:
        self._pending_value: int | None = None
        self._separator_received = False

    def feed_line(self, line: str) -> tuple[float, float] | None:
        clean_line = line.strip()
        if clean_line == ";":
            self._receive_separator()
            return

        try:
            value = int(clean_line)
        except ValueError:
            self.reset()
            return

        return self._receive_value(value)

    def _receive_separator(self) -> None:
        if self._pending_value is not None and not self._separator_received:
            self._separator_received = True
        else:
            self.reset()

    def _receive_value(self, value: int) -> tuple[float, float] | None:
        if not 0 <= value <= 1023:
            self.reset()
            return

        if self._pending_value is not None and self._separator_received:
            result = adc_to_percent(self._pending_value), adc_to_percent(value)
            self.reset()
            return result

        self._pending_value = value
        return

    def reset(self) -> None:
        self._pending_value = None
        self._separator_received = False
