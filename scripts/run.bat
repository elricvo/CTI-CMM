@echo off
REM Author: eric vanoverbeke
REM Date: 2026-01-18
cd /d "%~dp0.."
set "APP_TEST_DATA="
for %%A in (%*) do (
  if /I "%%A"=="--test-data" set "APP_TEST_DATA=1"
)
if defined APP_TEST_DATA (
  set "APP_DATA_DIR=%CD%\\data-test"
)
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 9999
) else (
  python -m uvicorn app.main:app --host 127.0.0.1 --port 9999
)
