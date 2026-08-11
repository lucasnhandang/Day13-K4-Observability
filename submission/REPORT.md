# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 30/100
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: (Phụng điền sau khi hoàn thiện dashboard UI)
- Evidence dashboard: (Phụng bổ sung ảnh 6 panel)
- SLO đã chọn và lý do (`config/slo.yaml`):
  - `latency_p95_ms` ≤ 3000ms, target 99.5% — chat là tương tác thời gian thực, p95 > 3s bị cảm nhận là treo/lỗi.
  - `error_rate_pct` ≤ 2%, target 99.0% — pipeline phụ thuộc RAG/tool ngoài nên chấp nhận lỗi thoáng qua nhỏ, quá 2% nghĩa là người dùng thực sự không nhận được phản hồi.
  - `daily_cost_usd` ≤ 2.5, target 100% — ngân sách demo/lab cho mỗi khung thời gian theo dõi, khớp threshold cost trên dashboard.
  - `quality_score_avg` ≥ 0.75, target 95% — ngưỡng tối thiểu để câu trả lời còn hữu ích.
- Alert rules và runbook (`config/alert_rules.yaml`, `docs/alerts.md`):
  - `HighLatencyP95` (warning) — p95 > 3000ms/5m → runbook `docs/alerts.md#alert-1`.
  - `ElevatedErrorRate` (critical) — error rate > 2%/5m → runbook `docs/alerts.md#alert-2`.
  - `CostBudgetBurn` (warning) — cost/phút > 2x baseline/10m → runbook `docs/alerts.md#alert-3`.
  - Đã kiểm chứng cả 3 alert bằng `scripts/inject_incident.py` (`rag_slow`, `tool_fail`, `cost_spike`) + `scripts/load_test.py`, log/metric minh chứng: `submission/evidence/alert_verification_loi.md`.

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Lợi (D) | SRE & Alerts: chốt SLO (`config/slo.yaml`), viết 3 alert rule symptom-based (`config/alert_rules.yaml`), 3 runbook đầy đủ (`docs/alerts.md`), kiểm chứng bằng incident injection (`submission/evidence/alert_verification_loi.md`) | (điền hash sau khi tự commit) | Percentile p95 vs trung bình; alert nên bám triệu chứng thay vì tên hàm nội bộ để không vỡ khi refactor; cần threshold + thời gian duy trì để tránh alert giật do nhiễu tạm thời |
| | | | |
