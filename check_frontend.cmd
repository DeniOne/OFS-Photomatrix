@echo off
chcp 65001 > nul
color 0E
title Проверка работы фронтенда

echo ╔════════════════════════════════════════╗
echo ║   ПРОВЕРКА РАБОТЫ ФРОНТЕНДА OFS-PHOTO  ║
echo ╚════════════════════════════════════════╝

echo Проверяем доступность фронтенда...
curl -s http://localhost:5173 -o nul
if errorlevel 1 (
    color 0C
    echo Фронтенд не отвечает!
    echo Проверьте, запущен ли start_frontend.cmd
) else (
    color 0A
    echo.
    echo ✓ Фронтенд работает нормально!
    echo.
    echo Доступ к приложению:
    echo http://localhost:5173
    
    :: Проверяем наличие процессов vite
    wmic process where "commandline like '%%vite%%'" get processid | find /i "ProcessId" > nul
    if errorlevel 1 (
        color 0E
        echo.
        echo ! Предупреждение: процесс Vite не найден, хотя порт доступен
        echo  Возможно, порт занят другим приложением
    )
)

pause 