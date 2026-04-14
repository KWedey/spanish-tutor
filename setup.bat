@echo off
setlocal
rem Windows entry point for Spanish Fluency Tutor setup.
rem Invokes scripts\setup.py using the Python Launcher (py) if available,
rem falling back to python. Run this from inside the language\ folder.

where py >nul 2>&1
if %ERRORLEVEL% equ 0 goto :use_py
where python >nul 2>&1
if %ERRORLEVEL% equ 0 goto :use_python
goto :no_python

:use_py
py scripts\setup.py %*
exit /b %ERRORLEVEL%

:use_python
python scripts\setup.py %*
exit /b %ERRORLEVEL%

:no_python
echo.
echo Error: Python not found on PATH.
echo Install Python 3.10+ from https://python.org
echo During installation, check "Add Python to PATH".
exit /b 1
