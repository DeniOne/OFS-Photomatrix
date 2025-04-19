@echo off
chcp 65001 > nul
color 0A
title Запуск проекта OFS-Photomatrix

echo ╔════════════════════════════════════════╗
echo ║      ЗАПУСК ПРОЕКТА OFS-PHOTOMATRIX    ║
echo ╚════════════════════════════════════════╝

:: Проверяем наличие всех необходимых файлов
if not exist "start_backend.cmd" (
    color 0C
    echo Ошибка: Файл start_backend.cmd не найден!
    goto END
)

if not exist "start_frontend.cmd" (
    color 0C
    echo Ошибка: Файл start_frontend.cmd не найден!
    goto END
)

echo [1] Запускаем бэкенд в отдельном окне...
start "OFS-Photomatrix Backend" cmd /c start_backend.cmd

echo [2] Ждем 5 секунд для инициализации бэкенда...
timeout /t 5 /nobreak > nul

echo [3] Проверяем статус бэкенда...
curl -s http://127.0.0.1:8000/health > nul
if errorlevel 1 (
    echo    - Бэкенд еще не запустился, ждем еще 10 секунд...
    timeout /t 10 /nobreak > nul
    
    :: Повторная проверка
    curl -s http://127.0.0.1:8000/health > nul
    if errorlevel 1 (
        color 0E
        echo    - Предупреждение: Бэкенд не отвечает, но продолжаем запуск фронтенда...
    ) else (
        echo    - Бэкенд успешно запущен!
    )
) else (
    echo    - Бэкенд успешно запущен!
)

echo [4] Запускаем фронтенд...
start "OFS-Photomatrix Frontend" cmd /c start_frontend.cmd

echo [5] Ждем 5 секунд для инициализации фронтенда...
timeout /t 5 /nobreak > nul

echo.
echo ╔════════════════════════════════════════╗
echo ║     ПРОЕКТ OFS-PHOTOMATRIX ЗАПУЩЕН     ║
echo ╚════════════════════════════════════════╝
echo.
echo * Бэкенд: http://127.0.0.1:8000/docs
echo * Фронтенд: http://localhost:5173
echo.
echo Приложение запущено в отдельных окнах. Для завершения работы:
echo 1. Закройте окна с бэкендом и фронтендом
echo 2. Или используйте Ctrl+C в каждом окне
echo.

:END
pause 