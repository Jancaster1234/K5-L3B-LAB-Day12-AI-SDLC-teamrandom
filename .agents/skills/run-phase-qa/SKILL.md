---
name: run-phase-qa
description: Chạy kiểm tra QA của lab Chợ Nổi trước khi tích hợp hoặc gắn tag phase, ghi log thật và phân biệt lỗi môi trường với lỗi luật chơi.
---

# QA trước tích hợp

Chạy từ gốc repo. Đọc `AGENTS.md`, `docs/plan/phase-1.md` và phần
liên quan trong `docs/contracts/README.md`; contract đang là bản nháp nên
ghi rõ giả định còn chờ PO trong kết luận.

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\lab.ps1 setup
powershell -ExecutionPolicy Bypass -File .\lab.ps1 test
```

Nếu chạy thủ công, dùng `$env:PYTHONPATH = 'tests;.'`, không dùng `tests:.`.
Tên `python3` trong contract phải trỏ tới Python thật; `lab.ps1` đặt PATH
vào venv có alias riêng, không cần thay contract hoặc cấu hình alias toàn máy.
Linux/macOS: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`.

Ghi lệnh, commit nền, phiên bản Python, exit code, số test và toàn bộ stdout/stderr
vào `docs/proof/phase-1/qa-lat5/` (hoặc thư mục phase được giao).
Suite có test hộp đen gather → kho → quan và tất định từng byte;
chỉ ghi đạt cho phạm vi mà test thực sự bao phủ.

Nếu lỗi `helpers`/không tìm thấy `python3`, sửa môi trường rồi chạy lại.
Nếu assertion sai luật, ghi failure và chuyển cho chủ lát; không sửa test,
contract hay luật của lát khác chỉ để có kết quả xanh.
Link kết quả trong verification. Làm ở nhánh riêng, kiểm tra diff trước commit;
việc gộp main và gắn tag thuộc Integrator theo TEAM.md.
