from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_metrics_endpoint_exposes_all_dashboard_fields() -> None:
    expected_fields = {
        "latency_p50",
        "latency_p95",
        "latency_p99",
        "traffic",
        "error_rate_pct",
        "error_breakdown",
        "total_cost_usd",
        "avg_cost_usd",
        "tokens_in_total",
        "tokens_out_total",
        "quality_avg",
    }

    with TestClient(app) as client:
        response = client.get("/metrics")

    assert response.status_code == 200
    assert expected_fields <= response.json().keys()
