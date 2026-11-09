@echo off
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 "%~dp0launch.py" --with-cellpose --prepare-only
) else (
    python "%~dp0launch.py" --with-cellpose --prepare-only
)
if errorlevel 1 pause
