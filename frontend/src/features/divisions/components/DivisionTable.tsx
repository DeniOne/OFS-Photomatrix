import { useCallback, useMemo } from 'react';
import { ActionIcon, Badge, Group, Paper, Table, Text, Box, Loader, Alert } from '@mantine/core';
import { IconEdit, IconTrash } from '@tabler/icons-react';
import { useQueryClient } from '@tanstack/react-query';
import { useFetchDivisions, useDeleteDivisionMutation } from '../api/divisionApi';
import { Division, DivisionType } from '../../../types/division';
import { useAuth } from '../../../hooks/useAuth';

interface DivisionTableProps {
  onEdit: (division: Division, allDivisions: Division[]) => void;
  onDelete: (division: Division) => void;
  onCreateDepartment: (allDivisions: Division[]) => void;
  onCreateDivision: (allDivisions: Division[]) => void;
}

export function DivisionTable({ onEdit, onDelete, onCreateDepartment, onCreateDivision }: DivisionTableProps) {
  const { getToken } = useAuth();
  const token = getToken();
  
  const { data: divisions, isLoading, error } = useFetchDivisions(token);
  const queryClient = useQueryClient();
  const deleteMutation = useDeleteDivisionMutation(queryClient);

  // Сортировка подразделений: сначала департаменты, затем отделы
  const sortedDivisions = useMemo(() => {
    if (!divisions) return [];
    
    // Сортировка по типу и имени
    return [...divisions].sort((a, b) => {
      // Сначала сортируем по типу (департаменты первыми)
      if (a.type === DivisionType.DEPARTMENT && b.type !== DivisionType.DEPARTMENT) {
        return -1;
      }
      if (a.type !== DivisionType.DEPARTMENT && b.type === DivisionType.DEPARTMENT) {
        return 1;
      }
      
      // Затем сортируем по имени для одинаковых типов
      return a.name.localeCompare(b.name);
    });
  }, [divisions]);

  // Структурированное отображение иерархии подразделений
  const structuredDivisions = useMemo(() => {
    if (!divisions) return [];
    
    const result: Division[] = [];
    
    // Добавляем департаменты (корневые подразделения)
    const departments = divisions.filter(div => div.type === DivisionType.DEPARTMENT);
    
    departments.forEach(department => {
      result.push(department);
      
      // Добавляем отделы, относящиеся к текущему департаменту
      const childDivisions = divisions.filter(div => 
        div.type === DivisionType.DIVISION && div.parent_id === department.id
      );
      
      childDivisions.forEach(division => {
        result.push(division);
      });
    });
    
    // Добавляем отделы без департамента в конец
    const orphanDivisions = divisions.filter(div => 
      div.type === DivisionType.DIVISION && !div.parent_id
    );
    
    orphanDivisions.forEach(division => {
      result.push(division);
    });
    
    return result;
  }, [divisions]);

  const handleDelete = useCallback((division: Division) => {
    onDelete(division);
    deleteMutation.mutate({ id: division.id, token });
  }, [onDelete, deleteMutation, token]);

  if (isLoading) {
    return (
      <Box style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
        <Loader />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert color="red" title="Ошибка загрузки">
        {error.message}
      </Alert>
    );
  }

  if (!divisions || divisions.length === 0) {
    return (
      <Paper p="md" radius="sm">
        <Text align="center" color="dimmed">
          Подразделения отсутствуют. Создайте новое подразделение.
        </Text>
      </Paper>
    );
  }

  return (
    <Paper shadow="xs" p="md" radius="sm">
      <Table striped highlightOnHover withTableBorder withColumnBorders>
        <Table.Thead>
          <Table.Tr>
            <Table.Th style={{ width: '30%' }}>Название</Table.Th>
            <Table.Th style={{ width: '10%' }}>Код</Table.Th>
            <Table.Th style={{ width: '15%' }}>Тип</Table.Th>
            <Table.Th style={{ width: '25%' }}>Организация</Table.Th>
            <Table.Th style={{ width: '10%' }}>Статус</Table.Th>
            <Table.Th style={{ width: '10%' }}>Действия</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {structuredDivisions.map((division) => (
            <Table.Tr key={division.id}>
              <Table.Td>
                <Group spacing="xs">
                  {division.type === DivisionType.DIVISION && division.parent_id && (
                    <Text style={{ marginLeft: '20px' }} size="sm">
                      {division.name}
                    </Text>
                  )}
                  {(division.type === DivisionType.DEPARTMENT || !division.parent_id) && (
                    <Text weight={division.type === DivisionType.DEPARTMENT ? 'bold' : 'normal'} size="sm">
                      {division.name}
                    </Text>
                  )}
                </Group>
              </Table.Td>
              <Table.Td>{division.code || '-'}</Table.Td>
              <Table.Td>
                <Badge 
                  color={division.type === DivisionType.DEPARTMENT ? 'blue' : 'green'}
                >
                  {division.type === DivisionType.DEPARTMENT ? 'Департамент' : 'Отдел'}
                </Badge>
              </Table.Td>
              <Table.Td>
                <Text size="sm">
                  {division.organization_name || 'Не указана'}
                </Text>
              </Table.Td>
              <Table.Td>
                <Badge color={division.is_active ? 'green' : 'red'}>
                  {division.is_active ? 'Активно' : 'Неактивно'}
                </Badge>
              </Table.Td>
              <Table.Td>
                <Group gap="xs">
                  <ActionIcon variant="subtle" color="blue" onClick={() => onEdit(division, divisions)}>
                    <IconEdit size={16} />
                  </ActionIcon>
                  <ActionIcon variant="subtle" color="red" onClick={() => handleDelete(division)}>
                    <IconTrash size={16} />
                  </ActionIcon>
                </Group>
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </Paper>
  );
} 