# Kiểm chứng Alert Rules — Lợi (SRE & Alerts)

Xác nhận 3 alert rule trong `config/alert_rules.yaml` thực sự bắt được triệu chứng, bằng cách bật từng incident trong `app/incidents.py` qua `scripts/inject_incident.py`, tạo traffic bằng `scripts/load_test.py`, và đọc `/metrics`.

## Baseline (không bật incident)

```
{"traffic":20,"latency_p50":1019.0,"latency_p95":1482.0,"latency_p99":1482.0,
 "avg_cost_usd":0.0019,"total_cost_usd":0.0372,"error_breakdown":{},"quality_avg":0.88}
```

Tất cả trong ngưỡng SLO (`config/slo.yaml`): p95 < 3000ms, error 0% < 2%, cost tích lũy nhỏ, quality 0.88 > 0.75.

## Alert 1 — `high_latency_p95` (`rag_slow`)

Lệnh: `inject_incident.py --scenario rag_slow` → `load_test.py`

```
{"traffic":30,"latency_p95":3540.0,"latency_p99":3752.0, ...}
```

Kết quả: p95 = 3540ms > ngưỡng 3000ms → điều kiện `latency_p95_ms > 3000 for 5 minutes` trong `config/alert_rules.yaml` sẽ khớp. Runbook: `docs/alerts.md#alert-1`.

## Alert 2 — `error_rate_high` (`tool_fail`)

Lệnh: `inject_incident.py --scenario tool_fail` → `load_test.py`

```
10/10 request trả về HTTP 500
"error_breakdown":{"RuntimeError":10}
```

Kết quả: 100% request trong batch lỗi (RuntimeError) → vượt xa ngưỡng `error_rate_pct > 2 for 5 minutes`. Runbook: `docs/alerts.md#alert-2`.

Log line minh chứng (`data/logs.jsonl`), có `correlation_id` xuyên suốt và root cause cụ thể:

```json
{"service": "api", "error_type": "RuntimeError", "payload": {"detail": "Vector store timeout", "message_preview": "How do I debug tail latency?"}, "event": "request_failed", "correlation_id": "req-9e7abcd1", "session_id": "s08", "model": "gpt-4o-mini", "env": "dev", "feature": "qa", "user_id_hash": "2f015d970c0b", "level": "error", "ts": "2026-08-11T08:23:39.236215Z"}
```

Điều này khớp đúng bước 2–3 của runbook Alert 2: mở trace theo `correlation_id` → thấy span RAG/vector-store timeout → lọc log theo cùng `correlation_id` để xác nhận `detail: "Vector store timeout"` là root cause.

## Alert 3 — `daily_cost_budget` (`cost_spike`)

Lệnh: `inject_incident.py --scenario cost_spike` → `load_test.py`

```
Baseline: avg_cost_usd ≈ 0.0018 / request
Khi cost_spike bật: avg cost batch này ≈ (0.1413 - 0.0586) / 10 ≈ 0.0083 / request
```

Kết quả: cost/request tăng ~4.6 lần so với baseline → vượt điều kiện `cost_rate_per_minute > 2x baseline for 10 minutes`. Runbook: `docs/alerts.md#alert-3`.

## Kết luận

Cả 3 alert rule đều được kích hoạt đúng bởi kịch bản incident tương ứng và trỏ đúng runbook. Sau mỗi lần test đã tắt incident (`--disable`) để trả hệ thống về baseline sạch.
