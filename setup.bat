@echo off
setlocal
rem Windows entry point for Spanish Fluency Tutor setup.
rem Invokes scripts\setup.py using the Python Launcher (py) if available,
rem falling back to python. Run this from inside the language\ folder.

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    py scripts\setup.py %*
    exit /b %ERRORLEVEL%
)
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python scripts\setup.py %*
    exit /b %ERRORLEVEL%
)
echo.
echo Error: Python not found on PATH.
echo Install Python 3.10+ from https://python.org
echo During installation, check "Add Python to PATH".
exit /b 1
