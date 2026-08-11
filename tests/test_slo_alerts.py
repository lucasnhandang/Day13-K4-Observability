from __future__ import annotations

import re
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_slo_contract_has_four_documented_slis() -> None:
    payload = yaml.safe_load((REPO_ROOT / "config" / "slo.yaml").read_text(encoding="utf-8"))
    slis = payload["slis"]

    assert set(slis) == {
        "latency_p95_ms",
        "error_rate_pct",
        "daily_cost_usd",
        "quality_score_avg",
    }
    for sli in slis.values():
        assert isinstance(sli["objective"], (int, float))
        assert isinstance(sli["target"], (int, float))
        assert sli["note"]
        assert "replace" not in sli["note"].lower()


def test_three_symptom_alerts_link_to_complete_runbooks() -> None:
    config_text = (REPO_ROOT / "config" / "alert_rules.yaml").read_text(encoding="utf-8")
    runbook_text = (REPO_ROOT / "docs" / "alerts.md").read_text(encoding="utf-8")
    alerts = yaml.safe_load(config_text)["alerts"]

    assert len(alerts) == 3
    assert "TODO" not in config_text
    assert "TODO" not in runbook_text
    assert {alert["name"] for alert in alerts} == {
        "high_latency_p95",
        "error_rate_high",
        "daily_cost_budget",
    }

    for index, alert in enumerate(alerts, start=1):
        assert alert["severity"] in {"warning", "critical"}
        assert alert["type"] == "symptom-based"
        assert alert["owner"]
        assert re.search(r"for \d+ minutes?", alert["condition"])
        assert alert["runbook"] == f"docs/alerts.md#alert-{index}"
        assert f"## Alert {index}" in runbook_text

    assert runbook_text.count("**Ba bước kiểm tra đầu tiên:**") == 3
    assert runbook_text.count("**Mitigation tạm thời:**") == 3
    assert runbook_text.count("**Owner:**") == 3
