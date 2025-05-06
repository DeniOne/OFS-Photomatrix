@echo off
cd backend
set PYTHONPATH=%cd%

echo Пытаемся запустить сервер с выводом ошибок...
python main.py > error_full.log 2>&1
echo Сервер завершил работу, ошибка записана в файл error_full.log

type error_full.log
pause
