# OFS Photomatrix

**Organizational Framework System** - система управления организационной структурой компании с возможностью расширения до полноценной ERP.

## Основные возможности

- Управление организационной структурой (холдинги, юр. лица, подразделения)
- Управление сотрудниками и должностями
- Система ценностных функций и конечных продуктов
- Функциональные отношения и матрицы ответственности
- Аналитика и визуализация оргструктуры

## Технологии

### Бэкенд
- Python 3.11
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Pydantic 2.x
- JWT-авторизация

### Фронтенд
- React 18
- TypeScript
- Tailwind CSS
- Mantine или Chakra UI
- React Query
- Recharts/ApexCharts

## Установка и запуск

### Требования
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+
- Poetry

### Настройка бэкенда

1. Клонировать репозиторий:
```
git clone https://github.com/username/ofs-photomatrix.git
cd ofs-photomatrix
```

2. Установить зависимости бэкенда:
```
cd backend
poetry install
```

3. Создать базу данных:
```
createdb ofs_photomatrix
```

4. Настроить переменные окружения (создать файл .env):
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ofs_photomatrix
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
SECRET_KEY=your-secret-key
```

5. Запустить миграции:
```
poetry run alembic upgrade head
```

6. Запустить сервер:
```
poetry run uvicorn main:app --reload
```

## Структура проекта

```
/backend              # Backend API
  /app                # Основной код приложения
  /migrations         # Миграции Alembic
  /tests              # Тесты
  /scripts            # Скрипты

/frontend             # React frontend
  /src                # Исходный код
  /public             # Статичные файлы
```

## API Документация

API документация доступна по адресу `/docs` или `/redoc` после запуска сервера.

## Лицензия

MIT 