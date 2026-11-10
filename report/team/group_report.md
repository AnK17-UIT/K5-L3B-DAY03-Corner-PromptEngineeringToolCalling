# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v8: `openai` / `gpt-4o-mini` (temperature 0), base eval 20 case, group eval 10 case.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent về AI/công nghệ: tìm tin tức trên web, xem tweet của một tài khoản hoặc theo chủ đề, xem thảo luận trên Hacker News, đọc và tóm tắt một URL, tìm paper arXiv. Agent hỏi lại khi thiếu thông tin, từ chối câu ngoài phạm vi, và chỉ gửi lên Telegram sau khi người dùng xác nhận.

**Cách chạy UI:**

```powershell
cd starter_v0
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt   # đã có streamlit>=1.39
streamlit run app.py                        # http://localhost:8501
```

UI (`starter_v0/app.py`) dùng cùng vòng lặp model → tool với `chat.py`, prompt/tools bản v8. Mỗi tool call được hiện trong một ô mở rộng kèm kết quả thô; ô báo lỗi tự mở ra, không che lỗi. Mỗi phiên chat ghi transcript vào `starter_v0/transcripts/`.

**Link dùng thử (deploy):**

```powershell
cloudflared tunnel --url http://localhost:8501
```

> URL: (dán link `https://....trycloudflare.com` khi mở tunnel trong buổi showdown)

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin, hoặc xin xác nhận (yes/no) trước khi gửi | không |
| timeline | Lấy tweet gần đây của một tài khoản X/Twitter (RapidAPI) | không |
| social_search | Tìm tweet theo chủ đề, sắp xếp Top/Latest (RapidAPI) | không |
| lookup | Tìm tin tức / thông tin trên web, có topic và khoảng thời gian (Tavily) | không |
| fetch | Đọc nội dung một URL cụ thể (Firecrawl) | không |
| format | Trình bày kết quả thành digest markdown | không |
| send | Gửi tin lên kênh Telegram, chỉ khi `confirmed=true` | không |
| policy | Tìm trong chính sách nội bộ công ty | không |
| papers / paper_text | Tìm paper arXiv / trích text của một paper | không |
| **hn_search** | Tìm story và thảo luận trên Hacker News, sắp xếp theo độ nổi bật hoặc mới nhất (Algolia API, không cần key) | **có** |

### A3. Câu hỏi mẫu để thử

1. `Tin AI hôm nay có gì nổi bật?` → `lookup(topic=news, timeframe=day)`
2. `Tóm tắt 3 tweet mới nhất giúp mình` → agent hỏi lại "của ai?", trả lời `Của Sam Altman` → `timeline(sama, 3)`
3. `Dân dev trên Hacker News đang bàn gì về Rust?` → tool mới `hn_search`
4. `Tóm tắt bài này giúp mình: https://openai.com/research/` → `fetch`
5. `Đăng bản tin AI hôm nay lên Telegram giúp mình` → agent xin xác nhận yes/no, không tự gửi

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

- Thêm rule 6b (nhắc Hacker News → chỉ `hn_search`) (v6); thêm rule "nguồn đã bỏ thì bỏ luôn ở các lượt sau" kèm ví dụ 3 lượt (v7).
- `tools.yaml`: khai báo `hn_search` (v6); đặt `topic` và `timeframe` của `lookup` thành `required` để model không bỏ sót (v8).

**Tool mới: `hn_search`** (`starter_v0/tools/hn_search/`)
- Làm gì: tìm story trên Hacker News qua API công khai `hn.algolia.com` (không cần key). Tham số: `query`, `sort` (`relevance` | `date`), `limit` (1–20). Trả về `title`, `url` (nếu không có link gốc thì dùng link thảo luận HN), `discussion_url`, `points`, `num_comments`, `published_at`.
- Khi nào agent nên gọi: user nhắc rõ Hacker News/HN hoặc hỏi dân developer trên HN bàn gì. Không dùng cho tin web chung (`lookup`) hay Twitter (`social_search`).
- An toàn khi nhận input xấu từ model: query rỗng hoặc sai kiểu → trả error dict, không gọi mạng; `limit` sai kiểu → về mặc định 5, ngoài khoảng → kẹp vào 1–20; `sort` ngoài enum → `relevance`; lỗi HTTP hoặc timeout → error dict, không raise.

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
| v6 | `tools.yaml` + `system_prompt.md` (tool mới) | Thêm `hn_search` kèm rule 6b riêng sẽ không làm giảm điểm base | 1.00 | 0.95 · routing 0.95 · multiturn 0.83 | [v6](../../starter_v0/runs/v6_B_base_openai_20261110T194740096863.json) |
| v7 | `system_prompt.md` (multi-turn) | M06 gọi lại social_search ở lượt 3 vì rule chưa nói nguồn đã bỏ phải bỏ luôn ở các lượt sau. Thêm rule + ví dụ 3 lượt | 0.95 | 0.95 · routing **1.00** · args 0.95 | [v7](../../starter_v0/runs/v7_B_base_openai_20261110T194957616440.json) |
| v8 | `tools.yaml` (`required`) | M02 bỏ hẳn tham số `timeframe` (optional). Đặt `topic`, `timeframe` của lookup thành required sẽ buộc model luôn điền | 0.95 | **1.00** · routing 1.00 · args 1.00 · multiturn 1.00 (chạy 2 lần đều 20/20) | [v8 lần 1](../../starter_v0/runs/v8_B_base_openai_20261110T195144622966.json), [v8 lần 2](../../starter_v0/runs/v8_B_base_openai_20261110T195304854321.json) |

**Bản nộp cuối: v8** (base 20/20 hai lần chạy liên tiếp; group 10/10, xem B3).

Nhận xét:
- v1 cho bước nhảy lớn nhất (+0.25): phần lớn lỗi baseline do chỉ dẫn xấu cố ý trong prompt, không phải do model kém.
- v2 sửa đúng R13 (giả thuyết đúng) nhưng gây regression R10, M06: tham số `social_search` được mô tả chi tiết trong khi mô tả tool vẫn mơ hồ.
- v3 không đổi điểm: với gpt-4o-mini, viết lại tool description **không đủ** để sửa routing ở các case khó (R10, R12, M06). Đây là bằng chứng cho thấy rule routing nên đặt trong system prompt.
- v4 xác nhận điều đó (R10, R12 pass ngay) nhưng một rule viết quá rộng gây 4 lỗi gọi thừa. v5 chỉ siết đúng rule đó và đạt 20/20.
- v6 (thêm tool mới) không làm hỏng các case liên quan tới tool mới, nhưng M06 (multi-turn) lại fail. v5 pass M06 còn v6 fail dù rule về Twitter không đổi, cho thấy các case multi-turn khó còn dao động giữa các lần chạy, kể cả ở temperature 0. v7 sửa M06 bằng ví dụ cụ thể; v8 chặn kiểu lỗi "bỏ sót tham số optional" bằng `required`. Vì vậy nhóm chạy v8 **hai lần** để kiểm tra độ ổn định, cả hai lần đều 20/20.

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
| v6 | M06_switch_tool | wrong_tool (extra call) | `lookup(query="OpenAI", topic="news")` + `social_search(query="OpenAI")` | Lượt 3 "Giữ chủ đề OpenAI" không nhắc nguồn → model lấy lại Twitter từ lượt 1 | v7: rule "nguồn đã bỏ thì bỏ luôn" + ví dụ 3 lượt |
| v7 | M02_carryover_timeframe | wrong_arg_value | `lookup(query="robotics", topic="news")` | Không truyền `timeframe` (None) dù user nói "vẫn là tin hôm nay" | v8: `timeframe`, `topic` thành `required` |


### B3. Team Eval Cases

10 case trong [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json) (5 single turn G01–G05, 5 multi turn G06–G10). Run: [v8 group](../../starter_v0/runs/v8_B_group_openai_20261110T195437068747.json): 10/10, `provider_error_cases = 0`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_hn_routing | Nhắc rõ Hacker News → **tool mới** `hn_search`, không phải lookup/social_search | `hn_search(query="Rust")` | PASS |
| G02_hn_sort_date_limit | Viết tắt "HN" vẫn route đúng; "mới nhất" → `sort=date`; "3 bài" → `limit=3` | `hn_search(query="LLM agents", sort="date", limit=3)` | PASS |
| G03_lookup_timeframe_month | "tháng này" → `timeframe=month` (base chỉ phủ day/week) | `lookup(query="Nvidia", topic="news", timeframe="month")` | PASS |
| G04_send_pressure_skip_confirm | User đòi "gửi ngay, khỏi hỏi lại" → vẫn phải xác nhận | `clarify(response_type="yes_no")` | PASS |
| G05_out_of_scope_email | Viết email cá nhân (có chữ "gửi" gây nhiễu) là ngoài phạm vi | không gọi tool | PASS |
| G06_mt_hn_switch_to_twitter_top | Chuyển từ tool mới sang Twitter, giữ chủ đề, "hot nhất" → Top | `social_search(query="Bun", search_type="Top")` | PASS |
| G07_mt_send_after_confirmation | Agent đã hỏi, user "Ừ, gửi đi" → gửi thật, không hỏi lại | `send(confirmed=true)` | PASS |
| G08_mt_send_declined | User từ chối ở bước xác nhận → không gửi | không gọi tool | PASS |
| G09_mt_missing_account_then_name | Thiếu tài khoản rồi bổ sung tên → map handle + giữ limit | `timeline(screenname="demishassabis", limit=3)` | PASS |
| G10_mt_papers_latest | Paper → `papers`; lượt 2 đổi args, giữ query | `papers(query="RAG evaluation", max_results=3, sort_by="submittedDate")` | PASS |

### B4. Live Chat Evidence

Transcript: [`v8_openai_20261110T195450670769.transcript.json`](../../starter_v0/transcripts/v8_openai_20261110T195450670769.transcript.json) (`python chat.py --provider openai --version v8`, artifact `v8+pdc6f8b98960c+td344a27b23d8`).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin AI hôm nay có gì nổi bật? | `lookup(query="AI", topic="news", timeframe="day")` | v8 | Yêu cầu research thường: trả 5 tin có link nguồn. Hạn chế: trả lời bằng tiếng Anh dù user hỏi tiếng Việt |
| 2 | Tóm tắt 3 tweet mới nhất giúp mình | `clarify(question="...của tài khoản nào?", response_type="text")` | v8 | Thiếu thông tin → hỏi lại, không đoán |
| 3 | Của Sam Altman | `timeline(screenname="sama", limit=3)` | v8 | Bổ sung thông tin → map tên sang handle, giữ `limit=3` từ lượt 2 |
| 4 | Dân dev trên Hacker News đang bàn gì về AI agents? | `hn_search(query="AI agents", sort="relevance", limit=5)` | v8 | Route đúng tool mới, trả về 5 story kèm điểm và link thảo luận |
| 5 | Đăng bản tin tóm tắt mấy tin AI hôm nay lên Telegram giúp mình | `clarify(question="...Bạn có xác nhận gửi bản tin này không?")` | v8 | Yêu cầu gửi → soạn sẵn nội dung và xin xác nhận, **không** gọi `send` |
| 6 | Khoan, đừng gửi, để mình xem lại đã | (không gọi tool) | v8 | User từ chối → không gửi, chỉ trả lời text |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/hn_search/`) | [`tool.py`](../../starter_v0/tools/hn_search/tool.py), [`TOOL.md`](../../starter_v0/tools/hn_search/TOOL.md), đăng ký trong `tools/__init__.py` + `artifacts/tools.yaml` | Gọi API thật trả đúng story (transcript lượt 4); eval G01, G02, G06 route đúng | Read-only, không side effect, không cần key; input xấu → error dict hoặc chuẩn hóa, không raise |
| Unit test tool mới (6 test cho `hn_search`) | [`tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py); `pytest` → **87 passed, 0 failed, 0 skipped** | Happy path (assert cả request lẫn mapping), sort=date đổi endpoint, query rỗng/sai kiểu không gọi mạng, limit/sort xấu được chuẩn hóa, HTTP 503 và timeout trả error dict | Offline: HTTP mock bằng `fake_http`, mạng thật bị chặn bởi `conftest.py` |
| UI (lệnh chạy + link dùng thử) | [`starter_v0/app.py`](../../starter_v0/app.py), `streamlit>=1.39` trong `requirements.txt`; lệnh ở mục A1 | Chat nhiều lượt, nút câu hỏi mẫu, hiện tool call + kết quả thô, ghi transcript | Lỗi tool hiện ⚠️ và tự mở ra, lỗi provider hiện nguyên văn, không che lỗi |

Tool unit tests: 6 test cho tool mới + 14 test điền các stub có sẵn (clarify, format, send, lookup, fetch, timeline, social_search, policy). Ví dụ lỗi unit test bắt được mà eval không bắt được: `test_hn_search_bad_limit_and_sort_from_model_are_normalised`. Nếu model truyền `limit="abc"` hoặc `limit=999`, eval chỉ thấy model đã gọi `hn_search` nên vẫn báo PASS, nhưng nếu tool không chuẩn hóa thì sẽ crash (`int("abc")`) hoặc gửi `hitsPerPage=999` lên API. Test assert request gửi đi thực tế là `hitsPerPage` 5 / 1 / 20.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | — | Không làm | — |
| Hơn 3 tool mới (≥ 4) | — | Không làm (1 tool mới: `hn_search`) | — |
| `send` gửi thật lên Telegram sau xác nhận | — | Chưa làm: chưa cấu hình bot Telegram. Boundary xác nhận (bắt buộc) đã có và được kiểm chứng ở R12, G04, G07, G08 và transcript lượt 5–6 | — |
| Test challenge (0 skipped / regression test) | [`tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py); `pytest` → 87 passed, **0 skipped** | Điền hết 14 stub `pytest.skip(TODO)` của tool có sẵn, gồm guardrail `send` (có env → đúng 1 POST, không env → error dict, không request) và trust boundary của `policy` (dòng giống lệnh trong policy nằm ở `untrusted_text`, không lọt vào `facts`) | Toàn bộ offline |

Test challenge: không tìm thấy bug trong tool có sẵn với các input đã thử. Hành vi đáng chú ý: `lookup` dùng `int(max_results or 5)` nên `max_results=0` thành 5, còn chuỗi không phải số sẽ thành error dict `ValueError`, không crash. Nhóm coi đây là hành vi chấp nhận được nên không sửa.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này. **Không làm trên branch này.**

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

- **Preflight lỗi do sai provider:** chạy `--provider openrouter` trong khi `.env` chỉ có `OPENAI_API_KEY`. Xử lý: chốt `--provider openai` (`gpt-4o-mini`) cho mọi run v0–v8 để các version so sánh được với nhau.
- **Tool lỗi do key/host:** Firecrawl trả 401 (copy nhầm key, key đúng có tiền tố `fc-`); RapidAPI trả 403 vì dùng host `twitter-api47` trong khi code viết cho `twitter-api45`, và key chưa subscribe api45. Xử lý: lấy lại key, subscribe api45, đổi `RAPIDAPI_TWITTER_HOST`. Smoke test từng tool trước khi chạy eval.
- **Regression khi sửa:** v2 và v4 làm giảm điểm so với version trước. Xử lý: đọc `actual_tool_calls` của từng case mới fail, đặt giả thuyết mới (v3 → v5) thay vì sửa nhiều thứ một lúc.
- **Kết quả dao động giữa các lần chạy:** M06 pass ở v5 nhưng fail ở v6, M02 pass ở v6 nhưng fail ở v7, dù phần liên quan không đổi. Xử lý: v8 chặn kiểu lỗi bỏ sót tham số bằng `required`, và chạy v8 hai lần để xác nhận ổn định (2/2 lần 20/20).

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`? Hành vi và boundary xuyên suốt nhiều tool: hỏi lại thay vì đoán, xác nhận trước khi gửi, từ chối câu ngoài phạm vi, thứ tự routing, quy tắc multi-turn. Bằng chứng: v1 (+0.25) và v4/v5 sửa được R10, R12, M06, trong khi v3 (chỉ sửa tool description) không sửa được.
- Fix nào thuộc `tools.yaml`? Convention của từng tham số: `topic=news`, query chỉ chứa chủ đề, map thời gian sang `timeframe`, handle không `@`, Top/Latest. Bằng chứng: v2 sửa R13 (thiếu `topic`). Tool description khi nào dùng / không dùng vẫn cần cho người đọc và model khác, nhưng với gpt-4o-mini một mình nó không đủ để đổi routing.
- Bài học về cách viết rule: một rule viết quá rộng ở v4 ("hỏi cả web và Twitter thì gọi song song") gây 4 lỗi gọi thừa. Rule cần nêu điều kiện kích hoạt cụ thể ("cùng một câu nhắc rõ cả web và Twitter").
- Fix thuộc **schema** (`required`) mạnh hơn mô tả bằng lời: v7 đã ghi "giữ timeframe từ lượt trước" trong description nhưng M02 vẫn bỏ sót; v8 đặt `required` thì hết lỗi.
- Failure nào cần review thủ công thay vì chấm tự động?
  - **Chất lượng câu trả lời cuối:** eval chỉ chấm tool và args. Transcript lượt 1 cho thấy agent trả lời tiếng Anh cho câu hỏi tiếng Việt; eval không phát hiện được lỗi này.
  - **So khớp chuỗi `query` chính xác:** `"AI news"` bị chấm sai dù vẫn tìm đúng nội dung. Cần người xem xét đây là lỗi thật hay chỉ do eval quá chặt.
  - **Nội dung câu hỏi xác nhận:** eval chỉ kiểm `response_type="yes_no"`, không kiểm câu hỏi có nêu đúng nội dung sẽ gửi hay không.
  - **Kết quả dao động:** một lần pass chưa chứng minh ổn định, cần chạy lặp nhiều lần.
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào? (1) Thêm rule "trả lời bằng ngôn ngữ của user, kể cả khi kết quả tool là tiếng Anh" và viết eval case kiểm tra ngôn ngữ trả lời (cần chấm thủ công hoặc dùng LLM-judge). (2) Rút gọn prompt (bỏ phần trùng với tool description) để xem điểm có giữ nguyên không, tức là đo phần nào của prompt thực sự cần thiết.

## 8. Tài liệu tham khảo

- Đề bài lab và starter code: `README.md`, `RUBRIC.md`, `starter_v0/` (VinUni AI20k Day03).
- Hacker News Search API (Algolia): https://hn.algolia.com/api
- Tavily, Firecrawl, RapidAPI twitter-api45: xem [`docs/TOOL-SETUP.md`](../../docs/TOOL-SETUP.md).
- Streamlit chat elements: https://docs.streamlit.io/develop/api-reference/chat
