@echo off
echo ========================================
echo = Экспорт департаментов из БД в JSON-файл =
echo ========================================
echo.

python export_divisions_to_json.py

echo.
echo Нажмите любую клавишу для выхода...
pause > nul 