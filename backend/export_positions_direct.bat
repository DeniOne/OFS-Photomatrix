@echo off
setlocal enabledelayedexpansion

echo ===========================================
echo Прямой экспорт должностей из БД для телеграм-бота
echo ===========================================
echo.

cd %~dp0

REM Запрашиваем параметры подключения к БД, если не заданы
if "%DB_HOST%"=="" (
  set /p DB_HOST="Введите хост БД (по умолчанию: localhost): "
  if "!DB_HOST!"=="" set DB_HOST=localhost
)

if "%DB_PORT%"=="" (
  set /p DB_PORT="Введите порт БД (по умолчанию: 5432): "
  if "!DB_PORT!"=="" set DB_PORT=5432
)

if "%DB_USER%"=="" (
  set /p DB_USER="Введите имя пользователя БД (по умолчанию: postgres): "
  if "!DB_USER!"=="" set DB_USER=postgres
)

if "%DB_PASS%"=="" (
  set /p DB_PASS="Введите пароль БД: "
)

if "%DB_NAME%"=="" (
  set /p DB_NAME="Введите имя БД (по умолчанию: ofs_photomatrix): "
  if "!DB_NAME!"=="" set DB_NAME=ofs_photomatrix
)

REM Устанавливаем переменные окружения
set DB_HOST=%DB_HOST%
set DB_PORT=%DB_PORT%
set DB_USER=%DB_USER%
set DB_PASS=%DB_PASS%
set DB_NAME=%DB_NAME%

REM Проверяем наличие psycopg2
python -c "import psycopg2" 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Установка недостающего модуля psycopg2...
  pip install psycopg2
  if %ERRORLEVEL% NEQ 0 (
    echo Не удалось установить psycopg2, пробуем psycopg2-binary...
    pip install psycopg2-binary
    if %ERRORLEVEL% NEQ 0 (
      echo [ОШИБКА] Не удалось установить модуль psycopg2
      pause
      exit /b 1
    )
  )
)

REM Запускаем скрипт
python export_positions_direct.py

if %ERRORLEVEL% NEQ 0 (
  echo [ОШИБКА] Экспорт должностей не удался!
  pause
  exit /b 1
)

echo.
echo Нажмите любую клавишу для завершения...
pause > nul

endlocal 