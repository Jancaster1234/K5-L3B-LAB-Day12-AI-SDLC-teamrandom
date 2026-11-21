# Kiểm tra môi trường Windows — 2026-11-21

- Python 3.13.3, môi trường riêng `.venv`, chỉ dùng thư viện chuẩn.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\lab.ps1 setup`: exit 0.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\lab.ps1 test`: 32 tests, 11.135s, OK (exit 0), gồm kiểm tra HTTP live server.
- `lab.ps1 headless -Mode gather` và `lab.ps1 headless -Mode quan`: exit 0;
  mỗi file có 62 dòng JSONL, kết thúc với ticks=600, reason=tick_limit.
- Đầu ra cục bộ trong `.local/`, không đưa vào Git.
- Phạm vi: chuẩn bị môi trường và lệnh PowerShell; chưa triển khai các TODO luật chơi.
