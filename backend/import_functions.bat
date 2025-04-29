@echo off
echo ===========================================
echo Импорт функций из Excel в базу данных
echo ===========================================
echo.

REM Проверяем наличие файла Excel (новое имя - functions.xlsx)
if not exist "functions.xlsx" (
  echo [ERROR] Файл "functions.xlsx" не найден!
  echo Пожалуйста, поместите Excel-файл в текущую директорию.
  echo.
  pause
  exit /b 1
)

REM Запрашиваем начальный номер функции
set /p START_NUM="С какого номера начать нумерацию функций (по умолчанию 0): "
if "%START_NUM%"=="" set START_NUM=0

echo [1/3] Установка необходимых зависимостей...
python install_dependencies.py
if %ERRORLEVEL% NEQ 0 (
  echo [ERROR] Ошибка при установке зависимостей!
  pause
  exit /b 1
)

echo.
echo [2/3] Очистка существующих функций и должностей в БД...
python clean_positions_functions.py
if %ERRORLEVEL% NEQ 0 (
  echo [ERROR] Ошибка при очистке базы данных!
  pause
  exit /b 1
)

echo.
echo [3/3] Импорт функций из Excel-файла...
python import_functions_from_excel.py %START_NUM%
if %ERRORLEVEL% NEQ 0 (
  echo [ERROR] Ошибка при импорте функций!
  pause
  exit /b 1
)

echo.
echo ===========================================
echo ГОТОВО! Функции успешно импортированы.
echo ===========================================
echo.
pause 