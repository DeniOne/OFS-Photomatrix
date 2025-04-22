# Модуль управления организациями

## Структура и компоненты

### Бэкенд (FastAPI)

#### Необходимые компоненты
1. **База данных**:
   - Таблица `organization` с полями:
     - `id` (PK)
     - `name` (название организации)
     - `code` (уникальный код)
     - `description` (описание)
     - `org_type` (тип: HOLDING, LEGAL_ENTITY, LOCATION)
     - `parent_id` (FK, ссылка на родительскую организацию)
     - `is_active` (активность)
     - `created_at`/`updated_at` (даты создания/обновления)

2. **API Endpoints**:
   - `GET /api/v1/organizations/` - получение списка всех организаций
   - `POST /api/v1/organizations/` - создание новой организации
   - `GET /api/v1/organizations/{id}` - получение организации по ID
   - `PUT /api/v1/organizations/{id}` - обновление организации
   - `DELETE /api/v1/organizations/{id}` - удаление организации
   - `GET /api/v1/organizations/tree` - получение дерева организаций
   - `GET /api/v1/organizations/root` - получение корневых организаций

3. **Аутентификация**:
   - JWT-токены с сохранением в localStorage
   - Пользователь-администратор (admin@example.com / admin123)
   - Обязательная аутентификация для всех эндпоинтов (кроме автономного режима разработки)

4. **CRUD операции**:
   - Правильное обращение к методам CRUD через `crud_organization`:
     ```python
     await crud_organization.get(db, id=id)  # Правильно
     await crud_organization.organization.get(db, id=id)  # Неправильно
     ```

5. **Логирование**:
   - Файлы логов:
     - `logs/app.log` - общие логи приложения
     - `logs/db.log` - логи базы данных (SQLAlchemy)
     - `logs/error.log` - логи только с ошибками
   - Ротация логов через RotatingFileHandler
   - Уровень логирования: INFO

### Фронтенд (React + Mantine UI)

#### Навигация
1. **Боковое меню (DashboardLayout.tsx)**:
   - Пункт "Организации" со свойствами:
     ```tsx
     <NavLink
       to="/organizations"
       label="Организации"
       icon={<IconBuildingSkyscraper size={20} />}
       active={location.pathname.startsWith('/organizations')}
       isSidebarOpen={isSidebarOpen}
     />
     ```
   - Маршрутизация на страницу:
     ```tsx
     <Route 
       path="/organizations"
       element={isAuthenticated ? <OrganizationsPage /> : <Navigate to="/login" replace />}
     />
     ```

#### Страница организаций (OrganizationsPage.tsx)
```tsx
// Основная структура
<Box p="md">
  <Group justify="space-between" mb="lg">
    <Title order={2}>Управление Организациями</Title>
    <Group>
      <Button onClick={simulateLogin}>Эмуляция входа</Button>
      <Button onClick={logout}>Выход</Button>
    </Group>
  </Group>
  
  <Button onClick={() => openFormModal()}>Создать Организацию</Button>
  
  <OrganizationTable 
    organizations={organizations} 
    onEdit={openFormModal} 
    onDelete={openDeleteModal} 
  />
  
  {/* Модальные окна */}
</Box>
```

#### Модальное окно для создания/редактирования (в OrganizationsPage.tsx)
```tsx
<Modal
  opened={formModalOpened}
  onClose={() => setFormModalOpened(false)}
  title={selectedOrganization ? 'Редактирование организации' : 'Создание организации'}
  // Настройки для правильного отображения
  size="md"
  centered
  overlayProps={{
    backgroundOpacity: 0.55,
    blur: 3,
  }}
>
  <OrganizationForm
    organizationToEdit={selectedOrganization}
    onSuccess={() => setFormModalOpened(false)}
  />
</Modal>
```

#### Форма организации (OrganizationForm.tsx)
```tsx
// Упрощенная версия с прямым управлением состоянием
<form onSubmit={handleSubmit}>
  <Stack gap="md">
    <TextInput
      label="Название"
      value={name}
      onChange={(e) => setName(e.target.value)}
      required
    />
    
    <TextInput
      label="Код"
      value={code}
      onChange={(e) => setCode(e.target.value)}
      required
      disabled={!!organizationToEdit}
    />
    
    <Select
      label="Тип организации"
      value={orgType}
      onChange={(val) => setOrgType(val as 'HOLDING' | 'LEGAL_ENTITY' | 'LOCATION')}
      data={[
        { value: 'HOLDING', label: 'Холдинг' },
        { value: 'LEGAL_ENTITY', label: 'Юридическое лицо' },
        { value: 'LOCATION', label: 'Локация' }
      ]}
      required
    />
    
    <Textarea
      label="Описание"
      value={description}
      onChange={(e) => setDescription(e.target.value)}
    />
    
    <Checkbox
      label="Активна"
      checked={isActive}
      onChange={(e) => setIsActive(e.currentTarget.checked)}
    />
    
    <Group justify="flex-end">
      <Button type="submit" loading={isSubmitting}>
        {organizationToEdit ? 'Сохранить' : 'Создать'}
      </Button>
    </Group>
  </Stack>
</form>
```

## Важные аспекты

### Аутентификация
Frontend сохраняет JWT-токен в localStorage и отправляет его в заголовке `Authorization: Bearer <token>` при каждом запросе. Бэкенд проверяет этот токен.

```tsx
// Функция для эмуляции входа (временное решение для разработки)
const simulateLogin = async () => {
  // Фиксированный JWT-токен для разработки
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxOTExNzA0ODUzfQ.qFKLyZ3DIkzVTvnZlnSVrgZXEe-RxV6kOL_rw8pJzYU';
  localStorage.setItem('access_token', token);
  
  // Обновляем данные на странице
  queryClient.invalidateQueries({ queryKey: ['organizations'] });
};
```

### API запросы
Запросы к API реализованы через TanStack Query (React Query) с хуками для организаций:

```tsx
// Хук для получения списка организаций
export const useOrganizations = () => {
  return useQuery<Organization[], Error>({
    queryKey: ['organizations'],
    queryFn: fetchOrganizations,
  });
};

// Хук для создания организации
export const useCreateOrganization = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Organization, Error, OrganizationCreateDto>({
    mutationFn: createOrganization,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });
};
```

### Стили модального окна
Используется Mantine UI с настройками:

```tsx
// Конфигурация для модального окна (modalSettings.ts)
export const formModalSettings = {
  size: "md",
  centered: true,
  overlayProps: {
    backgroundOpacity: 0.55,
    blur: 3,
  },
  closeButtonProps: {
    "aria-label": "Close"
  },
  withinPortal: true,
};
```

## Критические моменты при разработке

1. **CORS-настройки**: Бэкенд должен разрешать запросы с адресов фронтенда
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173", "http://localhost:5174"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **JWT-аутентификация**: Правильная настройка проверки токенов
   
3. **Обращение к CRUD**: Если crud_organization - это экземпляр класса, то обращение к методам должно быть напрямую:
   ```python
   await crud_organization.get(db, id=id)  # Правильно
   ```

4. **Управление формой**: В React использовать правильное управление состоянием формы:
   - Либо с useForm (Mantine)
   - Либо с прямым управлением через useState и обработчики onChange 