import React from 'react';
import { Table, ActionIcon, Badge, Group, TextInput, Box, Loader, Text, Stack, Tooltip } from '@mantine/core';
import { IconEdit, IconTrash, IconSearch, IconUserPlus, IconRocket, IconEye } from '@tabler/icons-react';
import { Staff } from '../../../types/staff';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { useNavigate } from 'react-router-dom';

interface StaffTableProps {
  data: Staff[];
  loading: boolean;
  searchTerm: string;
  onSearchChange: (value: string) => void;
  onEdit: (staff: Staff) => void;
  onDelete: (staff: Staff) => void;
  onCreateUser?: (staff: Staff) => void;
  onRocketChatIntegration?: (staff: Staff) => void;
}

export const StaffTable: React.FC<StaffTableProps> = ({
  data,
  loading,
  searchTerm,
  onSearchChange,
  onEdit,
  onDelete,
  onCreateUser,
  onRocketChatIntegration,
}) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <Box pt="xl" style={{ display: 'flex', justifyContent: 'center' }}>
        <Loader />
      </Box>
    );
  }

  if (data.length === 0) {
    return (
      <Stack>
        <Group mb="md">
          <TextInput
            placeholder="Поиск по имени, фамилии или email"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.currentTarget.value)}
            leftSection={<IconSearch size={16} />}
            style={{ flex: 1 }}
          />
        </Group>
        <Text ta="center" c="dimmed" size="sm">
          Нет сотрудников для отображения
        </Text>
      </Stack>
    );
  }

  // Функция для форматирования даты
  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    try {
      return format(new Date(dateString), 'dd.MM.yyyy', { locale: ru });
    } catch (e) {
      return dateString;
    }
  };

  // Функция для получения полного имени
  const getFullName = (staff: Staff) => {
    const middle = staff.middle_name ? ` ${staff.middle_name}` : '';
    return `${staff.last_name} ${staff.first_name}${middle}`;
  };

  // Переход к детальной странице сотрудника
  const handleRowClick = (staff: Staff) => {
    navigate(`/staff/${staff.id}`);
  };

  const rows = data.map((staff) => (
    <Table.Tr 
      key={staff.id} 
      style={{ cursor: 'pointer' }}
      onClick={() => handleRowClick(staff)}
    >
      <Table.Td>{getFullName(staff)}</Table.Td>
      <Table.Td>{staff.email || '-'}</Table.Td>
      <Table.Td>{staff.phone || '-'}</Table.Td>
      <Table.Td>{formatDate(staff.hire_date)}</Table.Td>
      <Table.Td>
        <Badge color={staff.is_active ? 'green' : 'red'}>
          {staff.is_active ? 'Активен' : 'Неактивен'}
        </Badge>
      </Table.Td>
      <Table.Td>
        <Badge color={staff.user_id ? 'blue' : 'gray'}>
          {staff.user_id ? 'Есть' : 'Нет'}
        </Badge>
      </Table.Td>
      <Table.Td onClick={(e) => e.stopPropagation()}>
        <Group gap="xs">
          <Tooltip label="Просмотреть">
            <ActionIcon variant="subtle" color="teal" onClick={() => handleRowClick(staff)}>
              <IconEye size={16} />
            </ActionIcon>
          </Tooltip>
          
          <ActionIcon variant="subtle" color="blue" onClick={() => onEdit(staff)}>
            <IconEdit size={16} />
          </ActionIcon>
          
          {!staff.user_id && onCreateUser && (
            <Tooltip label="Создать пользователя">
              <ActionIcon variant="subtle" color="green" onClick={() => onCreateUser(staff)}>
                <IconUserPlus size={16} />
              </ActionIcon>
            </Tooltip>
          )}
          
          {onRocketChatIntegration && (
            <Tooltip label="Интеграция с Rocket.Chat">
              <ActionIcon variant="subtle" color="violet" onClick={() => onRocketChatIntegration(staff)}>
                <IconRocket size={16} />
              </ActionIcon>
            </Tooltip>
          )}
          
          <ActionIcon variant="subtle" color="red" onClick={() => onDelete(staff)}>
            <IconTrash size={16} />
          </ActionIcon>
        </Group>
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <Stack>
      <Group mb="md">
        <TextInput
          placeholder="Поиск по имени, фамилии или email"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.currentTarget.value)}
          leftSection={<IconSearch size={16} />}
          style={{ flex: 1 }}
        />
      </Group>

      <Table striped highlightOnHover withTableBorder withColumnBorders>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>ФИО</Table.Th>
            <Table.Th>Email</Table.Th>
            <Table.Th>Телефон</Table.Th>
            <Table.Th>Дата приема</Table.Th>
            <Table.Th>Статус</Table.Th>
            <Table.Th>Пользователь</Table.Th>
            <Table.Th>Действия</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </Stack>
  );
}; 