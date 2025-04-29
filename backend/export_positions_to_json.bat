@echo off
echo ========================================
echo = Экспорт должностей из БД в JSON-файл =
echo ========================================
echo.

python export_positions_to_json.py

echo.
echo Нажмите любую клавишу для выхода...
pause > nul 