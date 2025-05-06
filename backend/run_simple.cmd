@echo off
echo ====================================
echo Запуск упрощенного сервера FastAPI
echo ====================================

cd %~dp0

REM Проверка и исправление импортов в __init__.py
echo Проверяем и исправляем импорты в endpoints/__init__.py...

REM Создаем новый файл __init__.py с абсолютными импортами
echo # Инициализация пакета endpoints > app\api\endpoints\__init__.py.new
echo """>> app\api\endpoints\__init__.py.new
echo Этот файл экспортирует модули роутеров для доступа по имени>> app\api\endpoints\__init__.py.new
echo """>> app\api\endpoints\__init__.py.new
echo.>> app\api\endpoints\__init__.py.new
echo # Импортируем модули вручную с абсолютными импортами>> app\api\endpoints\__init__.py.new
echo from app.api.endpoints.auth import router as login>> app\api\endpoints\__init__.py.new
echo from app.api.endpoints.users import router as users>> app\api\endpoints\__init__.py.new
echo from app.api.endpoints.organizations import router as organizations>> app\api\endpoints\__init__.py.new
echo from app.api.endpoints.divisions import router as divisions>> app\api\endpoints\__init__.py.new
echo from app.api.endpoints.positions import router as positions>> app\api\endpoints\__init__.py.new
echo from app.api.endpoints.staff import router as staff>> app\api\endpoints\__init__.py.new
echo from app.api.endpoints.value_products import router as value_products>> app\api\endpoints\__init__.py.new
echo from app.api.endpoints.functions import router as functions>> app\api\endpoints\__init__.py.new
echo from app.api.endpoints.sections import router as sections>> app\api\endpoints\__init__.py.new
echo.>> app\api\endpoints\__init__.py.new
echo # Экспортируем имена>> app\api\endpoints\__init__.py.new
echo __all__ = [>> app\api\endpoints\__init__.py.new
echo     "login", "users", "organizations", "divisions",>> app\api\endpoints\__init__.py.new
echo     "positions", "staff", "value_products", "functions",>> app\api\endpoints\__init__.py.new
echo     "sections">> app\api\endpoints\__init__.py.new
echo ]>> app\api\endpoints\__init__.py.new
echo.>> app\api\endpoints\__init__.py.new
echo print("Успешно импортированы роутеры в endpoints/__init__.py:", __all__)>> app\api\endpoints\__init__.py.new

REM Заменяем оригинальный файл
move /Y app\api\endpoints\__init__.py.new app\api\endpoints\__init__.py

REM Удаляем кэш Python, чтобы гарантировать, что импорты будут перезагружены
echo Удаляем кэш Python...
rmdir /S /Q app\api\__pycache__ 2>nul
rmdir /S /Q app\api\endpoints\__pycache__ 2>nul

REM Убедимся, что нет проблемного файла orgchart.py
if exist app\api\endpoints\orgchart.py (
    echo Переименовываем проблемный файл orgchart.py...
    ren app\api\endpoints\orgchart.py orgchart.py.bak2
)

echo Запускаем упрощенный сервер...
python simple_server.py

pause
