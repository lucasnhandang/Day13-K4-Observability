# Phân chia công việc — Day 13 AI Observability

## Nguyên tắc làm việc

- Làm phần cốt lõi của lab trước; các hạng mục ghi **mở rộng** chỉ thực hiện khi checkpoint tương ứng đã đạt.
- Không sửa `config/challenge.json`, không commit `.env`, secret hoặc log chưa redact PII.
- Mỗi thành viên làm trên nhánh/PR riêng, bàn giao commit và evidence để ghi vào `submission/REPORT.md`.
- Luồng điều tra bắt buộc là **Metrics → Trace → Log theo correlation ID → Root cause**.

## Phân công theo thành viên

| Thành viên | Vai trò | Phạm vi thực hiện | File/phần chính | Đầu ra và tiêu chí bàn giao |
|---|---|---|---|---|
| **Nhân (A)** | API & Middleware | Hoàn thành CP1 middleware: xóa `contextvars` đầu mỗi request; lấy `x-request-id` hoặc tạo `req-<8-hex>`; bind `correlation_id`; trả `x-request-id` và `x-response-time-ms`. Bổ sung metadata request ở API: `user_id_hash`, `session_id`, `feature`, `model`, `env`. **Mở rộng:** exception handler nếu không làm ảnh hưởng contract hiện tại. | `app/middleware.py`, `app/main.py` | Một request `/chat` có correlation ID xuyên suốt log/response header; metadata đủ; test/PR của Nhân. Handoff cho Phụng và Mai sau khi merge để tạo dữ liệu chuẩn. |
| **Thịnh (B)** | Security Engineer | Hoàn thành CP1 PII scrubbing: bổ sung regex phù hợp, bảo đảm processor scrub chạy **trước** JSON render/ghi file; thử email, số điện thoại VN, CCCD và số thẻ mẫu. Kiểm chứng log không còn PII nguyên văn. | `app/pii.py`, `app/logging_config.py`, có thể thêm test PII | `python scripts/validate_logs.py` đạt tối thiểu 80/100; log JSON minh chứng correlation ID và các PII đã redact; test/PR của Thịnh. Review chéo log do Nhân sinh ra. |
| **Phụng (C)** | Metrics & Dashboard | Kiểm tra metrics, đặc biệt `error_rate_pct`; dựng dashboard đúng 6 nhóm chỉ số từ `data/logs.jsonl`: latency, traffic, errors, cost, tokens, quality. Giữ time range 60 phút, refresh 30 giây, tên/đơn vị/threshold theo contract. | `app/metrics.py` nếu cần chỉnh đúng contract; `config/dashboard.yaml`; dashboard runtime và evidence | `python scripts/validate_dashboard.py` báo `HỢP LỆ: 6/6 panel`; ảnh dashboard đủ 6 panel, time range, đơn vị, threshold. Cung cấp metric baseline và metric lúc practice incident cho Mai/Lợi. |
| **Lợi (D)** | SRE & Alerts Engineer | Hoàn thành CP2 SLO, 3 alert rules và 3 runbook theo triệu chứng/SLO: điều kiện, thời gian duy trì, severity, tác động, ba bước kiểm tra đầu, mitigation, owner. Alert không dựa trực tiếp vào tên implementation nội bộ. | `config/slo.yaml`, `config/alert_rules.yaml`, `docs/alerts.md` | Ba rule không còn `TODO`, trỏ đúng runbook; SLO có lý do chọn; evidence/commit của Lợi. Review với Phụng để threshold alert khớp dashboard. |
| **Mai (E)** | QA & Chief Investigator | Chạy baseline/load test, quản lý evidence và regression. Phụ trách Langfuse: tạo prompt `day13-chat` v1/v2, labels `baseline`, `candidate`, `production`; chạy trace cho từng label; đổi và rollback `production`. **Mở rộng:** quan sát trace/span RAG–LLM. Sau khi Coach release, dẫn dắt CP3 challenge và hoàn thiện report nhóm. | `.env` cục bộ (không commit), Langfuse, `scripts/load_test.py`, `scripts/inject_incident.py`, `submission/evidence/`, `submission/REPORT.md` | Tối thiểu 10 traces có metadata; hai trace thể hiện `prompt_name`, `prompt_label`, `prompt_version`; evidence rollback; kết quả full test; incident evidence metric + trace ID + correlation ID/log line + root cause/fix/prevention; report hoàn chỉnh. |

## Trình tự phối hợp và handoff

1. **0:00–0:30 — Cả nhóm:** setup, chạy `/health`, `python scripts/load_test.py`, hai validator để lưu baseline. Mai tạo checklist evidence; không đưa key Langfuse vào Git.
2. **0:30–1:30 — Nhân + Thịnh:** hoàn thành logging, correlation ID, metadata và PII. Phụng chỉ dùng `data/logs.jsonl` sau khi PR của Nhân/Thịnh được review và merge.
3. **1:30–2:15 — Phụng + Lợi + Mai:** Phụng hoàn thành dashboard contract và số liệu baseline; Lợi chốt SLO/alert/runbook từ threshold đó; Mai tạo prompt/traces và chụp evidence.
4. **2:15–3:00 — Mai dẫn dắt, cả nhóm hỗ trợ:** chạy practice incident trước. Chỉ chạy challenge chính thức sau khi Lab Coach release `config/challenge.json`. Nhân/Thịnh cung cấp log và correlation ID; Phụng cung cấp metric; Mai mở trace; Lợi đối chiếu runbook/fix. Trước 3:00, hoàn tất `python -m pytest -q`, `python scripts/validate_logs.py` và `python scripts/validate_dashboard.py`.
5. **3:00–4:00 — Hoàn thiện UI và demo:** Phụng hoàn thiện UI dashboard để dễ đọc trong lúc trình bày (đủ 6 panel, time range, đơn vị, threshold); Mai tích hợp evidence/report và điều phối rehearsal. Cả nhóm diễn tập luồng Metrics → Traces → Logs → Root cause, kiểm tra `git status --short`, xác nhận commit/PR từng người và chuẩn bị phần giải thích cá nhân. Không mở thêm hạng mục kỹ thuật mới trong giờ này, trừ lỗi chặn demo.

## Checklist evidence trước khi nộp

- [ ] Kết quả cuối `validate_logs.py` và log JSON có correlation ID/metadata, không lộ PII.
- [ ] Danh sách ít nhất 10 traces, một waterfall, hai prompt version, trace theo label/version và ảnh rollback.
- [ ] Kết quả validator dashboard cùng ảnh 6 panel runtime.
- [ ] SLO, 3 alert rules và 3 runbook hoàn thiện.
- [ ] Challenge có metric, trace ID, correlation ID/log line, root cause, fix và preventive measure.
- [ ] `submission/REPORT.md` ghi rõ đóng góp và commit/PR của Nhân, Thịnh, Phụng, Lợi, Mai.
