# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Corner
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3 và group: OpenAI / gpt-4o-mini

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Agent Corner tìm nguồn trên web, X và arXiv, đọc nội dung theo URL, tra cứu chính sách nội bộ và soạn bản tổng hợp có nguồn.

**Chạy demo:** từ `starter_v0`, cài `python -m pip install -r requirements.txt`, cấu hình `OPENAI_API_KEY` trong `.env`, rồi chạy `python -m streamlit run app.py` và mở `http://localhost:8501`. Demo hiển thị tên công cụ đã gọi và giữ hội thoại trong phiên. Chế độ demo chỉ soạn nội dung, không gửi Telegram. Link public chưa được tạo.

### A2. Công cụ

| Công cụ | Chức năng |
|---|---|
| `clarify` | Hỏi lại khi thiếu thông tin |
| `timeline` | Đọc bài đăng từ một tài khoản X |
| `social_search` | Tìm bài đăng trên X theo chủ đề |
| `lookup` | Tìm nguồn web |
| `fetch` | Đọc nội dung URL |
| `format` | Định dạng bản tổng hợp |
| `send` | Gửi Telegram sau xác nhận trong chế độ CLI |
| `policy` | Tra cứu tài liệu chính sách nội bộ |
| `papers` | Tìm bài nghiên cứu trên arXiv |
| `paper_text` | Đọc nội dung bài nghiên cứu |
| `dedupe_sources` | Lọc URL trùng, công cụ nhóm bổ sung |

### A3. Câu hỏi mẫu

1. Tìm 3 bài arXiv mới về retrieval-augmented generation.
2. Tìm 3 tin web về pin thể rắn trong một tháng qua.
3. Lọc URL trùng trong danh sách: https://example.com/a, https://example.com/b, https://example.com/a.

## 3. Giải pháp

- Tool mới `dedupe_sources` loại URL trùng theo chuỗi nguyên văn, giữ thứ tự xuất hiện đầu tiên và trả số mục đã loại; chỉ xử lý danh sách HTTP(S) URL đã có.
- Đợt kiểm chứng sửa import tool còn thiếu, bỏ declaration `trending_topics` chưa có implementation và thêm 4 unit test cho tool mới.
- Đồng bộ hash, artifact version và đường dẫn trong `version_log.csv` từ run JSON thật. Các giả thuyết lịch sử cần đối chiếu thêm snapshot artifact; không suy ra toàn bộ thay đổi chỉ từ metric.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Xem version_log; cần snapshot để xác minh giả thuyết lịch sử | — | 70% | [run](../../starter_v0/runs/v0_B_base_openai_20261110T180948251846.json) |
| v1 | system_prompt.md | Xem version_log; cần snapshot để xác minh giả thuyết lịch sử | 70% | 95% | [run](../../starter_v0/runs/v1_B_base_openai_20261110T183603209801.json) |
| v2 | prompt/tools (hash đều đổi so với v1) | Xem version_log; cần snapshot để xác minh giả thuyết lịch sử | 95% | 100% | [run](../../starter_v0/runs/v2_B_base_openai_20261110T185812745130.json) |
| v3 | tools.yaml | Xem version_log; cần snapshot để xác minh giả thuyết lịch sử | 100% | 100% | [run](../../starter_v0/runs/v3_B_base_openai_20261110T192215323929.json) |

### B2. Failure Analysis

Các lỗi dưới đây lấy từ run baseline ở B1. Cột cuối ghi phiên bản đầu tiên đạt trên cùng ca đánh giá.

| Ca | Lỗi ghi nhận ở v0 | Phiên bản đầu tiên đạt |
|---|---|---|
| R08_out_of_scope | expected no tool call | v1 |
| R10_missing_handle | missing tool call clarify<br>extra tool call timeline | v1 |
| R11_missing_url | missing tool call clarify<br>extra tool call fetch | v1 |
| R12_confirm_before_send | missing tool call clarify<br>extra tool call send | v1 |
| R13_parallel_web_and_tweets | query: expected 'AI', got 'AI news'<br>topic: expected 'news', got None | v1 |
| R14_out_of_scope_coding | expected no tool call | v1 |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_dedupe_given_urls | Chọn tool mới và truyền cả URL trùng để tool xử lý. | dedupe_sources | PASS |
| G02_internal_policy_area | Chọn kho chính sách nội bộ, giữ đúng phạm vi và số mục. | policy | PASS |
| G03_monthly_web_news | Truyền đúng bộ lọc một tháng và giới hạn kết quả cho tin web. | lookup | PASS |
| G04_arxiv_recent_papers | Dùng tìm kiếm arXiv và truyền đúng số lượng, thứ tự ngày nộp. | papers | PASS |
| G05_outside_research_poem | Yêu cầu sáng tác ngoài phạm vi không kích hoạt tool. | Không gọi tool | PASS |
| G06_dedupe_prior_links | Dùng tool mới với danh sách URL từ lượt trước. | dedupe_sources | PASS |
| G07_cancel_publish | Yêu cầu hủy chặn đăng và kết thúc quy trình xác nhận. | Không gọi tool | PASS |
| G08_switch_web_to_social | Đổi nguồn từ web sang X, giữ chủ đề và dùng Top. | social_search | PASS |
| G09_format_prior_sources | Định dạng dữ liệu đã có theo đúng khuôn và tiêu đề. | format | PASS |
| G10_policy_area_correction | Ưu tiên nhóm chính sách và giới hạn được đính chính ở lượt cuối. | policy | PASS |

Bộ group: 5 single turn + 5 multi turn, 10/10 PASS; routing, argument và multiturn accuracy đều 100%, provider_error_cases=0. [Run thật](../../starter_v0/runs/v3-group_B_group_openai_20261110T213547741621.json).

### B4. Live Chat Evidence

Ba lượt chạy thật qua `chat.py` với OpenAI / `gpt-4o-mini`, artifact `v3-group+p954ac2a1d8bc+t084c3dae21b1`. [Transcript](../../starter_v0/transcripts/v3-group_openai_20261110T221657720474.transcript.json).

| Lượt | Yêu cầu | Công cụ | Kết quả |
|---|---|---|---|
| 1 | Lọc danh sách ba URL có một URL trùng | `dedupe_sources` | Giữ hai URL theo thứ tự ban đầu |
| 2 | Lọc lại danh sách URL vừa rồi | `dedupe_sources` | Dùng lại danh sách từ lượt trước và trả hai URL |
| 3 | Mở URL trong ngữ cảnh có hai URL | `fetch` | Đọc được trang đầu tiên, nhưng agent tự chọn URL khi người dùng chưa chỉ định URL nào |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| `dedupe_sources` | [tool](../../starter_v0/tools/dedupe_sources/tool.py) và [TOOL.md](../../starter_v0/tools/dedupe_sources/TOOL.md) | Lọc trùng, giữ thứ tự | Input sai trả error dict |
| Unit test tool mới | [tests](../../starter_v0/tests/test_tools_todo.py) | 4 test mới; toàn suite 71 passed, 14 skipped | Chưa hoàn thành bonus 0 skipped |
| UI | [app.py](../../starter_v0/app.py) | Chat nhiều lượt và hiển thị tên công cụ | Demo giới hạn ở nghiên cứu và soạn nội dung |  |

Unit test kiểm tra giữ thứ tự URL và URL lỗi; eval chỉ so tên tool và args, không kiểm tra output này. [Ghi chú kiểm chứng](../../starter_v0/analysis/verification.md).

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

- Thiếu import `dedupe_sources` làm pytest/eval lỗi ngay khi khởi động; sửa import và kiểm tra lại contract.
- `trending_topics` có declaration nhưng thiếu code và TOOL.md; bỏ declaration để đồng bộ với tool thực tế.
- Lần chạy trong sandbox bị APIConnectionError cả 10 case, không dùng để tính chất lượng model. Chạy lại ngoài sandbox đạt 10/10 với 0 provider error; xem [ghi chú kiểm chứng](../../starter_v0/analysis/verification.md).

## 6. Tổng hợp đóng góp

Các thành viên đều thực hiện CP1–CP5 theo thông tin nhóm cung cấp. Bảng dưới ghi các phần việc có thể đối chiếu từ báo cáo và commit trên từng nhánh. Số liệu ở B1–B4 thuộc nhánh Gia An. Kết quả trên các nhánh khác được ghi riêng.

| Thành viên | Đóng góp có minh chứng |
|---|---|
| Nguyễn Hoàng Gia An | Trưởng nhóm, viết và tổng hợp báo cáo. Tích hợp và kiểm chứng `dedupe_sources`, chạy eval nhóm 10/10, triển khai Streamlit và lưu ba lượt chat live. [Báo cáo cá nhân](2A202603799_NguyenHoangGiaAn.md) |
| Hà Lê Duy | Duyệt các vòng eval đến v7, kiểm tra tool lọc URL và unit test, duyệt bộ eval nhóm và thử Streamlit. [Báo cáo cá nhân](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/052bd27/report/team/2A202603851_HaLeDuy.md) |
| Nguyễn Thiên Bảo | Thử các vòng v0–v8, thêm `hn_search` và kiểm thử, chạy eval nhóm v8 đạt 10/10, làm UI, lưu transcript và cập nhật báo cáo trên nhánh riêng. [Báo cáo nhánh](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/5deed44/report/team/group_report.md) |
| Nguyễn Đức Nhật | Chạy và phân tích baseline v0, cập nhật log, sửa system prompt và đo lại v1. [Baseline](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/364263e) · [Prompt và run v1](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/89be98d) |

Xem thêm [TEAM.md](../../TEAM.md) để đối chiếu các commit theo thành viên.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Ban đầu nhóm dễ xem điểm eval cao là dấu hiệu agent đã trả lời tốt. Hai ca policy tiếng Việt vẫn trả danh sách rỗng và G09 truyền đúng headline nhưng đầu ra chưa hiển thị tiêu đề. Nhóm học được cách kiểm tra riêng quyết định gọi tool, kết quả tool và câu trả lời cuối.
- So sánh các nhánh cho thấy điểm tổng có thể che mất lỗi nhiều lượt. M06 trên nhánh Duy cho thấy agent vẫn gọi nguồn X sau khi người dùng chuyển sang web. Nhánh Bảo cũng ghi nhận điểm giảm sau khi bổ sung quy tắc routing. Nhóm học được cách giữ log của từng vòng và so sánh hành vi theo từng ca trước khi chọn thay đổi.
- Lượt chat live thứ ba cho thấy agent tự chọn URL đầu tiên khi có hai URL trong ngữ cảnh. Vòng tiếp theo có thể kiểm tra giả thuyết rằng yêu cầu `clarify` khi có nhiều URL phù hợp sẽ giảm chọn nhầm mà vẫn đọc được ngay khi chỉ có một URL rõ ràng.
- Giao diện đã chạy local. Báo cáo còn thiếu link dùng thử công khai.

## 8. Tài liệu tham khảo

-
