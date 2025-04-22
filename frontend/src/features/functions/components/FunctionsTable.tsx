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
  ScrollArea 
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
    <>
      {/* Поиск функций */}
      <TextInput
        placeholder="Поиск функций..."
        mb="md"
        icon={<IconSearch size={16} />}
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
      />

      {/* Таблица функций */}
      <ScrollArea>
        <Table striped highlightOnHover>
          <thead>
            <tr>
              <th>Название</th>
              <th>Код</th>
              <th>Описание</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {data.length === 0 ? (
              <tr>
                <td colSpan={5}>
                  <Text color="dimmed" align="center">Функций не найдено</Text>
                </td>
              </tr>
            ) : (
              data.map((func) => (
                <tr key={func.id}>
                  <td>{func.name}</td>
                  <td>{func.code}</td>
                  <td>{func.description || '—'}</td>
                  <td>
                    <Badge 
                      color={func.is_active ? 'green' : 'red'}
                    >
                      {func.is_active ? 'Активна' : 'Неактивна'}
                    </Badge>
                  </td>
                  <td>
                    <Group spacing={0} position="left">
                      <Tooltip label="Редактировать">
                        <ActionIcon onClick={() => onEdit(func)}>
                          <IconEdit size={16} />
                        </ActionIcon>
                      </Tooltip>
                      <Tooltip label="Удалить">
                        <ActionIcon color="red" onClick={() => onDelete(func)}>
                          <IconTrash size={16} />
                        </ActionIcon>
                      </Tooltip>
                    </Group>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </Table>
      </ScrollArea>
    </>
  );
} 