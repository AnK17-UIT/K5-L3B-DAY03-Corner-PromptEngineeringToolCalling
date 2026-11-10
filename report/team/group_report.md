# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Corner
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Phạm vi chính: nhánh `NguyenHoangGiaAn`, dùng OpenAI / GPT-4o-mini cho v0–v3 và eval nhóm. Mục 6 ghi riêng kết quả của các nhánh thành viên.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Agent Corner tìm nguồn trên web, X và arXiv, đọc nội dung theo URL, tra cứu chính sách nội bộ và soạn bản tổng hợp có nguồn.

**Chạy demo:** từ `starter_v0`, cài `python -m pip install -r requirements.txt`, cấu hình `OPENAI_API_KEY` trong `.env`, rồi chạy `python -m streamlit run app.py` và mở `http://localhost:8501`. Demo hiển thị tên công cụ đã gọi và giữ hội thoại trong phiên. Chế độ demo chỉ soạn nội dung, không gửi Telegram. Link public chưa được tạo.

### A2. Công cụ

| Công cụ | Chức năng |
|---|---|
| `clarify` | Hỏi lại khi thiếu thông tin |
| `timeline` | Xác minh đúng handle X qua hồ sơ rồi đọc bài đăng khi được yêu cầu |
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
3. Lọc URL trùng trong danh sách gồm `https://example.com/a`, `https://example.com/b` và `https://example.com/a`.
4. Kiểm tra tài khoản X `@NASA` có tồn tại không.

## 3. Giải pháp

- Tool mới `dedupe_sources` loại URL trùng theo chuỗi nguyên văn, giữ thứ tự xuất hiện đầu tiên và trả số mục đã loại; chỉ xử lý danh sách HTTP(S) URL đã có.
- Đợt kiểm chứng sửa import tool còn thiếu, bỏ declaration `trending_topics` chưa có implementation và thêm 4 unit test cho tool mới.
- Đồng bộ hash, artifact version và đường dẫn trong `version_log.csv` từ run JSON thật. Các giả thuyết lịch sử cần đối chiếu thêm snapshot artifact; không suy ra toàn bộ thay đổi chỉ từ metric.

- Luồng chat yêu cầu handle hoặc URL hồ sơ do người dùng cung cấp. Khi chỉ có tên hiển thị, agent hỏi lại. API trả trạng thái tìm thấy, không tìm thấy hoặc chưa xác minh được. Tên hiển thị và URL hồ sơ giúp người dùng tự đối chiếu danh tính. [Luồng chat](../../starter_v0/chat.py) · [Tra hồ sơ](../../starter_v0/tools/timeline/tool.py).

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi của cấu hình ban đầu | — | 70% | [run](../../starter_v0/runs/v0_B_base_openai_20261110T180948251846.json) |
| v1 | system_prompt.md | Hỏi lại khi thiếu dữ liệu, xin xác nhận trước khi gửi và tách từ khóa khỏi bộ lọc tin tức | 70% | 95% | [run](../../starter_v0/runs/v1_B_base_openai_20261110T183603209801.json) |
| v2 | prompt/tools (hash đều đổi so với v1) | Chuẩn hóa quy ước `lookup`. Cả hai hash đều đổi, nên chưa tách riêng tác động của từng tệp | 95% | 100% | [run](../../starter_v0/runs/v2_B_base_openai_20261110T185812745130.json) |
| v3 | tools.yaml | Thử thêm khai báo `trending_topics`. Bộ base đạt nhưng không đo việc thực thi công cụ này | 100% | 100% | [run](../../starter_v0/runs/v3_B_base_openai_20261110T192215323929.json) |

### B2. Failure Analysis

Các lỗi dưới đây lấy từ run baseline ở B1. Cột cuối ghi phiên bản đầu tiên đạt trên cùng ca đánh giá.

| Ca | Nhóm lỗi | Sai lệch quan sát được ở v0 | Bản đầu tiên đạt |
|---|---|---|---|
| R08_out_of_scope | out_of_scope | expected no tool call | v1 |
| R10_missing_handle | missing_info | missing tool call clarify<br>extra tool call timeline | v1 |
| R11_missing_url | missing_info | missing tool call clarify<br>extra tool call fetch | v1 |
| R12_confirm_before_send | wrong_boundary | missing tool call clarify<br>extra tool call send | v1 |
| R13_parallel_web_and_tweets | wrong_tool | query: expected 'AI', got 'AI news'<br>topic: expected 'news', got None | v1 |
| R14_out_of_scope_coding | out_of_scope | expected no tool call | v1 |

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
| UI | [app.py](../../starter_v0/app.py) | Chat nhiều lượt và hiển thị tên công cụ | Demo giới hạn ở nghiên cứu và soạn nội dung |

Unit test kiểm tra giữ thứ tự URL và URL lỗi; eval chỉ so tên tool và args, không kiểm tra output này. [Ghi chú kiểm chứng](../../starter_v0/analysis/verification.md).

### B5. Bonus Evidence

| Hạng mục | Trạng thái và minh chứng |
|---|---|
| Small Local Model Challenge | Có hai baseline Ollama, hai vòng thử và một run kiểm tra ngược trên cloud. Xem [B7](#b7-small-local-model-challenge-bonus). |
| Test challenge | Báo cáo Bảo ghi 95 đạt, 0 bỏ qua trên nhánh `nguyenthienbao-main`. Nhánh Gia An chạy lại được 71 đạt, 14 bỏ qua. [Báo cáo Bảo](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/da7b538/report/team/2A202603861_NguyenThienBao.md). |
| Gửi Telegram thật và mốc ít nhất 4 công cụ mới | Chưa ghi nhận minh chứng đạt trên nhánh báo cáo. |

### B7. Small Local Model Challenge (bonus)

Các lượt dùng cùng 20 ca trong `eval_base.json`. Snapshot prompt và YAML v3 được khôi phục từ commit `6f49b26` và đối chiếu hash với run cloud. Các artifact thí nghiệm nằm trong [artifacts/ollama](../../starter_v0/artifacts/ollama). v4 viết quy tắc routing theo thứ tự ưu tiên, còn v5 giữ nguyên prompt v4 và thu gọn YAML còn sáu công cụ. Cấu hình v5 dành cho bộ base.

| Phiên bản | Model | Prompt / YAML | Số ca đạt | Routing | Args | Nhiều lượt | Lỗi provider | Minh chứng |
|---|---|---|---:|---:|---:|---:|---:|---|
| v3 | gpt-4o-mini (openai) | v3 / v3 | 20/20 | 100% | 100% | 100% | 0 | [Run JSON](../../starter_v0/runs/v3_B_base_openai_20261110T192215323929.json) |
| v3-llama3.2 | llama3.2:3b (ollama) | v3 / v3 | 9/20 | 65% | 45% | 50% | 0 | [Run JSON](../../starter_v0/runs/v3-llama3.2_B_base_ollama_20261111T000026444838.json) |
| v3-qwen3.5 | qwen3.5:2b (ollama) | v3 / v3 | 12/20 | 65% | 60% | 50% | 0 | [Run JSON](../../starter_v0/runs/v3-qwen3.5_B_base_ollama_20261111T001129392568.json) |
| v4-local | llama3.2:3b (ollama) | v4 / v3 | 6/20 | 65% | 30% | 17% | 0 | [Run JSON](../../starter_v0/runs/v4-local_B_base_ollama_20261111T000418237860.json) |
| v5-local | llama3.2:3b (ollama) | v4 / v5 | 5/20 | 55% | 25% | 17% | 0 | [Run JSON](../../starter_v0/runs/v5-local_B_base_ollama_20261111T000730354503.json) |
| v5-local-cloud | gpt-4o-mini (openai) | v4 / v5 | 19/20 | 95% | 95% | 83% | 0 | [Run JSON](../../starter_v0/runs/v5-local-cloud_B_base_openai_20261111T000407893802.json) |

Số ca mắc từng dạng lỗi, tính theo lời gọi thực tế. Một ca có thể xuất hiện ở nhiều cột.

| Phiên bản | Gọi công cụ ngoài danh sách mong đợi | Args JSON lỗi | Thiếu toàn bộ lời gọi bắt buộc | Bỏ sót clarify | Gọi lặp hoặc gọi thừa |
|---|---:|---:|---:|---:|---:|
| v3 | 0 | 0 | 0 | 0 | 0 |
| v3-llama3.2 | 5 | 0 | 0 | 3 | 7 |
| v3-qwen3.5 | 4 | 0 | 3 | 3 | 4 |
| v4-local | 5 | 0 | 0 | 3 | 7 |
| v5-local | 6 | 0 | 0 | 3 | 9 |
| v5-local-cloud | 1 | 0 | 0 | 0 | 1 |

- Llama v3 gọi `social_search` khi thiếu handle (R10), gọi `format` khi thiếu URL (R11) và chọn `send` thay vì `clarify` ở R12. R05 truyền giới hạn dưới dạng chuỗi; R03, R13 và M02 ghép từ chỉ thời gian hoặc thể loại vào `lookup.query`.
- **Quy tắc routing có thứ tự ưu tiên**. Điểm thay đổi từ 45% đến 30%. Ca mới đạt gồm không có. Ca bị tụt gồm M05, M06, R06.
- **Thu gọn danh sách công cụ**. Điểm thay đổi từ 30% đến 25%. Ca mới đạt gồm không có. Ca bị tụt gồm R14.
- **Kiểm tra ngược trên cloud**. Điểm thay đổi từ 100% đến 95%. Ca mới đạt gồm không có. Ca bị tụt gồm M06.
- Cùng cấu hình v3, Qwen đạt 12/20 so với 9/20 của Llama. Cả hai có routing 65%, nhưng Qwen đạt R05 với tham số giới hạn đúng kiểu và đạt cả R08, R09, R14 không cần công cụ. Hai model đều bỏ sót `clarify` ở R10–R12. Đổi model cho kết quả tốt hơn trên bộ ca này, còn hai thay đổi prompt/YAML đã thử trên Llama đều làm điểm giảm.
- Ở M06, OpenAI với v5 vẫn gọi thêm `social_search` sau khi người dùng chuyển sang web. Giữ cấu hình v3 cloud khi cần chất lượng base cao hơn. Qwen v3 là lựa chọn local có điểm cao nhất trong đợt thử này, nhưng các ca xác nhận và hội thoại nhiều lượt vẫn cần kiểm tra thêm. Model chạy local, còn công cụ tìm kiếm có thể gọi API bên ngoài.

## 5. Khó khăn và cách xử lý

- Thiếu import `dedupe_sources` làm pytest/eval lỗi ngay khi khởi động; sửa import và kiểm tra lại contract.
- `trending_topics` có declaration nhưng thiếu code và TOOL.md; bỏ declaration để đồng bộ với tool thực tế.
- Lần chạy trong sandbox bị APIConnectionError cả 10 case, không dùng để tính chất lượng model. Chạy lại ngoài sandbox đạt 10/10 với 0 provider error; xem [ghi chú kiểm chứng](../../starter_v0/analysis/verification.md).

## 6. Tổng hợp đóng góp

Các thành viên cùng thực hiện CP1–CP5. Kết quả dưới đây gắn với nhánh và cấu hình tương ứng.

| Thành viên | Đóng góp và kết quả |
|---|---|
| Nguyễn Hoàng Gia An | Trưởng nhóm, viết và tổng hợp báo cáo, tích hợp và kiểm chứng `dedupe_sources`, chạy group 10/10, làm UI, ghi transcript, xác minh handle X và chạy CP7. [Báo cáo cá nhân](2A202603799_NguyenHoangGiaAn.md). |
| Hà Lê Duy | Duyệt baseline và các vòng đến v7 trên OpenRouter, chốt 19/20 và ghi nhận lỗi M06. Kiểm tra tool lọc URL, unit test, eval nhóm 10/10 và demo Streamlit. [Báo cáo cá nhân](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/052bd27/report/team/2A202603851_HaLeDuy.md). |
| Nguyễn Thiên Bảo | Trên nhánh thử nghiệm riêng, v0 đạt 13/20 và v8 đạt 20/20. Trên `nguyenthienbao-main`, Bảo bổ sung `hn_search`, sáu test cho tool và 14 test TODO. Bản v10 trên OpenAI đạt 20/20 hai lần, group 10/10 và extension 3/3. Bộ extension giữ nguyên 10 ca group hiện có. [Báo cáo cá nhân](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/da7b538/report/team/2A202603861_NguyenThienBao.md) · [Base v10](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/da7b538/starter_v0/runs/v10_B_base_openai_20261110T223052527930.json) · [Group v10](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/da7b538/starter_v0/runs/v10_B_group_openai_20261110T223122934339.json) · [Extension v10](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/da7b538/starter_v0/runs/v10_B_extension_openai_20261110T223139440802.json). |
| Nguyễn Đức Nhật | Phân tích baseline 14/20 và sửa prompt v1 đạt 19/20. Trên nhánh riêng, Nhật chuẩn hóa mô tả công cụ, tích hợp lọc URL, cập nhật eval nhóm, làm UI theo dõi lời gọi và hoàn thiện thêm unit test. [Báo cáo cá nhân](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/27c9827/report/team/2A202603812_NguyenDucNhat.md) · [UI và eval](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/d9af40a) · [Unit test](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/27c9827). |

Chi tiết phân công và commit minh chứng nằm trong [TEAM.md](../../TEAM.md).

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Ban đầu nhóm dễ xem điểm eval cao là dấu hiệu agent đã trả lời tốt. Hai ca policy tiếng Việt vẫn trả danh sách rỗng và G09 truyền đúng headline nhưng đầu ra chưa hiển thị tiêu đề. Nhóm học được cách kiểm tra riêng quyết định gọi tool, kết quả tool và câu trả lời cuối.
- So sánh các nhánh cho thấy điểm tổng có thể che mất lỗi nhiều lượt. M06 trên nhánh Duy cho thấy agent vẫn gọi nguồn X sau khi người dùng chuyển sang web. Ở nhánh tích hợp của Bảo, v9 sửa được M06 nhưng lại gọi thừa `lookup` ở N03. Bảo đo lại cả base, group và extension ở v10 để theo dõi hai hành vi này. Nhóm học được cách giữ log của từng vòng và so sánh hành vi theo từng ca trước khi chọn thay đổi.
- Lượt chat live thứ ba cho thấy agent tự chọn URL đầu tiên khi có hai URL trong ngữ cảnh. Vòng tiếp theo có thể kiểm tra giả thuyết rằng yêu cầu `clarify` khi có nhiều URL phù hợp sẽ giảm chọn nhầm mà vẫn đọc được ngay khi chỉ có một URL rõ ràng.
- Giao diện đã chạy local. Báo cáo còn thiếu link dùng thử công khai.

## 8. Tài liệu tham khảo

- Yêu cầu bài lab, cách chấm và quy trình nộp bài. [README](../../README.md) · [Checkpoints](../../CHECKPOINTS.md) · [Rubric](../../RUBRIC.md) · [Quy định](../../RULES.md) · [Hướng dẫn nộp](../../SUBMISSION.md).
- Cấu hình provider, dịch vụ tìm kiếm và công cụ. [Hướng dẫn thiết lập tool](../../docs/TOOL-SETUP.md) · [Tool contract](../../starter_v0/tools/README.md).
- Tài liệu kỹ thuật cho giao diện, kiểm tra hồ sơ X, tìm kiếm Hacker News và chạy model local. [Streamlit Chat elements](https://docs.streamlit.io/develop/api-reference/chat) · [Twitter API45 User info](https://rapidapi.com/alexanderxbx/api/twitter-api45/playground/apiendpoint_b4db8ee2-25bc-4743-934d-8b9b4e774bd7) · [Hacker News Search API](https://hn.algolia.com/api) · [Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility).
- Báo cáo cá nhân và hồ sơ thử nghiệm của nhóm. [Gia An](2A202603799_NguyenHoangGiaAn.md) · [Duy](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/052bd27/report/team/2A202603851_HaLeDuy.md) · [Bảo](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/da7b538/report/team/2A202603861_NguyenThienBao.md) · [Nhật](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/27c9827/report/team/2A202603812_NguyenDucNhat.md) · [Version log](../../starter_v0/artifacts/version_log.csv).
