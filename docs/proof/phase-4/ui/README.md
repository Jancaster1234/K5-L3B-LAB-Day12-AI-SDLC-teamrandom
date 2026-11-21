# Bằng chứng giao diện — cảnh báo, đồ họa, màn phủ (AC-P2-08, AC-P4-02)

- **Người làm:** Jancaster1234 (Integrator, dùng Claude Code) · **Ngày:** 2026-11-21 · Windows 10, Python 3.12.0, Edge headless 1400×800.
- **Cách chụp:** chạy `chonoi.live` thật, điều khiển nhân vật bằng `POST /input` (cùng API trình duyệt dùng),
  chờ đúng điều kiện cảnh báo trong `GET /state`, rồi chụp `msedge --headless=new --screenshot`.
  Riêng `shop-mock.png` chụp từ server giả trả snapshot Shop dựng sẵn (xem cuối file).

| Ảnh | Lệnh / điều kiện | Thấy gì |
|---|---|---|
| [warn-monster.png](warn-monster.png) | `live --mode gather --seed 1`; lặn tới (54, 19) tới khi cách Cá Sấu M1 ≤ 10 m và độ sâu ≥ 10 | Banner "🐊 Thủy quái!", viền tím quanh màn hình, Cá Sấu ở trạng thái `chase` (dấu "!") |
| [warn-oxygen.png](warn-oxygen.png) | `live --mode gather --seed 1`; lặn nông ở (20, 6) tới khi oxy < 20% | Banner "💨 Oxy sắp hết", thanh oxy đỏ 5s |
| [warn-angry-customer.png](warn-angry-customer.png) | `live --mode quan --seed 1 --scenario docs/proof/phase-3/04-quan-fresh.scenario.json`; đứng yên 47 s tới khi kiên nhẫn < 22% | Banner "😠 Khách sắp giận: T1, T2", thanh kiên nhẫn đỏ, kho có hàng ươn |
| [dive.png](dive.png) | `live --mode day`; lặn xuống từ bến | Sprite cá Kenney, đáy cát, rong, Út Sen bơi có bình oxy, Cá Sấu |
| [quan.png](quan.png) | `live --mode quan` + fixture trên; nấu 2 bếp, phục vụ T2 | Bếp "Chín! (E)", khách T1 chờ "Lẩu cá linh điên điển", khách T2 đang ăn (tô bốc khói) |
| [shop-mock.png](shop-mock.png) | Server giả, snapshot Shop Ngày 2: đã mua bình oxy cấp 1, tiền 450 | Thẻ nâng cấp, "có hiệu lực từ Ngày 3", thông báo "Đã mua Bình oxy cấp 1 (−200k)" |

## Phát hiện khi chụp
- Biểu tượng 🫧 (Unicode 14) của hai cảnh báo oxy hiện thành ô vuông: font emoji Windows 10 không có ký tự này.
  Đã đổi sang ⚠️ (hết hơi) và 💨 (oxy sắp hết) trong `chonoi/web/index.html`; ảnh `warn-oxygen.png` chụp sau khi sửa.
- Lặn sát Cá Sấu tới khi oxy thấp thì bị cắn ngất trước, nên hai cảnh báo lặn được chụp riêng.

## Chơi trọn một Ngày — màn phủ, Shop thật, tương phản cao (sau v1.1.0)

- **Lệnh:** `live --mode day --days 1 --seed 1 --port 8790` + `node .agents/skills/ui-screenshot-check/scripts/playday.mjs 8790 <thư mục ảnh> <msedge.exe> <profile>`
  (skill [ui-screenshot-check](../../../../.agents/skills/ui-screenshot-check/SKILL.md)).
- **Cách làm:** Edge headless mở trang; phím **Enter / H / 1** bấm thật qua DevTools (`Input.dispatchKeyEvent`), di chuyển nhân vật qua `POST /input`.
  Bot hái bông súng N3/N4, về bến (gather kết thúc `docked`), tối nấu → bưng → phục vụ, vào Shop bấm `1`, `Enter` đóng Shop.
- **Kết quả `/state` cuối:** `reason: days_complete`, `history: [{day 1, served 3, left 1, shift_earned 86, tips 13, sold {goi_bong_sung: 3}, earned 86, reputation 3.1}]`, `score 386`.
  Chạy 2 lượt liên tiếp cho cùng kết quả; ảnh dưới là lượt 2 (code cuối của nhánh `ui-screens`).

| Ảnh | Thấy gì |
|---|---|
| [01-menu](screens/01-menu.png) | Menu: tên game, chế độ, bảng phím, công thức điểm; sim đứng yên (`paused`) tới khi Enter |
| [02-dayintro](screens/02-dayintro.png) | Ngày 1/1: thực đơn (cá lóc nướng trui × 3, gỏi bông súng × 3), cần lấy (bông súng × 6, cá lóc × 3), trang bị |
| [07-high-contrast](screens/07-high-contrast.png) | Bấm phím `H` thật giữa lúc lặn: "tương phản cao BẬT", nền đen, màu đậm |
| [03-evening](screens/03-evening.png) | Buổi tối: kho mang về (bông súng × 12, ươn 3), thực đơn, lưu ý cháy món / khách bỏ đi |
| [04-day-result](screens/04-day-result.png) | Kết quả Ngày 1: 4/5 sao, phục vụ 3, bỏ đi 1, thu 86k, boa 13k, uy tín 3.1, điểm 386, đã bán gỏi bông súng × 3 |
| [05-shop](screens/05-shop.png) | **Shop trong lượt chơi thật**: bấm `1` khi có 86k → sự kiện `buy_failed {funds}` → thông báo "Không đủ tiền" |
| [06-summary](screens/06-summary.png) | Tổng kết 1 Ngày: bảng từng Ngày, "Điểm cuối: 386 = 86 + 100 × 3" |

## Chưa có
- Ảnh chụp trên macOS.
- `shop-mock.png` ở bảng trên là ảnh cũ từ snapshot dựng sẵn; nay đã có [05-shop](screens/05-shop.png) từ lượt chơi thật.
