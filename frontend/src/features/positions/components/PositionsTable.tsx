import React from 'react';
import { Table, ActionIcon, Badge, Group, TextInput, Select, Box, Loader, Text, Stack } from '@mantine/core';
import { IconEdit, IconTrash, IconSearch } from '@tabler/icons-react';
import { Position } from '../../../types/position';

interface PositionsTableProps {
  data: Position[];
  loading: boolean;
  searchTerm: string;
  onSearchChange: (value: string) => void;
  sectionFilter: number | null;
  onSectionFilterChange: (value: number | null) => void;
  sections: { value: string; label: string }[];
  onEdit: (position: Position) => void;
  onDelete: (position: Position) => void;
}

export const PositionsTable: React.FC<PositionsTableProps> = ({
  data,
  loading,
  searchTerm,
  onSearchChange,
  sectionFilter,
  onSectionFilterChange,
  sections,
  onEdit,
  onDelete,
}) => {
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
            placeholder="Поиск по названию, коду или описанию"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.currentTarget.value)}
            leftSection={<IconSearch size={16} />}
            style={{ flex: 1 }}
          />
          <Select
            placeholder="Фильтр по отделу"
            data={sections}
            value={sectionFilter ? String(sectionFilter) : null}
            onChange={(value) => onSectionFilterChange(value ? Number(value) : null)}
            clearable
            style={{ width: 250 }}
          />
        </Group>
        <Text ta="center" c="dimmed" size="sm">
          Нет должностей для отображения
        </Text>
      </Stack>
    );
  }

  const rows = data.map((position) => (
    <Table.Tr key={position.id}>
      <Table.Td>{position.name}</Table.Td>
      <Table.Td>{position.code}</Table.Td>
      <Table.Td>
        {position.section_id ? 
          (position.section?.name ? 
            `${position.section.name}${position.section.division?.name ? ` (${position.section.division.name})` : ''}` 
            : `ID: ${position.section_id}`) 
          : '-'}
      </Table.Td>
      <Table.Td>{position.attribute || '-'}</Table.Td>
      <Table.Td>
        <Badge color={position.is_active ? 'green' : 'red'}>
          {position.is_active ? 'Активна' : 'Неактивна'}
        </Badge>
      </Table.Td>
      <Table.Td>
        <Group gap="xs">
          <ActionIcon variant="subtle" color="blue" onClick={() => onEdit(position)}>
            <IconEdit size={16} />
          </ActionIcon>
          <ActionIcon variant="subtle" color="red" onClick={() => onDelete(position)}>
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
          placeholder="Поиск по названию, коду или описанию"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.currentTarget.value)}
          leftSection={<IconSearch size={16} />}
          style={{ flex: 1 }}
        />
        <Select
          placeholder="Фильтр по отделу"
          data={sections}
          value={sectionFilter ? String(sectionFilter) : null}
          onChange={(value) => onSectionFilterChange(value ? Number(value) : null)}
          clearable
          style={{ width: 250 }}
        />
      </Group>

      <Table striped highlightOnHover withTableBorder withColumnBorders>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Название</Table.Th>
            <Table.Th>Код</Table.Th>
            <Table.Th>Отдел</Table.Th>
            <Table.Th>Уровень</Table.Th>
            <Table.Th>Статус</Table.Th>
            <Table.Th>Действия</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </Stack>
  );
}; 