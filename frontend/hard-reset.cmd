@echo off
color 0B
echo ==================================
echo =       HARD RESET VITE         =
echo ==================================
echo.
echo Запускаем скрипт для полного сброса...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0hard-reset.ps1"
echo.
echo Если скрипт не сработал, попробуйте запустить сами:
echo powershell -ExecutionPolicy Bypass -File hard-reset.ps1
echo.
pause 