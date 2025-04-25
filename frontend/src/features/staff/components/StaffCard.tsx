import React from 'react';
import {
  Paper, Text, Group, Avatar, Title, Stack, Grid, Badge, Divider,
  Button, ActionIcon, Box, Loader, Card, SimpleGrid
} from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { IconArrowLeft, IconEdit, IconTrash, IconDownload } from '@tabler/icons-react';
import { Staff } from '../../../types/staff';
import { DOCUMENT_TYPES } from './StaffForm';

// Константа с базовым URL API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Функция для формирования полного URL для файлов
const getFullFileUrl = (path: string | null | undefined): string | null => {
  if (!path) return null;
  
  // Если путь уже начинается с http или https, возвращаем его как есть
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  
  // Если путь начинается с /, предполагаем, что это относительный путь к API
  if (path.startsWith('/')) {
    return `${API_BASE_URL}${path}`;
  }
  
  return path;
};

interface StaffCardProps {
  staff: Staff | null;
  loading: boolean;
  onEdit: (staff: Staff) => void;
  onDelete: (id: number) => void;
  onDocumentDelete?: (staffId: number, docType: string) => void;
}

const StaffCard: React.FC<StaffCardProps> = ({
  staff,
  loading,
  onEdit,
  onDelete,
  onDocumentDelete
}) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <Box style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
        <Loader size="xl" />
      </Box>
    );
  }

  if (!staff) {
    return (
      <Paper p="md" withBorder>
        <Text ta="center">Сотрудник не найден</Text>
        <Button 
          leftSection={<IconArrowLeft size={16} />} 
          mt="md" 
          variant="outline" 
          onClick={() => navigate('/staff')}
        >
          Вернуться к списку
        </Button>
      </Paper>
    );
  }

  // Форматирование даты
  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'Не указана';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU');
    } catch {
      return dateString;
    }
  };

  // Получаем метку типа документа
  const getDocumentTypeLabel = (type: string) => {
    return DOCUMENT_TYPES.find((t: any) => t.value === type)?.label || type;
  };

  // Получаем инициалы для аватара
  const getInitials = (staff: Staff) => {
    const firstName = staff.first_name ? staff.first_name[0] : '';
    const lastName = staff.last_name ? staff.last_name[0] : '';
    return (firstName + lastName).toUpperCase();
  };

  return (
    <Paper p="md" withBorder>
      <Group justify="space-between" mb="md">
        <Group>
          <Button 
            leftSection={<IconArrowLeft size={16} />} 
            variant="subtle"
            onClick={() => navigate('/staff')}
          >
            К списку
          </Button>
          <Title order={2}>{staff.last_name} {staff.first_name} {staff.middle_name}</Title>
          {staff.is_active ? (
            <Badge color="green">Активен</Badge>
          ) : (
            <Badge color="red">Неактивен</Badge>
          )}
        </Group>
        <Group>
          <Button 
            leftSection={<IconEdit size={16} />} 
            onClick={() => onEdit(staff)}
          >
            Редактировать
          </Button>
          <ActionIcon 
            color="red" 
            variant="outline"
            onClick={() => onDelete(staff.id)}
          >
            <IconTrash size={18} />
          </ActionIcon>
        </Group>
      </Group>

      <Grid>
        <Grid.Col span={4}>
          <Avatar 
            src={getFullFileUrl(staff.photo_path) || undefined}
            alt={`${staff.last_name} ${staff.first_name}`}
            color="blue"
            size={250}
            radius="md"
            mx="auto"
            style={{ display: 'block' }}
          >
            {getInitials(staff)}
          </Avatar>
        </Grid.Col>
        <Grid.Col span={8}>
          <Stack gap="xs">
            <Title order={3}>Основная информация</Title>
            <Group>
              <Text fw={700}>Email:</Text>
              <Text>{staff.email || 'Не указан'}</Text>
            </Group>
            <Group>
              <Text fw={700}>Телефон:</Text>
              <Text>{staff.phone || 'Не указан'}</Text>
            </Group>
            <Group>
              <Text fw={700}>Дата приема на работу:</Text>
              <Text>{formatDate(staff.hire_date)}</Text>
            </Group>
            <Group>
              <Text fw={700}>Учетная запись:</Text>
              <Text>
                {staff.user_id 
                  ? `Привязана (ID: ${staff.user_id})` 
                  : 'Не создана'}
              </Text>
            </Group>
          </Stack>
        </Grid.Col>
      </Grid>

      {staff.document_paths && Object.keys(staff.document_paths).length > 0 && (
        <>
          <Divider my="md" />
          <Title order={3} mb="md">Документы</Title>
          <SimpleGrid cols={3}>
            {Object.entries(staff.document_paths).map(([type, path]) => (
              <Card key={type} withBorder p="sm">
                <Card.Section p="sm" bg="blue.0">
                  <Group justify="space-between">
                    <Badge size="lg">{getDocumentTypeLabel(type)}</Badge>
                    <ActionIcon 
                      color="red" 
                      variant="subtle"
                      onClick={() => onDocumentDelete && onDocumentDelete(staff.id, type)}
                    >
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Group>
                </Card.Section>
                <Text size="sm" mt="xs" mb="xs" truncate>
                  {path.split('/').pop()}
                </Text>
                <Button 
                  fullWidth
                  leftSection={<IconDownload size={16} />}
                  component="a"
                  href={getFullFileUrl(path) || ''}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Скачать
                </Button>
              </Card>
            ))}
          </SimpleGrid>
        </>
      )}
    </Paper>
  );
};

export default StaffCard; 