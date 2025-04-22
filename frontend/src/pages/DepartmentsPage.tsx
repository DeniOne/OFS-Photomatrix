import React, { useState } from "react";
import {
  Container,
  Button,
  Group,
  Modal,
  Text,
  Box,
  Title,
  Paper,
  Table,
} from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";
import { DivisionForm } from "../features/divisions/components/DivisionForm";
import {
  useDivisions,
  useDeleteDivision,
} from "../features/divisions/api/divisionApi";
import { Division, DivisionType } from "../types/division";
import { useOrganizations } from "../features/organizations/api/organizationApi";

export default function DepartmentsPage() {
  // Модальные окна
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [divisionToEdit, setDivisionToEdit] = useState<Division | undefined>(undefined);
  const [divisionToDelete, setDivisionToDelete] = useState<Division | undefined>(undefined);

  // Получение данных
  const { data: organizations = [] } = useOrganizations();
  const { data: allDivisions = [], refetch: refetchDivisions } = useDivisions();
  const deleteDivision = useDeleteDivision();

  // Находим холдинг "Фотоматрица"
  const holdingOrg = organizations.find(org => org.org_type === 'HOLDING');
  
  // Фильтруем только департаменты холдинга
  const departments = allDivisions.filter((div: Division) => 
    div.type === DivisionType.DEPARTMENT && 
    (holdingOrg ? div.organization_id === holdingOrg.id : true)
  );

  // Обновление данных
  const handleRefresh = () => {
    refetchDivisions();
  };

  // Редактирование
  const handleEdit = (division: Division) => {
    setDivisionToEdit(division);
    setEditModalOpen(true);
  };

  // Удаление
  const handleDelete = (division: Division) => {
    setDivisionToDelete(division);
    setDeleteConfirmOpen(true);
  };

  // Подтверждение удаления
  const handleConfirmDelete = async () => {
    if (divisionToDelete) {
      try {
        await deleteDivision.mutateAsync(divisionToDelete.id);
        setDeleteConfirmOpen(false);
        setDivisionToDelete(undefined);
        handleRefresh();
      } catch (error) {
        console.error("Ошибка при удалении департамента:", error);
      }
    }
  };

  return (
    <Box p="md">
      <Group justify="space-between" mb="lg">
        <Button 
          leftSection={<IconPlus size={16} />} 
          onClick={() => setCreateModalOpen(true)}
          size="md"
          color="indigo"
        >
          Создать департамент
        </Button>
      </Group>

      <Box mt="md">
        {departments.length === 0 ? (
          <Text ta="center" c="dimmed" py="md">Департаменты не найдены</Text>
        ) : (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Название</Table.Th>
                <Table.Th>Код</Table.Th>
                <Table.Th>Тип</Table.Th>
                <Table.Th>Родитель</Table.Th>
                <Table.Th>Статус</Table.Th>
                <Table.Th>Действия</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {departments.map((dept) => (
                <Table.Tr key={dept.id}>
                  <Table.Td>{dept.name}</Table.Td>
                  <Table.Td>{dept.code}</Table.Td>
                  <Table.Td>Департамент</Table.Td>
                  <Table.Td>-</Table.Td>
                  <Table.Td>
                    <Box style={{
                      background: '#2B8A3E',
                      color: 'white',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      display: 'inline-block',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      textTransform: 'uppercase'
                    }}>
                      Активна
                    </Box>
                  </Table.Td>
                  <Table.Td>
                    <Group gap={0} justify="flex-end">
                      <Button variant="subtle" size="xs" p={0} style={{ fontSize: '18px' }}>⋮</Button>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Box>

      {/* Модальное окно создания */}
      <Modal
        opened={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Создать департамент"
        size="md"
      >
        <DivisionForm
          organizationId={holdingOrg?.id}
          onSuccess={() => {
            setCreateModalOpen(false);
            handleRefresh();
          }}
          defaultType={DivisionType.DEPARTMENT}
        />
      </Modal>

      {/* Модальное окно редактирования */}
      <Modal
        opened={editModalOpen}
        onClose={() => {
          setEditModalOpen(false);
          setDivisionToEdit(undefined);
        }}
        title="Редактировать департамент"
        size="md"
      >
        {divisionToEdit && (
          <DivisionForm
            divisionToEdit={divisionToEdit}
            onSuccess={() => {
              setEditModalOpen(false);
              setDivisionToEdit(undefined);
              handleRefresh();
            }}
            defaultType={DivisionType.DEPARTMENT}
          />
        )}
      </Modal>

      {/* Модальное окно подтверждения удаления */}
      <Modal
        opened={deleteConfirmOpen}
        onClose={() => {
          setDeleteConfirmOpen(false);
          setDivisionToDelete(undefined);
        }}
        title="Подтвердите удаление"
        size="sm"
      >
        <Text mb="md">Вы уверены, что хотите удалить департамент "{divisionToDelete?.name}"?</Text>
        <Group justify="flex-end">
          <Button variant="outline" onClick={() => setDeleteConfirmOpen(false)}>
            Отмена
          </Button>
          <Button color="red" onClick={handleConfirmDelete}>
            Удалить
          </Button>
        </Group>
      </Modal>
    </Box>
  );
} 