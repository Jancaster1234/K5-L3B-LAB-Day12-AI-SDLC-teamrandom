# Changelog

## [Unreleased] - sau v1.1.0

### Fixed
- Cảnh báo oxy dùng emoji 🫧 (Unicode 14) hiện thành ô vuông trên Windows 10 → đổi sang ⚠️ / 💨.

### Added
- Bằng chứng giao diện `docs/proof/phase-4/ui/` (ảnh 3 cảnh báo + ba cảnh), clone sạch từ GitHub và chạy suite tại từng tag (`docs/proof/phase-4/qa/clean-clone.txt`).

## [v1.1.0] - 2026-11-21 — Đồ họa (Test Contract vẫn v1.3)

### Added
- Cảnh lặn: sprite Kenney Fish Pack (CC0) cho cá, đáy cát, rong, đá, bọt khí; vẽ Út Sen (nón lá / bình oxy) và Cá Sấu (trước đây client chưa vẽ).
- Cảnh quán: tilesheet Kenney Roguelike Indoors/Characters (CC0): bếp có lửa, bàn ghế, khách, bong bóng gọi món tên tiếng Việt, thanh kiên nhẫn đổi màu, tô món bốc khói.
- Shop: tiệm đồ lặn với chủ tiệm, kệ trưng bày, thẻ nâng cấp (hiệu quả hiện tại / cấp kế, giá, tối đa, hiệu lực từ Ngày kế), thông báo `bought` / `buy_failed`.
- `chonoi/live.py`: route `GET /assets/<file>` (chặn thoát thư mục) + test. Luật, contract, headless không đổi.

## [Phase 4] - 2026-11-21 — Test Contract v1.3 · Release v1.0.0

### Added
- `contract_version` 1.3: khai `bench_cmd` (`python3 -m chonoi.bench`, Đức Hải) và `soak_cmd` (`python3 -m chonoi.soak`, bot tất định).
- Cửa sổ chơi: `--mode day` (gather → quán → Shop), pause `Esc/P`, Shop bằng phím, 3 cảnh báo có chữ + biểu tượng, chế độ tương phản cao `H`.
- Tài liệu phát hành: README chạy từ clone sạch trong 3 lệnh, release notes, CREDITS (Hiệu); demo checklist (Tuấn); ma trận P4 và retro (Quang Hải).

### Fixed
- `chonoi.live` không còn sập khi in tiếng Việt trên console Windows (stdout cp1252).

## [Phase 3] - 2026-11-21 — Test Contract v1.2

### ⚠ Breaking change: kho đếm → kho cá thể
- File kho, `gather.hold`, `quan.stock`, `gather_end.inventory`: `{"items": {kind: n}}` → `{"items": [{"id","kind","fresh"}]}`. File kho đếm trả mã 2.
- `customers[].reserved`: map → mảng id cá thể. `cook_started.items`, `monster_hit.lost`, `faint.lost`: mảng cá thể.
- `base_price` chốt lúc nấu = `floor(giá niêm yết × trung bình fresh / 100)`.
- Cách cập nhật fixture: xem [ADR-0001](docs/adr/0001-kho-ca-the-v12.md).

### Added
- Độ tươi (`chonoi/fresh.py`): hao 0.5/s ở giỏ, 0.25/s ở kho quán, ươn khi < 30, event `spoiled`; giữ chỗ theo id (tươi nhất), giữ lại khi ươn; HUD thanh tươi.

## [Phase 2] - 2026-11-21 — Test Contract v1.1

### Added
- Số chuẩn Ticket-02 (6 nguyên liệu, 6 món, 2 bếp, 4 bàn, 8 đàn), cá bơi + sinh theo lịch, Cá Sấu Năm Chèo (patrol/chase/hit/recoil, bất tử).
- `--mode day` (D1–D5, Shop nâng cấp oxygen/hp, `--days`), pause cho cả ba mode, nút `pause/shop_done/attack/photo`, lệnh `buy`.
- Mở rộng `burn` (món chín quá 20 s thì cháy).

### Changed
- `contract_version` 1.0 → 1.1; `day` và `attack` từ "bị từ chối" thành hợp lệ.

## [Phase 1] - 2026-11-21

### Added
- **Quán Lát 4 (`chonoi/sim/quan.py`)**:
  - `_tick_stoves`: bếp nấu xong chuyển trạng thái sang `ready`, phát sự kiện `dish_ready`.
  - `_tick_eating`: khách ăn xong trả tiền (`paid`), tính tiền boa (tip) khi tỷ lệ kiên nhẫn lúc phục vụ $\ge 50\%$, cập nhật uy tín (`reputation` $+0.2$), khách rời bàn.
  - `_interact`: tương tác người chơi với bếp và bàn (`cook_started`, `dish_picked`, `served`), xử lý ưu tiên tie-break (khoảng cách gần nhất, bếp trước bàn, id nhỏ hơn).
  - Kết thúc ca quán (`quan_end`) khi hết thời gian.
  - Bộ test độc lập cho Lát 4 (`tests/test_quan_lat4.py`).
- **Hợp đồng tích hợp (`docs/contracts/quan.md`)**:
  - Chốt thứ tự gọi hàm trong `QuanSim.step()`.
  - Chốt schema trường của khách hàng (`Customer`) dùng chung cho Lát 3 và 4.
- **Bằng chứng kiểm chứng Lát 4 (`docs/proof/phase-1/quan-lat4/`)**:
  - Kịch bản 1: Bếp nấu chín sau 360 tick phát `dish_ready`.
  - Kịch bản 2: Khách ăn trong 3 tick phát `paid` kèm tiền boa và tăng uy tín.
- **Tiến độ Scrum/Release**:
  - Cập nhật biên bản standup giữa phase trong `docs/standup.md`.
  - Hoàn thiện hồ sơ thành viên `TEAM.md` và `docs/members/hoangngochieu10012000.md`.
