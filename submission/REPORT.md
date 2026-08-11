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

- Challenge ID: `day13-k4-observability-v1`.
- Triệu chứng từ metrics: Latency là chỉ số bất thường. 5/5 request của feature `monitoring` có backend latency `2655–2661ms`, vượt ngưỡng `2000ms` của challenge; baseline gần nhất có median khoảng `156ms`, tức latency tăng khoảng 17 lần. Client quan sát `10.66–13.33s` do các request bị xếp hàng khi tác vụ retrieval blocking chạy trong request handler. Cả 5 request đều trả HTTP 200, error rate là `0%`; cost mỗi request khoảng `0.0015–0.0021 USD`, không có dấu hiệu cost spike.
- Trace ID liên quan: `fd4451c5d2c3297eb986353ecc526fc5`. Trace có tổng latency `2.66s`; span `retrieve` mất `2.50s`, còn span `generate` mất `0.15s`. Retrieval chiếm khoảng 94% thời gian xử lý và là vị trí cần ưu tiên điều tra.
- Log line/correlation ID liên quan: `data/logs.jsonl:191`, correlation ID `req-33cbdb46`, session `k4-challenge-s02`. Event `response_sent` ghi nhận `latency_ms=2658`, `cost_usd=0.001749`, `quality_score=0.9` và không có event `request_failed`.
- Root cause: RAG retrieval/vector-store dependency phản hồi chậm khoảng `2.5s`, làm tăng latency của toàn bộ request. Trong implementation hiện tại, thao tác blocking trong retrieval được thực hiện trực tiếp trên đường xử lý của route async, nên khi có nhiều request đồng thời các request tiếp theo bị xếp hàng và client latency tăng cao.
- Fix action: Trong production, đặt timeout cứng cho retrieval và chuyển sang fallback response/cache khi vector store chậm; thực hiện retrieval bằng async I/O hoặc worker thread để không block event loop; đồng thời giới hạn số document/top-k khi hệ thống đang quá tải.
- Preventive measure: Duy trì alert `HighLatencyP95` khi P95 vượt `3000ms` trong 5 phút; bổ sung dashboard riêng cho latency của span `retrieve` và theo dõi queue/event-loop blocking; propagate correlation ID vào trace metadata để nối Metrics → Trace → Log; chạy load test định kỳ với concurrency thực tế và kiểm thử timeout, cache, circuit breaker của retrieval dependency.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Lợi (D) | SRE & Alerts: chốt SLO (`config/slo.yaml`), viết 3 alert rule symptom-based (`config/alert_rules.yaml`), 3 runbook đầy đủ (`docs/alerts.md`), kiểm chứng bằng incident injection (`submission/evidence/alert_verification_loi.md`) | (điền hash sau khi tự commit) | Percentile p95 vs trung bình; alert nên bám triệu chứng thay vì tên hàm nội bộ để không vỡ khi refactor; cần threshold + thời gian duy trì để tránh alert giật do nhiễu tạm thời |
| | | | |