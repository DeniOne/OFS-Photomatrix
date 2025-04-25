import React, { useState, useMemo } from 'react';
import { Box, Title, Button, Group, Modal, Text, Alert, Code, Tabs } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { IconPlus, IconAlertCircle, IconInfoCircle, IconRocket } from '@tabler/icons-react';

import { StaffTable } from '../components/StaffTable';
import StaffForm from '../components/StaffForm';
import RocketChatIntegrationForm from '../components/RocketChatIntegrationForm';
import { Staff, StaffCreateResponse, StaffRocketChat } from '../../../types/staff';
import { useStaffList, useCreateStaff, useUpdateStaff, useDeleteStaff } from '../api/staffApi';

const StaffPage: React.FC = () => {
  const queryClient = useQueryClient();
  
  // Состояния для модальных окон
  const [openedFormModal, { open: openFormModal, close: closeFormModal }] = useDisclosure(false);
  const [openedDeleteModal, { open: openDeleteModal, close: closeDeleteModal }] = useDisclosure(false);
  const [openedRocketChatModal, { open: openRocketChatModal, close: closeRocketChatModal }] = useDisclosure(false);
  const [openedActivationModal, { open: openActivationModal, close: closeActivationModal }] = useDisclosure(false);
  
  // Состояния для данных
  const [editingStaff, setEditingStaff] = useState<Staff | null>(null);
  const [deletingStaff, setDeletingStaff] = useState<Staff | null>(null);
  const [rocketChatStaff, setRocketChatStaff] = useState<Staff | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activationCode, setActivationCode] = useState<string | null>(null);
  
  // Получаем данные о сотрудниках
  const { 
    data: staffList = [], 
    isLoading: isLoadingStaff, 
    isError: isErrorStaff,
    error: staffError
  } = useStaffList();
  
  // Мутации для CRUD операций
  const createMutation = useCreateStaff();
  const updateMutation = useUpdateStaff();
  const deleteMutation = useDeleteStaff();
  
  // Функция закрытия всех модалок
  const handleCloseModals = () => {
    closeFormModal();
    closeDeleteModal();
    closeRocketChatModal();
    closeActivationModal();
    setEditingStaff(null);
    setDeletingStaff(null);
    setRocketChatStaff(null);
    setActivationCode(null);
  };
  
  // Открытие формы создания
  const handleOpenCreateModal = () => {
    setEditingStaff(null);
    openFormModal();
  };
  
  // Открытие формы редактирования
  const handleOpenEditModal = (staff: Staff) => {
    setEditingStaff(staff);
    openFormModal();
  };
  
  // Открытие модалки подтверждения удаления
  const handleOpenDeleteModal = (staff: Staff) => {
    setDeletingStaff(staff);
    openDeleteModal();
  };
  
  // Открытие модалки для интеграции с Rocket.Chat
  const handleOpenRocketChatModal = (staff: Staff) => {
    setRocketChatStaff(staff);
    openRocketChatModal();
  };
  
  // Обработка отправки формы сотрудника
  const handleFormSubmit = async (data: any) => {
    if (editingStaff) {
      // Обновление существующего сотрудника
      updateMutation.mutate(
        { id: editingStaff.id, data },
        {
          onSuccess: () => {
            handleCloseModals();
          }
        }
      );
    } else {
      // Создание нового сотрудника
      createMutation.mutate(
        data,
        {
          onSuccess: (response: StaffCreateResponse) => {
            // Если был создан пользователь и получен код активации
            if (response.activation_code) {
              setActivationCode(response.activation_code);
              closeFormModal();
              openActivationModal();
            } else {
              handleCloseModals();
            }
          }
        }
      );
    }
  };
  
  // Подтверждение удаления
  const handleConfirmDelete = () => {
    if (deletingStaff) {
      deleteMutation.mutate(
        deletingStaff.id,
        {
          onSuccess: () => {
            handleCloseModals();
          }
        }
      );
    }
  };
  
  // Обработка интеграции с Rocket.Chat
  const handleRocketChatIntegration = (data: StaffRocketChat) => {
    // TODO: Реализовать вызов API для интеграции с Rocket.Chat
    console.log('Интеграция с Rocket.Chat для сотрудника:', rocketChatStaff?.id, data);
    
    // Имитация успешной интеграции
    notifications.show({
      title: 'Демо-режим',
      message: 'Интеграция с Rocket.Chat находится в разработке',
      color: 'blue',
      icon: <IconInfoCircle size={16} />,
    });
    
    handleCloseModals();
  };
  
  // Фильтрация сотрудников по поисковому запросу
  const filteredStaff = useMemo(() => {
    if (!searchTerm) return staffList;
    
    const lowerCaseSearchTerm = searchTerm.toLowerCase();
    return staffList.filter(staff => 
      staff.first_name.toLowerCase().includes(lowerCaseSearchTerm) ||
      staff.last_name.toLowerCase().includes(lowerCaseSearchTerm) ||
      (staff.middle_name && staff.middle_name.toLowerCase().includes(lowerCaseSearchTerm)) ||
      (staff.email && staff.email.toLowerCase().includes(lowerCaseSearchTerm)) ||
      (staff.phone && staff.phone.toLowerCase().includes(lowerCaseSearchTerm))
    );
  }, [staffList, searchTerm]);
  
  return (
    <Box>
      <Group mb="lg">
        <Button leftSection={<IconPlus size={14} />} onClick={handleOpenCreateModal}>
          Добавить сотрудника
        </Button>
      </Group>
      
      {isErrorStaff && (
        <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка загрузки данных" color="red" mb="md">
          Не удалось загрузить список сотрудников: {staffError?.message || 'Неизвестная ошибка'}
        </Alert>
      )}
      
      <StaffTable
        data={filteredStaff}
        loading={isLoadingStaff}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        onEdit={handleOpenEditModal}
        onDelete={handleOpenDeleteModal}
        onRocketChatIntegration={handleOpenRocketChatModal}
      />
      
      {/* Модальное окно формы создания/редактирования */}
      <Modal
        opened={openedFormModal}
        onClose={handleCloseModals}
        title={editingStaff ? 'Редактировать сотрудника' : 'Добавить нового сотрудника'}
        size="lg"
        overlayProps={{
          backgroundOpacity: 0.55,
          blur: 3,
        }}
      >
        <StaffForm
          initialData={editingStaff}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModals}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />
      </Modal>
      
      {/* Модальное окно подтверждения удаления */}
      <Modal
        opened={openedDeleteModal}
        onClose={handleCloseModals}
        title="Подтверждение удаления"
        size="sm"
        overlayProps={{
          backgroundOpacity: 0.55,
          blur: 3,
        }}
      >
        <Text size="sm">
          Вы уверены, что хотите удалить сотрудника "{deletingStaff?.last_name} {deletingStaff?.first_name}"?
          {deletingStaff?.user_id && (
            <Text color="red" mt="xs">
              Внимание: Этот сотрудник имеет связанный аккаунт пользователя.
            </Text>
          )}
        </Text>
        <Group justify="flex-end" mt="md">
          <Button variant="default" onClick={handleCloseModals} disabled={deleteMutation.isPending}>
            Отмена
          </Button>
          <Button color="red" onClick={handleConfirmDelete} loading={deleteMutation.isPending}>
            Удалить
          </Button>
        </Group>
      </Modal>
      
      {/* Модальное окно для интеграции с Rocket.Chat */}
      <Modal
        opened={openedRocketChatModal}
        onClose={handleCloseModals}
        title="Интеграция с Rocket.Chat"
        size="lg"
        overlayProps={{
          backgroundOpacity: 0.55,
          blur: 3,
        }}
      >
        {rocketChatStaff && (
          <RocketChatIntegrationForm
            staff={rocketChatStaff}
            onSubmit={handleRocketChatIntegration}
            onCancel={handleCloseModals}
            isLoading={false} // TODO: Добавить состояние загрузки при интеграции
          />
        )}
      </Modal>
      
      {/* Модальное окно с кодом активации */}
      <Modal
        opened={openedActivationModal}
        onClose={handleCloseModals}
        title="Код активации пользователя"
        size="md"
        overlayProps={{
          backgroundOpacity: 0.55,
          blur: 3,
        }}
      >
        <Alert icon={<IconInfoCircle size="1rem" />} title="Сохраните этот код" color="blue" mb="md">
          Этот код активации будет показан только один раз. Сохраните его для передачи сотруднику.
        </Alert>
        
        <Text mb="md">Код активации:</Text>
        <Code block color="blue" mb="lg">
          {activationCode}
        </Code>
        
        <Text size="sm" mb="md">
          Сотрудник должен использовать этот код при первом входе в систему для активации своего аккаунта.
        </Text>
        
        <Group justify="flex-end">
          <Button onClick={handleCloseModals}>
            Закрыть
          </Button>
        </Group>
      </Modal>
    </Box>
  );
};

export default StaffPage; 