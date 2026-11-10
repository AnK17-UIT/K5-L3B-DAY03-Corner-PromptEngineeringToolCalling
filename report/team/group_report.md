# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi của starter trước khi tối ưu |  | 0.70 (14/20) | [Run v0](../../starter_v0/runs/v0_B_base_openrouter_20261110T175814995429.json) |
| v1 | `system_prompt.md` | Gọi `clarify` khi thiếu tài khoản hoặc URL sẽ giúp R10 và R11 đạt. | 0.70 (14/20) | 0.90 (18/20) | [Run v1](../../starter_v0/runs/v1_B_base_openrouter_20261110T180445251879.json) |
| v2 | `system_prompt.md` | Yêu cầu `clarify(response_type="yes_no")` trước khi gửi sẽ giúp R12 đạt. | 0.90 (18/20) | 0.90 (18/20) | [Run v2](../../starter_v0/runs/v2_B_base_openrouter_20261110T180925001898.json) |
| v3 | `system_prompt.md` | Tách xác nhận ý định khỏi duyệt nội dung sẽ giúp R12 hỏi `yes_no` trước. | 0.90 (18/20) | 0.85 (17/20) | [Run v3](../../starter_v0/runs/v3_B_base_openrouter_20261110T181244702942.json) |
| v4 | `tools.yaml` | Phân biệt tin web với bài đăng theo lựa chọn nguồn gần nhất sẽ giúp M02 và M06 đạt. | 0.85 (17/20) | 0.95 (19/20) | [Run v4](../../starter_v0/runs/v4_B_base_openrouter_20261110T181658156040.json) |
| v5 | `tools.yaml` | Khai báo rõ điều kiện sử dụng và tham số giúp R11 truyền `response_type` và giữ hành vi xác nhận của R12. | 0.95 (19/20) | 1.00 (20/20) | [Run v5](../../starter_v0/runs/v5_B_base_openrouter_20261110T182433343445.json) |
| v6 | `system_prompt.md` | Routing theo nguồn và theo thứ tự phụ thuộc sẽ giữ kết quả base khi bỏ quy tắc ép một tool. | 1.00 (20/20) | 0.95 (19/20) | [Run v6](../../starter_v0/runs/v6_B_base_openrouter_20261110T182703574719.json) |
| v7 | `system_prompt.md` | Tách đọc khỏi xác nhận gửi và từ chối rõ yêu cầu giải toán hoặc viết code. | 0.95 (19/20) | 0.95 (19/20) | [Run v7](../../starter_v0/runs/v7_B_base_openrouter_20261110T183204024791.json) |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run `v0` qua OpenRouter với `openai/gpt-4o-mini` chấm đủ 20 ca và có 0 lỗi provider. Tỷ lệ chọn đúng tool là 80%, tỷ lệ đúng tham số là 70%, và 6/6 ca nhiều lượt đạt. Cột Fix ghi các thay đổi đề xuất cho vòng sau.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R03_web_news_routing` | `wrong_tool` | `lookup(query="AI news", topic="news", timeframe="day", max_results=5)` | Tool đúng, nhưng `query` nhận `AI news` thay vì `AI`. | Ghi rõ chủ đề tìm kiếm nằm trong `query` và loại tin nằm trong `topic`. |
| `R08_out_of_scope` | `out_of_scope` | `send(text=...)` | Gọi tool gửi lời giải toán dù ca này yêu cầu không gọi tool. | Thêm quy tắc trả lời ngắn khi yêu cầu nằm ngoài phạm vi nghiên cứu. |
| `R10_missing_handle` | `missing_info` | `timeline(screenname="sama")` | Tự đoán tài khoản khi người dùng chưa cung cấp handle. | Gọi `clarify(response_type="text")` để hỏi tài khoản. |
| `R11_missing_url` | `missing_info` | `fetch(url="https://example.com/article")` | Tự điền URL thay vì hỏi người dùng. | Gọi `clarify(response_type="text")` để xin URL trước khi đọc. |
| `R12_confirm_before_send` | `wrong_boundary` | `send(text="Bản tin này")` | Gọi `send` trước khi xác nhận. Tool trả `needs_confirmation`. | Hỏi bằng `clarify(response_type="yes_no")` và chỉ gọi `send` sau khi người dùng xác nhận nội dung. |
| `R13_parallel_web_and_tweets` | `wrong_tool` | `lookup(query="AI news", timeframe="day", max_results=5)` và `social_search(query="AI", search_type="Latest", limit=5)` | Cả hai tool đều được gọi. `lookup` dùng sai `query` và thiếu `topic="news"`. | Tách từ khóa và bộ lọc tin tức cho nhánh web, giữ lời gọi tìm bài đăng riêng. |

Đối chiếu với `v1`, R10 và R11 chuyển sang PASS nhờ gọi `clarify(response_type="text")`. R03, R08 và R13 cũng chuyển sang PASS trong lần chạy này. R12 vẫn gọi `send` trước khi hỏi xác nhận. M02 chuyển từ PASS sang FAIL vì gọi `social_search(query="robotics")` thay cho `lookup(query="robotics", topic="news", timeframe="day")`. Tỷ lệ ca nhiều lượt giảm từ 6/6 xuống 5/6.

Ở `v2`, cả 18 ca từng PASS trong `v1` vẫn đạt. R12 chuyển từ `send` sang `clarify`, nhưng gửi `response_type="text"` để xin nội dung bản tin thay vì `yes_no` theo kỳ vọng. Điểm routing tăng từ 90% lên 95% trong khi điểm tổng giữ ở 90%. M02 vẫn chọn `social_search` cho yêu cầu tin robotics hôm nay.

Ở `v3`, R12 gọi `clarify(response_type="yes_no")` và chuyển sang PASS. Run không gọi `send`. M02 tiếp tục chọn `social_search` cho tin robotics. Hai ca chuyển từ PASS sang FAIL so với `v2`: R01 hỏi lại handle của Sam Altman thay vì gọi `timeline(screenname="sama")`, còn M06 vẫn dùng `social_search` sau khi người dùng yêu cầu chuyển sang tìm tin trên web. Tỷ lệ đạt giảm từ 18/20 xuống 17/20, và số ca nhiều lượt đạt giảm từ 5/6 xuống 4/6.

Ở `v4`, M02 và M06 dùng `lookup` cho tin web và chuyển sang PASS. R01 cũng chuyển sang PASS, còn R12 tiếp tục gọi `clarify` với `yes_no`. R11 chuyển từ PASS sang FAIL vì agent hỏi đúng URL bằng `clarify` nhưng bỏ tham số `response_type` mà eval yêu cầu. Run đạt 19/20 ca, chọn đúng tool ở 20/20 ca và đạt 6/6 ca nhiều lượt.

Ở `v5`, R11 gọi `clarify` với `response_type="text"`, R12 vẫn hỏi bằng `yes_no` và 19 ca từng PASS đều giữ kết quả. `tools.yaml` khai báo `response_type` là bắt buộc, nêu điều kiện sử dụng và quy ước tham số của các tool, và yêu cầu xác nhận nội dung chính xác trước khi gọi `send` với `confirmed=true`.

Ở `v6`, R01 chuyển từ PASS sang FAIL vì agent hỏi xác nhận bằng `clarify(response_type="yes_no")` thay vì gọi `timeline(screenname="sama")`. R12 vẫn hỏi xác nhận gửi, R13 gọi đủ hai tool và 6/6 ca nhiều lượt vẫn đạt. Kiểm tra thủ công `actual_text` của `v5` và `v6` cho thấy R08 và R14 vẫn giải toán và viết code. Hai ca PASS trong eval vì điều kiện chấm của `no_tool` chỉ xét tool call.

Ở `v7`, R01 gọi thẳng `timeline(screenname="sama")` và R12 vẫn hỏi xác nhận bằng `yes_no`. Kiểm tra `actual_text` cho thấy R08 từ chối giải tích phân và R14 từ chối viết hàm nhưng giải thích công thức Fibonacci. M06 từ PASS sang FAIL vì gọi thêm `social_search` sau khi người dùng đã chuyển sang tin web. Điểm tổng giữ ở 19/20 và số ca nhiều lượt đạt giảm xuống 5/6.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| `dedupe_sources` | [Hợp đồng tool](../../starter_v0/tools/dedupe_sources/TOOL.md), [mã Python](../../starter_v0/tools/dedupe_sources/tool.py) | Bỏ URL trùng và giữ thứ tự xuất hiện đầu tiên. | Xử lý tại chỗ, không đọc URL qua mạng. |
| Unit test tool mới | [Ba test](../../starter_v0/tests/test_tools_todo.py) | `pytest` có 70 test đạt, 14 test TODO được bỏ qua và 0 lỗi. | Test chuỗi thay cho danh sách và URL sai cú pháp trả error dict. |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Ba unit test kiểm tra thứ tự và số URL trùng, đầu vào sai kiểu, và URL sai cú pháp. Ca URL thiếu dấu đóng ngoặc kiểm tra lỗi từ bộ phân tích URL được trả dưới dạng error dict. Eval routing chỉ kiểm tra model chọn đúng tool và tham số.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
