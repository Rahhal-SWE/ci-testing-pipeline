import pytest
from src.metrics import PingResult, parse_result_line, summarize, percentile


def test_parse_ok_line():
    r = parse_result_line("host=1.1.1.1 status=OK latency_ms=12.3")
    assert r.host == "1.1.1.1"
    assert r.ok is True
    assert r.latency_ms == 12.3


def test_parse_fail_line():
    r = parse_result_line("host=google.com status=FAIL")
    assert r.host == "google.com"
    assert r.ok is False
    assert r.latency_ms is None


@pytest.mark.parametrize(
    "line",
    [
        "host= status=OK latency_ms=12.3",
        "host=1.1.1.1 status=OK",
        "host=1.1.1.1 status=FAIL latency_ms=10.0",
        "random nonsense",
        "",
    ],
)
def test_parse_invalid_lines(line):
    with pytest.raises(ValueError):
        parse_result_line(line)


def test_summarize_empty():
    s = summarize([])
    assert s["total"] == 0
    assert s["success_rate"] == 0.0
    assert s["avg_latency_ms"] is None
    assert s["p95_latency_ms"] is None


def test_summarize_all_failures():
    results = [
        PingResult("a", False, None),
        PingResult("b", False, None),
    ]
    s = summarize(results)
    assert s["total"] == 2
    assert s["success_rate"] == 0.0
    assert s["avg_latency_ms"] is None


def test_summarize_mixed_success_rate():
    results = [
        PingResult("a", True, 10.0),
        PingResult("b", False, None),
        PingResult("c", True, 30.0),
    ]
    s = summarize(results)
    assert s["total"] == 3
    assert s["success_rate"] == pytest.approx(2 / 3)
    assert s["avg_latency_ms"] == pytest.approx(20.0)


def test_percentile_single_value():
    assert percentile([42.0], 95) == 42.0


def test_percentile_bounds():
    xs = [10.0, 20.0, 30.0]
    assert percentile(xs, 0) == 10.0
    assert percentile(xs, 100) == 30.0


def test_percentile_median():
    xs = [10.0, 20.0, 30.0, 40.0]
    assert percentile(xs, 50) == pytest.approx(25.0)


def test_percentile_95():
    xs = [1, 2, 3, 4, 100]
    assert percentile(xs, 95) > 4


def test_percentile_invalid_values():
    with pytest.raises(ValueError):
        percentile([], 50)
    with pytest.raises(ValueError):
        percentile([1.0, 2.0], -1)
    with pytest.raises(ValueError):
        percentile([1.0, 2.0], 101)
