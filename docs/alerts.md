# Alert Rules và Runbook

Mỗi alert bên dưới dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên module hay implementation nội bộ. Ngưỡng khớp với `config/slo.yaml` và `config/dashboard.yaml`.

## Alert 1

- **Tên:** `high_latency_p95`
- **Severity:** `warning`
- **SLI/SLO liên quan:** `latency_p95_ms`; objective P95 ≤ 3000 ms.
- **Điều kiện và thời gian duy trì:** `latency_p95_ms > 3000 for 5 minutes`.
- **Ảnh hưởng tới người dùng:** ít nhất 5% request có thể mất hơn 3 giây, làm hội thoại phản hồi chậm hoặc người dùng gửi lại request.
- **Ba bước kiểm tra đầu tiên:**
  1. Mở panel Latency trong cửa sổ 60 phút, xác nhận P95 vượt 3000 ms liên tục 5 phút và đối chiếu Traffic để loại trừ cửa sổ quá ít mẫu.
  2. Trong Langfuse, lọc trace cùng khoảng thời gian và tag `lab`; mở một trace chậm, so sánh duration của `run`, `retrieve` và `generate` để khoanh vùng span bất thường.
  3. Lấy correlation ID của request chậm, tìm trong `data/logs.jsonl`, kiểm tra `latency_ms`, metadata request và trạng thái incident để chứng minh nguyên nhân.
- **Mitigation tạm thời:** tắt practice incident `rag_slow` nếu đang bật; chuyển sang retrieval fallback hoặc giảm tải/concurrency trong khi điều tra. Không xóa trace hay log chậm.
- **Owner:** `on-call-engineer`.

## Alert 2

- **Tên:** `error_rate_high`
- **Severity:** `critical`
- **SLI/SLO liên quan:** `error_rate_pct`; objective error rate ≤ 2%.
- **Điều kiện và thời gian duy trì:** `error_rate_pct > 2 for 3 minutes`.
- **Ảnh hưởng tới người dùng:** request `/chat` thất bại hoặc trả HTTP 5xx; người dùng không nhận được câu trả lời.
- **Ba bước kiểm tra đầu tiên:**
  1. Mở panel Error, xác nhận tỷ lệ lỗi vượt 2% liên tục 3 phút và xem `error_breakdown` để xác định loại lỗi chiếm ưu thế.
  2. Mở các trace lỗi trong Langfuse cùng khoảng thời gian; tìm span đầu tiên có lỗi và xác định lỗi nằm ở `retrieve`, `generate` hay toàn bộ `run`.
  3. Dùng correlation ID nối trace với `request_failed` trong `data/logs.jsonl`; kiểm tra `error_type`, health endpoint và trạng thái incident trước khi kết luận root cause.
- **Mitigation tạm thời:** tắt practice incident `tool_fail` nếu đang bật; bật câu trả lời fallback/degraded mode hoặc rollback thay đổi gần nhất. Giữ nguyên error evidence để điều tra.
- **Owner:** `on-call-engineer`.

## Alert 3

- **Tên:** `daily_cost_budget`
- **Severity:** `warning`
- **SLI/SLO liên quan:** `daily_cost_usd`; objective tổng cost ≤ 2.5 USD/ngày.
- **Điều kiện và thời gian duy trì:** `daily_cost_usd > 2.5 for 1 minute`.
- **Ảnh hưởng tới người dùng:** chưa nhất thiết gây lỗi tức thời, nhưng hệ thống vượt ngân sách và có nguy cơ phải giới hạn hoặc dừng dịch vụ.
- **Ba bước kiểm tra đầu tiên:**
  1. Mở panel Cost và Tokens, xác nhận tổng cost vượt 2.5 USD, kiểm tra mức tăng theo phút và xác định input hay output token tăng bất thường.
  2. Trong Langfuse, nhóm cost/token theo model, feature và prompt version; tìm nhóm đóng góp lớn nhất thay vì chỉ nhìn tổng chi phí.
  3. Mở các trace có cost cao nhất, kiểm tra `usage_details`, `cost_details`, prompt version và trạng thái incident `cost_spike` để xác định nguồn tăng.
- **Mitigation tạm thời:** tắt practice incident `cost_spike` nếu đang bật; giới hạn output token, giảm traffic không thiết yếu hoặc rollback prompt/model gây tăng chi phí.
- **Owner:** `team-lead`.

## Quy tắc vận hành chung

- Acknowledge alert và ghi thời điểm bắt đầu điều tra.
- Mọi kết luận root cause phải có metric cụ thể, trace ID và log line/correlation ID tương ứng.
- Sau mitigation, theo dõi ít nhất bằng đúng duration của alert để xác nhận SLI đã trở lại ngưỡng.
- Ghi fix dài hạn và preventive measure vào `submission/REPORT.md`; không coi việc tắt alert là một mitigation hợp lệ.
- `quality_score_avg` vẫn được theo dõi trên dashboard. Nhóm chưa tạo paging alert riêng vì đây là quality proxy; cần thêm dữ liệu đánh giá trước khi chọn duration đủ tin cậy.
