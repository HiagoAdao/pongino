import pytest

from pong.infra.input.serial.parser import PotStreamParser


@pytest.mark.parametrize(
    ("lines", "expected"),
    [
        (["0", ";", "1023"], (0.0, 100.0)),
        ([" 512 ", " ; ", "1023"], (50.0488758553, 100.0)),
        (["1023", ";", "0"], (100.0, 0.0)),
    ],
)
def test_parser_reads_two_adc_values(lines: list[str], expected: tuple[float, float]) -> None:
    parser = PotStreamParser()
    result: tuple[float, float] | None = None

    for line in lines:
        result = parser.feed_line(line)

    assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    "lines",
    [
        ["512", "invalid", ";", "1023"],
        ["-1", ";", "1023"],
        ["512", ";", "2048"],
        ["512", ";", ";", "1023"],
    ],
)
def test_parser_discards_malformed_sequences(lines: list[str]) -> None:
    parser = PotStreamParser()

    results = [parser.feed_line(line) for line in lines]

    assert all(result is None for result in results)


def test_parser_can_read_a_new_sequence_after_reset() -> None:
    parser = PotStreamParser()
    parser.feed_line("512")
    parser.feed_line("invalid")

    parser.feed_line("256")
    parser.feed_line(";")
    result = parser.feed_line("768")

    assert result == pytest.approx((25.0244379277, 75.0733137820))
