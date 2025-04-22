import React from 'react';
import { 
  Table, 
  Group, 
  Text, 
  ActionIcon, 
  Tooltip, 
  Badge, 
  TextInput, 
  Loader, 
  ScrollArea,
  Stack
} from '@mantine/core';
import { IconEdit, IconTrash, IconSearch } from '@tabler/icons-react';
import { Function } from '../../../types/function';

interface FunctionsTableProps {
  data: Function[];
  loading: boolean;
  onEdit: (func: Function) => void;
  onDelete: (func: Function) => void;
  searchTerm: string;
  onSearchChange: (value: string) => void;
}

export function FunctionsTable({ 
  data, 
  loading, 
  onEdit, 
  onDelete, 
  searchTerm, 
  onSearchChange 
}: FunctionsTableProps) {
  // Если данные загружаются, показываем лоадер
  if (loading) {
    return <Loader size="md" />;
  }

  // Рендерим таблицу с функциями
  return (
    <Stack>
      {/* Поиск функций */}
      <TextInput
        placeholder="Поиск функций..."
        icon={<IconSearch size={16} />}
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
      />

      {/* Таблица функций */}
      <ScrollArea>
        <Table striped highlightOnHover withTableBorder withColumnBorders>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Название</Table.Th>
              <Table.Th>Код</Table.Th>
              <Table.Th>Отдел</Table.Th>
              <Table.Th>Описание</Table.Th>
              <Table.Th>Статус</Table.Th>
              <Table.Th>Действия</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={6}>
                  <Text c="dimmed" ta="center">Функций не найдено</Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              data.map((func) => (
                <Table.Tr key={func.id}>
                  <Table.Td>{func.name}</Table.Td>
                  <Table.Td>{func.code}</Table.Td>
                  <Table.Td>{func.section?.name || '-'}</Table.Td>
                  <Table.Td>{func.description || '—'}</Table.Td>
                  <Table.Td>
                    <Badge 
                      color={func.is_active ? 'green' : 'red'}
                    >
                      {func.is_active ? 'Активна' : 'Неактивна'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      <ActionIcon variant="subtle" color="blue" onClick={() => onEdit(func)}>
                        <IconEdit size={16} />
                      </ActionIcon>
                      <ActionIcon variant="subtle" color="red" onClick={() => onDelete(func)}>
                        <IconTrash size={16} />
                      </ActionIcon>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))
            )}
          </Table.Tbody>
        </Table>
      </ScrollArea>
    </Stack>
  );
} 