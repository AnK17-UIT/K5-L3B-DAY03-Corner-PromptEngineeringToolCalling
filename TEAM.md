# Team

## Thông tin nhóm

- Tên nhóm: (trưởng nhóm chốt)
- Lớp: L3B
- Repo nhóm: [AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling) (tên repo theo yêu cầu của giảng viên)
- Nhánh nộp: `main`
- Commit chốt: (điền sau khi merge xong)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Hoàng Gia An | 2A202603799 | 26ai.annhg@vinuni.edu.vn | [AnK17-UIT](https://github.com/AnK17-UIT) | Chủ repo; tối ưu `tools.yaml` v2–v3 (OpenAI) |
|   2 | Hà Lê Duy | 2A202603851 | 26ai.duyhl@vinuni.edu.vn | [duyhale95](https://github.com/duyhale95) | Vòng tối ưu v0–v7, tool `dedupe_sources`, eval nhóm, UI Streamlit |
|   3 | Nguyễn Thiên Bảo | 2A202603861 | 26ai.baont5@vinuni.edu.vn | [Limdim1604](https://github.com/Limdim1604) | Tool `hn_search`, test challenge, v8–v10 (sửa M06) |
|   4 | Nguyễn Đức Nhật | (bổ sung) | 26ai.nhatnd@vinuni.edu.vn | [NguyenDucNhat3006](https://github.com/NguyenDucNhat3006) | Baseline v0 + phân tích CSV, cải tiến prompt v1 (OpenAI) |

Mỗi thành viên có báo cáo riêng `report/team/MSSV_HoTen.md`. Phần đóng góp bên dưới chỉ ghi những gì đã có commit; mỗi người tự cập nhật mục của mình khi merge lên `main`.

## Cá nhân

### Nguyễn Hoàng Gia An — 2A202603799

#### Phần việc phụ trách

- Tạo repo nhóm, khởi tạo danh sách thành viên.
- Tối ưu tool declaration v2–v3 với provider `openai` trên nhánh `NguyenHoangGiaAn`, nối tiếp v0–v1 của Nhật.

#### Đóng góp cụ thể

- Chạy thử base eval ban đầu và điền danh sách thành viên (commit `a4056bd`).
- v2: viết lại `tools.yaml`, base eval 0.95 → **1.00** (commit `403bf26`).
- v3: chỉnh tiếp `tools.yaml`, giữ 1.00 (commit `6f49b26`). Các run đều có 0 lỗi provider.

#### Bằng chứng

- Nhánh `NguyenHoangGiaAn`: commit `a4056bd`, `403bf26`, `6018554`, `6f49b26` (chờ rebase lên `main`).
- Báo cáo cá nhân: `report/team/2A202603799_NguyenHoangGiaAn.md` (đang là mẫu, An bổ sung).

### Hà Lê Duy — 2A202603851

#### Phần việc phụ trách

- Phần việc phụ trách gồm các vòng đánh giá prompt, tool lọc URL, bộ eval nhóm và demo agent trên nhánh `haleduy`.

#### Đóng góp cụ thể

- Baseline v0 và các vòng v1–v7 (OpenRouter), tool `dedupe_sources` + 3 unit test, 10 case eval nhóm (10/10), UI Streamlit, transcript live chat `v7-cp3`.

#### Bằng chứng

- Commit trên `main`: `2154f6b`, `b016f4d`, `9cc310b`, `aec3144`, `42721a9`.
- [Báo cáo cá nhân của Hà Lê Duy](report/team/2A202603851_HaLeDuy.md)

### Nguyễn Thiên Bảo — 2A202603861

#### Phần việc phụ trách

- Tool mới thứ hai `hn_search` và unit test.
- Test challenge: điền 14 unit test TODO của các tool có sẵn.
- Tiếp tục vòng tối ưu sau v7: đo lại trên provider `openai`, tích hợp tool mới, sửa lỗi M06 (v8–v10).

#### Đóng góp cụ thể

- `hn_search` (Hacker News Algolia API) + 6 unit test; bộ case riêng `eval_new_tool_hn_search.json` (3/3 ở v10).
- 14 test TODO cho clarify, format, send, lookup, fetch, timeline, social_search, policy. `pytest` lên **95 passed, 0 skipped** (trước đó 70 passed, 14 skipped).
- `v7-openai-recheck` → `v8` → `v9` → `v10`: base 20/20 (chạy 2 lần), group 10/10; ghi đủ `version_log.csv` và bảng B1/B2 trong báo cáo nhóm.
- Transcript live `v10` (hn_search → đổi sang Twitter → xin xác nhận gửi → user từ chối).
- Nhánh thử nghiệm độc lập `nguyenthienbao`: v0–v8 với OpenAI từ starter gốc (0.65 → 1.00).

#### Bằng chứng

- Nhánh `nguyenthienbao-main` (rebase trên `main`): test challenge `90f1b1b`, `hn_search` `116965e`, v8 `5f61ac7`, v9 `c353b4d`, v10 `fdd16e2`, transcript `00334ec`, báo cáo `0a5e5c1`.
- [Báo cáo cá nhân của Nguyễn Thiên Bảo](report/team/2A202603861_NguyenThienBao.md)

### Nguyễn Đức Nhật — (MSSV bổ sung)

#### Phần việc phụ trách

- Chạy baseline, phân tích run và cải tiến system prompt trên nhánh `NguyenDucNhat3006`.

#### Đóng góp cụ thể

- Thử baseline với Gemini (commit `364263e`), rồi chạy baseline v0 với `openai`: 0.70 (14/20), 0 lỗi provider (commit `fbbd6db`). Xuất bảng `analysis/base_runs.csv`.
- v1: cải tiến `system_prompt.md`, base eval 0.70 → **0.95**; xuất `analysis/v1.csv` (commit `89be98d`).

#### Bằng chứng

- Nhánh `NguyenDucNhat3006`: commit `364263e`, `fbbd6db`, `89be98d` (chờ rebase lên `main`).
- Báo cáo cá nhân: Nhật bổ sung `report/team/MSSV_NguyenDucNhat.md`.
