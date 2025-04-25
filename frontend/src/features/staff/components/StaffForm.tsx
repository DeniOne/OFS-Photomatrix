import React, { useState } from 'react';
import { 
  TextInput, Button, Group, Switch, Box, LoadingOverlay, Stack, 
  Checkbox, Textarea, FileInput, Divider, Text, Title
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { DateInput } from '@mantine/dates';
import { IconUpload } from '@tabler/icons-react';
import { Staff, StaffCreate, StaffUpdate } from '../../../types/staff';
import { ru } from 'date-fns/locale';

interface StaffFormProps {
  initialData?: Staff | null;
  onSubmit: (data: StaffCreate | StaffUpdate) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const StaffForm: React.FC<StaffFormProps> = ({
  initialData = null,
  onSubmit,
  onCancel,
  isLoading,
}) => {
  const [createUser, setCreateUser] = useState(false);

  // Парсинг даты из ISO формата
  const parseDate = (dateString?: string | null) => {
    if (!dateString) return null;
    try {
      return new Date(dateString);
    } catch (e) {
      return null;
    }
  };

  const form = useForm({
    initialValues: {
      first_name: initialData?.first_name || '',
      last_name: initialData?.last_name || '',
      middle_name: initialData?.middle_name || '',
      email: initialData?.email || '',
      phone: initialData?.phone || '',
      hire_date: parseDate(initialData?.hire_date),
      is_active: initialData?.is_active ?? true,
      photo_path: initialData?.photo_path || '',
      document_paths: initialData?.document_paths || {},
      create_user: false, // По умолчанию не создаем пользователя
    },
    validate: {
      first_name: (value) => (value.trim().length < 2 ? 'Имя должно содержать минимум 2 символа' : null),
      last_name: (value) => (value.trim().length < 2 ? 'Фамилия должна содержать минимум 2 символа' : null),
      email: (value) => {
        if (createUser && !value) return 'Email обязателен для создания пользователя';
        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Некорректный email';
        return null;
      },
    },
  });

  // Обработчик изменения флага создания пользователя
  const handleCreateUserChange = (checked: boolean) => {
    setCreateUser(checked);
    form.setFieldValue('create_user', checked);
  };

  const handleSubmit = (values: typeof form.values) => {
    const formData: StaffCreate | StaffUpdate = {
      ...values,
      hire_date: values.hire_date ? values.hire_date.toISOString().split('T')[0] : undefined,
    };
    
    onSubmit(formData);
  };

  return (
    <Box pos="relative">
      <LoadingOverlay visible={isLoading} />
      
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          <Group grow>
            <TextInput
              label="Фамилия"
              placeholder="Иванов"
              withAsterisk
              {...form.getInputProps('last_name')}
            />
            <TextInput
              label="Имя"
              placeholder="Иван"
              withAsterisk
              {...form.getInputProps('first_name')}
            />
          </Group>
          
          <TextInput
            label="Отчество"
            placeholder="Иванович"
            {...form.getInputProps('middle_name')}
          />
          
          <Group grow>
            <TextInput
              label="Email"
              placeholder="ivanov@example.com"
              {...form.getInputProps('email')}
            />
            <TextInput
              label="Телефон"
              placeholder="+7 (999) 123-45-67"
              {...form.getInputProps('phone')}
            />
          </Group>
          
          <DateInput
            valueFormat="DD.MM.YYYY"
            label="Дата приема на работу"
            placeholder="Выберите дату"
            locale={ru}
            clearable
            value={form.values.hire_date}
            onChange={(date) => form.setFieldValue('hire_date', date)}
            error={form.errors.hire_date}
          />

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
          
          <Divider label="Дополнительная информация" labelPosition="center" />
          
          <FileInput
            label="Фотография"
            placeholder="Загрузить фото сотрудника"
            accept="image/*"
            clearable
            leftSection={<IconUpload size={16} />}
            // TODO: Реализовать загрузку файлов и сохранение пути
          />
          
          <Switch
            label="Активен"
            checked={form.values.is_active}
            onChange={(event) => form.setFieldValue('is_active', event.currentTarget.checked)}
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