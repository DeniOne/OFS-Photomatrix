@echo off
chcp 65001 > nul
color 0A
title Запуск OFS-Photomatrix Frontend
setlocal enabledelayedexpansion

:MAIN_MENU
cls
echo ╔════════════════════════════════════════╗
echo ║   УПРАВЛЕНИЕ OFS-PHOTOMATRIX FRONTEND  ║
echo ╚════════════════════════════════════════╝
echo.
echo Выберите режим работы:
echo.
echo [1] - Запустить фронтенд
echo [2] - Диагностика фронтенда
echo [3] - Отладочный режим
echo [4] - Установка/переустановка фронтенда
echo [5] - Полный сброс (удаление node_modules)
echo [6] - Выход
echo.
choice /c 123456 /n /m "Ваш выбор (1-6): "

set choice_result=%errorlevel%
if %choice_result% equ 6 goto EXIT
if %choice_result% equ 5 goto RESET
if %choice_result% equ 4 goto INSTALL
if %choice_result% equ 3 goto DEBUG
if %choice_result% equ 2 goto DIAGNOSTICS
if %choice_result% equ 1 goto START

:START
cls
echo ╔════════════════════════════════════════╗
echo ║       ЗАПУСК ФРОНТЕНДА                 ║
echo ╚════════════════════════════════════════╝
echo.

echo [1] Проверяем окружение...
where node >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: Node.js не найден!
    echo Пожалуйста, установите Node.js и добавьте его в PATH
    pause
    goto MAIN_MENU
)

echo    - Node.js найден: 
node --version

where npm >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: NPM не найден!
    echo Пожалуйста, переустановите Node.js или проверьте PATH
    pause
    goto MAIN_MENU
)

echo    - npm найден: 
npm --version
echo.

echo [2] Проверяем наличие директории фронтенда...
echo    - Текущая директория: %cd%
if not exist "frontend" (
    color 0C
    echo ОШИБКА: Директория frontend не найдена!
    echo Возможно, вы запустили скрипт из неправильной директории.
    echo Текущая директория: %cd%
    pause
    goto MAIN_MENU
)
echo    - Директория frontend найдена

echo [3] Переходим в директорию фронтенда...
cd frontend
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: Не удалось перейти в директорию frontend!
    echo Возможно, нет прав доступа или директория заблокирована.
    pause
    goto MAIN_MENU
)
echo    - Текущая директория: %cd%
echo.

echo [4] Проверяем package.json...
if not exist "package.json" (
    color 0C
    echo ОШИБКА: package.json не найден!
    echo Возможно, проект не инициализирован.
    echo Текущая директория: %cd%
    
    echo Хотите инициализировать проект сейчас? (Y/N)
    choice /c YN /n
    if %errorlevel% equ 1 (
        cd ..
        goto INSTALL
    ) else (
        cd ..
        goto MAIN_MENU
    )
)
echo    - package.json найден

echo [5] Проверяем node_modules...
if not exist "node_modules" (
    color 0E
    echo ПРЕДУПРЕЖДЕНИЕ: node_modules не найден, выполняем установку...
    echo.
    echo Это может занять некоторое время. Пожалуйста, подождите...
    
    call npm install
    if %errorlevel% neq 0 (
        color 0C
        echo ОШИБКА: Не удалось установить зависимости!
        echo Проверьте доступ к интернету и права доступа к директории.
        pause
        cd ..
        goto MAIN_MENU
    )
    echo    - Установка зависимостей завершена
)
echo    - node_modules найден

echo [6] Проверяем скрипт dev в package.json...
type package.json | findstr "\"dev\":" >nul
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: Скрипт "dev" не найден в package.json!
    echo Содержимое package.json:
    type package.json
    echo.
    echo Проект не настроен для запуска с помощью "npm run dev".
    pause
    cd ..
    goto MAIN_MENU
)
echo    - Скрипт dev найден в package.json

echo [7] Проверяем доступность порта 5173...
netstat -ano | findstr ":5173" >nul
if %errorlevel% equ 0 (
    color 0E
    echo ПРЕДУПРЕЖДЕНИЕ: Порт 5173 уже занят другим процессом!
    echo Возможно, сервер фронтенда уже запущен.
    netstat -ano | findstr ":5173"
    echo.
    echo Продолжить запуск? (Y/N)
    choice /c YN /n
    if %errorlevel% equ 2 (
        cd ..
        goto MAIN_MENU
    )
)
echo    - Порт 5173 проверен

echo [8] Запускаем фронтенд...
echo.
echo Запуск команды: npm run dev
echo.
echo Адрес фронтенда: http://localhost:5173/
echo Для остановки нажмите Ctrl+C
echo.
echo Пожалуйста, подождите...

call npm run dev

set npm_result=%errorlevel%
if %npm_result% neq 0 (
    color 0C
    echo ОШИБКА: Не удалось запустить фронтенд! Код ошибки: %npm_result%
    echo.
    echo Возможные причины:
    echo 1. Скрипт dev не найден в package.json
    echo 2. Ошибка в коде фронтенда
    echo 3. Порт 5173 занят другим процессом
    echo.
    echo Для детальной информации запустите в режиме отладки (пункт 3)
) else (
    echo Фронтенд завершил работу нормально
)

cd ..
pause
goto MAIN_MENU

:DIAGNOSTICS
cls
color 0B
echo ╔════════════════════════════════════════╗
echo ║      ДИАГНОСТИКА FRONTEND              ║
echo ╚════════════════════════════════════════╝
echo.

echo [1] Текущая директория: %cd%

echo [2] Проверка директории frontend...
if exist "frontend" (
    echo     √ Директория frontend существует
) else (
    color 0C
    echo     X Директория frontend НЕ существует!
    pause
    goto MAIN_MENU
)

echo [3] Проверка Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo     X Node.js НЕ установлен или недоступен!
    echo Проверьте, установлен ли Node.js и добавлен ли он в PATH
) else (
    echo     √ Node.js установлен: 
    node --version
)

echo [4] Проверка npm...
where npm >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo     X npm НЕ установлен или недоступен!
    echo Проверьте, установлен ли npm и добавлен ли он в PATH
) else (
    echo     √ npm установлен: 
    npm --version
)

echo [5] Проверка перехода в директорию frontend...
echo     Пытаемся перейти в директорию frontend...
cd frontend 2>nul
if %errorlevel% neq 0 (
    echo     X Не удалось перейти в директорию frontend!
    pause
    goto MAIN_MENU
) else (
    echo     √ Переход в директорию frontend успешен
    echo     Текущая директория: %cd%
)

echo [6] Проверка содержимого директории frontend...
echo     Содержимое директории:
dir /b

echo [7] Проверка package.json...
if exist "package.json" (
    echo     √ package.json существует
    echo     Содержимое scripts в package.json:
    type package.json | findstr /C:"\"scripts\"" /C:"\"dev\"" /C:"vite"
) else (
    color 0C
    echo     X package.json НЕ существует!
)

echo [8] Проверка node_modules...
if exist "node_modules" (
    echo     √ node_modules существует
) else (
    color 0E
    echo     ! node_modules НЕ существует, установка не выполнялась
)

echo [9] Проверка React...
if exist "node_modules\react" (
    echo     √ React установлен
) else (
    echo     ! React НЕ установлен
)

echo [10] Проверка Vite...
if exist "node_modules\vite" (
    echo     √ Vite установлен
) else (
    echo     ! Vite НЕ установлен
)

echo [11] Проверка доступности порта 5173...
netstat -ano | findstr ":5173" >nul
if %errorlevel% equ 0 (
    color 0E
    echo     ! Порт 5173 занят другим процессом
    netstat -ano | findstr ":5173"
) else (
    echo     √ Порт 5173 свободен
)

echo [12] Проверка npm-команд...
call npm run --help >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo     X Ошибка при выполнении npm-команд!
) else (
    echo     √ npm-команды работают корректно
    echo     Доступные скрипты:
    call npm run
)

cd ..
echo.
echo Диагностика завершена. Нажмите любую клавишу для возврата в главное меню...
pause >nul
goto MAIN_MENU

:DEBUG
cls
color 0B
echo ╔════════════════════════════════════════╗
echo ║     ОТЛАДКА OFS-PHOTOMATRIX FRONTEND   ║
echo ╚════════════════════════════════════════╝
echo.

echo [1] Текущая директория: %cd%

echo [2] Проверка Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: Node.js не найден!
    echo Пожалуйста, установите Node.js и добавьте его в PATH
    goto DEBUG_ERROR
) else (
    echo Node.js: 
    node --version
)

echo [3] Проверка npm...
where npm >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: npm не найден!
    echo Пожалуйста, проверьте установку Node.js
    goto DEBUG_ERROR
) else (
    echo npm: 
    npm --version
)

echo [4] Переходим в директорию frontend...
if not exist "frontend" (
    color 0C
    echo ОШИБКА: Директория frontend не найдена!
    echo Текущая директория: %cd%
    goto DEBUG_ERROR
)

cd frontend 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: Не удалось перейти в директорию frontend!
    goto DEBUG_ERROR
)
echo Текущая директория: %cd%

echo [5] Проверка содержимого директории...
echo Содержимое директории:
dir

echo [6] Проверка package.json...
if not exist "package.json" (
    color 0C
    echo ОШИБКА: package.json не найден!
    goto DEBUG_ERROR
)

echo [7] Содержимое package.json:
type package.json

echo [8] Проверка скриптов в package.json...
type package.json | findstr "\"dev\":" >nul
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: Скрипт "dev" не найден в package.json!
    goto DEBUG_ERROR
)

echo [9] Содержимое скриптов в package.json:
type package.json | findstr /C:"\"scripts\"" /C:"\"dev\""

echo [10] Попытка запуска фронтенда в режиме отладки...
echo.
echo Запуск команды: npm run dev --verbose
echo.
echo Если приложение сразу закрывается, вероятно, возникает ошибка в скрипте npm
echo Попробуйте запустить вручную в отдельном окне консоли:
echo cd %cd% && npm run dev
echo.
echo Нажмите любую клавишу для запуска...
pause >nul

echo Запускаем npm в режиме verbose...
call npm run dev --verbose

set npm_result=%errorlevel%
if %npm_result% neq 0 (
    color 0C
    echo ОШИБКА: Не удалось запустить фронтенд! Код ошибки: %npm_result%
) else (
    echo Фронтенд завершил работу нормально
)
goto DEBUG_END

:DEBUG_ERROR
echo.
echo Обнаружены ошибки препятствующие запуску в отладочном режиме.
echo Попробуйте использовать опцию "Диагностика фронтенда" для выявления проблем.

:DEBUG_END
cd %~dp0
pause
goto MAIN_MENU

:INSTALL
cls
color 0D
echo ╔════════════════════════════════════════╗
echo ║     УСТАНОВКА OFS-PHOTOMATRIX FRONTEND ║
echo ╚════════════════════════════════════════╝
echo.

:INSTALL_CHECK
echo [1] Проверяем директорию frontend...
if not exist "frontend" (
    echo Создаем директорию frontend...
    mkdir frontend
    if %errorlevel% neq 0 (
        color 0C
        echo ОШИБКА: Не удалось создать директорию frontend!
        pause
        goto MAIN_MENU
    )
)

cd frontend
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: Не удалось перейти в директорию frontend!
    pause
    goto MAIN_MENU
)
echo Текущая директория: %cd%

echo [2] Проверка существующего package.json...
if exist "package.json" (
    echo package.json уже существует.
    echo.
    choice /c YN /n /m "Хотите перезаписать существующий проект? (Y/N): "
    if %errorlevel% equ 2 (
        echo Установка отменена.
        cd ..
        pause
        goto MAIN_MENU
    )
)

echo [3] Инициализация проекта...
echo Инициализация проекта React с TypeScript и Vite...
echo.
echo Этот процесс может занять некоторое время.
echo.
echo Нажмите любую клавишу для продолжения или Ctrl+C для отмены...
pause >nul

call npm init vite@latest . -- --template react-ts
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: Не удалось инициализировать проект!
    echo Возможные причины:
    echo 1. Нет доступа к интернету
    echo 2. Проблемы с npm registry
    echo 3. Недостаточно прав доступа
    cd ..
    pause
    goto MAIN_MENU
)

echo [4] Установка базовых зависимостей...
echo.
call npm install
if %errorlevel% neq 0 (
    color 0C
    echo ОШИБКА: Не удалось установить базовые зависимости!
    pause
    cd ..
    goto MAIN_MENU
)

echo [5] Установка дополнительных библиотек...
echo.
echo Установка Tailwind CSS...
call npm install -D tailwindcss postcss autoprefixer
call npx tailwindcss init -p

echo Установка Mantine...
call npm install @mantine/core @mantine/hooks @emotion/react

echo Установка React Router...
call npm install react-router-dom

echo Установка React Query...
call npm install @tanstack/react-query

echo Установка дополнительных пакетов...
call npm install axios @mantine/form @mantine/notifications

echo.
echo Установка завершена! 
cd ..
pause
goto MAIN_MENU

:RESET
cls
color 0E
echo ╔════════════════════════════════════════╗
echo ║     СБРОС OFS-PHOTOMATRIX FRONTEND     ║
echo ╚════════════════════════════════════════╝
echo.
echo ВНИМАНИЕ! Будут удалены все установленные пакеты (node_modules)
echo и потребуется их переустановка, что может занять время.
echo.
choice /c YN /n /m "Вы уверены, что хотите выполнить сброс? (Y/N): "

if %errorlevel% equ 2 goto MAIN_MENU

echo [1] Удаляем node_modules...
if exist "frontend\node_modules" (
    echo Удаление node_modules. Это может занять некоторое время...
    rd /s /q "frontend\node_modules"
    if %errorlevel% neq 0 (
        color 0C
        echo ОШИБКА: Не удалось удалить node_modules!
        echo Возможно, некоторые файлы заблокированы другим процессом.
    ) else (
        echo node_modules успешно удален
    )
) else (
    echo node_modules не найден
)

echo [2] Очистка кэша npm...
call npm cache clean --force
echo Кэш npm очищен

echo [3] Сброс выполнен успешно!
pause
goto MAIN_MENU

:EXIT
echo Выход из программы...
endlocal
exit /b 0 