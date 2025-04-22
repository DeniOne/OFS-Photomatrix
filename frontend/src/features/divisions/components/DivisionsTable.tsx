import { useState } from 'react';
import { Table, Group, Button, Badge, ActionIcon, Menu, Modal, Text, Box, TextInput } from '@mantine/core';
import { IconEdit, IconTrash, IconDotsVertical, IconSearch, IconPlus } from '@tabler/icons-react';
import { Division, DivisionType } from '../../../types/division';
import { DivisionForm } from './DivisionForm';
import { useDeleteDivision } from '../api/divisionApi';
import { notifications } from '@mantine/notifications';

export interface DivisionsTableProps {
  divisions: Division[];
  organizationId?: number | null;
  availableParents?: Division[];
  onRefresh: () => void;
  onEditClick: (division: Division) => void;
  onDeleteClick: (id: number) => void;
  title?: string;
  addButtonLabel?: string;
}

export function DivisionsTable({
  divisions,
  organizationId,
  availableParents,
  onRefresh,
  onEditClick,
  onDeleteClick,
  title = "Подразделения",
  addButtonLabel = "Добавить подразделение"
}: DivisionsTableProps) {
  const [search, setSearch] = useState('');
  const [editingDivision, setEditingDivision] = useState<Division | undefined>(undefined);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);
  
  const deleteDivision = useDeleteDivision();

  const filteredDivisions = divisions.filter(division => {
    if (organizationId) {
      return division.organization_id === organizationId;
    }
    return true;
  });

  const handleEdit = (division: Division) => {
    setEditingDivision(division);
    setIsEditModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteDivision.mutateAsync(id);
      notifications.show({
        title: 'Успешно!',
        message: 'Подразделение удалено',
        color: 'green',
      });
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      console.error('Ошибка при удалении подразделения:', error);
      notifications.show({
        title: 'Ошибка',
        message: 'Не удалось удалить подразделение. Пожалуйста, попробуйте снова.',
        color: 'red',
      });
    } finally {
      setDeleteConfirmId(null);
    }
  };

  const handleFormSuccess = () => {
    setIsEditModalOpen(false);
    setIsCreateModalOpen(false);
    setEditingDivision(undefined);
    if (onRefresh) {
      onRefresh();
    }
  };

  const getDivisionType = () => {
    if (title.toLowerCase().includes('департамент')) {
      return DivisionType.DEPARTMENT;
    } else if (title.toLowerCase().includes('отдел')) {
      return DivisionType.DIVISION;
    }
    return undefined;
  };

  const getParentName = (parentId?: number | null) => {
    if (!parentId) return '-';
    
    const parent = [...divisions, ...(availableParents || [])].find(d => d.id === parentId);
    return parent ? parent.name : `ID: ${parentId}`;
  };

  const getOrganizationName = (orgId?: number | null) => {
    return orgId ? `ID: ${orgId}` : '-';
  };

  const getDivisionTypeLabel = (type?: DivisionType) => {
    if (type === DivisionType.DEPARTMENT) {
      return <Badge color="blue">Департамент</Badge>;
    }
    if (type === DivisionType.DIVISION) {
      return <Badge color="green">Подразделение</Badge>;
    }
    return <Badge color="gray">Неизвестно</Badge>;
  };

  return (
    <>
      <Box mb="md">
        <Group justify="space-between">
          <TextInput
            placeholder={`Поиск по ${title.toLowerCase()}...`}
            leftSection={<IconSearch size="1rem" />}
            value={search}
            onChange={(e) => setSearch(e.currentTarget.value)}
            style={{ width: '300px' }}
          />
          <Button 
            leftSection={<IconPlus size="1rem" />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            {addButtonLabel}
          </Button>
        </Group>
      </Box>

      <Table striped highlightOnHover withTableBorder withColumnBorders>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Название</Table.Th>
            <Table.Th>Код</Table.Th>
            <Table.Th>Тип</Table.Th>
            <Table.Th>Родительское подразделение</Table.Th>
            <Table.Th>Описание</Table.Th>
            <Table.Th>Статус</Table.Th>
            <Table.Th style={{ width: '80px' }}>Действия</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {filteredDivisions.length === 0 ? (
            <Table.Tr>
              <Table.Td colSpan={7} align="center">
                {title} не найдены
              </Table.Td>
            </Table.Tr>
          ) : (
            filteredDivisions.map((division) => (
              <Table.Tr key={division.id}>
                <Table.Td>{division.name}</Table.Td>
                <Table.Td>{division.code}</Table.Td>
                <Table.Td>{getDivisionTypeLabel(division.type)}</Table.Td>
                <Table.Td>{getParentName(division.parent_id)}</Table.Td>
                <Table.Td>{division.description || '-'}</Table.Td>
                <Table.Td>
                  <Badge color={division.is_active ? 'green' : 'red'}>
                    {division.is_active ? 'Активно' : 'Неактивно'}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    <ActionIcon variant="subtle" color="blue" onClick={() => handleEdit(division)}>
                      <IconEdit size={16} />
                    </ActionIcon>
                    <ActionIcon variant="subtle" color="red" onClick={() => setDeleteConfirmId(division.id)}>
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))
          )}
        </Table.Tbody>
      </Table>

      <Modal 
        opened={isCreateModalOpen} 
        onClose={() => setIsCreateModalOpen(false)}
        title={`Создать ${title.toLowerCase().endsWith('ы') ? title.slice(0, -1) : title}`}
        size="lg"
      >
        <DivisionForm 
          organizationId={organizationId}
          availableParents={availableParents}
          onSuccess={handleFormSuccess}
          defaultType={getDivisionType()}
        />
      </Modal>

      <Modal 
        opened={isEditModalOpen} 
        onClose={() => {
          setIsEditModalOpen(false);
          setEditingDivision(undefined);
        }}
        title={`Редактировать ${title.toLowerCase().endsWith('ы') ? title.slice(0, -1) : title}`}
        size="lg"
      >
        {editingDivision && (
          <DivisionForm 
            divisionToEdit={editingDivision}
            availableParents={availableParents.filter(p => p.id !== editingDivision.id)}
            onSuccess={handleFormSuccess}
          />
        )}
      </Modal>

      <Modal
        opened={deleteConfirmId !== null}
        onClose={() => setDeleteConfirmId(null)}
        title="Подтверждение удаления"
        size="sm"
      >
        <Text>Вы уверены, что хотите удалить это подразделение?</Text>
        <Group justify="flex-end" mt="md">
          <Button variant="outline" onClick={() => setDeleteConfirmId(null)}>
            Отмена
          </Button>
          <Button 
            color="red" 
            onClick={() => deleteConfirmId && handleDelete(deleteConfirmId)}
            loading={deleteDivision.isPending}
          >
            Удалить
          </Button>
        </Group>
      </Modal>
    </>
  );
} 