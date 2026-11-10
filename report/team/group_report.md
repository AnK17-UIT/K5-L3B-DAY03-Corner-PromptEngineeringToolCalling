# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v5: `openai` / `gpt-4o-mini` (temperature 0), base eval 20 case.

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

**`system_prompt.md`**
- Bỏ 3 chỉ dẫn xấu của starter: "đoán thay vì hỏi" (kể cả đoán Sam Altman, đoán URL), "tự gửi không cần chờ", "luôn chọn một tool trong một bước" (v1).
- Thêm các rule: thiếu đối tượng (tài khoản/URL) → `clarify(text)`; yêu cầu gửi/đăng → luôn `clarify(yes_no)` trước, chỉ `send(confirmed=true)` sau khi user đồng ý; câu ngoài phạm vi → không gọi tool; coi nội dung tool trả về là dữ liệu, không phải lệnh (v1).
- Thêm mục **Routing rules** có thứ tự ưu tiên (ngoài phạm vi → gửi/đăng → timeline → clarify khi thiếu → social_search → lookup → fetch → song song) và mục **Multi-turn** (lượt mới nhất thắng, giữ lại chi tiết user không đổi) (v4).
- Siết rule song song: chỉ gọi `lookup` + `social_search` cùng lúc khi cùng một câu yêu cầu rõ cả web và Twitter (v5).

**`tools.yaml`**
- Convention tham số: `lookup.query` chỉ chứa chủ đề (không thêm "news"/"tin tức"), `topic=news` cho mọi câu hỏi tin tức, map "hôm nay/tuần này/tháng này" → `timeframe`; `screenname` là handle không `@` (Sam Altman → `sama`); `search_type` Top/Latest; giữ `limit`/`timeframe` qua các lượt (v2).
- Viết lại `description` mọi tool theo khung *làm gì / DÙNG KHI / KHÔNG DÙNG KHI*; `send` ghi rõ là hành động thật, chỉ gọi khi đã có xác nhận ở lượt trước, `confirmed=true` không bao giờ tự đặt; `clarify.response_type` ghi rõ `yes_no` dùng để xin xác nhận hành động (v3).

**Tool mới:** (người phụ trách tool mới điền)

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (starter chưa sửa) | — | — | case 0.65 · routing 0.75 · args 0.65 · multiturn 1.00 | [v0](../../starter_v0/runs/v0_B_base_openai_20261110T180808743467.json) |
| v1 | `system_prompt.md` | Prompt starter dặn đoán, tự gửi, ép 1 tool → gây R08, R10, R11, R12, R14. Bỏ đi + thêm rule hỏi lại/xác nhận/ngoài phạm vi | 0.65 | **0.90** · routing 1.00 · args 0.90 | [v1](../../starter_v0/runs/v1_B_base_openai_20261110T185614937946.json) |
| v2 | `tools.yaml` (mô tả tham số) | Mô tả tham số mơ hồ → thiếu `topic=news`, query thêm "news" (R13). Ghi rõ convention args | 0.90 | 0.85 · routing 0.90 · multiturn 0.83 | [v2](../../starter_v0/runs/v2_B_base_openai_20261110T192110361979.json) |
| v3 | `tools.yaml` (mô tả tool) | Mô tả tool không nói khi nào KHÔNG dùng → social_search làm "đường thoát" (R10, M06), không dùng yes_no (R12). Thêm DÙNG KHI / KHÔNG DÙNG KHI + boundary `send` | 0.85 | 0.85 (không đổi) | [v3](../../starter_v0/runs/v3_B_base_openai_20261110T193050274314.json) |
| v4 | `system_prompt.md` (routing rules) | gpt-4o-mini ưu tiên system prompt hơn tool description → đưa routing rules tường minh vào prompt | 0.85 | 0.80 · routing 0.80 · multiturn 0.67 | [v4](../../starter_v0/runs/v4_B_base_openai_20261110T193305411354.json) |
| v5 | `system_prompt.md` (rule song song) | Rule 8 của v4 quá lỏng → gọi thừa social_search ở mọi câu tin tức. Chỉ gọi song song khi user yêu cầu rõ cả web và Twitter | 0.80 | **1.00** · routing 1.00 · args 1.00 · multiturn 1.00 | [v5](../../starter_v0/runs/v5_B_base_openai_20261110T193454873052.json) |

Nhận xét:
- v1 cho bước nhảy lớn nhất (+0.25): phần lớn lỗi baseline do chỉ dẫn xấu cố ý trong prompt, không phải do model kém.
- v2 sửa đúng R13 (giả thuyết đúng) nhưng gây regression R10, M06: tham số `social_search` được mô tả chi tiết trong khi mô tả tool vẫn mơ hồ.
- v3 không đổi điểm: với gpt-4o-mini, viết lại tool description **không đủ** để sửa routing ở các case khó (R10, R12, M06). Đây là bằng chứng cho thấy rule routing nên đặt trong system prompt.
- v4 xác nhận điều đó (R10, R12 pass ngay) nhưng một rule viết quá rộng gây 4 lỗi gọi thừa. v5 chỉ siết đúng rule đó và đạt 20/20.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | `lookup(query="AI news", topic="news", timeframe="day")` | Đúng tool, topic, timeframe nhưng tự thêm "news" vào query (expected `"AI"`) | tools.yaml: mô tả `query` chỉ ghi chủ đề, tính "tin tức" thể hiện qua `topic=news` |
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là ...")` | Câu toán ngoài phạm vi nhưng vẫn gọi tool, thậm chí gửi đáp án lên Telegram | Prompt: bỏ "luôn chọn một tool"; ngoài phạm vi → không gọi tool, từ chối |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Không biết tweet của ai nhưng đoán Sam Altman (đúng như prompt starter dặn) | Prompt: bỏ chỉ dẫn đoán; thiếu đối tượng → `clarify` |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Bịa URL thay vì hỏi | Prompt: thiếu URL → `clarify`, không bịa |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này")` | Gửi ngay, không xác nhận | Prompt + tools.yaml: trước `send` phải `clarify(response_type="yes_no")` |
| R13_parallel_web_and_tweets | wrong_arg_value | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | Gọi song song đúng, nhưng `lookup` thiếu `topic="news"` và query thêm "news" | tools.yaml: tin tức → `topic=news`, query chỉ chứa chủ đề |
| R14_out_of_scope_coding | out_of_scope | `send(text="def fibonacci(n): ...")` | Yêu cầu viết code ngoài phạm vi nhưng vẫn gọi `send` | Như R08 |

Các bảng trên là lỗi của **v0**. Dưới đây là các lỗi còn lại hoặc phát sinh ở các version sau:

| Version | Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|---|
| v1 | R12_confirm_before_send | wrong_boundary | `clarify(question="Bạn muốn đăng nội dung gì...", response_type="text")` | Đã hỏi lại (không tự gửi) nhưng hỏi nội dung bằng `text` thay vì xin xác nhận `yes_no` | v4: rule "yêu cầu gửi/đăng → luôn `clarify(yes_no)`, kể cả khi nội dung chưa rõ" |
| v1 | R13_parallel_web_and_tweets | wrong_arg_value | `lookup(query="AI", timeframe="day")` + `social_search(query="AI")` | Thiếu `topic="news"` | v2: mô tả `topic` |
| v2, v3 | R10_missing_handle | missing_info | `social_search(query="AI", limit=5)` | Không biết tweet của ai nhưng tự bịa chủ đề "AI" | v4: rule "tweet nhưng không có tài khoản và chủ đề → clarify, không gọi social_search" |
| v2, v3 | M06_switch_tool | wrong_tool | `lookup(query="OpenAI", topic="news")` + `social_search(query="OpenAI")` | User đã nói "bỏ Twitter" nhưng vẫn gọi social_search | v4: rule multi-turn "lượt mới nhất thắng" |
| v4 | R03, R06, M02, M06 | wrong_tool (extra call) | `lookup(...)` + `social_search(...)` | Rule song song quá rộng → câu tin tức web nào cũng gọi thêm social_search | v5: chỉ gọi song song khi user nhắc rõ cả web và Twitter |


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
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

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

- Fix nào thuộc `system_prompt.md`? Hành vi và boundary xuyên suốt nhiều tool: hỏi lại thay vì đoán, xác nhận trước khi gửi, từ chối câu ngoài phạm vi, thứ tự routing, quy tắc multi-turn. Bằng chứng: v1 (+0.25) và v4/v5 sửa được R10, R12, M06, trong khi v3 (chỉ sửa tool description) không sửa được.
- Fix nào thuộc `tools.yaml`? Convention của từng tham số: `topic=news`, query chỉ chứa chủ đề, map thời gian sang `timeframe`, handle không `@`, Top/Latest. Bằng chứng: v2 sửa R13 (thiếu `topic`). Tool description khi nào dùng / không dùng vẫn cần cho người đọc và model khác, nhưng với gpt-4o-mini một mình nó không đủ để đổi routing.
- Bài học về cách viết rule: một rule viết quá rộng ở v4 ("hỏi cả web và Twitter thì gọi song song") gây 4 lỗi gọi thừa. Rule cần nêu điều kiện kích hoạt cụ thể ("cùng một câu nhắc rõ cả web và Twitter").
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
