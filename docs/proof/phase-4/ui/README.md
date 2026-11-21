# Bằng chứng giao diện — cảnh báo và đồ họa (AC-P4-02, v1.1.0)

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

## Chưa có
- Ảnh chế độ tương phản cao (`H`): bật bằng phím và lưu `localStorage`, Edge headless không gửi phím được, nên chưa có ảnh; mã nằm ở `warnings()` / `frame()` trong `chonoi/web/index.html`.
- Màn Shop trong lượt chơi thật (phải qua hết buổi sáng + tối); `shop-mock.png` chỉ chứng minh cách vẽ với snapshot đúng schema (`phase:"shop"`, `upgrades`, `active_upgrades`, `meta = tuning.shop`, sự kiện `bought`).
