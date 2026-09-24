@echo off
cd /d "%~dp0"
set "GMAIL_HOME=[путь владельца] May26\gmail"
"[путь владельца] Files\Python311\python.exe" -u batch_runner.py batch_evening.json 0 > run_evening.out 2>&1
