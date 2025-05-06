@echo off 
chcp 65001 > nul 
color 0A 
title Фронтенд OFS-Photomatrix 
 
cd frontend 
 
echo ===== ЗАПУСК ФРОНТЕНДА OFS-PHOTOMATRIX ===== 
echo. 
 
if not exist "node_modules" ( 
    echo [!] Установка зависимостей npm... 
    call npm install 
) 
 
REM Запускаем фронтенд с перенаправлением вывода 
echo [*] Запуск сервера разработки... 
echo [*] Адрес: http://localhost:5173/ 
echo [*] Логи сохраняются в ..\logs\frontend.log  
echo [*] Для завершения нажмите Ctrl+C 
 
npm run dev 2>> ..\logs\frontend_error.log 1>> ..\logs\frontend.log 
 
echo [!] Сервер остановлен или произошла ошибка 
echo [!] Проверьте логи ошибок в ..\logs\frontend_error.log 
pause 
