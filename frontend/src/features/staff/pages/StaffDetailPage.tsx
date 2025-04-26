import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Modal } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconCheck } from '@tabler/icons-react';

import StaffCard from '../components/StaffCard';
import StaffForm from '../components/StaffForm';
import { 
  useStaff, 
  useUpdateStaff, 
  useDeleteStaff,
  useUploadStaffPhoto,
  useUploadStaffDocument,
  useDeleteStaffDocument
} from '../api/staffApi';

const StaffDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const staffId = id ? parseInt(id, 10) : 0;
  const navigate = useNavigate();
  
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  
  // Запрос данных о сотруднике
  const { 
    data: staff, 
    isLoading: isLoadingStaff, 
    isError: isErrorStaff,
    error: staffError
  } = useStaff(staffId);
  
  // Мутации
  const updateMutation = useUpdateStaff();
  const deleteMutation = useDeleteStaff();
  const uploadPhotoMutation = useUploadStaffPhoto();
  const uploadDocumentMutation = useUploadStaffDocument();
  const deleteDocumentMutation = useDeleteStaffDocument();
  
  // Обработчики
  const handleOpenEditModal = () => {
    setEditModalOpen(true);
  };
  
  const handleCloseEditModal = () => {
    setEditModalOpen(false);
  };
  
  const handleOpenDeleteModal = () => {
    setDeleteModalOpen(true);
  };
  
  const handleCloseDeleteModal = () => {
    setDeleteModalOpen(false);
  };
  
  const handleUpdate = (data: any) => {
    console.log("Отправка данных для обновления сотрудника:", data);
    updateMutation.mutate(
      { id: staffId, data },
      {
        onSuccess: () => {
          console.log("Сотрудник успешно обновлен");
          // Принудительно закрываем модальное окно
          handleCloseEditModal();
          // Принудительно обновляем страницу после небольшой задержки
          setTimeout(() => {
            window.location.reload();
          }, 500);
        },
        onError: (error) => {
          console.error("Ошибка при обновлении сотрудника:", error);
          notifications.show({
            title: 'Ошибка',
            message: `Не удалось обновить данные сотрудника: ${error.message}`,
            color: 'red',
          });
        }
      }
    );
  };
  
  const handleDelete = () => {
    deleteMutation.mutate(staffId, {
      onSuccess: () => {
        navigate('/staff');
        notifications.show({
          title: 'Успешно',
          message: 'Сотрудник удален',
          color: 'green',
          icon: <IconCheck />
        });
      }
    });
  };
  
  const handlePhotoUpload = (staffId: number, photo: File) => {
    uploadPhotoMutation.mutate({ staffId, photo });
  };
  
  const handleDocumentUpload = (staffId: number, document: File, docType: string) => {
    uploadDocumentMutation.mutate({ staffId, document, docType });
  };
  
  const handleDocumentDelete = (staffId: number, docType: string) => {
    deleteDocumentMutation.mutate({ staffId, docType });
  };
  
  return (
    <>
      <StaffCard
        staff={staff || null}
        loading={isLoadingStaff}
        onEdit={handleOpenEditModal}
        onDelete={handleOpenDeleteModal}
        onDocumentDelete={handleDocumentDelete}
      />
      
      {/* Модальное окно редактирования */}
      <Modal
        opened={editModalOpen}
        onClose={handleCloseEditModal}
        title="Редактировать сотрудника"
        size="lg"
      >
        <StaffForm
          initialData={staff || null}
          onSubmit={handleUpdate}
          onCancel={handleCloseEditModal}
          isLoading={updateMutation.isPending}
          onPhotoUpload={handlePhotoUpload}
          onDocumentUpload={handleDocumentUpload}
        />
      </Modal>
      
      {/* Модальное окно подтверждения удаления */}
      <Modal
        opened={deleteModalOpen}
        onClose={handleCloseDeleteModal}
        title="Подтверждение удаления"
        size="sm"
      >
        <p>Вы уверены, что хотите удалить этого сотрудника?</p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 20 }}>
          <button 
            onClick={handleCloseDeleteModal}
            style={{ padding: '8px 16px', border: '1px solid #ccc', borderRadius: 4, background: 'white', cursor: 'pointer' }}
          >
            Отмена
          </button>
          <button
            onClick={handleDelete}
            style={{ padding: '8px 16px', border: 'none', borderRadius: 4, background: 'red', color: 'white', cursor: 'pointer' }}
          >
            Удалить
          </button>
        </div>
      </Modal>
    </>
  );
};

export default StaffDetailPage; 