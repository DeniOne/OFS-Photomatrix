@echo off
echo ===========================================
echo Экспорт должностей для Telegram-бота
echo ===========================================
echo.

cd %~dp0
python export_positions.py

if %ERRORLEVEL% NEQ 0 (
  echo [ОШИБКА] Экспорт должностей не удался!
  pause
  exit /b 1
)

echo.
echo Нажмите любую клавишу для завершения...
pause > nul 