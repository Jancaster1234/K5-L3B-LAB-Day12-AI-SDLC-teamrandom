---
name: verify-phase-proof
description: Đối chiếu bằng chứng headless của lab Chợ Nổi với lần chạy lại và liên kết bằng chứng vào ma trận verification, không suy diễn đạt toàn phase từ smoke test.
---

# Kiểm chứng và truy vết bằng chứng

Đọc `docs/proof/phase-1/gather-lat1/README.md`, các fixture tương ứng,
`docs/clarify.md` và `docs/verification/phase-1.md`. Dùng nhãn luật mô tả
nếu chưa có mã AC từ PRD; không tự tạo mã AC rồi gọi đó là yêu cầu chính thức.

Chạy lại 4 fixture lát 1 bằng Python của môi trường đã setup:

```powershell
.\.venv\Scripts\python.exe .agents\skills\verify-phase-proof\scripts\replay_lat1.py
```

Script ghi kết quả ra stdout, trả exit code khác 0 nếu chạy lỗi, output khác
bằng chứng đã lưu, kho khác hoặc hai lần chạy cùng seed khác nhau.
Output tái chạy ở thư mục tạm, không ghi đè bằng chứng gốc.
So byte với blob JSONL tại `HEAD` qua `git show`, vì `core.autocrlf=true`
có thể đổi LF thành CRLF khi checkout trên Windows. Hai output mới vẫn
phải giống nhau từng byte; script không chuẩn hóa output để che sai khác.
Lưu stdout/stderr và exit code thật vào proof của QA khi cần làm bằng chứng review.

Trong ma trận verification, link tương đối tới README, JSONL, fixture và log QA;
chỉ ghi đạt khi đã kiểm chứng. Ghi riêng điều kiện còn chờ PO
(clarify #6: tick ngạt đầu tiên; #7: ngất trước cập bến; schema event còn nháp).
Chạy suite bằng hướng dẫn `run-phase-qa` khi đánh giá hồi quy/tích hợp.
Thiếu artifact thì ghi chưa có bằng chứng, không tạo log giả hoặc mượn
kết quả của lát 1 để xác nhận lát 2–4.
