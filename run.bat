@echo off
setlocal
set PYTHONPATH=%~dp0src
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" -m lfdata %*
) else (
    python -m lfdata %*
)
endlocal
