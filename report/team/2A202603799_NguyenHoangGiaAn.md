# Báo cáo cá nhân — Nguyễn Hoàng Gia An — 2A202603799

## 1. Thông tin thành viên

- Họ tên: Nguyễn Hoàng Gia An
- MSSV: 2A202603799
- Email: 26ai.annhg@vinuni.edu.vn

## 2. Phần việc phụ trách

- Trưởng nhóm, viết và tổng hợp báo cáo nhóm.
- Tích hợp tool `dedupe_sources`, bổ sung eval nhóm và kiểm chứng kết quả chạy.

## 3. Đóng góp cụ thể

- Với hỗ trợ của Codex, bỏ declaration `trending_topics` chưa có implementation.
- Bổ sung 4 unit test cho tool lọc URL: giữ thứ tự, input rỗng, sai kiểu và URL không hợp lệ.
- Đối chiếu bộ eval nhóm đủ 10 case (5 single turn, 5 multi turn); chạy thật đạt 10/10 PASS.
- Đồng bộ hash và đường dẫn trong `version_log.csv` với run JSON.
- Làm giao diện Streamlit, ghi ba lượt chat live và kiểm tra luồng xác minh handle X.
- Chạy baseline Ollama với Llama và Qwen, thử hai thay đổi trên Llama và kiểm tra cấu hình cuối trên OpenAI. Tổng hợp kết quả vào B7, gồm cả những lần điểm giảm.

## 4. Bằng chứng

- File: [tool mới](../../starter_v0/tools/dedupe_sources/tool.py), [unit test](../../starter_v0/tests/test_tools_todo.py), [run group](../../starter_v0/runs/v3-group_B_group_openai_20261110T213547741621.json).
- AI/công cụ: Codex hỗ trợ đọc code, sửa lỗi, viết test và đối chiếu log. Kiểm chứng bằng pytest (71 passed, 14 skipped) và API thật OpenAI/gpt-4o-mini (10/10 case, không có provider error).
- [Ghi chú kiểm chứng](../../starter_v0/analysis/verification.md) · [Streamlit](../../starter_v0/app.py) · [Transcript ba lượt](../../starter_v0/transcripts/v3-group_openai_20261110T221657720474.transcript.json) · [Kết quả và run CP7](group_report.md#b7-small-local-model-challenge-bonus).

## 5. Tự đánh giá

**Kết quả.** Tôi tổng hợp báo cáo nhóm, tích hợp và kiểm chứng `dedupe_sources`, đối chiếu run eval nhóm đạt 10/10 và ghi lại ba lượt chat live để xem agent xử lý yêu cầu thực tế ra sao.

**Điều tiếp thu được.** Tôi học cách đọc một run theo ba lớp. Trước hết, tôi xem agent chọn công cụ và truyền tham số gì. Sau đó, tôi kiểm tra dữ liệu công cụ trả về và cách agent dùng dữ liệu đó trong câu trả lời. Khi đọc các nhánh của Duy và Bảo, tôi cũng học cách giữ lại run có điểm giảm và so sánh từng ca qua các vòng để phát hiện lỗi mà điểm tổng có thể che đi.

**Suy nghĩ đã thay đổi.** Ban đầu tôi xem 10/10 là dấu hiệu agent đã trả lời tốt cả 10 ca. Khi đọc kỹ log, tôi thấy hai ca policy tiếng Việt vẫn trả kết quả rỗng và G09 truyền đúng tiêu đề nhưng đầu ra chưa hiển thị tiêu đề. Tôi cũng từng nghĩ có URL trong lịch sử là đủ để agent đọc ngay. Lượt chat cuối cho thấy khi có hai URL, agent có thể tự chọn một URL dù người dùng chưa nói rõ. Ở vòng sau, tôi sẽ đọc đầu ra của các ca PASS và bổ sung một ca nhiều lượt kiểm tra agent có hỏi lại khi gặp nhiều URL phù hợp hay không.

## 6. Tài liệu tham khảo

- Quy trình đánh giá, cách kiểm tra bằng chứng và khai báo hỗ trợ AI. [README](../../README.md) · [Rubric](../../RUBRIC.md) · [Quy định](../../RULES.md).
- Nguồn đối chiếu khi tổng hợp đóng góp. [Báo cáo Duy](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/052bd27/report/team/2A202603851_HaLeDuy.md) · [Báo cáo Bảo](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/da7b538/report/team/2A202603861_NguyenThienBao.md) · [Báo cáo Nhật](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/27c9827/report/team/2A202603812_NguyenDucNhat.md).
- Tài liệu kỹ thuật liên quan đến demo và các lượt chạy model local. [Streamlit Chat elements](https://docs.streamlit.io/develop/api-reference/chat) · [Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility).
