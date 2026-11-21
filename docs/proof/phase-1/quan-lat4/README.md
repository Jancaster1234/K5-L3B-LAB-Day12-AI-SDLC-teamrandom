# Bằng chứng — Quán lát 4 (bếp, bàn, trả tiền, boa, uy tín, hết ca)

- **Code:** commit `b451805` (và merge `8f91a5d`), các hàm `_tick_stoves`, `_tick_eating`, `_interact`, `_can_cook`, `_dish_to_cook` trong `chonoi/sim/quan.py` · **Người làm:** Hoàng Ngọc Hiệu (`hoangngochieu10012000`, Scrum/Release)
- **Môi trường:** Python 3.13 / Windows 10/11 · **Ngày:** 2026-11-21
- **Số liệu** (từ `game.contract.json`): `walk_speed` 4.0 · `interact_radius` 1.5 · `eat_s` 10 (600 tick) · `tip_rate` 0.2 · `tip_min_patience_ratio` 0.5 · `tip_reputation` 0.2 · `reputation_initial` 3.0 · `reputation_min` 0 · `reputation_max` 5 · Menu: `ca_loc_nuong_trui` (cook 6s/360 tick, giá 60k), `goi_bong_sung` (cook 4s/240 tick, giá 40k), `lau_ca_linh_dien_dien` (cook 10s/600 tick, giá 120k).

Chạy lại từ thư mục gốc repo (trên Windows dùng `PYTHONPATH="tests;."`):

```bash
H="python3 -m chonoi.headless --mode quan --seed 1 --snapshot-every 1000"
P=docs/proof/phase-1/quan-lat4
$H --ticks 363 --scenario $P/01-stove-cook-ready.scenario.json --inputs $P/01-stove-cook-ready.inputs.json --out $P/01-stove-cook-ready.out.jsonl
$H --ticks 602 --scenario $P/02-serve-paid-tip.scenario.json --inputs $P/02-serve-paid-tip.inputs.json --out $P/02-serve-paid-tip.out.jsonl
$H --ticks 602 --scenario $P/03-serve-paid-notip.scenario.json --inputs $P/03-serve-paid-notip.inputs.json --out $P/03-serve-paid-notip.out.jsonl
$H --ticks 5   --scenario $P/04-quan-end.scenario.json --out $P/04-quan-end.out.jsonl
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

## Kết quả

| # | Luật | Kịch bản | Kết quả quan sát | Đạt? |
|---|---|---|---|---|
| 1 | Bếp nấu và lấy món: interact tại bếp `idle` đủ nguyên liệu → `cook_started`, đủ `cook_s` → `dish_ready`, interact tại bếp `ready` → `dish_picked` (tay cầm món, bếp về `idle`) | `01-stove-cook-ready`: kho có `{"ca_loc": 1}`, đứng tại bếp `B1`, bấm `interact` tick 0 và tick 361 | Tick 1: `cook_started {stove_id:"B1", dish_id:"ca_loc_nuong_trui"}` · Tick 361: `dish_ready {stove_id:"B1", dish_id:"ca_loc_nuong_trui"}` · Tick 362: `dish_picked {stove_id:"B1", dish_id:"ca_loc_nuong_trui"}`; tick 363: `hand = "ca_loc_nuong_trui"`, bếp `B1` về `idle`, kho trừ sạch cá | ✅ |
| 2 | Phục vụ khách & ăn & thanh toán có boa (patience $\ge 50\%$): interact tại bàn → `served`, khách chuyển `eating` (10s), ăn xong → `paid` (+20% tip), tăng uy tín +0.2 | `02-serve-paid-tip`: tay cầm món `ca_loc_nuong_trui`, khách `C1` tại bàn `T1` có patience 3000/3600 (83.3%), bấm `interact` tick 0 | Tick 1: `served {customer_id:"C1", table_id:"T1", dish_id:"ca_loc_nuong_trui"}` · Tick 601: `paid {customer_id:"C1", table_id:"T1", dish_id:"ca_loc_nuong_trui", price:60, tip:12, amount:72}`; tick 602: `money: 72`, `reputation: 3.2`, khách `C1` rời bàn | ✅ |
| 3 | Phục vụ khách & ăn & thanh toán không boa (patience $< 50\%$): ăn xong trả tiền nhưng không có tip, uy tín giữ nguyên | `03-serve-paid-notip`: khách `C2` tại bàn `T1` có patience 1000/3600 (27.7%), ăn món `goi_bong_sung` (40k) | Tick 1: `served` · Tick 601: `paid {price:40, tip:0, amount:40}`; tick 602: `money: 40`, `reputation: 3.0` (không tăng) | ✅ |
| 4 | Hết giờ kết thúc ca quán: `time_left_ticks` về 0 → phát sự kiện `quan_end` kèm đầy đủ số liệu ca | `04-quan-end`: `time_left_ticks: 3`, `reputation: 4.5`, chạy 5 tick | Tick 3: `quan_end {reason:"time", money:0, earned:0, shift_earned:0, reputation:4.5}`; dòng `end` có `state:"finished"`, `reason:"time"` | ✅ |
| 5 | Quy tắc ưu tiên tương tác (tie-break): khoảng cách gần nhất, nếu bằng thì bếp trước bàn (0 < 1), nếu cùng loại thì id nhỏ hơn | Test `test_interact_tie_break_stove_before_table` trong `tests/test_quan_lat4.py` | Người chơi đứng giữa bếp và bàn cùng khoảng cách 1.0 → ưu tiên tương tác bếp trước | ✅ |
| 6 | Giới hạn mang vác (`carry_limit: 1`): tay đang cầm món không thể bốc thêm món khác | Test `test_carry_limit_cannot_pick_second_dish` trong `tests/test_quan_lat4.py` | Tay đang cầm món không bốc thêm món từ bếp ready | ✅ |
| 7 | Tất định và toàn bộ test xanh: cùng seed ra cùng kết quả | Bộ 78 test gồm unit test, integration test, smoke test P1 | `Ran 78 tests … OK`, xem `test-output.txt` | ✅ |
