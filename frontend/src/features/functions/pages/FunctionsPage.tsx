import React, { useState, useMemo } from 'react';
import { Box, Title, Button, Group, Modal, Text, Alert } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useQueryClient, useMutation, useQuery } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { IconPlus, IconCheck, IconX, IconAlertCircle } from '@tabler/icons-react';

import { FunctionsTable } from '../components/FunctionsTable';
import FunctionForm from '../components/FunctionForm';
import { Function, FunctionCreate, FunctionUpdate } from '../../../types/function';
import { functionApi } from '../../../api/functionApi';

const FunctionsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [openedFormModal, { open: openFormModal, close: closeFormModal }] = useDisclosure(false);
  const [openedDeleteModal, { open: openDeleteModal, close: closeDeleteModal }] = useDisclosure(false);

  const [editingFunction, setEditingFunction] = useState<Function | null>(null);
  const [deletingFunction, setDeletingFunction] = useState<Function | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const { 
    data: functionsData, 
    isLoading: isLoadingFunctions, 
    isError: isErrorFunctions,
    error: functionsError
  } = useQuery<Function[], Error>({
    queryKey: ['functions'],
    queryFn: () => functionApi.getAll({ limit: 1000 })
  });

  const createMutation = useMutation({
    mutationFn: (newData: FunctionCreate) => functionApi.create(newData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['functions'] });
      notifications.show({
        title: 'Успешно',
        message: 'Функция успешно создана',
        color: 'green',
        icon: <IconCheck />,
      });
      handleCloseModals();
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось создать функцию: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number, data: FunctionUpdate }) => functionApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['functions'] });
      notifications.show({
        title: 'Успешно',
        message: 'Функция успешно обновлена',
        color: 'green',
        icon: <IconCheck />,
      });
      handleCloseModals();
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось обновить функцию: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => functionApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['functions'] });
      notifications.show({
        title: 'Успешно',
        message: 'Функция успешно удалена',
        color: 'green',
        icon: <IconCheck />,
      });
      handleCloseModals();
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось удалить функцию: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
      handleCloseModals();
    },
  });

  const handleCloseModals = () => {
    closeFormModal();
    closeDeleteModal();
    setEditingFunction(null);
    setDeletingFunction(null);
  };

  const handleOpenCreateModal = () => {
    setEditingFunction(null);
    openFormModal();
  };

  const handleOpenEditModal = (func: Function) => {
    setEditingFunction(func);
    openFormModal();
  };

  const handleOpenDeleteModal = (func: Function) => {
    setDeletingFunction(func);
    openDeleteModal();
  };

  const handleFormSubmit = (data: FunctionCreate | FunctionUpdate) => {
    if (editingFunction) {
      updateMutation.mutate({ id: editingFunction.id, data });
    } else {
      createMutation.mutate(data as FunctionCreate);
    }
  };

  const handleConfirmDelete = () => {
    if (deletingFunction) {
      deleteMutation.mutate(deletingFunction.id);
    }
  };

  const filteredFunctions = useMemo(() => {
    if (!functionsData) return [];
    if (!searchTerm) return functionsData;

    const lowerCaseSearchTerm = searchTerm.toLowerCase();
    return functionsData.filter(func => 
      func.name.toLowerCase().includes(lowerCaseSearchTerm) ||
      func.code.toLowerCase().includes(lowerCaseSearchTerm) ||
      (func.description && func.description.toLowerCase().includes(lowerCaseSearchTerm)) ||
      (func.section?.name && func.section.name.toLowerCase().includes(lowerCaseSearchTerm))
    );
  }, [functionsData, searchTerm]);

  const isMutating = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending;

  return (
    <Box>
      <Group mb="lg">
        <Button leftSection={<IconPlus size={14} />} onClick={handleOpenCreateModal}>
          Добавить функцию
        </Button>
      </Group>

      {isErrorFunctions && (
        <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка загрузки данных" color="red" mb="md">
          Не удалось загрузить список функций: {functionsError?.message || 'Неизвестная ошибка'}
        </Alert>
      )}

      <FunctionsTable
        data={filteredFunctions}
        loading={isLoadingFunctions}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        onEdit={handleOpenEditModal}
        onDelete={handleOpenDeleteModal}
      />

      <Modal
        opened={openedFormModal}
        onClose={handleCloseModals}
        title={editingFunction ? 'Редактировать функцию' : 'Создать новую функцию'}
        size="lg"
        overlayProps={{
           backgroundOpacity: 0.55,
           blur: 3,
        }}
        closeOnClickOutside={!isMutating}
        closeOnEscape={!isMutating}
      >
        <FunctionForm
          key={editingFunction?.id ?? 'create'}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModals}
          initialData={editingFunction}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />
      </Modal>

      <Modal
        opened={openedDeleteModal}
        onClose={handleCloseModals}
        title="Подтверждение удаления"
        size="sm"
         overlayProps={{
           backgroundOpacity: 0.55,
           blur: 3,
        }}
        closeOnClickOutside={!isMutating}
        closeOnEscape={!isMutating}
      >
        <Text size="sm">
          Вы уверены, что хотите удалить функцию "{deletingFunction?.name}"? Это действие необратимо.
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
    </Box>
  );
};

export default FunctionsPage; 