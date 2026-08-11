# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: High Latency (P95 Response Time)
- Severity: Warning (nâng lên Critical nếu duy trì liên tục trên 15 phút)
- SLI/SLO liên quan: `latency_p95_ms` ≤ 3000ms, target 99.5% (config/slo.yaml)
- Điều kiện và thời gian duy trì: p95 latency (cửa sổ rolling 5 phút) > 3000ms, duy trì liên tục ≥ 5 phút
- Ảnh hưởng tới người dùng: Chat phản hồi chậm rõ rệt, cảm giác đơ/treo; người dùng có thể bỏ ngang phiên chat
- Ba bước kiểm tra đầu tiên:
  1. Xem panel Latency (p50/p95/p99) trên dashboard để xác nhận mức tăng và khoảng thời gian bị ảnh hưởng
  2. Mở trace mới nhất trong Langfuse ở khoảng thời gian alert nổ ra, xác định span nào (RAG retrieval, LLM call, hay tool call) chiếm phần lớn thời gian
  3. Lọc log theo `correlation_id` của các request chậm để kiểm tra có kèm lỗi/timeout hay không
- Mitigation tạm thời: Nếu span RAG retrieval là nguyên nhân, giảm tạm số lượng document retrieve hoặc bật cache; nếu do một dependency cụ thể chậm, fallback tạm thời sang phản hồi rút gọn/không dùng RAG
- Owner: On-call SRE (Lợi)

## Alert 2

- Tên: Elevated Error Rate
- Severity: Critical
- SLI/SLO liên quan: `error_rate_pct` ≤ 2%, target 99.0% (config/slo.yaml)
- Điều kiện và thời gian duy trì: error rate (cửa sổ rolling 5 phút) > 2%, duy trì liên tục ≥ 5 phút
- Ảnh hưởng tới người dùng: Một phần request bị fail hoàn toàn — người dùng nhận lỗi hoặc không có phản hồi
- Ba bước kiểm tra đầu tiên:
  1. Xem panel Errors (error_rate_pct và breakdown theo `error_type`) trên dashboard để biết loại lỗi chiếm ưu thế
  2. Tìm trace tương ứng trong Langfuse, xác định span fail (tool call, LLM call, hay validation)
  3. Lọc log theo `correlation_id` của các request lỗi để lấy nguyên nhân cụ thể
- Mitigation tạm thời: Nếu lỗi tập trung ở một tool/dependency, tạm thời disable tool đó hoặc retry với backoff; nếu do input không hợp lệ, trả lỗi rõ ràng (4xx) cho client thay vì lỗi hệ thống (5xx)
- Owner: On-call SRE (Lợi)

## Alert 3

- Tên: Cost Budget Burn
- Severity: Warning
- SLI/SLO liên quan: `daily_cost_usd` ≤ 2.5, target 100% (config/slo.yaml)
- Điều kiện và thời gian duy trì: Tổng cost trong time range hiện tại (60 phút) vượt 2.5 USD, hoặc tốc độ cost/phút tăng gấp đôi baseline, duy trì liên tục ≥ 10 phút
- Ảnh hưởng tới người dùng: Không ảnh hưởng UX ngay lập tức, nhưng rủi ro vượt ngân sách vận hành, có thể dẫn tới việc phải giới hạn/tắt tính năng nếu không xử lý kịp
- Ba bước kiểm tra đầu tiên:
  1. Xem panel Cost (sum theo phút) và panel Tokens trên dashboard để xác định tăng do tần suất request hay do token/response dài bất thường
  2. Mở trace của các request cost cao nhất trong Langfuse, kiểm tra model và tokens_in/tokens_out
  3. Lọc log theo `feature`/`model` để xác định có phải một feature hoặc model cụ thể đang gây tăng cost
- Mitigation tạm thời: Giới hạn `max_tokens` hoặc chuyển tạm sang model rẻ hơn cho feature gây spike; áp rate-limit tạm thời nếu nguyên nhân là traffic bất thường
- Owner: On-call SRE (Lợi)
