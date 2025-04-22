@echo off
chcp 65001 > nul
color 0A
title Очистка кэша Vite

echo ===================================================
echo          ОЧИСТКА КЭША VITE - ОФС ФОТОМАТРИЦА
echo ===================================================
echo.

cd %~dp0
echo Текущая директория: %cd%
echo.

echo 1. Очистка кэша Vite...
if exist "node_modules\.vite" (
    rmdir /s /q "node_modules\.vite"
    echo [УСПЕШНО] Кэш Vite удален!
) else (
    echo [ИНФО] Кэш Vite уже удален.
)
echo.

echo 2. Очистка кэша ESBuild...
if exist "node_modules\.esbuild" (
    rmdir /s /q "node_modules\.esbuild"
    echo [УСПЕШНО] Кэш ESBuild удален!
) else (
    echo [ИНФО] Кэш ESBuild уже удален.
)
echo.

echo 3. Очистка временных файлов сборки...
if exist "node_modules\.tmp" (
    rmdir /s /q "node_modules\.tmp"
    echo [УСПЕШНО] Временные файлы удалены!
) else (
    echo [ИНФО] Временные файлы уже удалены.
)
echo.

echo 4. Очистка завершена! Теперь запустите приложение с помощью:
echo npm run fast-dev
echo.

echo Для выхода нажмите любую клавишу...
pause > nul 