# Team

## Thông tin nhóm

- Tên nhóm: Corner
- Lớp: L3B
- Repo nhóm: `K5-L3A-DAY03-TenNhom-ResearchAgentToolEval` hoặc `K5-L3B-DAY03-TenNhom-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: 

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Hoàng Gia An | 2A202603799 | 26ai.annhg@vinuni.edu.vn | https://github.com/AnK17-UIT | Trưởng nhóm, viết và tổng hợp báo cáo, tích hợp tool và kiểm chứng eval |
|   2 | Hà Lê Duy | 2A202603851 | 26ai.duyhl@vinuni.edu.vn | https://github.com/duyhale95 | Kiểm chứng eval, duyệt prompt, tool và demo Streamlit |
|   3 | Nguyễn Thiên Bảo | 2A202603799 | 26ai.baont@vinuni.edu.vn | https://github.com/Limdim1604 | Tối ưu prompt/tool, phát triển Hacker News search, eval và demo |
|   4 | Nguyễn Đức Nhật | 2A202603799 | 26ai.nhatnd@vinuni.edu.vn | https://github.com/NguyenDucNhat3006 | Chạy baseline, phân tích log và nắm chính cải tiến system prompt |


## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## Nguyễn Hoàng Gia An - 2A202603799

### Phần việc phụ trách

- Trưởng nhóm, viết và tổng hợp báo cáo nhóm.
- Tích hợp `dedupe_sources`, kiểm chứng eval nhóm và đồng bộ bằng chứng kết quả.

### Đóng góp cụ thể

- Với hỗ trợ Codex, sửa import tool mới và bỏ khai báo tool chưa có implementation.
- Bổ sung 4 unit test; kiểm tra bộ eval nhóm đủ 5 single turn + 5 multi turn.
- Chạy eval thật đạt 10/10 PASS; sửa hash và đường dẫn version log theo run JSON.

### Bằng chứng

- [Báo cáo cá nhân](report/team/2A202603799_NguyenHoangGiaAn.md).
- [Run group](starter_v0/runs/v3-group_B_group_openai_20261110T213547741621.json).
- [Kiểm chứng](starter_v0/analysis/verification.md): pytest 71 passed, 14 skipped; các skip thuộc challenge của tool có sẵn.

## Hà Lê Duy — 2A202603851

### Phần việc phụ trách

- Kiểm chứng các vòng đánh giá, duyệt thay đổi prompt và mô tả công cụ, kiểm tra tool mới và thử giao diện Streamlit trên nhánh `haleduy`.

### Đóng góp cụ thể

- Đối chiếu baseline và các vòng v1–v7. Ở v7, kết quả đạt 19/20 và còn lỗi M06 khi agent tiếp tục gọi nguồn X sau khi người dùng chuyển sang web.
- Chuẩn hóa thông tin tác giả trong version log và kiểm tra `dedupe_sources` cùng ba unit test.
- Duyệt bộ eval nhóm gồm 5 ca một lượt và 5 ca nhiều lượt, đối chiếu kết quả 10/10, thử UI và kiểm tra transcript.

### Bằng chứng

- [Báo cáo cá nhân trên origin/main](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/052bd27/report/team/2A202603851_HaLeDuy.md).
- [Prompt và run v7](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/b016f4d), [tool và unit test](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/9cc310b).
- [Eval nhóm](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/aec3144), [Streamlit và transcript](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/42721a9).

## Nguyễn Thiên Bảo - 2A202603861

### Phần việc phụ trách

- Tối ưu prompt và khai báo công cụ, phát triển công cụ tìm kiếm Hacker News, kiểm thử và chuẩn bị demo trên nhánh `nguyenthienbao`.

### Đóng góp cụ thể

- Thử các vòng v0–v8, điều chỉnh cách chọn nguồn ở hội thoại nhiều lượt và yêu cầu truyền đủ bộ lọc `topic` và `timeframe` khi gọi `lookup`.
- Tích hợp `hn_search` qua Hacker News Algolia, hoàn thiện các unit test TODO và thêm ca eval kiểm tra cách agent chọn công cụ mới. Run nhóm v8 đạt 10/10 trên nhánh này.
- Làm giao diện Streamlit hiển thị lời gọi và kết quả công cụ, lưu transcript demo, cập nhật Phần A và B của báo cáo.

### Bằng chứng

- [Thay đổi ở v8](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/582adc5), [công cụ và unit test](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/c9350b7), [run nhóm](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/b476e18).
- [Transcript](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/72c9f3c), [Streamlit](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/c6ea9dc), [báo cáo trên nhánh](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/5deed44/report/team/group_report.md).

## Nguyễn Đức Nhật - 2A202603812

### Phần việc phụ trách

- Chạy baseline, phân tích lỗi từ log và cải tiến system prompt trên nhánh `NguyenDucNhat3006`.

### Đóng góp cụ thể

- Chạy và phân tích baseline v0, sau đó cập nhật log JSON để lưu bằng chứng đánh giá.
- Chỉnh system prompt v1 để agent hỏi lại khi thiếu handle hoặc URL, xin xác nhận trước khi gửi và tách từ khóa tìm kiếm khỏi bộ lọc tin tức.
- Chạy lại v1 sau khi chỉnh prompt và lưu run JSON cùng bảng phân tích v1.

### Bằng chứng

- [Baseline v0](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/364263e), [cập nhật log JSON](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/fbbd6db).
- [System prompt, run JSON và bảng phân tích v1](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/89be98d).
