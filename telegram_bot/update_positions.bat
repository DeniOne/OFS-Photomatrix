@echo off
echo ===========================================
echo Обновление должностей для Telegram-бота
echo ===========================================
echo.

cd %~dp0
python update_positions.py

echo.
echo Нажмите любую клавишу для завершения...
pause > nul 