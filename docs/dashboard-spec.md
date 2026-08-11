# Thiết kế Dashboard — Day 13 AI Observability

## Phạm vi và công cụ

- Công cụ sử dụng: FastAPI endpoint `GET /metrics` để xem snapshot live; tài liệu này là dashboard spec dùng làm evidence.
- Nguồn lịch sử chuẩn: `data/logs.jsonl`, đúng contract trong `config/dashboard.yaml`.
- Khoảng thời gian mặc định: **60 phút**.
- Chu kỳ refresh đề xuất: **30 giây**.
- Dashboard chính có đúng **6 panel**.

`/metrics` lưu số liệu trong bộ nhớ của tiến trình API, phù hợp để kiểm tra live nhưng sẽ reset khi API khởi động lại. Khi cần biểu đồ lịch sử 60 phút, dashboard phải tổng hợp `data/logs.jsonl`; không coi snapshot `/metrics` là time series.

## Đặc tả 6 panel

| # | Tên panel | Snapshot live từ `/metrics` | Nguồn lịch sử và phép tính | Cách hiển thị | Đơn vị | Threshold/SLO line |
|---|---|---|---|---|---|---|
| 1 | **Latency P50/P95/P99** | `latency_p50`, `latency_p95`, `latency_p99` | `response_sent.latency_ms`; percentile P50/P95/P99 | Ba single values và line chart theo thời gian | ms | P95 ≤ **3000 ms** |
| 2 | **Request Traffic** | `traffic` | Đếm `request_received` theo từng phút | Counter tổng request và line chart request/phút | requests/minute | ≥ **1 request/phút** để đủ tín hiệu quan sát |
| 3 | **Error Rate & Breakdown** | `error_rate_pct`, `error_breakdown` | `request_failed / request_received × 100`; group theo `error_type` | Gauge tỷ lệ lỗi và bảng/bar chart loại lỗi | %, count | Error rate ≤ **2%** |
| 4 | **Cost Over Time** | `total_cost_usd`, `avg_cost_usd` | Tổng `response_sent.cost_usd` theo phút và toàn cửa sổ | Single value tổng cost và line chart cost/phút | USD | Tổng cost ≤ **2.5 USD/cửa sổ** |
| 5 | **Input & Output Tokens** | `tokens_in_total`, `tokens_out_total` | Tổng riêng `response_sent.tokens_in` và `tokens_out` | Hai single values hoặc stacked bar | tokens | Mỗi tổng ≤ **50,000 tokens/cửa sổ** |
| 6 | **Quality Average** | `quality_avg` | Trung bình `response_sent.quality_score` | Gauge hoặc single value | score 0–1 | Quality ≥ **0.75** |

## Ý nghĩa cảnh báo

- Latency, error và cost chuyển trạng thái cảnh báo khi **cao hơn** ngưỡng.
- Quality chuyển trạng thái cảnh báo khi **thấp hơn** ngưỡng.
- Traffic dưới 1 request/phút được đánh dấu thiếu dữ liệu quan sát, không mặc định kết luận dịch vụ hỏng.
- Tokens vượt ngưỡng là tín hiệu cần kiểm tra prompt, độ dài response hoặc incident `cost_spike`.

## Kiểm tra dữ liệu live

Khởi động API bằng `.env`, sau đó đọc snapshot:

```powershell
curl.exe http://127.0.0.1:8000/metrics | python -m json.tool
```

Kết quả phải có đủ 11 field:

```text
% Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100    228 100    228   0      0    823      0                              0
{
    "traffic": 10,
    "latency_p50": 154.0,
    "latency_p95": 1365.0,
    "latency_p99": 1365.0,
    "avg_cost_usd": 0.002,
    "total_cost_usd": 0.0198,
    "tokens_in_total": 330,
    "tokens_out_total": 1256,
    "error_rate_pct": 0.0,
    "error_breakdown": {},
    "quality_avg": 0.88
}
```

## Kiểm tra contract và evidence

```powershell
python scripts/validate_dashboard.py
```

Kết quả đạt yêu cầu phải có `HỢP LỆ: 6/6 panel`. Evidence của phần thiết kế gồm file spec này và kết quả validator. Nếu nhóm dựng thêm dashboard trên Grafana/Langfuse, ảnh chụp phải thấy đủ tên panel, time range 60 phút, đơn vị và threshold/SLO line.
