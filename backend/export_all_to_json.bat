@echo off
echo ====================================================
echo = Экспорт всех данных из БД в JSON-файлы для бота  =
echo ====================================================
echo.

echo 1. Экспорт департаментов (divisions) в telegram_bot/data/divisions.json
python export_divisions_to_json.py
echo.

echo 2. Экспорт отделов (sections) в telegram_bot/data/sections.json
python export_sections_to_json.py
echo.

echo 3. Экспорт должностей (positions) в telegram_bot/data/positions.json
python export_positions_to_json.py
echo.

echo ✅ Экспорт всех данных завершен!
echo.
echo Нажмите любую клавишу для выхода...
pause > nul 