# Выявленные критические проблемы и памятка по ошибкам

Опираясь на детальный анализ документации и кода проекта, я выявил следующие фундаментальные проблемы и возможные точки сбоя:

### 1. Несовместимость версий компонентов
- **Проблема**: Сильная зависимость от конкретных версий библиотек, особенно в связке FastAPI 0.99.x + Pydantic 1.x + Python 3.7-3.9
- **Ошибки**: 
  - `ModuleNotFoundError: No module named 'pydantic_settings'`
  - `ImportError: cannot import name 'field_validator'`
  - `NameError: name '_SessionBindKey' is not defined`
  - `NameError: name 'Optional' is not defined` (проблема с типами в Python 3.12+)
- **Решение**: Строгая фиксация версий всех зависимостей, использование Docker для изоляции среды

### 2. Чрезмерная сложность типизации
- **Проблема**: Сложная схема типов с кастомными аннотациями и неявными зависимостями
- **Ошибки**:
  - `TypeError: Cannot resolve ForwardRef` (сложности с отложенными ссылками в типах)
  - Несовместимость типов между Pydantic 1.x и 2.x
  - Проблемы с Generic[T] и TypeVar
- **Решение**: Упрощение схемы типов, использование строгой типизации с современным синтаксисом Python 3.10+

### 3. Смешение синхронного и асинхронного кода
- **Проблема**: В проекте смешивается синхронный SQLAlchemy и асинхронный asyncpg
- **Ошибки**: 
  - Блокировки потоков при вызове синхронного кода из асинхронного контекста
  - Проблемы с транзакциями и закрытием соединений
- **Решение**: Полный переход на асинхронный стек с использованием asyncpg, SQLAlchemy 2.0 с async поддержкой

### 4. Проблемы с базой данных и миграциями
- **Проблема**: Множественные скрипты для исправления схемы БД, нестабильность Alembic
- **Ошибки**:
  - Отсутствие нужных колонок и ограничений в таблицах
  - Проблемы с типами enum в Postgres
  - Сложности при миграции с SQLite на PostgreSQL
- **Решение**: Четкая схема БД, написанная с нуля с корректными типами и ограничениями

### 5. Неконсистентные API-маршруты
- **Проблема**: Разрозненное определение роутеров и эндпоинтов
- **Ошибки**:
  - Несогласованность URL-паттернов (`/organizations` vs `/api/v1/organizations`)
  - Отсутствие стандартизации ответов
- **Решение**: Единообразные REST-эндпоинты с консистентной структурой ответов

### 6. Архитектурные проблемы фронтенда
- **Проблема**: Переход с Material UI на Ant Design, проблемы с зависимостями
- **Ошибки**:
  - `Ошибка загрузки @ant-design/graphs: ReferenceError: require is not defined`
  - `Failed to resolve import "./components/layout/MainLayout"`
- **Решение**: Полный рефакторинг с использованием современных практик и библиотек

### 7. Проблемы интеграции
- **Проблема**: Нестабильные интеграции с внешними сервисами (Telegram)
- **Решение**: Четкие API-контракты и строгая типизация для интеграций

## Детальный технический промт для рефакторинга

На основе всего проанализированного материала, я создам первую часть промта, который будет фокусироваться на архитектуре и технологиях для нового проекта. В следующих частях мы детализируем бизнес-логику и особенности реализации.

---

# Промт для рефакторинга OFS Global

## 1. Архитектура и технологический стек

### Бэкенд
- **Язык программирования**: Python 3.11
- **Веб-фреймворк**: FastAPI 0.104.0 (стабильная версия)
- **ORM**: SQLAlchemy 2.0.x с асинхронной поддержкой
- **Валидация данных**: Pydantic 2.4.x
- **Миграции**: Alembic 1.12.x
- **База данных**: PostgreSQL 15
- **Типизация**: Строгая, с использованием нативных типов Python
- **Документация**: OpenAPI (Swagger UI)
- **Аутентификация**: JWT с использованием современных библиотек
- **Контейнеризация**: Docker для изоляции среды разработки и развертывания

### Фронтенд
- **Язык программирования**: TypeScript 5.x
- **Фреймворк**: React 18.x с хуками
- **Сборка**: Vite (не Webpack)
- **Стилизация и UI**: 
  - Tailwind CSS 3.x для базовых стилей
  - Styled Components для продвинутой кастомизации
  - Mantine UI или Chakra UI как основа компонентов (вместо Ant Design)
  - Neumorphism-ui пакет для объёмных контролов
- **Графики и визуализации**:
  - Recharts для базовых графиков
  - ApexCharts или D3.js для продвинутой визуализации данных
  - react-flow для диаграмм связей и оргструктуры
- **Анимации**:
  - Framer Motion для анимаций интерфейса
  - react-spring для 3D-эффектов и сложных переходов
- **Управление состоянием**: React Context API + React Query для запросов
- **Маршрутизация**: React Router 6.x
- **Типизация**: Строгий TypeScript с правильной настройкой tsconfig

### Структура проекта

#### Бэкенд
```
/backend
  /app
    /api
      /endpoints      # API-эндпоинты группированные по функциональности
      /deps.py        # Зависимости для FastAPI
    /core
      /config.py      # Конфигурация приложения
      /security.py    # Аутентификация и авторизация
    /crud             # CRUD операции для моделей
    /db
      /base.py        # Базовые классы для моделей
      /session.py     # Управление сессиями БД
    /models           # SQLAlchemy модели
    /schemas          # Pydantic схемы
    /services         # Бизнес-логика
    /utils            # Вспомогательные функции
    main.py           # Входная точка приложения
  /migrations         # Миграции Alembic
  /tests              # Тесты
  /scripts            # Скрипты для обслуживания
  Dockerfile          # Для контейнеризации
  pyproject.toml      # Зависимости (Poetry)
  docker-compose.yml  # Конфигурация Docker Compose
```

#### Фронтенд
```
/frontend
  /public             # Статические файлы
  /src
    /api              # API-клиенты
    /components       # React-компоненты
    /hooks            # Кастомные хуки
    /layouts          # Шаблоны страниц
    /pages            # Страницы приложения
    /routes           # Маршрутизация
    /services         # Сервисы для бизнес-логики
    /store            # Управление состоянием
    /types            # TypeScript типы
    /utils            # Вспомогательные функции
    App.tsx           # Корневой компонент
    main.tsx          # Входная точка
  /tests              # Тесты
  vite.config.ts      # Конфигурация Vite
  package.json        # Зависимости
  tsconfig.json       # Конфигурация TypeScript
  Dockerfile          # Для контейнеризации
```

### Принципы реализации и лучшие практики

1. **Полностью асинхронный бэкенд**:
   - Использование `async/await` во всем коде
   - Правильное управление соединениями и транзакциями

2. **Четкое разделение слоев**:
   - Модели данных (БД) отделены от схем API (Pydantic)
   - Бизнес-логика в сервисах, а не в маршрутах

3. **Единообразие API**:
   - Консистентная структура URL (`/api/v1/resource`)
   - Стандартные ответы с пагинацией, сортировкой, фильтрацией
   - Четкая обработка ошибок

4. **Современная типизация**:
   - Строгие типы во всем проекте (и бэкенд, и фронтенд)
   - Избегание сложных конструкций типов, когда это возможно

5. **Чистый и тестируемый код**:
   - Маленькие функции с понятной ответственностью
   - Внедрение зависимостей для тестируемости
   - Покрытие тестами критических компонентов

6. **Прозрачные зависимости**:
   - Строгая фиксация версий всех библиотек
   - Документирование всех зависимостей и их назначения

7. **Безопасность**:
   - Правильная аутентификация и авторизация
   - Валидация всех входных данных
   - Использование HTTPS

8. **Документация кода**:
   - Комментарии для сложных участков
   - Автоматическая генерация документации из кода
   - Типы как форма документации

## 2. Модель данных и схема базы данных

Создадим чистую, нормализованную схему БД для основных сущностей проекта:

```sql
-- Пользователи системы
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_superuser BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Организации
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    org_type VARCHAR(50) NOT NULL,
    parent_id INTEGER REFERENCES organizations(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Подразделения
CREATE TABLE divisions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    parent_id INTEGER REFERENCES divisions(id),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(code, organization_id)
);

-- Отделы
CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    division_id INTEGER NOT NULL REFERENCES divisions(id),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(code, division_id)
);

-- Должности
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    division_id INTEGER REFERENCES divisions(id),
    section_id INTEGER REFERENCES sections(id),
    attribute VARCHAR(50), -- Уровень должности (Директор, Руководитель и т.д.)
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(code, division_id)
);

-- Сотрудники
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    hire_date DATE,
    user_id INTEGER REFERENCES users(id),
    photo_path VARCHAR(255),
    document_paths JSONB,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Связь сотрудников и должностей (M:N)
CREATE TABLE staff_positions (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES staff(id),
    position_id INTEGER NOT NULL REFERENCES positions(id),
    is_primary BOOLEAN NOT NULL DEFAULT false,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(staff_id, position_id)
);

-- Функции
CREATE TABLE functions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Ценностные функции
CREATE TABLE value_functions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    parent_id INTEGER REFERENCES value_functions(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Функциональные назначения (связь должностей и функций)
CREATE TABLE functional_assignments (
    id SERIAL PRIMARY KEY,
    position_id INTEGER NOT NULL REFERENCES positions(id),
    function_id INTEGER NOT NULL REFERENCES functions(id),
    percentage INTEGER NOT NULL DEFAULT 100,
    is_primary BOOLEAN NOT NULL DEFAULT false,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(position_id, function_id)
);

-- Функциональные связи
CREATE TABLE functional_relations (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES positions(id),
    target_id INTEGER NOT NULL REFERENCES positions(id),
    relation_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Места расположения
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    region VARCHAR(100),
    country VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Связь сотрудников и мест расположения
CREATE TABLE staff_locations (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES staff(id),
    location_id INTEGER NOT NULL REFERENCES locations(id),
    is_primary BOOLEAN NOT NULL DEFAULT false,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(staff_id, location_id)
);
```

## 3. Ключевые компоненты для реализации

## 4. Детализация бизнес-логики и компонентов системы

На основе анализа Контекст.ini, который описывает сложную организационную структуру "Фотоматрицы", детализируем ключевые бизнес-требования и компоненты.

### 4.1 Бизнес-сущности и их взаимоотношения

#### Иерархия управления
```
Совет учредителей
    ↓
Генеральный директор
    ↓
Директора (по направлениям)
    ↓
Руководители департаментов (divisions)
    ↓
Руководители отделов (sections)
    ↓
Функции (functions)
    ↓
Должности (positions)
    ↓
Сотрудники (staff)
```

#### Параллельные структуры
- **HOLDING** - Главная бизнес-структура
- **LEGAL_ENTITY** - Юридические лица
- **LOCATION** - Территориальные подразделения

#### Критические особенности взаимоотношений
1. **Множественное подчинение**:
   - Должности могут иметь несколько родителей-функций и родителей-руководителей
   - Отделы могут подчиняться нескольким департаментам
   - Функции могут подчиняться разным отделам и/или департаментам

2. **Динамичное распределение сотрудников**:
   - Сотрудник может занимать разные должности в разные смены
   - Сотрудник может менять локации ситуативно
   - Сотрудник может выполнять несколько функций из разных отделов одновременно

3. **Многоуровневые отношения**:
   - Функциональные отношения (FunctionalRelation) отдельно от иерархической структуры
   - Атрибуты иерархии для должностей (уровни доступа к информации)

### 4.2 API-эндпоинты и структура данных

#### Основные API-эндпоинты

##### Организационная структура
```
/api/v1/organizations             # CRUD для организаций (HOLDING, LEGAL_ENTITY)
/api/v1/locations                 # CRUD для локаций
/api/v1/divisions                 # CRUD для департаментов
/api/v1/sections                  # CRUD для отделов
/api/v1/functions                 # CRUD для функций
/api/v1/positions                 # CRUD для должностей
/api/v1/value-functions           # CRUD для ценностных функций
```

##### Сотрудники и назначения
```
/api/v1/staff                     # CRUD для сотрудников
/api/v1/staff-positions           # Управление должностями сотрудников
/api/v1/staff-locations           # Управление локациями сотрудников
/api/v1/functional-assignments    # Назначение функций на должности
/api/v1/functional-relations      # Управление функциональными связями
```

##### Визуализация и аналитика
```
/api/v1/org-chart                 # Получение данных для оргструктуры
/api/v1/org-chart/holding         # Визуализация по холдингу
/api/v1/org-chart/legal           # Визуализация по юр. лицам
/api/v1/org-chart/location        # Визуализация по локациям
/api/v1/org-chart/hierarchy       # Полная иерархия отношений
/api/v1/value-products            # ЦКП (Ценный конечный продукт) и связанные сущности
```

#### Дополнительные API для интеграции с будущей ERP
```
/api/v1/social-rating             # Система социального рейтинга сотрудников
/api/v1/company-tokens            # Управление внутренними токенами компании
/api/v1/schedules                 # Управление расписанием и сменами
/api/v1/performance               # Показатели эффективности (KPI)
```

### 4.3 Специфичные модели данных

#### Ключевые реляционные модели для гибкой организационной структуры

```python
# Модель для динамического назначения сотрудников на должности
class StaffPositionAssignment(BaseModel):
    id: int
    staff_id: int
    position_id: int
    is_primary: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    schedule_pattern: Optional[str] = None  # Шаблон расписания или смен
    rotation_type: Optional[str] = None     # Тип ротации (постоянно, временно, по сменам)
    
# Модель для сложных функциональных отношений
class FunctionalRelation(BaseModel):
    id: int
    source_id: int                 # ID должности-источника
    target_id: int                 # ID должности-приемника
    relation_type: str             # Тип отношения (руководство, наставничество, координация)
    weight: float = 1.0            # Вес связи для визуализации и расчетов
    description: Optional[str] = None
    
# Модель для иерархических атрибутов доступа
class HierarchyAttribute(BaseModel):
    id: int
    name: str                      # Название атрибута
    level: int                     # Уровень в иерархии (1 - высший)
    access_rights: Dict[str, bool] # Права доступа к различным компонентам системы
    
# Модель для ценного конечного продукта
class ValueProduct(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_entity_type: str         # Тип сущности-владельца (division, section, function)
    owner_entity_id: int           # ID сущности-владельца
    metrics: List[Dict]            # Метрики для оценки продукта
    dependencies: List[int]        # Зависимые сущности
    parent_id: Optional[int] = None        # ID родительского ЦКП (для иерархии)
    weight: float = 1.0            # Вес влияния на родительский ЦКП (от 0.1 до 1.0)
    completion_metrics: Dict[str, Any] = {} # Метрики выполнения ЦКП
    target_values: Dict[str, Any] = {}      # Целевые значения для метрик
    current_values: Dict[str, Any] = {}     # Текущие значения метрик
    status: str = "active"         # Статус ЦКП (active, completed, suspended)
```

# Расширенная модель для структуры ЦКП (Ценного Конечного Продукта)
```python
# Модель для структуры ЦКП и связей между ними
class ValueProductHierarchy(BaseModel):
    id: int
    parent_id: Optional[int] = None        # ID родительского ЦКП
    child_id: int                          # ID дочернего ЦКП
    influence_weight: float = 1.0          # Коэффициент влияния на родительский ЦКП (0.1-1.0)
    required_for_completion: bool = False  # Обязательно для выполнения родительского ЦКП
    
# Модель для измерения прогресса выполнения ЦКП
class ValueProductProgress(BaseModel):
    id: int
    value_product_id: int                  # ID ЦКП
    reporting_period: str                  # Период отчетности (день, неделя, месяц)
    target_value: float                    # Целевое значение
    current_value: float                   # Текущее значение
    achievement_percentage: float          # Процент выполнения
    updated_at: datetime                   # Время последнего обновления
    
# Модель для трекинга вклада сотрудников в выполнение ЦКП
class StaffValueContribution(BaseModel):
    id: int
    staff_id: int                          # ID сотрудника
    value_product_id: int                  # ID ЦКП
    contribution_coefficient: float        # Коэффициент вклада (0.1-1.0)
    reporting_period: str                  # Период отчетности
    contribution_metrics: Dict[str, float] # Метрики вклада
    notes: Optional[str] = None            # Примечания
```

#### Модели для интеграции с ERP-функциями

```python
# Социальный рейтинг сотрудника
class SocialRating(BaseModel):
    id: int
    staff_id: int
    total_points: int = 0
    activity_log: List[Dict]        # История активностей
    rewards: List[Dict]             # Полученные награды
    valid_until: Optional[date] = None

# Внутренние токены компании
class CompanyToken(BaseModel):
    id: int
    token_type: str                 # "regular" или "gold"
    amount: float
    staff_id: int
    issued_at: datetime
    expires_at: Optional[datetime] = None
    transaction_type: str           # "reward", "bonus", "exchange"
    description: Optional[str] = None
```

### 4.4 UI-компоненты и визуализация

#### Ключевые компоненты интерфейса

1. **Интерактивная оргструктура** с тремя представлениями:
   - Холдинговая структура
   - Юридическая структура
   - Территориальная структура

2. **Визуализация функциональных отношений**:
   - Графовое представление взаимосвязей
   - Матрица RACI для определения ответственности
   - Тепловые карты нагрузки/эффективности

3. **Управление должностями и сотрудниками**:
   - Быстрое назначение/переназначение сотрудников
   - Управление сменами и расписанием
   - Профили сотрудников с историей назначений

4. **Аналитические дашборды**:
   - Анализ эффективности организационной структуры
   - Мониторинг загруженности отделов/сотрудников
   - Отчеты по ЦКП и достижению целей

### 4.5 Интеграции с внешними системами

1. **Rocket.Chat для коммуникаций и управления персоналом**:
   - Регистрация сотрудников и личные кабинеты
   - Корпоративные коммуникации и уведомления
   - Административный интерфейс для управления
   - ИИ-ассистент для помощи сотрудникам и руководителям
   - Интеграция с основной системой ОФС через API

2. **Интеграция с системами учета времени**:
   - Автоматическая регистрация рабочего времени
   - Контроль смен и присутствия

3. **Финансовые интеграции**:
   - Связь с системой начисления заработной платы
   - Интеграция с 1С Бухгалтерия

4. **Аналитика и ИИ**:
   - Анализ эффективности организационной структуры
   - Рекомендации по оптимизации структуры
   - Прогнозирование потребности в персонале
   - Аналитика выполнения ЦКП и влияния на бизнес-показатели

## 4.6 Система ЦКП (Ценного Конечного Продукта)

### Основные концепции ЦКП

1. **Иерархическая структура ЦКП**:
   - Каждая сущность организационной структуры (от совета учредителей до отдельных должностей) имеет свой ЦКП
   - ЦКП верхнего уровня включает в себя ЦКП нижних уровней
   - Выполнение ЦКП нижних уровней напрямую влияет на выполнение ЦКП верхних уровней
   - Влияние нижних ЦКП на верхние определяется весовыми коэффициентами

2. **Метрики и измерения ЦКП**:
   - Каждый ЦКП имеет конкретные измеримые показатели
   - Система отслеживает прогресс выполнения ЦКП в реальном времени
   - Аналитические дашборды показывают взаимосвязь ЦКП разных уровней

3. **Вклад сотрудников в выполнение ЦКП**:
   - Система отслеживает вклад каждого сотрудника в выполнение ЦКП
   - Вклад учитывается при расчете социального рейтинга и вознаграждений
   - Визуализация показывает эффективность сотрудников относительно ЦКП

### Структура данных ЦКП в базе данных

```sql
-- Ценные конечные продукты (ЦКП)
CREATE TABLE value_products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    owner_entity_type VARCHAR(50) NOT NULL, -- (organization, division, section, position, function)
    owner_entity_id INTEGER NOT NULL,
    parent_id INTEGER REFERENCES value_products(id),
    metrics JSONB,
    status VARCHAR(50) DEFAULT 'active',
    weight FLOAT DEFAULT 1.0,
    target_values JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Иерархия ЦКП
CREATE TABLE value_product_hierarchy (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES value_products(id),
    child_id INTEGER NOT NULL REFERENCES value_products(id),
    influence_weight FLOAT DEFAULT 1.0,
    required_for_completion BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(parent_id, child_id)
);

-- Прогресс выполнения ЦКП
CREATE TABLE value_product_progress (
    id SERIAL PRIMARY KEY,
    value_product_id INTEGER NOT NULL REFERENCES value_products(id),
    reporting_period VARCHAR(50) NOT NULL,
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    target_value FLOAT,
    current_value FLOAT,
    achievement_percentage FLOAT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Вклад сотрудников в ЦКП
CREATE TABLE staff_value_contributions (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES staff(id),
    value_product_id INTEGER NOT NULL REFERENCES value_products(id),
    contribution_coefficient FLOAT DEFAULT 1.0,
    reporting_period VARCHAR(50) NOT NULL,
    period_date DATE NOT NULL,
    contribution_metrics JSONB,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### API для работы с ЦКП

```
/api/v1/value-products                      # CRUD для ЦКП
/api/v1/value-products/hierarchy            # Управление иерархией ЦКП
/api/v1/value-products/{id}/progress        # Отслеживание прогресса выполнения ЦКП
/api/v1/value-products/{id}/children        # Получение дочерних ЦКП
/api/v1/value-products/{id}/contributors    # Сотрудники, вносящие вклад в ЦКП
/api/v1/staff/{id}/value-contributions      # Вклад сотрудника в различные ЦКП
/api/v1/analytics/value-chain               # Аналитика цепочки создания ценности
/api/v1/analytics/completion-forecast       # Прогноз выполнения ЦКП
```

### Визуализация и аналитика ЦКП

1. **Дерево ЦКП**:
   - Интерактивная визуализация иерархии ЦКП
   - Цветовая индикация статуса выполнения
   - Возможность проследить влияние нижних ЦКП на верхние

2. **Дашборды прогресса**:
   - Текущий статус выполнения ЦКП по подразделениям
   - Исторические тренды выполнения
   - Прогнозы на основе текущей динамики

3. **Карты влияния**:
   - Визуализация влияния сотрудников на выполнение ЦКП
   - Идентификация критических зависимостей в цепочке создания ценности
   - Анализ узких мест в процессах

### Интеграция ЦКП с другими компонентами системы

1. **ЦКП и социальный рейтинг**:
   - Вклад в выполнение ЦКП влияет на социальный рейтинг сотрудника
   - Система автоматически отслеживает и вознаграждает значительный вклад в ЦКП

2. **ЦКП и планирование ресурсов**:
   - Распределение ресурсов на основе приоритетности ЦКП
   - Планирование кадровых потребностей исходя из целей ЦКП

3. **ЦКП и стратегическое управление**:
   - ЦКП верхнего уровня связаны со стратегическими целями организации
   - Автоматическое каскадирование изменений в стратегии на нижние уровни ЦКП

## 5. Сравнение Java и React для фронтенда

### Java для фронтенда (JavaFX, Spring MVC с Thymeleaf/JSP)

#### Преимущества:
1. **Монолитная среда разработки**: Единый язык программирования для бэкенда и фронтенда
2. **Производительность и надежность**: Java хорошо подходит для сложных корпоративных приложений
3. **Зрелая экосистема**: Проверенные инструменты для разработки корпоративных приложений
4. **Безопасность**: Строгая типизация и проверки на этапе компиляции
5. **Корпоративная поддержка**: Широкая поддержка в корпоративной среде
6. **Настольные приложения**: Возможность создания десктопного клиента с JavaFX

#### Недостатки:
1. **Сложность разработки интерфейсов**: Более громоздкое создание современных UI
2. **Ограниченная гибкость обновлений**: Требуется полное перестроение и перезагрузка для изменений
3. **Ограниченная экосистема UI-компонентов**: Меньше готовых библиотек для современных интерфейсов
4. **Тяжеловесность**: Более высокие требования к ресурсам клиента
5. **Меньше специалистов на рынке**: Сложнее найти разработчиков современных UI на Java

### React для фронтенда

#### Преимущества:
1. **Современный UI/UX**: Легко создавать высококачественные современные интерфейсы
2. **Огромная экосистема**: Доступность множества библиотек и готовых компонентов
3. **Компонентная архитектура**: Идеально для сложных интерфейсов с переиспользуемыми компонентами
4. **Реактивность и отзывчивость**: Быстрое обновление UI без перезагрузки
5. **Большое сообщество разработчиков**: Легче найти специалистов
6. **Мобильная разработка**: Возможность использования React Native для мобильных приложений
7. **Производительность**: Virtual DOM обеспечивает высокую производительность UI

#### Недостатки:
1. **Разделение стеков разработки**: Разные технологии для бэкенда и фронтенда
2. **JavaScript/TypeScript**: Менее строгая типизация по сравнению с Java
3. **Быстрое развитие экосистемы**: Необходимость регулярного обновления зависимостей
4. **Безопасность**: Большая часть логики на клиенте требует дополнительных мер безопасности

### Рекомендация для проекта ОФС:

**React с TypeScript** более предпочтителен для данного проекта по следующим причинам:

1. **Сложная визуализация**: Проект требует гибкой визуализации оргструктуры и отношений, что значительно проще реализовать с использованием современных JavaScript-библиотек (D3.js, Three.js, Ant Design Charts)

2. **Быстрое обновление данных**: Для динамичного управления сотрудниками и должностями требуется реактивный интерфейс с обновлением в реальном времени

3. **Экосистема UI-компонентов**: Ant Design предоставляет богатый набор готовых компонентов для быстрой разработки

4. **Веб-ориентированность**: Система будет доступна через веб-интерфейс для работы с различных устройств и локаций

**Однако, если критически важны:**
- Десктопное приложение с расширенным доступом к ОС
- Строгая корпоративная политика безопасности
- Наличие Java-разработчиков в команде

То **Java (JavaFX)** может быть альтернативой для создания настольного приложения, которое будет работать в связке с веб-версией.

## 6. План поэтапной реализации и расширения до ERP

### Этап 1: Базовая ОФС (MVP)
1. Основные сущности оргструктуры
2. Управление сотрудниками и должностями
3. Визуализация организационной структуры
4. Базовые отчеты и аналитика

### Этап 2: Расширенная ОФС
1. Функциональные отношения и матрицы ответственности
2. Динамическое управление сменами и локациями
3. Расширенные визуализации и аналитика
4. Интеграция с Rocket.Chat для коммуникаций
5. Развертывание системы управления ЦКП

### Этап 3: Интеграция с HRM-функциями
1. Учет рабочего времени
2. Система социального рейтинга
3. Внутренние токены и мотивация
4. Расчет KPI и эффективности

### Этап 4: Расширение до полноценной ERP
1. Модуль управления производством
2. Модуль управления продажами
3. Финансовый модуль
4. Интеграция с внешними системами
5. Комплексная аналитика и ИИ
6. Расширенный модуль управления ЦКП с прогнозной аналитикой

### Этап 5: Масштабирование и оптимизация
1. Оптимизация производительности
2. Расширенные инструменты аналитики
3. Интеграция с новыми каналами взаимодействия
4. Безопасность и соответствие нормативным требованиям

## 7. Технические рекомендации для устойчивого развития

1. **Микросервисная архитектура**: Разделение на микросервисы по доменным областям для обеспечения масштабируемости
2. **Событийно-ориентированная коммуникация**: Использование брокеров сообщений для асинхронного обмена данными между сервисами
3. **Versioning API**: Поддержка версионирования API для обеспечения обратной совместимости
4. **Feature Flags**: Внедрение системы функциональных флагов для контролируемого выпуска новых функций
5. **CI/CD Pipeline**: Настройка автоматической сборки, тестирования и развертывания
6. **Контейнеризация**: Использование Docker и Kubernetes для унификации окружений

## 8. Ключевые аспекты безопасности

1. **Многоуровневый доступ**: Система ролей и разрешений, соответствующая организационной структуре
2. **Аудит действий**: Логирование всех изменений в организационной структуре
3. **Защита данных**: Шифрование чувствительной информации в базе данных
4. **Безопасность API**: Защита API с помощью OAuth 2.0 и JWT
5. **Регулярное тестирование безопасности**: Проведение пентестов и анализа кода 

## 9. Интеграция с Rocket.Chat

### 9.1 Преимущества использования Rocket.Chat

1. **Открытый исходный код и гибкость**:
   - Полный контроль над платформой и данными
   - Возможность размещения на собственных серверах
   - Расширяемость через API и плагины

2. **Функциональность для корпоративного использования**:
   - Групповые чаты и каналы
   - Личные сообщения
   - Файловый обмен
   - Видеоконференции
   - Интеграция с рабочими инструментами

3. **Безопасность и соответствие требованиям**:
   - Шифрование данных
   - Контроль доступа на основе ролей
   - Возможность соответствия нормативным требованиям (GDPR и др.)

### 9.2 Разработка на базе Rocket.Chat

1. **Архитектура интеграции с ОФС**:
   - Rocket.Chat как платформа для взаимодействия пользователей
   - Интеграция с основной системой через REST API
   - Синхронизация данных пользователей, ролей и разрешений

2. **Разработка пользовательских интерфейсов**:
   - Создание кастомных виджетов и панелей для ОФС
   - Встраивание компонентов управления и визуализации ЦКП
   - Адаптивный дизайн для разных устройств

3. **Возможности разработки на Rocket.Chat**:
   - Использование Meteor.js и React для UI
   - REST API для взаимодействия с внешними системами
   - Webhook-интеграции для реагирования на события
   - Разработка пользовательских бот-интеграций

### 9.3 Интеграция ИИ-ассистента в Rocket.Chat

1. **Технические возможности**:
   - Интеграция через Rocket.Chat API
   - Использование Rocket.Chat App Framework
   - Обработка сообщений через webhooks и боты

2. **Функциональность ИИ-ассистента**:
   - Ответы на вопросы о организационной структуре
   - Помощь в поиске информации о ЦКП и их статусе
   - Автоматизация рутинных задач управления персоналом
   - Уведомления о важных изменениях и событиях
   - Аналитические сводки по запросу

3. **Интеграция с моделями ИИ**:
   - Возможность подключения собственных моделей ИИ
   - Использование API популярных ИИ-сервисов
   - Обучение на корпоративных данных с соблюдением приватности

### 9.4 Модули ОФС в Rocket.Chat

1. **Личный кабинет сотрудника**:
   - Просмотр личной информации и назначений
   - Доступ к расписанию и сменам
   - Отслеживание социального рейтинга и вклада в ЦКП
   - Обратная связь и запросы

2. **Административный интерфейс**:
   - Управление пользователями и правами доступа
   - Мониторинг активности и показателей
   - Конфигурация уведомлений и интеграций
   - Настройка ИИ-ассистента

3. **Модуль коммуникаций**:
   - Структурированные каналы по подразделениям и проектам
   - Автоматические уведомления о изменениях в ЦКП
   - Целевые объявления на основе организационной структуры
   - Командное взаимодействие для достижения ЦКП 

## 10. Развертывание в российских облачных сервисах

### 10.1 Выбор провайдера

1. **Рекомендуемые провайдеры**:
   - **VK Cloud** (бывший Mail.Cloud Solutions):
     * Полностью российский провайдер
     * Оплата в рублях
     * Соответствие 152-ФЗ
     * Поддержка Kubernetes и Docker
     * SLA 99.95%
   
   - **Selectel**:
     * Российский провайдер с собственными ЦОД
     * Высокая производительность
     * Оплата в рублях
     * Простая миграция
     * Хорошая техподдержка
   
   - **Яндекс.Облако**:
     * Широкий набор сервисов
     * Managed Kubernetes и PostgreSQL
     * Соответствие российским нормативам
     * Интеграция с другими сервисами Яндекса
     * Мощные инструменты мониторинга

2. **Критерии выбора**:
   - Наличие сервисов управляемых баз данных (PostgreSQL)
   - Поддержка контейнеризации
   - Стоимость и прозрачность тарифов
   - Техническая поддержка на русском языке
   - Соответствие требованиям 152-ФЗ "О персональных данных"
   - Отказоустойчивость и SLA

### 10.2 Архитектура развертывания

1. **Контейнеризация с Docker**:
   ```
   /deployment
     /docker
       docker-compose.yml          # Основная конфигурация сервисов
       Dockerfile.frontend         # Сборка фронтенда
       Dockerfile.backend          # Сборка бэкенда
       Dockerfile.rocketchat       # Настройка Rocket.Chat
       .env.example                # Пример переменных окружения
     /scripts
       deploy.sh                   # Скрипт деплоя
       backup.sh                   # Скрипт резервного копирования
       restore.sh                  # Восстановление из бэкапа
       monitoring-setup.sh         # Настройка мониторинга
   ```

2. **Kubernetes (опционально для масштабирования)**:
   ```
   /deployment
     /k8s
       /backend
         deployment.yaml
         service.yaml
         ingress.yaml
       /frontend
         deployment.yaml
         service.yaml
         ingress.yaml
       /database
         statefulset.yaml
         pvc.yaml
       /rocketchat
         deployment.yaml
         service.yaml
       kustomization.yaml
   ```

3. **CI/CD для автоматизации**:
   - GitLab CI с раннером на собственном сервере
   - Настройка автоматической сборки и деплоя
   - Интеграция с системой мониторинга

### 10.3 Безопасность и соответствие требованиям

1. **Шифрование и доступ**:
   - SSL/TLS для всех соединений
   - VPN для доступа к административным интерфейсам
   - Настройка брандмауэров и групп безопасности

2. **Резервное копирование**:
   - Ежедневные автоматические бэкапы БД
   - Еженедельные полные бэкапы
   - Хранение в географически распределенных локациях

3. **Мониторинг и алертинг**:
   - Prometheus + Grafana для мониторинга
   - Настройка оповещений о критических событиях
   - Логирование всех действий с персональными данными

4. **Соответствие 152-ФЗ**:
   - Документирование обработки персональных данных
   - Обезличивание данных в тестовых средах
   - Разграничение доступа к персональным данным

### 10.4 Необходимые ресурсы

1. **Минимальная конфигурация**:
   - **Backend**: 2 CPU, 4GB RAM, 50GB SSD
   - **Frontend**: 1 CPU, 2GB RAM, 20GB SSD
   - **База данных**: 2 CPU, 8GB RAM, 100GB SSD
   - **Rocket.Chat**: 2 CPU, 4GB RAM, 50GB SSD

2. **Рекомендуемая конфигурация**:
   - **Backend**: 4 CPU, 8GB RAM, 100GB SSD
   - **Frontend**: 2 CPU, 4GB RAM, 40GB SSD
   - **База данных**: 4 CPU, 16GB RAM, 200GB SSD с репликацией
   - **Rocket.Chat**: 4 CPU, 8GB RAM, 100GB SSD
   - **Мониторинг**: 2 CPU, 4GB RAM, 100GB SSD

## 11. Проверка совместимости и фиксация версий

### 11.1 Бэкенд

| Компонент | Версия | Примечания по совместимости |
|-----------|--------|------------------------------|
| Python | 3.11.x | Стабильная версия, совместима со всеми указанными библиотеками |
| FastAPI | 0.104.0 | Последняя стабильная версия, совместимая с Pydantic 2.x |
| Pydantic | 2.4.x | Новый API, несовместим с Pydantic 1.x |
| SQLAlchemy | 2.0.x | Поддерживает асинхронные операции, несовместим с 1.x |
| asyncpg | 0.27.x | Совместим с Python 3.11 и SQLAlchemy 2.0 |
| Alembic | 1.12.x | Совместим с SQLAlchemy 2.0 |
| PostgreSQL | 15.x | Стабильная версия с поддержкой JSON типов и других нужных фич |
| python-jose | 3.3.x | Для JWT, совместим с FastAPI |
| passlib | 1.7.x | Для хеширования паролей |
| pytest | 7.x | Для тестирования |
| uvicorn | 0.23.x | ASGI сервер для FastAPI |

### 11.2 Фронтенд

| Компонент | Версия | Примечания по совместимости |
|-----------|--------|------------------------------|
| Node.js | 18.x LTS | Долгосрочная поддержка, стабильная |
| TypeScript | 5.2.x | Стабильная версия |
| React | 18.2.x | Hooks, Suspense, Concurrent Mode |
| Vite | 4.5.x | Быстрая сборка, HMR, совместима с React 18 |
| React Router | 6.16.x | Современный API, несовместим с v5 |
| Tailwind CSS | 3.3.x | Высокая гибкость, хорошая производительность |
| Mantine | 7.x | Современные компоненты, темы, несовместим с v6 |
| Styled Components | 6.x | Поддержка TypeScript и React 18 |
| React Query | 5.x | TanStack Query, переименован с v4 |
| Recharts | 2.9.x | Современные React-графики |
| ApexCharts | 3.44.x | Продвинутые графики, совместим с React 18 |
| Framer Motion | 10.16.x | Анимации, transitions |

### 11.3 DevOps и инфраструктура

| Компонент | Версия | Примечания по совместимости |
|-----------|--------|------------------------------|
| Docker | 24.x | Стабильная версия |
| Docker Compose | 2.23.x | Синтаксис V2, не совместим с V1 |
| Kubernetes (опционально) | 1.27.x | Стабильная версия |
| Nginx | 1.24.x | Стабильная версия |
| PostgreSQL | 15.4+ | Стабильная версия для продакшена |
| Prometheus | 2.47.x | Мониторинг |
| Grafana | 10.x | Визуализация метрик |

## 12. Чек-лист проекта ОФС Global

### 12.1 Бэкенд

- [ ] **Настройка основы проекта**
  - [ ] Создание структуры каталогов
  - [ ] Настройка Poetry для управления зависимостями
  - [ ] Инициализация Git-репозитория
  - [ ] Настройка pre-commit хуков и линтеров
  - [ ] Настройка CI/CD пайплайнов

- [ ] **Настройка базы данных**
  - [ ] Инициализация PostgreSQL
  - [ ] Настройка Alembic для миграций
  - [ ] Создание базовых миграций для схемы из раздела 2

- [ ] **Разработка ядра**
  - [ ] Настройка FastAPI с маршрутизацией
  - [ ] Настройка аутентификации и авторизации
  - [ ] Настройка Pydantic-моделей
  - [ ] Разработка базовых CRUD-операций

- [ ] **Разработка API**
  - [ ] Реализация API для организационной структуры 
  - [ ] Реализация API для сотрудников и должностей
  - [ ] Реализация API для ЦКП
  - [ ] Разработка API для визуализации и аналитики

- [ ] **Разработка бизнес-логики**
  - [ ] Имплементация сложных иерархических отношений
  - [ ] Логика обработки ЦКП и их взаимосвязей
  - [ ] Расчеты и агрегация для аналитических отчетов

- [ ] **Интеграции**
  - [ ] Интеграция с Rocket.Chat через API
  - [ ] Настройка API-шлюзов для внешних систем

- [ ] **Тестирование**
  - [ ] Модульные тесты для ключевых компонентов
  - [ ] Интеграционные тесты для API
  - [ ] Нагрузочное тестирование

### 12.2 Фронтенд

- [ ] **Настройка основы проекта**
  - [ ] Создание проекта с Vite + React + TypeScript
  - [ ] Настройка ESLint и Prettier
  - [ ] Настройка Tailwind CSS и базовых стилей
  - [ ] Интеграция Mantine UI или Chakra UI
  - [ ] Настройка React Router и основных маршрутов

- [ ] **Разработка инфраструктуры UI**
  - [ ] Создание базовых компонентов в неоморфном стиле
  - [ ] Настройка тем (светлая/темная)
  - [ ] Разработка layout-компонентов
  - [ ] Настройка анимаций с Framer Motion

- [ ] **Разработка основных страниц**
  - [ ] Аутентификация и управление пользователями
  - [ ] Страницы организационной структуры
  - [ ] Управление сотрудниками и должностями
  - [ ] Интерфейсы для ЦКП

- [ ] **Разработка визуализации**
  - [ ] Интерактивные графики с ApexCharts
  - [ ] Визуализация оргструктуры
  - [ ] Дашборды аналитики
  - [ ] Графы взаимосвязей и влияния ЦКП

- [ ] **Интеграция с API**
  - [ ] Настройка API-клиентов
  - [ ] Кэширование и обработка ошибок
  - [ ] Настройка React Query для запросов

- [ ] **Дополнительные функции**
  - [ ] Экспорт/импорт данных
  - [ ] Печатные формы и отчеты
  - [ ] Уведомления и алерты
  - [ ] Встроенная документация

### 12.3 Rocket.Chat интеграция

- [ ] **Установка и настройка Rocket.Chat**
  - [ ] Развертывание сервера
  - [ ] Настройка безопасности
  - [ ] Интеграция с основной системой аутентификации

- [ ] **Разработка интеграций**
  - [ ] Создание API-клиентов для связи с ОФС
  - [ ] Разработка вебхуков для уведомлений
  - [ ] Интеграция ИИ-ассистента

- [ ] **Пользовательский интерфейс**
  - [ ] Настройка каналов и групп
  - [ ] Разработка пользовательских виджетов
  - [ ] Интеграция компонентов для отображения ЦКП

### 12.4 Развертывание

- [ ] **Подготовка инфраструктуры**
  - [ ] Выбор и настройка облачного провайдера в РФ
  - [ ] Настройка виртуальных машин/контейнеров
  - [ ] Настройка сети и безопасности

- [ ] **Контейнеризация**
  - [ ] Разработка Docker-файлов 
  - [ ] Настройка Docker Compose
  - [ ] Настройка оркестрации (опционально Kubernetes)

- [ ] **Базы данных**
  - [ ] Настройка PostgreSQL с репликацией
  - [ ] Настройка бэкапов
  - [ ] Оптимизация производительности

- [ ] **CI/CD**
  - [ ] Настройка автоматической сборки
  - [ ] Настройка автоматического тестирования
  - [ ] Настройка автоматического деплоя

- [ ] **Мониторинг**
  - [ ] Настройка Prometheus
  - [ ] Настройка Grafana-дашбордов
  - [ ] Настройка алертинга

### 12.5 Документация и обучение

- [ ] **Документация для разработчиков**
  - [ ] API-документация (Swagger/OpenAPI)
  - [ ] Документация по архитектуре
  - [ ] Руководства по разработке

- [ ] **Документация для пользователей**
  - [ ] Руководства пользователя
  - [ ] Инструкции по работе с ЦКП
  - [ ] Справочники по интерфейсу

- [ ] **Обучающие материалы**
  - [ ] Видеоуроки
  - [ ] Интерактивные подсказки
  - [ ] База знаний

## 13. Памятка по проекту ОФС Global

### Основные цели проекта
1. Создать современную систему управления организационной структурой (ОФС)
2. Обеспечить гибкое управление ЦКП (Ценными Конечными Продуктами) и их взаимосвязями
3. Заложить основу для будущего расширения до полноценной ERP-системы
4. Интегрировать коммуникационную платформу Rocket.Chat с поддержкой ИИ
5. Создать красивый современный интерфейс с неоморфным дизайном

### Ключевые особенности
1. Сложная организационная структура с множественным подчинением
2. Иерархия ЦКП с каскадными влияниями и метриками выполнения
3. Динамическое распределение сотрудников по должностям и локациям
4. Аналитика и визуализация эффективности структуры и выполнения ЦКП
5. Интеграция в российское облако с учетом требований безопасности

### Технологический стек
1. **Бэкенд**: Python 3.11, FastAPI, SQLAlchemy 2.0, PostgreSQL
2. **Фронтенд**: React 18, TypeScript, Tailwind CSS, Mantine/Chakra UI
3. **Коммуникация**: Rocket.Chat, ИИ-ассистент
4. **DevOps**: Docker, CI/CD, российское облачное хостинг

### Критические риски и их снижение
1. **Несовместимость версий**: Строгая фиксация версий, Docker для изоляции
2. **Сложность типизации**: Простые схемы типов, современный синтаксис Python 3.10+
3. **Смешение sync/async кода**: Полностью асинхронный стек на бэкенде
4. **Проблемы с БД и миграциями**: Четкая стабильная схема с нуля
5. **Фронтенд ограничения**: Замена Ant Design на более гибкие Tailwind+Mantine

### Порядок разработки
1. Начать с базовой инфраструктуры (репозитории, настройка окружения)
2. Реализовать ядро бэкенда и базовую схему БД
3. Разработать основные API-эндпоинты
4. Создать базовый UI с главными экранами
5. Реализовать ключевые визуализации
6. Интегрировать Rocket.Chat
7. Настроить развертывание в облаке
8. Расширять функциональность итеративно

### Напоминания по разработке
1. Строго придерживаться зафиксированных версий библиотек
2. Регулярно делать коммиты и документировать изменения
3. Писать тесты параллельно с разработкой кода
4. Не усложнять архитектуру без необходимости
5. Сначала MVP, затем постепенное расширение 