import React, { useState } from 'react';
import { Box, Title, Text, LoadingOverlay, Alert, Button, Group } from '@mantine/core';
import { IconAlertCircle, IconPlus } from '@tabler/icons-react';
import { useUsers } from '@/hooks/users';
import { User } from '@/types/user';
import UserTable from './UserTable';
import UserFormModal from './UserFormModal';
import { useDisclosure } from '@mantine/hooks';
// import UserFormModal from './UserFormModal'; // Компонент модалки формы (создадим позже)

const UsersPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [limit] = useState(10); // Количество элементов на странице
  const [opened, { open: openModal, close: closeModal }] = useDisclosure(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const { data: usersData, isLoading, isError, error, refetch } = useUsers({ page, limit });
  // const deleteUserMutation = useDeleteUser();

  const handleAddUser = () => {
    setSelectedUser(null);
    openModal();
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    openModal();
  };

  const handleDeleteUser = (id: number) => {
    // Пока просто выводим в консоль
    console.log('Confirm delete user:', id);
    /*
    modals.openConfirmModal({
      title: 'Подтвердите удаление',
      children: (
        <Text size="sm">
          Вы уверены, что хотите удалить этого пользователя? Это действие необратимо.
        </Text>
      ),
      labels: { confirm: 'Удалить', cancel: 'Отмена' },
      confirmProps: { color: 'red' },
      onConfirm: () => {
        console.log('Deleting user:', id);
        // deleteUserMutation.mutate(id);
      },
    });
    */
  };

  const handleModalClose = () => {
    closeModal();
    setSelectedUser(null);
    refetch();
  };

  // Подготавливаем данные для таблицы
  const users = usersData?.data || [];
  const total = usersData?.total || 0;

  return (
    <Box>
      <Group justify="space-between" mb="lg">
        <Title order={2}>Управление пользователями</Title>
        <Button 
          leftSection={<IconPlus size={14} />} 
          onClick={handleAddUser}
          // disabled // Временно разблокируем для теста модалки
        >
          Добавить пользователя
        </Button>
      </Group>

      <Box pos="relative">
        <LoadingOverlay visible={isLoading} overlayProps={{ radius: "sm", blur: 2 }} />

        {isError && (
          <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка загрузки!" color="red" mb="lg">
            {(error as Error)?.message || 'Не удалось загрузить список пользователей.'}
          </Alert>
        )}

        {/* Используем UserTable с защитой от undefined */ }
        <UserTable 
          users={users}
          total={total}
          page={page}
          limit={limit}
          onPageChange={setPage}
          onEdit={handleEditUser}
          onDelete={handleDeleteUser}
        />
      </Box>

      <UserFormModal 
        opened={opened}
        onClose={handleModalClose}
        user={selectedUser}
      />
    </Box>
  );
};

export default UsersPage; 