import { Table, ActionIcon, Menu, Badge } from '@mantine/core';
import { IconEdit, IconTrash, IconDotsVertical, IconBuildingCommunity, IconEye } from '@tabler/icons-react';
import { Organization } from '@/types/organization';
import { Link } from 'react-router-dom';

interface OrganizationTableProps {
  organizations: Organization[];
  onEdit: (organization: Organization) => void;
  onDelete: (id: number) => void;
  onViewDetails?: (id: number) => void;
}

export const OrganizationTable = ({ 
  organizations, 
  onEdit, 
  onDelete,
  onViewDetails
}: OrganizationTableProps) => {
  // Функция для получения строкового представления типа организации
  const getOrgTypeLabel = (type: string) => {
    switch (type) {
      case 'HOLDING': return 'Холдинг';
      case 'LEGAL_ENTITY': return 'Юридическое лицо';
      case 'LOCATION': return 'Локация';
      default: return type;
    }
  };

  // Функция для получения имени родительской организации
  const getParentName = (org: Organization) => {
    const parentId = org.parent_id;
    if (!parentId) return '-';
    
    // Ищем родительскую организацию в списке
    const parent = organizations.find(o => o.id === parentId);
    return parent ? parent.name : '-';
  };

  return (
    <Table striped highlightOnHover>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>Название</Table.Th>
          <Table.Th>Код</Table.Th>
          <Table.Th>Тип</Table.Th>
          <Table.Th>Родитель</Table.Th>
          <Table.Th>Статус</Table.Th>
          <Table.Th style={{ width: '80px' }}>Действия</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {organizations.map((org) => (
          <Table.Tr key={org.id}>
            <Table.Td>{org.name}</Table.Td>
            <Table.Td>{org.code}</Table.Td>
            <Table.Td>{getOrgTypeLabel(org.org_type)}</Table.Td>
            <Table.Td>{getParentName(org)}</Table.Td>
            <Table.Td>
              <Badge color={org.is_active ? 'green' : 'red'}>
                {org.is_active ? 'Активна' : 'Неактивна'}
              </Badge>
            </Table.Td>
            <Table.Td>
              <Menu position="bottom-end" withinPortal>
                <Menu.Target>
                  <ActionIcon variant="subtle">
                    <IconDotsVertical size="1rem" />
                  </ActionIcon>
                </Menu.Target>
                <Menu.Dropdown>
                  {onViewDetails && (
                    <Menu.Item 
                      leftSection={<IconEye size="1rem" />}
                      onClick={() => onViewDetails(org.id)}
                    >
                      Просмотреть
                    </Menu.Item>
                  )}
                  <Menu.Item 
                    leftSection={<IconBuildingCommunity size="1rem" />}
                    component={Link}
                    to={`/divisions/organization/${org.id}`}
                  >
                    Подразделения
                  </Menu.Item>
                  <Menu.Item 
                    leftSection={<IconEdit size="1rem" />}
                    onClick={() => onEdit(org)}
                  >
                    Редактировать
                  </Menu.Item>
                  <Menu.Item 
                    leftSection={<IconTrash size="1rem" />}
                    color="red"
                    onClick={() => onDelete(org.id)}
                  >
                    Удалить
                  </Menu.Item>
                </Menu.Dropdown>
              </Menu>
            </Table.Td>
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  );
}; 