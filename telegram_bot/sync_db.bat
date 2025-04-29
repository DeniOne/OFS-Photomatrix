@echo off
setlocal enabledelayedexpansion

echo ============================================
echo =   СИНХРОНИЗАЦИЯ ДАННЫХ ИЗ БАЗЫ ДАННЫХ   =
echo ============================================

REM Проверка наличия Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python не установлен или не добавлен в PATH
    exit /b 1
)

REM Проверка наличия корневого .env файла
if not exist "..\\.env" (
    echo [!] Корневой .env файл не найден. Используются настройки по умолчанию.
)

echo [i] Запуск синхронизации данных из БД...
python sync_db.py

if %ERRORLEVEL% EQU 0 (
    echo [+] Синхронизация успешно завершена
) else (
    echo [!] Ошибка при синхронизации данных (код: %ERRORLEVEL%)
)

echo [i] Готово! 