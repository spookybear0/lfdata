@echo off
setlocal
cd /d "%~dp0"

echo Creating Windows virtual environment (venv)...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment. Please check that Python is installed.
    exit /b %errorlevel%
)

echo Installing dependencies in editable mode...
"venv\Scripts\pip.exe" install -e .[dev]
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b %errorlevel%
)

echo Setup complete! You can now run the tool using run.bat.
endlocal
