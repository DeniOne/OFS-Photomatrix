@echo off
chcp 65001 > nul
color 0A
title Запуск фронтенда

echo Запуск фронтенда OFS-Photomatrix...
echo.

cd frontend
echo Текущая директория: %cd%

if not exist "package.json" (
    echo ОШИБКА: package.json не найден! Запуск невозможен.
    echo Возможно, вы запустили скрипт из неправильной директории.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo Установка зависимостей npm...
    call npm install
)

echo.
echo Запуск сервера разработки...
echo Адрес: http://localhost:5173/
echo Для остановки нажмите Ctrl+C
echo.

call npm run dev

cd ..
pause 