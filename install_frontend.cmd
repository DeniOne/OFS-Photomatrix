@echo off
echo ===================================================
echo Установка фронтенда для проекта ОФС Фотоматрица
echo ===================================================
echo.

cd frontend

echo Инициализация проекта React с TypeScript и Vite...
echo.

call npm init vite@latest . -- --template react-ts

echo.
echo Установка зависимостей...
echo.

call npm install

echo.
echo Установка Tailwind CSS...
echo.

call npm install -D tailwindcss postcss autoprefixer
call npx tailwindcss init -p

echo.
echo Установка библиотеки UI (Mantine)...
echo.

call npm install @mantine/core @mantine/hooks @emotion/react

echo.
echo Установка React Router...
echo.

call npm install react-router-dom

echo.
echo Установка React Query для запросов...
echo.

call npm install @tanstack/react-query

echo.
echo Установка дополнительных пакетов...
echo.

call npm install axios @mantine/form @mantine/notifications

echo.
echo Установка завершена! Чтобы запустить фронтенд, введите:
echo cd frontend
echo npm run dev
echo.

pause 