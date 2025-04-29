@echo off
echo ========================================
echo =    Экспорт отделов из БД в JSON-файл   =
echo ========================================
echo.

python export_sections_to_json.py

echo.
echo Нажмите любую клавишу для выхода...
pause > nul 