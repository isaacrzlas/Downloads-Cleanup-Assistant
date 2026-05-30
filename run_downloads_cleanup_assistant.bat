@echo off
setlocal
set "APP_DIR=%~dp0"
set "VENV_PY=%APP_DIR%.venv\Scripts\python.exe"

if exist "%VENV_PY%" (
  "%VENV_PY%" "%APP_DIR%main.py"
) else (
  python "%APP_DIR%main.py"
)
