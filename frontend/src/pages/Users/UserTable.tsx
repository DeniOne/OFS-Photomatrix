import React from 'react';
import { Table, Pagination, Group, ActionIcon, Text, Badge } from '@mantine/core';
import { IconPencil, IconTrash } from '@tabler/icons-react';
import { User } from '@/types/user';

interface UserTableProps {
  users: User[];
  total: number;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  onEdit: (user: User) => void;
  onDelete: (id: number) => void;
}

const UserTable: React.FC<UserTableProps> = (
  { users, total, page, limit, onPageChange, onEdit, onDelete }
) => {
  const totalPages = Math.ceil(total / limit);

  const rows = users.map((user) => (
    <Table.Tr key={user.id}>
      <Table.Td>{user.id}</Table.Td>
      <Table.Td>{user.email}</Table.Td>
      <Table.Td>{user.full_name || '-'}</Table.Td>
      <Table.Td>
        <Badge color={user.is_active ? 'green' : 'gray'}>
          {user.is_active ? 'Активен' : 'Неактивен'}
        </Badge>
      </Table.Td>
      <Table.Td>
        {user.is_superuser && <Badge color='orange'>Администратор</Badge>}
      </Table.Td>
      <Table.Td>{new Date(user.created_at).toLocaleDateString()}</Table.Td>
      <Table.Td>
        <Group gap="xs">
          <ActionIcon 
            variant="subtle" 
            color="blue" 
            onClick={() => onEdit(user)}
            aria-label={`Редактировать ${user.email}`}
          >
            <IconPencil size={16} />
          </ActionIcon>
          <ActionIcon 
            variant="subtle" 
            color="red" 
            onClick={() => onDelete(user.id)}
            aria-label={`Удалить ${user.email}`}
          >
            <IconTrash size={16} />
          </ActionIcon>
        </Group>
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <>
      <Table striped highlightOnHover withTableBorder withColumnBorders>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>ID</Table.Th>
            <Table.Th>Email</Table.Th>
            <Table.Th>ФИО</Table.Th>
            <Table.Th>Статус</Table.Th>
            <Table.Th>Роль</Table.Th>
            <Table.Th>Создан</Table.Th>
            <Table.Th>Действия</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {rows.length > 0 ? (
             rows
          ) : (
            <Table.Tr>
              <Table.Td colSpan={7}>
                <Text ta="center">Пользователи не найдены</Text>
              </Table.Td>
            </Table.Tr>
          )}
          </Table.Tbody>
      </Table>

      {totalPages > 1 && (
        <Pagination 
          total={totalPages} 
          value={page} 
          onChange={onPageChange} 
          mt="lg" 
          style={{ display: 'flex', justifyContent: 'center' }}
        />
      )}
    </>
  );
};

export default UserTable; 