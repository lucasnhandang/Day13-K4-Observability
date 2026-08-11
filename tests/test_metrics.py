from app import metrics
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) == 200.0
    assert percentile(list(range(1, 21)), 95) == 19.0


def test_snapshot_exposes_error_rate_for_all_attempted_requests(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 8)
    monkeypatch.setattr(metrics, "ERRORS", metrics.Counter({"TimeoutError": 2}))

    result = metrics.snapshot()

    assert result["traffic"] == 10
    assert result["error_rate_pct"] == 20.0
    assert result["error_breakdown"] == {"TimeoutError": 2}
