import React, { useState, useEffect } from 'react';
import { 
  TextInput, Button, Group, Switch, Box, LoadingOverlay, Stack, 
  Checkbox, FileInput, Divider, Text, 
  Select, Badge, ActionIcon, Paper, List, Anchor
} from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { IconUpload, IconTrash } from '@tabler/icons-react';
import { Staff, StaffCreate, StaffUpdate } from '../../../types/staff';
import { usePositionsList, useOrganizationsList } from '../api/staffApi';

export const DOCUMENT_TYPES = [
  { value: 'passport', label: 'Паспорт' },
  { value: 'contract', label: 'Трудовой договор' },
  { value: 'diploma', label: 'Диплом' },
  { value: 'medical', label: 'Медицинская книжка' },
  { value: 'other', label: 'Другое' },
];

// Функция для получения названия типа документа
const getDocumentTypeName = (docType: string): string => {
  const foundType = DOCUMENT_TYPES.find(type => type.value === docType);
  return foundType ? foundType.label : docType;
};

// Константы для проверки уровней должностей - должны совпадать с теми, что используются в PositionForm
const LEVEL_DIRECTOR = 'DIRECTOR';
const LEVEL_HEAD = 'HEAD';
const LEVEL_LEAD = 'LEAD';

// Парсинг даты из ISO формата
const parseDate = (dateString?: string | null) => {
  if (!dateString) return null;
  try {
    return new Date(dateString);
  } catch (e) {
    return null;
  }
};

interface StaffFormProps {
  initialData?: Staff | null;
  onSubmit: (data: StaffCreate | StaffUpdate) => void;
  onCancel: () => void;
  isLoading: boolean;
  onPhotoUpload?: (staffId: number, photo: File) => void;
  onDocumentUpload?: (staffId: number, document: File, docType: string) => void;
}

const StaffForm: React.FC<StaffFormProps> = ({
  initialData = null,
  onSubmit,
  onCancel,
  isLoading,
  onPhotoUpload,
  onDocumentUpload,
}) => {
  // Базовые состояния
  const [createUser, setCreateUser] = useState(false);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<string | null>(null);
  const [, setSelectedPositionLevel] = useState<string | null>(null);
  const [showLocationField, setShowLocationField] = useState(true);
  
  // Загружаем списки должностей и организаций
  const { data: positions = [], isLoading: isPositionsLoading } = usePositionsList();
  const { data: organizations = [], isLoading: isOrganizationsLoading } = useOrganizationsList();
  
  // Фильтрация организаций по типам
  const legalEntities = organizations?.filter(org => org.org_type === 'LEGAL_ENTITY') || [];
  const locations = organizations?.filter(org => org.org_type === 'LOCATION') || [];
  const defaultHolding = organizations?.find(org => org.org_type === 'HOLDING');

  // Состояния формы
  const [firstName, setFirstName] = useState(initialData?.first_name || '');
  const [lastName, setLastName] = useState(initialData?.last_name || '');
  const [middleName, setMiddleName] = useState(initialData?.middle_name || '');
  const [email, setEmail] = useState(initialData?.email || '');
  const [phone, setPhone] = useState(initialData?.phone || '');
  const [hireDate, setHireDate] = useState<Date | null>(parseDate(initialData?.hire_date));
  const [isActive, setIsActive] = useState(initialData?.is_active ?? true);
  const [] = useState(initialData?.photo_path || '');
  const [] = useState(initialData?.document_paths || {});
  
  // Состояния ошибок
  const [firstNameError, setFirstNameError] = useState<string | null>(null);
  const [lastNameError, setLastNameError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [positionIdError, setPositionIdError] = useState<string | null>(null);
  const [organizationIdError, setOrganizationIdError] = useState<string | null>(null);
  
  // ID полей с зависимостями
  const [positionId, setPositionId] = useState<string | null>(
    initialData?.staff_positions?.[0]?.position_id 
      ? String(initialData.staff_positions[0].position_id) 
      : null
  );
  
  const [organizationId, setOrganizationId] = useState<string | null>(
    defaultHolding?.id ? String(defaultHolding.id) : null
  );
  
  const [locationId, setLocationId] = useState<string | null>(
    initialData?.staff_positions?.[0]?.position?.section_id 
      ? String(initialData.staff_positions[0].position.section_id) 
      : null
  );

  // Эффект для обновления уровня должности при выборе должности
  useEffect(() => {
    if (positionId) {
      const selectedPosition = positions.find(p => String(p.id) === positionId);
      if (selectedPosition) {
        console.log('Выбрана должность:', selectedPosition.name, 'уровень:', selectedPosition.attribute);
        setSelectedPositionLevel(selectedPosition.attribute);
        
        // Определяем, нужно ли показывать поле выбора локации
        // Локация не нужна для директоров и руководителей
        const posLevel = selectedPosition.attribute;
        const shouldShowLocation = posLevel !== LEVEL_DIRECTOR && posLevel !== LEVEL_HEAD;
        setShowLocationField(shouldShowLocation);
        
        // Если локация скрыта, очищаем значение
        if (!shouldShowLocation) {
          setLocationId(null);
        }
      }
    } else {
      // Если должность не выбрана, показываем поле локации по умолчанию
      setShowLocationField(true);
    }
  }, [positionId, positions]);

  // Обработчик изменения флага создания пользователя
  const handleCreateUserChange = (checked: boolean) => {
    setCreateUser(checked);
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    
    // Валидация формы
    if (!firstName.trim() || firstName.trim().length < 2) {
      setFirstNameError('Имя должно содержать минимум 2 символа');
      return;
    }
    
    if (!lastName.trim() || lastName.trim().length < 2) {
      setLastNameError('Фамилия должна содержать минимум 2 символа');
      return;
    }
    
    if (createUser && !email) {
      setEmailError('Email обязателен для создания пользователя');
      return;
    }
    
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setEmailError('Некорректный email');
      return;
    }
    
    if (!positionId) {
      setPositionIdError('Необходимо выбрать должность');
      return;
    }
    
    if (!organizationId) {
      setOrganizationIdError('Необходимо выбрать организацию');
      return;
    }
    
    // Преобразуем форму в формат для отправки
    const formData: StaffCreate | StaffUpdate = {
      first_name: firstName,
      last_name: lastName,
      middle_name: middleName || undefined,
      email: email || undefined,
      phone: phone || undefined,
      hire_date: hireDate 
        ? `${hireDate.getFullYear()}-${String(hireDate.getMonth() + 1).padStart(2, '0')}-${String(hireDate.getDate()).padStart(2, '0')}` // Формат YYYY-MM-DD
        : undefined,
      is_active: isActive,
      create_user: createUser,
      // Добавляем ID из отдельных состояний
      position_id: positionId ? Number(positionId) : undefined,
      organization_id: organizationId ? Number(organizationId) : undefined,
      location_id: showLocationField && locationId ? Number(locationId) : undefined,
      is_primary_position: true,
    };
    
    onSubmit(formData);
    
    // Если есть фото для загрузки и указан ID сотрудника - загружаем фото
    if (photoFile && initialData?.id && onPhotoUpload) {
      onPhotoUpload(initialData.id, photoFile);
    }
  };

  // Обработчик загрузки фото после создания сотрудника

  // Обработчик загрузки документа после создания сотрудника

  // Преобразуем должности в формат для компонента Select
  const positionOptions = positions?.map(position => ({
    value: position.id.toString(),
    label: position.name,
  })) || [];

  // Рендерим список документов
  const renderDocumentList = () => {
    if (!initialData || !initialData.document_paths || Object.keys(initialData.document_paths || {}).length === 0) {
      return <Text c="dimmed">Документы не загружены</Text>;
    }

    return (
      <List>
        {Object.entries(initialData.document_paths || {}).map(([docName, path]) => (
          <List.Item key={docName}>
            <Group>
              <Text>{getDocumentTypeName(docName)}</Text>
              <Anchor href={path} target="_blank">
                Открыть
              </Anchor>
            </Group>
          </List.Item>
        ))}
      </List>
    );
  };

  return (
    <Box pos="relative">
      <LoadingOverlay visible={isLoading || isPositionsLoading || isOrganizationsLoading} />
      
      <form onSubmit={handleSubmit}>
        <Stack>
          <Group grow>
            <TextInput
              label="Фамилия"
              placeholder="Иванов"
              withAsterisk
              value={lastName}
              onChange={(event) => setLastName(event.target.value)}
              error={lastNameError}
            />
            <TextInput
              label="Имя"
              placeholder="Иван"
              withAsterisk
              value={firstName}
              onChange={(event) => setFirstName(event.target.value)}
              error={firstNameError}
            />
          </Group>
          
          <TextInput
            label="Отчество"
            placeholder="Иванович"
            value={middleName}
            onChange={(event) => setMiddleName(event.target.value)}
          />
          
          <Group grow>
            <TextInput
              label="Email"
              placeholder="ivanov@example.com"
              withAsterisk
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              error={emailError}
            />
            <TextInput
              label="Телефон"
              placeholder="+7 (999) 123-45-67"
              value={phone}
              onChange={(event) => setPhone(event.target.value)}
            />
          </Group>
          
          <DateInput
            label="Дата приема на работу"
            placeholder="Выберите дату"
            valueFormat="DD.MM.YYYY"
            clearable
            value={hireDate}
            onChange={(date) => setHireDate(date)}
            error={null}
          />
          
          <Divider label="Должность и организация" labelPosition="center" />
          
          <Select
            label="Должность"
            placeholder="Выберите должность"
            data={positionOptions}
            searchable
            withAsterisk
            value={positionId}
            onChange={setPositionId}
            error={positionIdError}
          />
          
          <Select
            label="Организация"
            placeholder="Выберите организацию"
            data={legalEntities?.map(org => ({
              value: org.id.toString(),
              label: org.name,
            })) || []}
            searchable
            clearable
            required
            value={organizationId}
            onChange={setOrganizationId}
            error={organizationIdError}
          />
          
          {showLocationField && (
            <Select
              label="Локация"
              placeholder="Выберите локацию"
              data={locations?.map(loc => ({
                value: loc.id.toString(),
                label: loc.name,
              })) || []}
              searchable
              clearable
              value={locationId}
              onChange={setLocationId}
            />
          )}
          
          <Divider label="Пользовательский аккаунт" labelPosition="center" />
          
          {!initialData?.user_id && (
            <Checkbox
              label="Создать пользовательский аккаунт в системе"
              checked={createUser}
              onChange={(event) => handleCreateUserChange(event.currentTarget.checked)}
            />
          )}

          {createUser && (
            <Box p="xs" style={{ backgroundColor: 'rgba(0, 0, 0, 0.05)', borderRadius: '4px' }}>
              <Text size="sm" mb="xs">
                Будет создан пользователь с кодом активации. 
                <br />Код будет показан после создания сотрудника.
                <br />Email обязателен для создания пользователя.
              </Text>
            </Box>
          )}
          
          {initialData?.user_id && (
            <Text size="sm" c="dimmed">
              Сотрудник имеет связанный аккаунт пользователя. ID: {initialData.user_id}
            </Text>
          )}
          
          <Divider label="Фотография" labelPosition="center" />
          
          <FileInput
            label="Фотография сотрудника"
            placeholder="Загрузить фото сотрудника"
            accept="image/*"
            clearable
            leftSection={<IconUpload size={16} />}
            value={photoFile}
            onChange={setPhotoFile}
          />
          
          {initialData?.photo_path && (
            <Box mt="xs">
              <Text fw={500} mb="xs">Текущее фото:</Text>
              <img 
                src={initialData.photo_path} 
                alt="Фотография сотрудника" 
                style={{ maxWidth: '100%', maxHeight: '200px', borderRadius: '4px' }} 
              />
            </Box>
          )}
          
          <Divider label="Документы" labelPosition="center" />
          
          {initialData && (
            <Paper p="xs" withBorder>
              <Text fw={500} mb="xs">Загруженные документы:</Text>
              {renderDocumentList()}
            </Paper>
          )}
          
          {initialData && (
            <Group align="flex-end" grow>
              <Select
                label="Тип документа"
                placeholder="Выберите тип документа"
                data={DOCUMENT_TYPES}
                value={documentType}
                onChange={setDocumentType}
                clearable
              />
              <FileInput
                label="Загрузить документ"
                placeholder="Выберите файл документа"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                clearable
                leftSection={<IconUpload size={16} />}
                value={documentFile}
                onChange={setDocumentFile}
                disabled={!documentType}
              />
              <Button 
                disabled={!documentFile || !documentType} 
                onClick={() => onDocumentUpload && initialData.id && documentFile && documentType && 
                  onDocumentUpload(initialData.id, documentFile, documentType)
                }
              >
                Загрузить
              </Button>
            </Group>
          )}
          
          <Switch
            label="Активен"
            checked={isActive}
            onChange={(event) => setIsActive(event.currentTarget.checked)}
          />
          
          <Group justify="flex-end" mt="xl">
            <Button variant="outline" onClick={onCancel} disabled={isLoading}>
              Отмена
            </Button>
            <Button type="submit" loading={isLoading}>
              {initialData ? 'Сохранить' : 'Создать'}
            </Button>
          </Group>
        </Stack>
      </form>
    </Box>
  );
};

export default StaffForm; 