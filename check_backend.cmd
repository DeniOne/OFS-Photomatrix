@echo off
chcp 65001 > nul
color 0E
title Проверка работы бэкенда

echo ╔════════════════════════════════════════╗
echo ║    ПРОВЕРКА РАБОТЫ OFS-PHOTOMATRIX     ║
echo ╚════════════════════════════════════════╝

echo Проверяем доступность API...
curl -s http://127.0.0.1:8000/health
if errorlevel 1 (
    color 0C
    echo Бэкенд не отвечает!
    echo Проверьте, запущен ли start_backend.cmd
) else (
    color 0A
    echo.
    echo ✓ Бэкенд работает нормально!
    echo.
    echo Документация API доступна по адресу:
    echo http://127.0.0.1:8000/docs
)

pause 