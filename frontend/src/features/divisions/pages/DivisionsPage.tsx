import { useState, useEffect } from 'react';
import { Box, Button, Group, Modal, Title, Text } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconPlus } from '@tabler/icons-react';
import { Division, DivisionType } from '../../../types/division';
import { DivisionForm } from '../components/DivisionForm';
import { DivisionTable } from '../components/DivisionTable';
import { useAuth } from '../../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { Breadcrumbs } from '@mantine/core';

export function DivisionsPage() {
  const [isCreateDepartmentModalOpen, setIsCreateDepartmentModalOpen] = useState(false);
  const [isCreateDivisionModalOpen, setIsCreateDivisionModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedDivision, setSelectedDivision] = useState<Division | null>(null);
  const [allDivisions, setAllDivisions] = useState<Division[]>([]);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Проверка аутентификации
  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Закрытие всех модальных окон
  const handleCloseModals = () => {
    setIsCreateDepartmentModalOpen(false);
    setIsCreateDivisionModalOpen(false);
    setIsEditModalOpen(false);
    setIsDeleteModalOpen(false);
    setSelectedDivision(null);
  };

  // Обработчики для открытия модальных окон создания
  const handleOpenCreateDepartmentModal = (divisions: Division[]) => {
    setAllDivisions(divisions);
    setIsCreateDepartmentModalOpen(true);
  };

  const handleOpenCreateDivisionModal = (divisions: Division[]) => {
    setAllDivisions(divisions);
    setIsCreateDivisionModalOpen(true);
  };

  // Обработчик для открытия модального окна редактирования
  const handleOpenEditModal = (division: Division, divisions: Division[]) => {
    setSelectedDivision(division);
    setAllDivisions(divisions);
    setIsEditModalOpen(true);
  };

  // Обработчик для открытия модального окна удаления
  const handleOpenDeleteModal = (division: Division) => {
    setSelectedDivision(division);
    setIsDeleteModalOpen(true);
  };

  // Обработчик успешного сохранения формы
  const handleFormSuccess = () => {
    handleCloseModals();
    notifications.show({
      title: "Успешно",
      message: "Операция выполнена успешно",
      color: "green",
    });
  };

  const items = [
    { title: 'Главная', href: '/' },
    { title: 'Подразделения', href: '#' },
  ].map((item, index) => (
    <Text key={index} onClick={() => item.href !== '#' && navigate(item.href)}>
      {item.title}
    </Text>
  ));

  return (
    <Box p="md">
      <Group justify="space-between" mb="lg">
        <div>
          <Breadcrumbs>{items}</Breadcrumbs>
          <Title order={1} mt="md">Подразделения</Title>
        </div>
        <Group>
          <Button 
            leftSection={<IconPlus size={16} />} 
            onClick={() => handleOpenCreateDepartmentModal(allDivisions)}
          >
            Добавить департамент
          </Button>
        </Group>
      </Group>

      <DivisionTable
        onEdit={handleOpenEditModal}
        onDelete={handleOpenDeleteModal}
        onCreateDepartment={handleOpenCreateDepartmentModal}
        onCreateDivision={handleOpenCreateDivisionModal}
      />

      {/* Модальное окно для создания департамента */}
      <Modal
        opened={isCreateDepartmentModalOpen}
        onClose={handleCloseModals}
        title="Создать департамент"
        centered
      >
        <DivisionForm
          type={DivisionType.DEPARTMENT}
          onCancel={handleCloseModals}
          onSuccess={handleFormSuccess}
          allDivisions={allDivisions}
        />
      </Modal>

      {/* Модальное окно для создания отдела */}
      <Modal
        opened={isCreateDivisionModalOpen}
        onClose={handleCloseModals}
        title="Создать отдел"
        centered
      >
        <DivisionForm
          type={DivisionType.DIVISION}
          onCancel={handleCloseModals}
          onSuccess={handleFormSuccess}
          allDivisions={allDivisions}
        />
      </Modal>

      {/* Модальное окно для редактирования подразделения */}
      <Modal
        opened={isEditModalOpen}
        onClose={handleCloseModals}
        title={selectedDivision?.type === DivisionType.DEPARTMENT
          ? "Редактировать департамент"
          : "Редактировать отдел"
        }
        centered
      >
        {selectedDivision && (
          <DivisionForm
            initialData={selectedDivision}
            type={selectedDivision.type}
            onCancel={handleCloseModals}
            onSuccess={handleFormSuccess}
            allDivisions={allDivisions}
          />
        )}
      </Modal>

      {/* Модальное окно для подтверждения удаления */}
      <Modal
        opened={isDeleteModalOpen}
        onClose={handleCloseModals}
        title="Подтверждение удаления"
        centered
      >
        <Text mb="md">
          Вы уверены, что хотите удалить {selectedDivision?.type === DivisionType.DEPARTMENT
            ? "департамент"
            : "отдел"
          } "{selectedDivision?.name}"?
        </Text>
        <Group position="right">
          <Button variant="outline" onClick={handleCloseModals}>Отмена</Button>
          <Button color="red" onClick={() => {
            handleCloseModals();
            notifications.show({
              title: "Успешно",
              message: "Подразделение удалено",
              color: "green",
            });
          }}>
            Удалить
          </Button>
        </Group>
      </Modal>
    </Box>
  );
} 