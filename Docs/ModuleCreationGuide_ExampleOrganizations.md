# Памятка по созданию стандартного модуля (на примере "Организации")

Этот документ описывает шаги и структуру для создания нового модуля управления сущностью в проекте OFS Photomatrix, используя модуль "Организации" как рабочий пример.

## 1. Общая структура

### Бэкенд (`backend/app/`)

```
app/
├── models/
│   └── organization.py       # Модель SQLAlchemy
├── schemas/
│   └── organization.py       # Схемы Pydantic (Base, Create, Update, Read)
├── crud/
│   └── crud_organization.py  # CRUD операции (репозиторий)
├── api/
│   └── endpoints/
│       └── organizations.py    # API эндпоинты (FastAPI роутер)
│   └── api.py                # Подключение роутера организации к основному api_router
└── main.py                 # Основной файл FastAPI (подключение api_router)
```

### Фронтенд (`frontend/src/`)

```
src/
├── features/
│   └── organizations/
│       ├── api/
│       │   └── organizationApi.ts  # Функции API и хуки React Query
│       ├── components/
│       │   ├── OrganizationTable.tsx # Компонент таблицы
│       │   └── OrganizationForm.tsx  # Компонент формы
│       └── ... (другие компоненты, если нужны)
├── pages/
│   └── OrganizationsPage.tsx     # Компонент страницы модуля
├── types/
│   └── organization.ts         # TypeScript типы/интерфейсы
├── App.tsx                     # Маршрутизация (добавление Route)
└── layouts/
    └── DashboardLayout.tsx     # Навигация (добавление NavLink)
```

## 2. Бэкенд (FastAPI)

### 2.1 Модель (`models/organization.py`)

Определите модель SQLAlchemy, наследуясь от `Base`. Используйте стандартные типы SQLAlchemy, `relationship` для связей.

```python
# models/organization.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
import datetime

class OrganizationType(str, enum.Enum):
    HOLDING = "HOLDING"
    LEGAL_ENTITY = "LEGAL_ENTITY"
    LOCATION = "LOCATION"

class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    org_type = Column(Enum(OrganizationType), nullable=False)

    parent_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    parent = relationship("Organization", remote_side=[id], back_populates="children")
    children = relationship("Organization", back_populates="parent", cascade="all, delete-orphan") # Пример каскадного удаления

    divisions = relationship("Division", back_populates="organization") # Связь с подразделениями

    is_active = Column(Boolean(), default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Organization(name='{self.name}', code='{self.code}')>"
```

### 2.2 Схемы (`schemas/organization.py`)

Определите Pydantic схемы для валидации данных API:
*   `OrganizationBase`: Общие поля.
*   `OrganizationCreate`: Поля для создания (наследуется от Base).
*   `OrganizationUpdate`: Поля для обновления (наследуется от Base, все поля опциональны).
*   `Organization`: Поля для чтения (наследуется от Base, включает ID и др. поля из БД).

```python
# schemas/organization.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.organization import OrganizationType # Импорт Enum из модели

class OrganizationBase(BaseModel):
    name: str
    code: str
    org_type: OrganizationType
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    pass # Все поля из Base обязательны

class OrganizationUpdate(OrganizationBase):
    # Делаем все поля опциональными для обновления
    name: Optional[str] = None
    code: Optional[str] = None # Код обычно не меняют, но для примера
    org_type: Optional[OrganizationType] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None

class Organization(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) # Раньше было orm_mode = True

# Схема для чтения с дочерними элементами (если нужно дерево)
class OrganizationWithChildren(Organization):
    children: List['OrganizationWithChildren'] = [] # Рекурсивная схема
```

### 2.3 CRUD (`crud/crud_organization.py`)

Создайте класс CRUD, наследуясь от `CRUDBase`. Добавьте специфичные методы, если нужны (например, `get_by_code`).

```python
# crud/crud_organization.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.crud.base import CRUDBase
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Organization]:
        query = select(self.model).filter(self.model.code == code)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi_by_parent(
        self, db: AsyncSession, *, parent_id: Optional[int], skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        query = select(self.model).filter(self.model.parent_id == parent_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_root_organizations(self, db: AsyncSession) -> List[Organization]:
         query = select(self.model).filter(self.model.parent_id == None)
         result = await db.execute(query)
         return result.scalars().all()

    # Можно добавить get_tree и другие методы при необходимости

# Создаем экземпляр CRUD
organization = CRUDOrganization(Organization)
```

### 2.4 API Эндпоинты (`api/endpoints/organizations.py`)

Создайте роутер FastAPI и определите эндпоинты.

**ВАЖНО:**
*   Используйте слеш `/` в конце для эндпоинтов, работающих со списком или созданием (GET список, POST).
*   НЕ используйте слеш `/` в конце для эндпоинтов, работающих с конкретным ID (GET по ID, PUT, DELETE).
*   Используйте `Depends` для внедрения зависимостей (сессия БД, текущий пользователь).
*   Обрабатывайте ошибки (не найдено, дубликат и т.д.) через `HTTPException`.

```python
# api/endpoints/organizations.py
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_active_user
from app.crud import organization as crud_organization
from app.models.user import User
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate

router = APIRouter()

# GET Список (со слешем!)
@router.get("/", response_model=List[Organization])
async def read_organizations(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    organizations = await crud_organization.get_multi(db=db, skip=skip, limit=limit)
    return organizations

# POST Создание (со слешем!)
@router.post("/", response_model=Organization, status_code=status.HTTP_201_CREATED)
async def create_organization(
    *,
    db: AsyncSession = Depends(get_db),
    organization_in: OrganizationCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    existing_org = await crud_organization.get_by_code(db, code=organization_in.code)
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization with this code already exists")
    organization = await crud_organization.create(db=db, obj_in=organization_in)
    return organization

# GET по ID (БЕЗ слеша!)
@router.get("/{organization_id}", response_model=Organization)
async def read_organization(
    *,
    db: AsyncSession = Depends(get_db),
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    organization = await crud_organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

# PUT Обновление (БЕЗ слеша!)
@router.put("/{organization_id}", response_model=Organization)
async def update_organization(
    *,
    db: AsyncSession = Depends(get_db),
    organization_id: int,
    organization_in: OrganizationUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    organization = await crud_organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    # Можно добавить проверку уникальности кода при изменении
    organization = await crud_organization.update(db=db, db_obj=organization, obj_in=organization_in)
    return organization

# DELETE Удаление (БЕЗ слеша!)
@router.delete("/{organization_id}", response_model=Organization)
async def delete_organization(
    *,
    db: AsyncSession = Depends(get_db),
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    organization = await crud_organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    # Важно: Проверить наличие зависимостей перед удалением!
    # Например, проверить, есть ли у организации подразделения
    if organization.divisions: # Проверяем, если есть relationship 'divisions'
         raise HTTPException(status_code=400, detail="Cannot delete organization with associated divisions")
    deleted_organization = await crud_organization.remove(db=db, id=organization_id)
    return deleted_organization # Возвращаем удаленный объект
```

### 2.5 Подключение роутера (`api/api.py`)

Добавьте импорт и `include_router` для вашего нового модуля.

```python
# api/api.py
from fastapi import APIRouter
from app.api.endpoints import auth, users, organizations # Добавить organizations

api_router = APIRouter()
# ... другие роутеры
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
```

## 3. Фронтенд (React)

### 3.1 Типы (`types/organization.ts`)

Определите TypeScript интерфейсы, соответствующие Pydantic схемам.

```typescript
// types/organization.ts
export enum OrganizationType {
  HOLDING = "HOLDING",
  LEGAL_ENTITY = "LEGAL_ENTITY",
  LOCATION = "LOCATION",
}

export interface Organization {
  id: number;
  name: string;
  code: string;
  org_type: OrganizationType;
  description: string | null;
  parent_id: number | null;
  is_active: boolean;
  created_at: string; // Или Date, если парсить
  updated_at: string; // Или Date
  // Добавить children, если используется схема WithChildren
  // children?: Organization[];
}

// Тип для формы создания (поля, которые отправляются на бэк)
export interface OrganizationCreateDto {
  name: string;
  code: string;
  org_type: OrganizationType;
  description?: string | null;
  parent_id?: number | null;
  is_active?: boolean;
}

// Тип для формы обновления
export type OrganizationUpdateDto = Partial<OrganizationCreateDto>; // Все поля опциональны
```

### 3.2 API-клиент (`features/organizations/api/organizationApi.ts`)

Создайте функции для вызова API и хуки React Query.

**ВАЖНО:** Следите за **слешами** в URL!
*   `/organizations/` для GET списка и POST.
*   `/organizations/{id}` для GET по ID, PUT, DELETE.

```typescript
// features/organizations/api/organizationApi.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/client'; // Используем настроенный Axios instance 'api'
import { Organization, OrganizationCreateDto, OrganizationUpdateDto } from '@/types/organization';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconX } from '@tabler/icons-react';

const ORGANIZATIONS_QUERY_KEY = ['organizations']; // Ключ для кэша React Query

// --- Функции для вызова API ---

const fetchOrganizations = async (): Promise<Organization[]> => {
  // Слеш в конце!
  const response = await api.get<Organization[]>('/api/v1/organizations/');
  return response.data;
};

const createOrganization = async (data: OrganizationCreateDto): Promise<Organization> => {
  // Слеш в конце!
  const response = await api.post<Organization>('/api/v1/organizations/', data);
  return response.data;
};

const updateOrganization = async ({ id, data }: { id: number; data: OrganizationUpdateDto }): Promise<Organization> => {
  // БЕЗ слеша!
  const response = await api.put<Organization>(`/api/v1/organizations/${id}`, data);
  return response.data;
};

const deleteOrganization = async (id: number): Promise<void> => {
  // БЕЗ слеша!
  await api.delete(`/api/v1/organizations/${id}`);
};

// --- Хуки React Query ---

export const useOrganizations = () => {
  return useQuery<Organization[], Error>({
    queryKey: ORGANIZATIONS_QUERY_KEY,
    queryFn: fetchOrganizations,
    // Доп. опции, если нужны (staleTime, gcTime и т.д.)
  });
};

export const useCreateOrganization = () => {
  const queryClient = useQueryClient();
  return useMutation<Organization, Error, OrganizationCreateDto>({
    mutationFn: createOrganization,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ORGANIZATIONS_QUERY_KEY });
      notifications.show({ /* ... успех ... */ });
    },
    onError: (error) => {
      notifications.show({ /* ... ошибка ... */ });
    },
  });
};

export const useUpdateOrganization = () => {
  const queryClient = useQueryClient();
  return useMutation<Organization, Error, { id: number; data: OrganizationUpdateDto }>({
    mutationFn: updateOrganization,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ORGANIZATIONS_QUERY_KEY });
      // Можно обновить и кэш конкретного элемента, если он используется
      // queryClient.invalidateQueries({ queryKey: [ORGANIZATIONS_QUERY_KEY[0], data.id] });
      notifications.show({ /* ... успех ... */ });
    },
    onError: (error) => {
      notifications.show({ /* ... ошибка ... */ });
    },
  });
};

export const useDeleteOrganization = () => {
  const queryClient = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: deleteOrganization,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ORGANIZATIONS_QUERY_KEY });
      notifications.show({ /* ... успех ... */ });
    },
    onError: (error) => {
      notifications.show({ /* ... ошибка ... */ });
    },
  });
};
```

### 3.3 Страница (`pages/OrganizationsPage.tsx`)

Основной компонент страницы, который собирает всё вместе.

```typescript
// pages/OrganizationsPage.tsx
import { useState } from 'react';
import { Box, Button, Loader, Alert, Group, Modal, Title, Text } from '@mantine/core';
import { IconPlus, IconAlertCircle } from '@tabler/icons-react';
import { useOrganizations, useDeleteOrganization } from '@/features/organizations/api/organizationApi';
import { OrganizationTable } from '@/features/organizations/components/OrganizationTable';
import { OrganizationForm } from '@/features/organizations/components/OrganizationForm';
import { Organization } from '@/types/organization'; // Импорт типа

export default function OrganizationsPage() {
  // Получение данных
  const { data: organizations, isLoading, error, isError } = useOrganizations();
  // Мутация для удаления
  const deleteMutation = useDeleteOrganization();

  // Состояния для модальных окон
  const [formModalOpened, setFormModalOpened] = useState(false);
  const [selectedOrganization, setSelectedOrganization] = useState<Organization | null>(null);
  const [deleteModalOpened, setDeleteModalOpened] = useState(false);
  const [organizationToDelete, setOrganizationToDelete] = useState<number | null>(null);

  // Обработчики открытия/закрытия модалок
  const openFormModal = (organization: Organization | null = null) => {
    setSelectedOrganization(organization);
    setFormModalOpened(true);
  };

  const closeFormModal = () => {
    setFormModalOpened(false);
    setSelectedOrganization(null); // Сбрасываем выбранный элемент
  };

  const openDeleteModal = (id: number) => {
    setOrganizationToDelete(id);
    setDeleteModalOpened(true);
  };

  const closeDeleteModal = () => {
    setDeleteModalOpened(false);
    setOrganizationToDelete(null);
  };

  // Подтверждение удаления
  const confirmDelete = () => {
    if (organizationToDelete) {
      deleteMutation.mutate(organizationToDelete, {
        onSuccess: () => {
          closeDeleteModal(); // Закрываем модалку при успехе
        },
        // onError обработается в хуке useDeleteOrganization
      });
    }
  };

  return (
    <Box p="md">
      <Group justify="space-between" mb="lg">
        <Title order={2}>Управление Организациями</Title>
        <Button
          leftSection={<IconPlus size={16} />}
          onClick={() => openFormModal()} // Открываем форму для создания
        >
          Создать организацию
        </Button>
      </Group>

      {isLoading && <Loader />}

      {isError && (
        <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка!" color="red" mb="lg">
          Не удалось загрузить список организаций: {error?.message || 'Неизвестная ошибка'}
        </Alert>
      )}

      {!isLoading && !isError && organizations && (
        <OrganizationTable
          organizations={organizations}
          onEdit={openFormModal} // Передаем организацию для редактирования
          onDelete={openDeleteModal} // Передаем ID для удаления
        />
      )}

      {/* Модальное окно формы */}
      <Modal
        opened={formModalOpened}
        onClose={closeFormModal}
        title={selectedOrganization ? 'Редактировать организацию' : 'Создать организацию'}
        size="lg" // Размер можно подобрать
      >
        <OrganizationForm
          organizationToEdit={selectedOrganization}
          onSuccess={closeFormModal} // Закрываем модалку при успехе формы
        />
      </Modal>

      {/* Модальное окно подтверждения удаления */}
      <Modal
        opened={deleteModalOpened}
        onClose={closeDeleteModal}
        title="Подтверждение удаления"
        size="sm"
      >
        <Text mb="lg">Вы уверены, что хотите удалить эту организацию?</Text>
        <Group justify="flex-end">
          <Button variant="default" onClick={closeDeleteModal}>
            Отмена
          </Button>
          <Button color="red" onClick={confirmDelete} loading={deleteMutation.isPending}>
            Удалить
          </Button>
        </Group>
      </Modal>
    </Box>
  );
}

```

### 3.4 Таблица (`components/OrganizationTable.tsx`)

Компонент для отображения данных в таблице Mantine.

```typescript
// components/OrganizationTable.tsx
import { Table, ActionIcon, Group, Badge } from '@mantine/core';
import { IconEdit, IconTrash } from '@tabler/icons-react';
import { Organization } from '@/types/organization'; // Импорт типа

interface OrganizationTableProps {
  organizations: Organization[];
  onEdit: (organization: Organization) => void; // Функция для открытия формы редактирования
  onDelete: (id: number) => void; // Функция для открытия модалки удаления
}

export function OrganizationTable({ organizations, onEdit, onDelete }: OrganizationTableProps) {
  const rows = organizations.map((org) => (
    <Table.Tr key={org.id}>
      <Table.Td>{org.name}</Table.Td>
      <Table.Td>{org.code}</Table.Td>
      <Table.Td>{org.org_type}</Table.Td>
      <Table.Td>{org.parent_id || '-'}</Table.Td> {/* Пример отображения родителя */}
      <Table.Td>
        <Badge color={org.is_active ? 'green' : 'red'}>
          {org.is_active ? 'Активна' : 'Неактивна'}
        </Badge>
      </Table.Td>
      <Table.Td>
        <Group gap="xs">
          <ActionIcon variant="subtle" color="blue" onClick={() => onEdit(org)}>
            <IconEdit size={16} />
          </ActionIcon>
          <ActionIcon variant="subtle" color="red" onClick={() => onDelete(org.id)}>
            <IconTrash size={16} />
          </ActionIcon>
        </Group>
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <Table striped highlightOnHover withTableBorder withColumnBorders>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>Название</Table.Th>
          <Table.Th>Код</Table.Th>
          <Table.Th>Тип</Table.Th>
          <Table.Th>Родитель ID</Table.Th>
          <Table.Th>Статус</Table.Th>
          <Table.Th>Действия</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>{rows}</Table.Tbody>
    </Table>
  );
}
```

### 3.5 Форма (`components/OrganizationForm.tsx`)

Компонент формы Mantine для создания и редактирования.

```typescript
// components/OrganizationForm.tsx
import { useForm } from '@mantine/form';
import { TextInput, Button, Group, Select, Textarea, Checkbox, Stack } from '@mantine/core';
import { Organization, OrganizationCreateDto, OrganizationUpdateDto, OrganizationType } from '@/types/organization';
import { useCreateOrganization, useUpdateOrganization } from '../api/organizationApi';
import { useEffect } from 'react';

interface OrganizationFormProps {
  organizationToEdit?: Organization | null; // Организация для редактирования или null для создания
  onSuccess: () => void; // Колбэк при успешном сабмите
}

export function OrganizationForm({ organizationToEdit = null, onSuccess }: OrganizationFormProps) {
  const createMutation = useCreateOrganization();
  const updateMutation = useUpdateOrganization();

  const form = useForm<OrganizationCreateDto | OrganizationUpdateDto>({
    initialValues: {
      name: organizationToEdit?.name || '',
      code: organizationToEdit?.code || '',
      org_type: organizationToEdit?.org_type || OrganizationType.LEGAL_ENTITY, // Значение по умолчанию
      description: organizationToEdit?.description || '',
      parent_id: organizationToEdit?.parent_id || null,
      is_active: organizationToEdit?.is_active ?? true, // По умолчанию true при создании
    },
    validate: {
      name: (value) => (value.trim().length < 2 ? 'Название должно содержать минимум 2 символа' : null),
      code: (value) => (value.trim().length < 1 ? 'Код обязателен' : null),
      org_type: (value) => (!value ? 'Тип обязателен' : null),
      // Другие валидации...
    },
  });

  // Сброс формы при смене organizationToEdit (например, закрыли модалку, открыли снова)
  useEffect(() => {
    form.setValues({
      name: organizationToEdit?.name || '',
      code: organizationToEdit?.code || '',
      org_type: organizationToEdit?.org_type || OrganizationType.LEGAL_ENTITY,
      description: organizationToEdit?.description || '',
      parent_id: organizationToEdit?.parent_id || null,
      is_active: organizationToEdit?.is_active ?? true,
    });
    form.resetDirty(); // Сбросить 'грязное' состояние
    form.clearErrors(); // Сбросить ошибки
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [organizationToEdit]); // Добавляем form в зависимости не нужно, т.к. он стабилен

  const handleSubmit = (values: OrganizationCreateDto | OrganizationUpdateDto) => {
    if (organizationToEdit) {
      // Обновление
      updateMutation.mutate(
        { id: organizationToEdit.id, data: values as OrganizationUpdateDto },
        { onSuccess } // Вызываем onSuccess колбэк при успехе
      );
    } else {
      // Создание
      createMutation.mutate(values as OrganizationCreateDto, { onSuccess });
    }
  };

  return (
    <form onSubmit={form.onSubmit(handleSubmit)}>
      <Stack>
        <TextInput
          label="Название"
          placeholder="ООО Рога и Копыта"
          required
          {...form.getInputProps('name')}
        />
        <TextInput
          label="Код"
          placeholder="ORG_01"
          required
          // Запрещаем редактирование кода для существующей организации
          disabled={!!organizationToEdit}
          {...form.getInputProps('code')}
        />
        <Select
          label="Тип организации"
          required
          data={Object.values(OrganizationType).map(type => ({ value: type, label: type }))}
          {...form.getInputProps('org_type')}
        />
        <Textarea
          label="Описание"
          placeholder="Основная компания холдинга..."
          {...form.getInputProps('description')}
        />
        <TextInput
          type="number" // Для ID родителя
          label="Родительская организация (ID)"
          placeholder="ID родительской организации (если есть)"
          {...form.getInputProps('parent_id')}
        />
        <Checkbox
          mt="md"
          label="Активна"
          {...form.getInputProps('is_active', { type: 'checkbox' })}
        />
        <Group justify="flex-end" mt="xl">
          <Button type="submit" loading={createMutation.isPending || updateMutation.isPending}>
            {organizationToEdit ? 'Сохранить' : 'Создать'}
          </Button>
        </Group>
      </Stack>
    </form>
  );
}
```

### 3.6 Маршрутизация и Навигация

*   **`App.tsx`**: Добавьте `Route` для вашей новой страницы внутри `Routes`, обернув его в `WrappedRoute` для использования лэйаута и проверки аутентификации.
    ```typescript
    // App.tsx
    const OrganizationsPage = lazy(() => import('./pages/OrganizationsPage'));
    // ...
    <Route
      path="/organizations" // Путь к странице
      element={isAuthenticated ?
        <WrappedRoute element={<OrganizationsPage />} /> :
        <Navigate to="/login" replace />
      }
    />
    ```
*   **`DashboardLayout.tsx`**: Добавьте `NavLink` в боковое меню.
    ```typescript
    // layouts/DashboardLayout.tsx
    import { IconBuildingSkyscraper } from '@tabler/icons-react'; // Выберите иконку
    // ...
    <NavLink
      to="/organizations"
      label="Организации"
      leftSection={<IconBuildingSkyscraper size={20} />}
      active={location.pathname.startsWith('/organizations')} // Подсветка активного пункта
      onClick={closeSidebar} // Закрытие меню при клике на мобилке
    />
    ```

## 4. Миграции Базы Данных (Alembic)

1.  После создания или изменения модели (`models/organization.py`), сгенерируйте новую миграцию:
    ```bash
    cd backend
    alembic revision --autogenerate -m "Add organization module models"
    ```
2.  Проверьте сгенерированный файл миграции в `backend/migrations/versions/`. При необходимости внесите правки (например, для Enum, server_default).
3.  Примените миграцию:
    ```bash
    alembic upgrade head
    ```

## 5. Важные моменты

*   **Слеши в URL:** Строго следите за наличием/отсутствием слеша в конце URL при вызове API на фронтенде в соответствии с определением роутов на бэкенде.
*   **Аутентификация:** Все эндпоинты по умолчанию защищены (`Depends(get_current_active_user)`). Фронтенд должен отправлять `Bearer` токен.
*   **Обработка ошибок:** Используйте `HTTPException` на бэке и обработку `onError` в `useMutation` на фронте для обратной связи пользователю.
*   **Зависимости при удалении:** На бэкенде перед удалением сущности проверяйте наличие связанных данных (например, нельзя удалить организацию, если у нее есть подразделения), чтобы избежать ошибок БД и обеспечить целостность данных.
*   **React Query:** Используйте для управления серверным состоянием, кэширования, инвалидации кэша при мутациях.

Эта памятка должна помочь создавать новые модули единообразно и с учетом уже решенных проблем. 