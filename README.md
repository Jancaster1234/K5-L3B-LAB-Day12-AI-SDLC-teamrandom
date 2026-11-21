# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

## Cách chạy (teamrandom)

### Chạy từ clone sạch (tối đa 3 lệnh trên macOS/Linux)
```bash
git clone https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom.git
cd K5-L3B-LAB-Day12-AI-SDLC-teamrandom
python3 -m chonoi.live --mode gather
```
* **Yêu cầu môi trường:** Python 3.10+, không cần cài thêm (chỉ dùng thư viện chuẩn Python).
* **Các chế độ chơi live khác:**
  - Ca quán: `python3 -m chonoi.live --mode quan`
  - Cả ngày: `python3 -m chonoi.live --mode day`

### Điều khiển
* **Di chuyển:** `WASD` hoặc các phím mũi tên.
* **Tương tác:** `E` (hái cây, bỏ nguyên liệu vào bếp, lấy món chín, phục vụ bàn).
* **Bắt cá:** `Space` (khi tiếp cận gần cá).
* **Tạm dừng / Tiếp tục:** `Esc` hoặc `P`.

### Công thức tính điểm
$$\text{điểm} = \text{earned} + 100 \times \lfloor\text{reputation}\rfloor$$
(hoặc: `điểm = earned + 100 × floor(reputation)`).

### Lệnh chạy test
```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

### Chế độ Headless (Mô phỏng tất định)
```bash
python3 -m chonoi.headless --mode gather|quan|day --seed 1 --ticks 600 --out out.jsonl
```
*(Thêm `--days 1..5` khi chạy ở chế độ `--mode day`, ví dụ `--days 2`)*.

### Chạy Benchmark hiệu năng
```bash
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json
```

### Chạy Soak test độ ổn định dài hạn
```bash
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
```

## Mở rộng đã làm
* **`burn`:** Món nấu chín trên bếp nếu để quá 20 giây (tương đương 1200 tick) mà người chơi không lấy ra thì món sẽ bị cháy hỏng (`dish_burnt`), bếp trở về trạng thái rảnh `idle`, đơn của khách nếu kho còn nguyên liệu sẽ được giữ chỗ lại (`reserved`), nếu thiếu sẽ chuyển sang `unfulfillable` khách vẫn tiếp tục chờ.
  * Bộ test kiểm chứng: `tests/test_ext_burn.py`.

## Sáng tạo của nhóm
* **Chưa có:** Nhóm tập trung tối đa nguồn lực vào việc hoàn thiện chính xác 100% hợp đồng kỹ thuật (PRD-0, Test Contract v1.0, v1.1, v1.2), bảo đảm tính tất định và tối ưu hiệu năng/độ ổn định qua toàn bộ các Phase.

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Bắt đầu nhanh

```bash
git clone <fork-của-nhóm> && cd <fork-của-nhóm>
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v        # smoke test
python3 -m chonoi.live --mode gather                                # chơi thử trên trình duyệt (tùy chọn)
```

Game cần chế độ **headless** theo Test Contract (`python3 -m chonoi.headless --mode gather|quan …`) để được chạy và chấm tự động. **Công nghệ không ràng buộc**: khung Python trong `chonoi/` chỉ là gợi ý, chi tiết ở [`docs/STARTER.md`](docs/STARTER.md).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.
