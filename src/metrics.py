from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional
import re
import statistics


@dataclass(frozen=True)
class PingResult:
    host: str
    ok: bool
    latency_ms: Optional[float]  # None if failed


_PING_RE = re.compile(
    r"host=(?P<host>[a-zA-Z0-9\.\-]+)\s+status=(?P<status>OK|FAIL)(?:\s+latency_ms=(?P<lat>\d+(\.\d+)?))?$"
)


def parse_result_line(line: str) -> PingResult:
    """
    Parse a structured ping log line.

    Expected formats:
      "host=1.1.1.1 status=OK latency_ms=12.3"
      "host=google.com status=FAIL"

    Raises:
      ValueError if the line is invalid.
    """
    line = line.strip()
    m = _PING_RE.match(line)
    if not m:
        raise ValueError(f"Invalid log line: {line}")

    host = m.group("host")
    status = m.group("status")
    lat_str = m.group("lat")

    ok = status == "OK"
    latency = float(lat_str) if lat_str is not None else None

    if ok and latency is None:
        raise ValueError("OK status must include latency_ms")
    if not ok and latency is not None:
        raise ValueError("FAIL status must not include latency_ms")

    return PingResult(host=host, ok=ok, latency_ms=latency)


def summarize(results: Iterable[PingResult]) -> dict:
    """
    Return summary metrics:
      - total
      - success_rate (0..1)
      - avg_latency_ms (None if no successes)
      - p95_latency_ms (None if < 1 success)
    """
    results = list(results)
    total = len(results)
    if total == 0:
        return {
            "total": 0,
            "success_rate": 0.0,
            "avg_latency_ms": None,
            "p95_latency_ms": None,
        }

    oks = [r for r in results if r.ok and r.latency_ms is not None]
    success_rate = len(oks) / total

    latencies = [r.latency_ms for r in oks]  # type: ignore[list-item]
    if not latencies:
        return {
            "total": total,
            "success_rate": success_rate,
            "avg_latency_ms": None,
            "p95_latency_ms": None,
        }

    avg_latency = statistics.fmean(latencies)
    p95 = percentile(latencies, 95)

    return {
        "total": total,
        "success_rate": success_rate,
        "avg_latency_ms": avg_latency,
        "p95_latency_ms": p95,
    }


def percentile(values: list[float], p: float) -> float:
    """
    Compute percentile using linear interpolation between closest ranks.
    Requires non-empty list and 0<=p<=100
    """
    if not values:
        raise ValueError("values must be non-empty")
    if not (0 <= p <= 100):
        raise ValueError("p must be between 0 and 100")

    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]

    k = (len(xs) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    if f == c:
        return xs[f]
    d0 = xs[f] * (c - k)
    d1 = xs[c] * (k - f)
    return d0 + d1
