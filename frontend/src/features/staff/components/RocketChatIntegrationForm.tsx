import React from 'react';
import { 
  TextInput, Button, Group, Switch, Box, LoadingOverlay, Stack, 
  Checkbox, Text, Alert, Select
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { IconRocket, IconAlertCircle } from '@tabler/icons-react';
import { Staff } from '../../../types/staff';
import { StaffRocketChat } from '../../../types/staff';

interface RocketChatIntegrationFormProps {
  staff: Staff;
  onSubmit: (data: StaffRocketChat) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const RocketChatIntegrationForm: React.FC<RocketChatIntegrationFormProps> = ({
  staff,
  onSubmit,
  onCancel,
  isLoading,
}) => {
  // Предлагаем значения на основе данных сотрудника
  const suggestedUsername = staff.email 
    ? staff.email.split('@')[0] 
    : `${staff.last_name.toLowerCase()}.${staff.first_name.toLowerCase()}`;
  
  const fullName = `${staff.last_name} ${staff.first_name}${staff.middle_name ? ' ' + staff.middle_name : ''}`;

  const form = useForm({
    initialValues: {
      username: suggestedUsername,
      email: staff.email || '',
      name: fullName,
      password: '',
      generatePassword: true,
      roles: ['user'], // По умолчанию обычный пользователь
      active: true,
    },
    validate: {
      username: (value) => (value.trim().length < 3 ? 'Имя пользователя должно содержать минимум 3 символа' : null),
      email: (value) => (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? 'Некорректный email' : null),
      password: (value, values) => {
        if (!values.generatePassword && (!value || value.length < 8)) {
          return 'Пароль должен содержать минимум 8 символов';
        }
        return null;
      },
    },
  });

  const handleSubmit = (values: typeof form.values) => {
    // Конвертируем в формат StaffRocketChat
    const rocketChatData: StaffRocketChat = {
      username: values.username,
      email: values.email || staff.email || '',
      name: values.name,
      password: values.generatePassword ? undefined : values.password,
      roles: values.roles,
      active: values.active,
    };
    
    onSubmit(rocketChatData);
  };

  return (
    <Box pos="relative">
      <LoadingOverlay visible={isLoading} />
      
      <Alert icon={<IconAlertCircle size="1rem" />} title="Интеграция с Rocket.Chat" color="blue" mb="md">
        Эта форма создаст нового пользователя в Rocket.Chat и свяжет его с сотрудником.
        <br />
        <Text fw="bold">Обратите внимание:</Text> Для успешной интеграции сервер Rocket.Chat должен быть доступен.
      </Alert>
      
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          <TextInput
            label="Имя пользователя (username)"
            placeholder="ivan.ivanov"
            description="Уникальный идентификатор пользователя в Rocket.Chat"
            withAsterisk
            leftSection={<IconRocket size={16} />}
            {...form.getInputProps('username')}
          />
          
          <TextInput
            label="Email"
            placeholder="ivan.ivanov@example.com"
            withAsterisk
            {...form.getInputProps('email')}
          />
          
          <TextInput
            label="Полное имя"
            placeholder="Иванов Иван Иванович"
            description="Отображаемое имя в Rocket.Chat"
            withAsterisk
            {...form.getInputProps('name')}
          />
          
          <Checkbox
            label="Сгенерировать случайный пароль"
            checked={form.values.generatePassword}
            onChange={(event) => form.setFieldValue('generatePassword', event.currentTarget.checked)}
          />
          
          {!form.values.generatePassword && (
            <TextInput
              label="Пароль"
              type="password"
              placeholder="Минимум 8 символов"
              withAsterisk
              {...form.getInputProps('password')}
            />
          )}
          
          <Select
            label="Роль пользователя"
            data={[
              { value: 'user', label: 'Пользователь' },
              { value: 'admin', label: 'Администратор' },
              { value: 'moderator', label: 'Модератор' },
            ]}
            defaultValue="user"
            description="Роль пользователя в Rocket.Chat"
            onChange={(value) => form.setFieldValue('roles', value ? [value] : ['user'])}
          />
          
          <Switch
            label="Активный пользователь"
            checked={form.values.active}
            onChange={(event) => form.setFieldValue('active', event.currentTarget.checked)}
          />
          
          <Group justify="flex-end" mt="md">
            <Button variant="outline" onClick={onCancel} disabled={isLoading}>
              Отмена
            </Button>
            <Button type="submit" loading={isLoading} color="blue">
              Создать пользователя в Rocket.Chat
            </Button>
          </Group>
        </Stack>
      </form>
    </Box>
  );
};

export default RocketChatIntegrationForm; 