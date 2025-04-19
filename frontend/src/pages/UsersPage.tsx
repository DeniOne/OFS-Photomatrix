import React, { useState } from 'react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import {
  Box, Text, Title, Button, Group, Table, Modal, TextInput, PasswordInput, Select, LoadingOverlay
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconPlus, IconCheck, IconX } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { useForm } from '@mantine/form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createUser } from '../api/client';

// Временные данные для примера
const mockUsers = [
  { id: '1', name: 'Админ Админов', email: 'admin@example.com', role: 'Администратор', status: 'Активен' },
  { id: '2', name: 'Иван Петров', email: 'ivan.p@example.com', role: 'Менеджер', status: 'Активен' },
  { id: '3', name: 'Мария Сидорова', email: 'maria.s@example.com', role: 'Редактор', status: 'Заблокирован' },
];

const UsersPage = () => {
  const [opened, { open, close }] = useDisclosure(false);
  const queryClient = useQueryClient();

  console.log('UsersPage RENDER - Modal opened state:', opened);

  const form = useForm({
    initialValues: {
      full_name: '',
      email: '',
      password: '',
      role: 'Администратор',
    },
    validate: {
      full_name: (value) => (value.trim().length < 2 ? 'Имя должно содержать минимум 2 символа' : null),
      email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Неверный формат email'),
      password: (value) => (value.length < 6 ? 'Пароль должен содержать минимум 6 символов' : null),
      role: (value) => (value ? null : 'Роль обязательна'),
    },
  });

  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: (data) => {
      console.log('Пользователь успешно создан:', data);
      notifications.show({
        title: 'Успех!',
        message: `Пользователь ${data.full_name || data.email} успешно создан.`,
        color: 'green',
        icon: <IconCheck />,
      });
      close();
      form.reset();
    },
    onError: (error) => {
      console.error('Ошибка при создании пользователя:', error);
      notifications.show({
        title: 'Ошибка!',
        message: `Не удалось создать пользователя: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });

  const handleFormSubmit = (values: typeof form.values) => {
    console.log('Отправка данных на бэкенд:', values);
    mutation.mutate({ 
      email: values.email, 
      password: values.password, 
      full_name: values.full_name, 
      role: values.role 
    });
  };

  const handleOpenModal = () => {
    console.log('Кнопка "Добавить пользователя" нажата!');
    form.setFieldValue('role', 'Администратор');
    open();
  };

  const rows = mockUsers.map((user) => (
    <Table.Tr key={user.id}>
      <Table.Td>{user.name}</Table.Td>
      <Table.Td>{user.email}</Table.Td>
      <Table.Td>{user.role}</Table.Td>
      <Table.Td>
        <Text c={user.status === 'Активен' ? 'green' : 'red'}>
          {user.status}
        </Text>
      </Table.Td>
      <Table.Td>
        <Group gap="xs">
          <Button variant="subtle" size="xs">Редакт.</Button>
          <Button variant="subtle" color="red" size="xs">Удалить</Button>
        </Group>
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <DashboardLayout>
      <LoadingOverlay visible={mutation.isPending} overlayProps={{ radius: "sm", blur: 2 }} />
      <Box>
        <Group justify="space-between" mb="xl">
          <Title order={2}>Управление пользователями</Title>
          <Button leftSection={<IconPlus size={16} />} onClick={handleOpenModal}>
            Добавить пользователя
          </Button>
        </Group>

        <Modal 
          opened={opened} 
          onClose={close} 
          title="Добавить нового пользователя" 
          centered 
          withinPortal={false}
        >
          <form onSubmit={form.onSubmit(handleFormSubmit)}>
            <TextInput
              label="Имя"
              placeholder="Полное имя"
              required
              mb="md"
              {...form.getInputProps('full_name')}
            />
            <TextInput
              label="Email"
              placeholder="user@example.com"
              required
              type="email"
              mb="md"
              {...form.getInputProps('email')}
            />
            <PasswordInput
              label="Пароль"
              placeholder="Введите пароль"
              required
              mb="md"
              {...form.getInputProps('password')}
            />
            <Select
              label="Роль"
              placeholder="Выберите роль"
              required
              data={['Администратор', 'Менеджер', 'Редактор', 'Пользователь']}
              mb="xl"
              {...form.getInputProps('role')}
            />
            <Group justify="flex-end" mt="lg">
              <Button variant="default" onClick={() => { close(); form.reset(); }}>Отмена</Button>
              <Button type="submit" loading={mutation.isPending}>Сохранить</Button>
            </Group>
          </form>
        </Modal>

        <Box style={{ 
          border: `1px solid var(--mantine-color-dark-6)`,
          borderRadius: 'var(--mantine-radius-md)',
          overflow: 'hidden'
        }}>
          <Table 
            striped 
            highlightOnHover 
            verticalSpacing="sm"
            style={{ backgroundColor: 'var(--mantine-color-dark-7)' }}
          >
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Имя</Table.Th>
                <Table.Th>Email</Table.Th>
                <Table.Th>Роль</Table.Th>
                <Table.Th>Статус</Table.Th>
                <Table.Th>Действия</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{rows}</Table.Tbody>
          </Table>
        </Box>

      </Box>
    </DashboardLayout>
  );
};

export default UsersPage; 