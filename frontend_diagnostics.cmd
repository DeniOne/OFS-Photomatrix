@echo on
title Диагностика фронтенда OFS-Photomatrix
color 0E

echo ===================================================
echo          ДИАГНОСТИКА ФРОНТЕНДА OFS-PHOTO          
echo ===================================================
echo.

echo 1. Проверяем текущую директорию
echo Текущий путь: %cd%
echo.

echo 2. Проверяем наличие директории frontend
if exist "frontend" (
    echo [УСПЕШНО] Директория frontend найдена
) else (
    echo [ОШИБКА] Директория frontend не найдена!
)
echo.

echo 3. Проверяем версии Node.js и npm
echo --- Версия Node.js:
node --version
echo --- Версия npm:
npm --version
echo.

echo 4. Переходим в директорию frontend
cd frontend
echo Текущий путь: %cd%
echo.

echo 5. Проверяем содержимое директории frontend
dir
echo.

echo 6. Проверка package.json
if exist "package.json" (
    echo [УСПЕШНО] package.json найден
    echo --- Содержимое package.json:
    type package.json
) else (
    echo [ОШИБКА] package.json не найден!
)
echo.

echo 7. Проверка директории node_modules
if exist "node_modules" (
    echo [УСПЕШНО] Директория node_modules найдена
    echo --- Проверка ключевых модулей:
    if exist "node_modules\react" (
        echo [УСПЕШНО] React найден
    ) else (
        echo [ОШИБКА] React не найден!
    )
    
    if exist "node_modules\vite" (
        echo [УСПЕШНО] Vite найден
    ) else (
        echo [ОШИБКА] Vite не найден!
    )
) else (
    echo [ОШИБКА] Директория node_modules не найдена!
)
echo.

echo 8. Проверка занятости порта 5173
netstat -ano | findstr ":5173" | findstr "LISTENING"
if errorlevel 1 (
    echo [УСПЕШНО] Порт 5173 свободен
) else (
    echo [ПРЕДУПРЕЖДЕНИЕ] Порт 5173 уже занят!
)
echo.

echo 9. Тестовый запуск npm в корне frontend
echo --- Выполняем npm --version:
npm --version
echo.

echo 10. Тестовый запуск npm run
echo --- Выполняем npm run:
call npm run --help
echo.

echo 11. Пытаемся запустить npm run dev с флагом --verbose
echo --- Выполняем npm run dev --verbose:
echo !!! ВНИМАНИЕ: После запуска вы увидите подробный лог. Для остановки нажмите Ctrl+C
echo Нажмите любую клавишу для продолжения...
pause > nul

call npm run dev --verbose

echo.
echo ===================================================
echo          ДИАГНОСТИКА ЗАВЕРШЕНА                   
echo ===================================================
echo.
echo Если вы видите это сообщение, значит скрипт запуска отработал полностью.
echo Пожалуйста, сохраните весь вывод для анализа.
echo.

pause 