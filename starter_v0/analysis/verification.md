# Kiểm chứng README và lần chạy eval_group

## Bằng chứng đã kiểm tra

- Base v0: 14/20 (70%); v1: 19/20 (95%); v2, v3: 20/20 (100%). Cả bốn run có provider_error_cases=0, measured_cases=total_cases=20.
- Đã sửa artifact_version, prompt_hash, tools_hash, run_file và metric_after trong version_log.csv theo JSON thực tế. Các giả thuyết lịch sử chưa thể xác minh đầy đủ vì không có snapshot artifact từng version. Hash prompt v1 và v2 khác nhau dù log cũ ghi v2 chỉ sửa tools.yaml.
- eval_group.json: đúng 10 case, 5 query + 5 turns, phase B, đủ failure_type/expect/metadata; có hai case route tới tool mới dedupe_sources.
- Sửa import dedupe_sources còn thiếu; bỏ declaration trending_topics vì không có implementation hoặc TOOL.md.
- Thêm 4 unit test offline cho dedupe_sources: giữ thứ tự, danh sách rỗng, sai kiểu input, URL lỗi trả error dict.
- Pytest: 71 passed, 14 skipped. Các skip thuộc challenge cho tool có sẵn, được README cho phép; các test tool mới đã chạy.
- Run group thật: [v3-group_B_group_openai_20261110T213547741621.json](../runs/v3-group_B_group_openai_20261110T213547741621.json), provider openai, model gpt-4o-mini. 10/10 PASS; routing/argument/multiturn accuracy=1.0; provider_error_cases=0.
- Run group trước đó trong sandbox có 10 APIConnectionError, measured_cases=0; không dùng run đó để báo cáo chất lượng model.

## Giới hạn của kết quả

Eval chấm tên tool và tập con args, không chứng minh chất lượng nội dung hay mọi field output. Hai case policy (G02/G10) trả results=[] với query tiếng Việt. G09 format dạng bullets không hiện headline trong markdown dù model truyền đúng headline. Cần phân biệt các hành vi này với điểm routing/args 100%. Hàm normalize_value của harness sắp xếp list khi so sánh; việc giữ thứ tự URL được kiểm chứng riêng bằng unit test và output thật của G01/G06.

## Các mục README chưa có đủ bằng chứng hoàn thành

- Chưa thấy code UI hoặc dependency Streamlit, link dùng thử vẫn trống trong báo cáo nhóm.
- Chưa thấy transcript chat live trong starter_v0/transcripts/ (samples chỉ là ví dụ).
- Báo cáo nhóm và cá nhân còn nhiều chỗ mẫu/trống; tên nhóm trong TEAM.md và group_report.md chưa thống nhất.
- TEAM.md còn trống vai trò và URL repo; MSSV của bốn thành viên đang giống nhau, cần thành viên tự xác nhận.
- Preflight chưa được chạy riêng trong đợt kiểm tra này; lần eval thật chứng minh provider đã kết nối được.
- Không đánh dấu toàn bộ checklist hoàn thành vì các mục trên chưa có bằng chứng.

## Chạy lại

Từ starter_v0/:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python run_eval.py --provider openai --version v3-group --suite group --eval-cases data/eval_group.json
```
