from re import IGNORECASE, compile
from pong.domain.potenciometro.normalization import adc_to_percent, clamp


_PREFIX_PATTERN = compile(
    r"P1\s*:\s*(?P<p1>[-+]?\d*\.?\d+)\s*,\s*P2\s*:\s*(?P<p2>[-+]?\d*\.?\d+)",
    IGNORECASE,
)


def _normalize_serial_value(value: float) -> float:
    return adc_to_percent(value) if value > 100.0 else clamp(value)


def parse_serial_line(line: str) -> tuple[float, float]:
    clean_line = line.strip()
    if not clean_line or ("," not in clean_line and ";" not in clean_line):
        raise ValueError(f"Linha serial é inválida ou sem separador: '{clean_line}'")

    standart = clean_line.replace(";", ",")
    prefix_math = _PREFIX_PATTERN.search(standart)
    if prefix_math:
        value1 = float(prefix_math.group('p1'))
        value2 = float(prefix_math.group('p2'))
        return _normalize_serial_value(value1), _normalize_serial_value(value2)

    try:
        part1, part2 = standart.split(",")
        value1 = float(part1)
        value2 = float(part2)
    except ValueError as err:
        raise err

    return _normalize_serial_value(value1), _normalize_serial_value(value2)


class PotStreamParser:
    def __init__(self) -> None:
        self._pending_value1: int | None = None
        self._separator_received = False

    def feed_line(self, line: str) -> tuple[float, float] | None:
        clean_line = line.strip()
        if not clean_line:
            return

        if (";" in clean_line and clean_line != ";") or ("," in clean_line and clean_line != ","):
            try:
                return parse_serial_line(clean_line)
            except ValueError:
                return

        if clean_line == ";":
            if self._pending_value1 is not None:
                self._separator_received = True
            return

        try:
            value = int(float(clean_line))
        except ValueError:
            return

        if self._pending_value1 is not None and self._separator_received:
            value1 = self._pending_value1
            self.reset()
            try:
                return adc_to_percent(value1), adc_to_percent(value)
            except ValueError:
                return

        self._pending_value1 = value
        self._separator_received = False
        return

    def reset(self) -> None:
        self._pending_value1 = None
        self._separator_received = False
