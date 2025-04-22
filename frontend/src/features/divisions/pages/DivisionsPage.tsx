import { useState } from 'react';
import { Button, Group, Modal, Title, Box, Text, Stack } from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { DivisionForm } from '../components/DivisionForm';
import { DivisionTable } from '../components/DivisionTable';
import { useDisclosure } from '@mantine/hooks';
import { Division, DivisionType } from '../../../types/division';

export function DivisionsPage() {
  const [createModalOpened, { open: openCreateModal, close: closeCreateModal }] = useDisclosure(false);
  const [deleteModalOpened, { open: openDeleteModal, close: closeDeleteModal }] = useDisclosure(false);
  const [editModalOpened, { open: openEditModal, close: closeEditModal }] = useDisclosure(false);
  const [divisionToEdit, setDivisionToEdit] = useState<Division | null>(null);
  const [divisionToDelete, setDivisionToDelete] = useState<Division | null>(null);
  const [availableDivisions, setAvailableDivisions] = useState<Division[]>([]);
  const [departmentFormOpen, { open: openDepartmentForm, close: closeDepartmentForm }] = useDisclosure(false);
  const [divisionFormOpen, { open: openDivisionForm, close: closeDivisionForm }] = useDisclosure(false);

  const handleEditDivision = (division: Division, allDivisions: Division[]) => {
    setDivisionToEdit(division);
    setAvailableDivisions(allDivisions);
    openEditModal();
  };

  const handleDeleteDivision = (division: Division) => {
    setDivisionToDelete(division);
    openDeleteModal();
  };

  const resetModals = () => {
    setDivisionToEdit(null);
    setDivisionToDelete(null);
    setAvailableDivisions([]);
  };

  const handleCreateDepartment = (allDivisions: Division[]) => {
    setAvailableDivisions(allDivisions);
    openDepartmentForm();
  };

  const handleCreateDivision = (allDivisions: Division[]) => {
    setAvailableDivisions(allDivisions);
    openDivisionForm();
  };

  return (
    <Box p="md">
      <Stack spacing="md">
        <Group position="apart" mb="md">
          <Title order={2}>Организационная структура</Title>
          <Group>
            <Button 
              leftIcon={<IconPlus size={16} />} 
              onClick={() => openDepartmentForm()}
              variant="filled"
              color="blue"
            >
              Добавить департамент
            </Button>
            <Button 
              leftIcon={<IconPlus size={16} />} 
              onClick={() => openDivisionForm()}
              variant="outline"
              color="blue"
            >
              Добавить отдел
            </Button>
          </Group>
        </Group>

        <Box>
          <Text size="sm" color="dimmed" mb="xs">
            Управление организационной структурой компании. Здесь вы можете добавлять, редактировать и удалять департаменты и отделы.
          </Text>
        </Box>

        <DivisionTable 
          onEdit={handleEditDivision} 
          onDelete={handleDeleteDivision} 
          onCreateDepartment={handleCreateDepartment}
          onCreateDivision={handleCreateDivision}
        />
      </Stack>

      {/* Модальное окно для создания департамента */}
      <Modal
        opened={departmentFormOpen}
        onClose={closeDepartmentForm}
        title="Создание нового департамента"
        size="lg"
      >
        <DivisionForm 
          onSuccess={() => {
            closeDepartmentForm();
            resetModals();
          }}
          availableParents={availableDivisions}
          defaultType={DivisionType.DEPARTMENT}
        />
      </Modal>

      {/* Модальное окно для создания отдела */}
      <Modal
        opened={divisionFormOpen}
        onClose={closeDivisionForm}
        title="Создание нового отдела"
        size="lg"
      >
        <DivisionForm 
          onSuccess={() => {
            closeDivisionForm();
            resetModals();
          }}
          availableParents={availableDivisions}
          defaultType={DivisionType.DIVISION}
        />
      </Modal>

      {/* Модальное окно для редактирования */}
      <Modal
        opened={editModalOpened}
        onClose={() => {
          closeEditModal();
          resetModals();
        }}
        title={`Редактирование ${divisionToEdit?.type === DivisionType.DEPARTMENT ? 'департамента' : 'отдела'}`}
        size="lg"
      >
        {divisionToEdit && (
          <DivisionForm 
            divisionToEdit={divisionToEdit}
            onSuccess={() => {
              closeEditModal();
              resetModals();
            }}
            availableParents={availableDivisions}
          />
        )}
      </Modal>

      {/* Модальное окно для удаления */}
      <Modal
        opened={deleteModalOpened}
        onClose={() => {
          closeDeleteModal();
          resetModals();
        }}
        title="Подтвердите удаление"
        size="sm"
      >
        <Box p="md">
          <Text mb="md">
            Вы уверены, что хотите удалить {divisionToDelete?.type === DivisionType.DEPARTMENT ? 'департамент' : 'отдел'} <strong>{divisionToDelete?.name}</strong>?
            {divisionToDelete?.type === DivisionType.DEPARTMENT && ' Это также удалит все отделы, связанные с этим департаментом.'}
          </Text>
          <Group position="right">
            <Button variant="outline" onClick={() => {
              closeDeleteModal();
              resetModals();
            }}>
              Отмена
            </Button>
            <Button 
              color="red"
              onClick={() => {
                // Удаление будет обрабатываться в DivisionTable через onDelete callback
                closeDeleteModal();
                resetModals();
              }}
            >
              Удалить
            </Button>
          </Group>
        </Box>
      </Modal>
    </Box>
  );
} 