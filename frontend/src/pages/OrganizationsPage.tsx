import { useState } from 'react';
import { Title, Button, Table, Loader, Alert, Modal, Box } from '@mantine/core';
import { IconPlus, IconAlertCircle } from '@tabler/icons-react';
import { useOrganizations } from '../features/organizations/api/organizationApi';
import OrganizationForm from '../features/organizations/components/OrganizationForm';

const OrganizationsPage = () => {
  const { data: organizations, isLoading, error, isError } = useOrganizations();
  const [modalOpened, setModalOpened] = useState(false);

  // TODO: Добавить обработку состояний (сортировка, пагинация, фильтры)
  // TODO: Добавить редактирование и удаление

  const rows = organizations?.map((org) => (
    <Table.Tr key={org.id}>
      <Table.Td>{org.id}</Table.Td>
      <Table.Td>{org.name}</Table.Td>
      <Table.Td>{org.code}</Table.Td>
      <Table.Td>{org.org_type}</Table.Td>
      <Table.Td>{org.parent_id || '-'}</Table.Td> 
      <Table.Td>{org.is_active ? 'Да' : 'Нет'}</Table.Td>
      {/* Добавить колонку с действиями (редактировать, удалить) */}
    </Table.Tr>
  ));

  return (
    <Box p="md">
      <Title order={2} mb="lg">Управление Организациями</Title>
      
      <Button 
        leftSection={<IconPlus size={14} />} 
        onClick={() => setModalOpened(true)}
        mb="md"
      >
        Создать Организацию
      </Button>

      {isLoading && <Loader />}

      {isError && (
        <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка!" color="red">
          Не удалось загрузить список организаций: {error?.message || 'Неизвестная ошибка'}
        </Alert>
      )}

      {!isLoading && !isError && organizations && (
        <Table striped highlightOnHover withTableBorder withColumnBorders>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Название</Table.Th>
              <Table.Th>Код</Table.Th>
              <Table.Th>Тип</Table.Th>
              <Table.Th>Родитель ID</Table.Th>
              <Table.Th>Активна</Table.Th>
              {/* <Table.Th>Действия</Table.Th> */}
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{rows}</Table.Tbody>
        </Table>
      )}
      
      {/* Модальное окно для создания/редактирования */}
      <Modal
        opened={modalOpened}
        onClose={() => setModalOpened(false)}
        title="Создать Организацию"
        size="lg"
      >
        <OrganizationForm 
          onSuccess={() => setModalOpened(false)} // Закрываем модалку при успехе
          // Передаем тип по умолчанию для создания Холдинга
          initialValues={{ org_type: 'HOLDING' }}
        />
      </Modal>

    </Box>
  );
};

export default OrganizationsPage; 