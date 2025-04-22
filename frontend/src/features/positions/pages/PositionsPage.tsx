import React, { useState, useMemo } from 'react';
import { Box, Title, Button, Group, Modal, Text, Alert } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { IconPlus, IconAlertCircle } from '@tabler/icons-react';

import { PositionsTable } from '../components/PositionsTable';
import PositionForm from '../components/PositionForm';
import { Position } from '../../../types/position';
import { usePositions, useCreatePosition, useUpdatePosition, useDeletePosition } from '../api/positionApi.tsx';
import { useSections } from '../../sections/api/sectionApi';

const PositionsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [openedFormModal, { open: openFormModal, close: closeFormModal }] = useDisclosure(false);
  const [openedDeleteModal, { open: openDeleteModal, close: closeDeleteModal }] = useDisclosure(false);

  const [editingPosition, setEditingPosition] = useState<Position | null>(null);
  const [deletingPosition, setDeletingPosition] = useState<Position | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sectionFilter, setSectionFilter] = useState<number | null>(null);

  // Получаем данные о должностях
  const { 
    data: positionsData, 
    isLoading: isLoadingPositions, 
    isError: isErrorPositions,
    error: positionsError
  } = usePositions(sectionFilter);

  // Получаем данные об отделах для фильтра
  const { data: sectionsData = [] } = useSections(null);

  // Мутации для CRUD операций
  const createMutation = useCreatePosition();
  const updateMutation = useUpdatePosition();
  const deleteMutation = useDeletePosition();

  // Опции отделов для фильтра
  const sectionOptions = useMemo(() => {
    return sectionsData.map(section => ({
      value: String(section.id),
      label: `${section.name} (${section.division?.name || 'Нет подразделения'})`,
    }));
  }, [sectionsData]);

  // Закрытие всех модальных окон
  const handleCloseModals = () => {
    closeFormModal();
    closeDeleteModal();
    setEditingPosition(null);
    setDeletingPosition(null);
  };

  // Открытие формы создания
  const handleOpenCreateModal = () => {
    setEditingPosition(null);
    openFormModal();
  };

  // Открытие формы редактирования
  const handleOpenEditModal = (position: Position) => {
    setEditingPosition(position);
    openFormModal();
  };

  // Открытие модалки подтверждения удаления
  const handleOpenDeleteModal = (position: Position) => {
    setDeletingPosition(position);
    openDeleteModal();
  };

  // Обработка отправки формы
  const handleFormSubmit = (data: any) => {
    if (editingPosition) {
      updateMutation.mutate(
        { id: editingPosition.id, data },
        {
          onSuccess: () => {
            handleCloseModals();
          }
        }
      );
    } else {
      createMutation.mutate(
        data,
        {
          onSuccess: () => {
            handleCloseModals();
          }
        }
      );
    }
  };

  // Подтверждение удаления
  const handleConfirmDelete = () => {
    if (deletingPosition) {
      deleteMutation.mutate(deletingPosition.id);
    }
  };

  // Фильтрация должностей по поисковому запросу
  const filteredPositions = useMemo(() => {
    if (!positionsData) return [];
    if (!searchTerm) return positionsData;

    const lowerCaseSearchTerm = searchTerm.toLowerCase();
    return positionsData.filter(position => 
      position.name.toLowerCase().includes(lowerCaseSearchTerm) ||
      position.code.toLowerCase().includes(lowerCaseSearchTerm) ||
      (position.description && position.description.toLowerCase().includes(lowerCaseSearchTerm)) ||
      (position.attribute && position.attribute.toLowerCase().includes(lowerCaseSearchTerm)) ||
      (position.section?.name && position.section.name.toLowerCase().includes(lowerCaseSearchTerm))
    );
  }, [positionsData, searchTerm]);

  // Проверка, выполняется ли мутация
  const isMutating = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending;

  return (
    <Box>
      <Group mb="lg">
        <Button leftSection={<IconPlus size={14} />} onClick={handleOpenCreateModal}>
          Добавить должность
        </Button>
      </Group>

      {isErrorPositions && (
        <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка загрузки данных" color="red" mb="md">
          Не удалось загрузить список должностей: {positionsError?.message || 'Неизвестная ошибка'}
        </Alert>
      )}

      <PositionsTable
        data={filteredPositions}
        loading={isLoadingPositions}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        sectionFilter={sectionFilter}
        onSectionFilterChange={setSectionFilter}
        sections={sectionOptions}
        onEdit={handleOpenEditModal}
        onDelete={handleOpenDeleteModal}
      />

      <Modal
        opened={openedFormModal}
        onClose={handleCloseModals}
        title={editingPosition ? 'Редактировать должность' : 'Создать новую должность'}
        size="lg"
        overlayProps={{
           backgroundOpacity: 0.55,
           blur: 3,
        }}
        closeOnClickOutside={!isMutating}
        closeOnEscape={!isMutating}
      >
        <PositionForm
          key={editingPosition?.id ?? 'create'}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModals}
          initialData={editingPosition}
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
          Вы уверены, что хотите удалить должность "{deletingPosition?.name}"? Это действие необратимо.
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

export default PositionsPage; 