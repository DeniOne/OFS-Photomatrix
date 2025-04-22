# Памятка по созданию нового раздела во фронтенде

## 1. Структура папок и файлов

```
frontend/src/features/название_раздела/
  ├── api/
  │   └── названиеРазделаApi.tsx - API для взаимодействия с бэкендом
  ├── components/
  │   ├── НазваниеРазделаTable.tsx - Таблица для отображения списка
  │   ├── НазваниеРазделаForm.tsx - Форма создания/редактирования
  │   └── ... (другие компоненты)
  └── hooks/
      └── useНазваниеРаздела.tsx - Хуки для работы с данными (опционально)
```

## 2. Создание API-клиента (первым делом)

1. Создать файл `frontend/src/features/название_раздела/api/названиеРазделаApi.tsx`:
   ```tsx
   import axios from 'axios';
   import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
   import { notifications } from '@mantine/notifications';
   import { IconCheck, IconX } from '@tabler/icons-react';
   import { useAuth } from '../../../hooks/useAuth';
   
   // Тип сущности (ключевой момент)
   interface ТипСущности {
     id: number;
     name: string;
     // Другие поля
   }
   
   // Типы для создания/обновления
   interface ТипСущностиCreate {
     name: string;
     // Поля для создания
   }
   
   interface ТипСущностиUpdate {
     id: number;
     // Поля для обновления
   }
   
   const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
   
   // API-функции
   export const fetchЭлементы = async (): Promise<ТипСущности[]> => {
     try {
       const token = localStorage.getItem('access_token');
       const response = await axios.get(`${API_URL}/api/v1/путь_к_ресурсу/`, {
         headers: { Authorization: `Bearer ${token}` }
       });
       return response.data;
     } catch (error) {
       // Обработка ошибок
       console.error('Ошибка при получении данных:', error);
       throw error;
     }
   };
   
   // Другие функции: create, update, delete, getById и т.д.
   
   // React Query хуки
   export const useЭлементы = () => {
     const { isAuthenticated } = useAuth();
     return useQuery({
       queryKey: ['название_ресурса'],
       queryFn: fetchЭлементы,
       enabled: isAuthenticated
     });
   };
   
   export const useCreateЭлемент = () => {
     const queryClient = useQueryClient();
     return useMutation({
       mutationFn: createЭлемент,
       onSuccess: () => {
         queryClient.invalidateQueries({ queryKey: ['название_ресурса'] });
         notifications.show({
           title: 'Успех!',
           message: 'Элемент успешно создан',
           color: 'green',
           icon: <IconCheck />
         });
       },
       onError: (error: Error) => {
         notifications.show({
           title: 'Ошибка!',
           message: error.message || 'Не удалось создать элемент',
           color: 'red',
           icon: <IconX />
         });
       }
     });
   };
   
   // Аналогично для update и delete
   ```

## 3. Создание компонентов

### 3.1 Таблица для отображения списка

```tsx
import { Table, ActionIcon, Group, Badge } from '@mantine/core';
import { IconEdit, IconTrash, IconEye } from '@tabler/icons-react';
import { ТипСущности } from '../../../types/типСущности';

interface НазваниеРазделаTableProps {
  элементы: ТипСущности[];
  onEdit: (элемент: ТипСущности) => void;
  onDelete: (id: number) => void;
  onViewDetails?: (id: number) => void;
}

export function НазваниеРазделаTable({ 
  элементы, 
  onEdit, 
  onDelete,
  onViewDetails 
}: НазваниеРазделаTableProps) {
  return (
    <Table>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>Название</Table.Th>
          <Table.Th>Код</Table.Th>
          {/* Другие колонки */}
          <Table.Th>Статус</Table.Th>
          <Table.Th>Действия</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {элементы.map((элемент) => (
          <Table.Tr key={элемент.id}>
            <Table.Td>{элемент.name}</Table.Td>
            <Table.Td>{элемент.code}</Table.Td>
            {/* Другие поля */}
            <Table.Td>
              <Badge color={элемент.is_active ? 'green' : 'red'}>
                {элемент.is_active ? 'АКТИВНА' : 'НЕАКТИВНА'}
              </Badge>
            </Table.Td>
            <Table.Td>
              <Group gap="xs">
                <ActionIcon variant="subtle" color="blue" onClick={() => onEdit(элемент)}>
                  <IconEdit size={16} />
                </ActionIcon>
                <ActionIcon variant="subtle" color="red" onClick={() => onDelete(элемент.id)}>
                  <IconTrash size={16} />
                </ActionIcon>
                {onViewDetails && (
                  <ActionIcon variant="subtle" color="gray" onClick={() => onViewDetails(элемент.id)}>
                    <IconEye size={16} />
                  </ActionIcon>
                )}
              </Group>
            </Table.Td>
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  );
}
```

### 3.2 Форма создания/редактирования

```tsx
import { useForm } from '@mantine/form';
import { Button, TextInput, Select, Textarea, Group } from '@mantine/core';
import { ТипСущности, ТипСущностиCreate, ТипСущностиUpdate } from '../../../types/типСущности';
import { useCreateЭлемент, useUpdateЭлемент } from '../api/названиеРазделаApi';

interface НазваниеРазделаFormProps {
  элементToEdit?: ТипСущности | null;
  onSuccess: () => void;
}

export default function НазваниеРазделаForm({ 
  элементToEdit = null, 
  onSuccess 
}: НазваниеРазделаFormProps) {
  const createMutation = useCreateЭлемент();
  const updateMutation = useUpdateЭлемент();
  
  const form = useForm({
    initialValues: элементToEdit ? {
      name: элементToEdit.name,
      code: элементToEdit.code,
      // Другие поля
    } : {
      name: '',
      code: '',
      // Значения по умолчанию
    },
    validate: {
      name: (value) => (value.length < 2 ? 'Название должно содержать минимум 2 символа' : null),
      code: (value) => (value.length < 1 ? 'Код обязателен' : null),
      // Другие валидации
    },
  });
  
  const handleSubmit = form.onSubmit((values) => {
    if (элементToEdit) {
      updateMutation.mutate({
        id: элементToEdit.id,
        ...values,
      } as ТипСущностиUpdate, {
        onSuccess: () => {
          onSuccess();
        },
      });
    } else {
      createMutation.mutate(values as ТипСущностиCreate, {
        onSuccess: () => {
          onSuccess();
        },
      });
    }
  });
  
  return (
    <form onSubmit={handleSubmit}>
      <TextInput
        label="Название"
        required
        {...form.getInputProps('name')}
        mb="md"
      />
      <TextInput
        label="Код"
        required
        {...form.getInputProps('code')}
        mb="md"
      />
      
      {/* Другие поля формы */}
      
      <Group justify="flex-end" mt="xl">
        <Button 
          type="submit" 
          loading={createMutation.isPending || updateMutation.isPending}
        >
          {элементToEdit ? 'Сохранить' : 'Создать'}
        </Button>
      </Group>
    </form>
  );
}
```

## 4. Создание страницы

Создать файл `frontend/src/pages/НазваниеРазделаPage.tsx`:

```tsx
import { useState } from 'react';
import { Box, Button, Loader, Alert, Group, Modal, Text } from '@mantine/core';
import { IconPlus, IconAlertCircle } from '@tabler/icons-react';
import { useЭлементы, useDeleteЭлемент } from '../features/название_раздела/api/названиеРазделаApi';
import { НазваниеРазделаTable } from '../features/название_раздела/components/НазваниеРазделаTable';
import НазваниеРазделаForm from '../features/название_раздела/components/НазваниеРазделаForm';

export default function НазваниеРазделаPage() {
  const { data: элементы, isLoading, error, isError } = useЭлементы();
  const deleteMutation = useDeleteЭлемент();
  
  const [formModalOpened, setFormModalOpened] = useState(false);
  const [selectedЭлемент, setSelectedЭлемент] = useState(null);
  const [deleteModalOpened, setDeleteModalOpened] = useState(false);
  const [элементToDelete, setЭлементToDelete] = useState(null);
  
  // Обработчики
  const openFormModal = (элемент = null) => {
    setSelectedЭлемент(элемент);
    setFormModalOpened(true);
  };
  
  const openDeleteModal = (id) => {
    setЭлементToDelete(id);
    setDeleteModalOpened(true);
  };
  
  const confirmDelete = () => {
    if (элементToDelete) {
      deleteMutation.mutate(элементToDelete, {
        onSuccess: () => {
          setDeleteModalOpened(false);
          setЭлементToDelete(null);
        }
      });
    }
  };
  
  return (
    <Box p="md">
      <Group justify="flex-end" mb="lg">
        <Button 
          leftSection={<IconPlus size={16} />} 
          onClick={() => openFormModal()}
        >
          Создать 
        </Button>
      </Group>
      
      {isLoading && <Loader />}
      
      {isError && (
        <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка!" color="red">
          {error?.message || 'Произошла ошибка при загрузке данных'}
        </Alert>
      )}
      
      {!isLoading && !isError && элементы && (
        <НазваниеРазделаTable 
          элементы={элементы} 
          onEdit={openFormModal} 
          onDelete={openDeleteModal}
        />
      )}
      
      {/* Модальное окно формы */}
      <Modal
        opened={formModalOpened}
        onClose={() => setFormModalOpened(false)}
        title={selectedЭлемент ? 'Редактировать' : 'Создать'}
      >
        <НазваниеРазделаForm
          элементToEdit={selectedЭлемент}
          onSuccess={() => {
            setFormModalOpened(false);
          }}
        />
      </Modal>
      
      {/* Модальное окно удаления */}
      <Modal
        opened={deleteModalOpened}
        onClose={() => setDeleteModalOpened(false)}
        title="Подтверждение удаления"
      >
        <Text mb="lg">Вы уверены, что хотите удалить этот элемент?</Text>
        <Group justify="flex-end">
          <Button variant="outline" onClick={() => setDeleteModalOpened(false)}>
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

## 5. Подключение к маршрутизации

Добавить маршрут в файл `frontend/src/App.tsx` или `frontend/src/router.tsx`:

```tsx
import { Routes, Route } from 'react-router-dom';
import НазваниеРазделаPage from './pages/НазваниеРазделаPage';

// В компоненте Routes добавить:
<Route path="/название_раздела" element={<НазваниеРазделаPage />} />
```

## 6. Добавление в навигацию

Добавить в `frontend/src/layouts/DashboardLayout.tsx` или другой файл с навигацией:

```tsx
<NavLink
  to="/название_раздела"
  label="Название раздела"
  icon={<ИконкаРаздела size={20} />}
  active={location.pathname.startsWith('/название_раздела')}
  isSidebarOpen={isSidebarOpen}
/>
```

## 7. Создание типов

Создать или дополнить файл типов `frontend/src/types/типСущности.ts`:

```tsx
export interface ТипСущности {
  id: number;
  name: string;
  code: string;
  // Другие поля
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ТипСущностиCreate {
  name: string;
  code: string;
  // Поля для создания
}

export interface ТипСущностиUpdate {
  id: number;
  name?: string;
  code?: string;
  // Опциональные поля для обновления
}
```

## Советы и особенности
- Используй React Query для работы с запросами и кэшированием данных
- Не забывай всегда добавлять `/api/v1/` в начале всех URL для запросов к бэкенду
- Для модального окна используй компонент Modal из Mantine
- Обрабатывай ошибки и отображай уведомления через notifications.show()
- Убедись, что Bearer токен добавляется ко всем запросам

Это базовая структура для добавления нового раздела. При необходимости можно дополнять и расширять в зависимости от специфики раздела. 