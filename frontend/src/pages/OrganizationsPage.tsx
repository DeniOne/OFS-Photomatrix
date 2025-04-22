import { useState } from 'react';
import { Button, Loader, Alert, Box, Group, Text, Modal } from '@mantine/core';
import { IconPlus, IconAlertCircle } from '@tabler/icons-react';
import { useOrganizations, useDeleteOrganization } from '../features/organizations/api/organizationApi';
import { Organization } from '@/types/organization';
import { OrganizationTable } from '@/features/organizations/components/OrganizationTable';
import OrganizationForm from '@/features/organizations/components/OrganizationForm';
import { formModalSettings, confirmModalSettings } from '@/config/modalSettings';
import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

const OrganizationsPage = () => {
  const { data: organizations, isLoading, error, isError } = useOrganizations();
  const deleteOrganizationMutation = useDeleteOrganization();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  
  const [formModalOpened, setFormModalOpened] = useState(false);
  const [selectedOrganization, setSelectedOrganization] = useState<Organization | null>(null);
  const [deleteModalOpened, setDeleteModalOpened] = useState(false);
  const [organizationToDelete, setOrganizationToDelete] = useState<number | null>(null);

  // Открыть модальное окно для создания/редактирования
  const openFormModal = (organization?: Organization) => {
    setSelectedOrganization(organization || null);
    setFormModalOpened(true);
  };

  // Открыть подтверждение удаления
  const openDeleteModal = (id: number) => {
    setOrganizationToDelete(id);
    setDeleteModalOpened(true);
  };

  // Подтвердить удаление
  const confirmDelete = () => {
    if (organizationToDelete !== null) {
      deleteOrganizationMutation.mutate(organizationToDelete, {
        onSuccess: () => {
          setDeleteModalOpened(false);
          setOrganizationToDelete(null);
        }
      });
    }
  };

  // Просмотр деталей организации
  const handleViewDetails = (id: number) => {
    navigate(`/organizations/${id}`);
  };

  return (
    <Box p="md">
      <Group justify="space-between" mb="lg">
        <Button 
          leftSection={<IconPlus size={16} />} 
          onClick={() => openFormModal()}
          size="md"
          color="indigo"
        >
          Создать организацию
        </Button>
      </Group>

      {isLoading && <Loader />}

      {isError && (
        <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка!" color="red">
          Не удалось загрузить список организаций: {error?.message || 'Неизвестная ошибка'}
        </Alert>
      )}

      {!isLoading && !isError && organizations && (
        <OrganizationTable 
          organizations={organizations} 
          onEdit={openFormModal} 
          onDelete={openDeleteModal}
          onViewDetails={handleViewDetails}
        />
      )}
      
      {/* Модальное окно для формы создания/редактирования */}
      <Modal
        opened={formModalOpened}
        onClose={() => setFormModalOpened(false)}
        title={selectedOrganization ? 'Редактирование организации' : 'Создание организации'}
        {...formModalSettings}
      >
        <OrganizationForm
          organizationToEdit={selectedOrganization} 
          onSuccess={() => {
            setFormModalOpened(false);
            queryClient.invalidateQueries({ queryKey: ['organizations'] });
          }} 
        />
      </Modal>

      {/* Модальное окно подтверждения удаления */}
      <Modal
        opened={deleteModalOpened}
        onClose={() => setDeleteModalOpened(false)}
        title="Подтверждение удаления"
        {...confirmModalSettings}
      >
        <Text mb="md">Вы уверены, что хотите удалить эту организацию?</Text>
        <Group justify="flex-end"> 
          <Button 
            variant="outline" 
            onClick={() => setDeleteModalOpened(false)}
          >
            Отмена
          </Button>
          <Button 
            color="red" 
            onClick={confirmDelete}
            loading={deleteOrganizationMutation.isPending}
          >
            Удалить
          </Button>
        </Group>
      </Modal>
    </Box>
  );
};

export default OrganizationsPage; 