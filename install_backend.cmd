@echo off
chcp 65001 > nul
echo Устанавливаем зависимости для бэкенда...

cd backend

echo Устанавливаем зависимости...
pip install -r requirements.txt 2>nul

:: Если requirements.txt нет, пробуем через poetry
if errorlevel 1 (
    echo Пробуем установить через poetry...
    pip install poetry 2>nul
    poetry install
)

:: Если и это не сработает, устанавливаем основные зависимости напрямую
if errorlevel 1 (
    echo Устанавливаем необходимые пакеты напрямую...
    pip install fastapi uvicorn sqlalchemy asyncpg psycopg2 psycopg2-binary
)

:: Создаем файл-флаг, указывающий, что зависимости установлены
echo 1 > .deps_installed

echo Установка завершена!
pause 