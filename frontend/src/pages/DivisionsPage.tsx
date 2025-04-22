import { useState } from "react";
import {
  Button,
  Group,
  Modal,
  Text,
  Box,
  Table,
  Loader,
  Alert,
} from "@mantine/core";
import { IconPlus, IconAlertCircle } from "@tabler/icons-react";
import { SectionForm } from "../features/sections/components/SectionForm";
import {
  useDivisions,
} from "../features/divisions/api/divisionApi";
import { useSections, useDeleteSection } from "../features/sections/api/sectionApi";
import { Section } from "../types/section";

export default function DivisionsPage() {
  // Модальные окна
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [sectionToEdit, setSectionToEdit] = useState<Section | undefined>(undefined);
  const [sectionToDelete, setSectionToDelete] = useState<Section | undefined>(undefined);

  // Получение данных
  const { data: allDivisions = [], refetch: refetchDivisions } = useDivisions();
  const { 
    data: sections = [],
    refetch: refetchSections,
    isLoading: isLoadingSections,
    isError: isErrorSections
  } = useSections(null);
  const deleteSectionMutation = useDeleteSection();

  // Обновление данных
  const handleRefresh = () => {
    refetchDivisions();
    refetchSections();
  };

  // Редактирование
  const handleEditClick = (section: Section) => {
    setSectionToEdit(section);
    setEditModalOpen(true);
  };

  // Удаление
  const handleDeleteClick = (section: Section) => {
    setSectionToDelete(section);
    setDeleteConfirmOpen(true);
  };

  // Подтверждение удаления
  const handleConfirmDelete = async () => {
    if (sectionToDelete) {
      try {
        await deleteSectionMutation.mutateAsync(sectionToDelete.id);
        setDeleteConfirmOpen(false);
        setSectionToDelete(undefined);
        handleRefresh();
      } catch (error) {
        console.error("Ошибка при удалении отдела:", error);
      }
    }
  };

  return (
    <Box p="md">
      <Group justify="space-between" mb="lg">
        <Button 
          leftSection={<IconPlus size={16} />} 
          onClick={() => setCreateModalOpen(true)}
          size="md"
          color="indigo"
        >
          Создать отдел
        </Button>
      </Group>

      {isLoadingSections && <Group justify="center" p="lg"><Loader /></Group>}
      {isErrorSections && 
        <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка загрузки отделов" color="red" mb="md">
          Не удалось загрузить список отделов. Попробуйте обновить страницу.
        </Alert>
      }

      {!isLoadingSections && !isErrorSections && (
        <Box mt="md">
          {sections.length === 0 ? (
            <Text ta="center" c="dimmed" py="md">Отделы не найдены</Text>
          ) : (
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Название</Table.Th>
                  <Table.Th>Код</Table.Th>
                  <Table.Th>Департамент</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th>Действия</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {sections.map((section) => {
                  const parentDept = allDivisions.find(d => d.id === section.division_id);
                  return (
                    <Table.Tr key={section.id}>
                      <Table.Td>{section.name}</Table.Td>
                      <Table.Td>{section.code}</Table.Td>
                      <Table.Td>{parentDept ? parentDept.name : '-'}</Table.Td>
                      <Table.Td>
                        <Box style={{
                          background: section.is_active ? '#2B8A3E' : 'grey',
                          color: 'white',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          display: 'inline-block',
                          fontSize: '12px',
                          fontWeight: 'bold',
                          textTransform: 'uppercase'
                        }}>
                          {section.is_active ? 'Активна' : 'Неактивна'}
                        </Box>
                      </Table.Td>
                      <Table.Td>
                        <Group gap={0} justify="flex-end">
                          <Button variant="subtle" size="xs" onClick={() => handleEditClick(section)}>Edit</Button>
                          <Button variant="subtle" size="xs" color="red" onClick={() => handleDeleteClick(section)}>Del</Button>
                        </Group>
                      </Table.Td>
                    </Table.Tr>
                  );
                })}
              </Table.Tbody>
            </Table>
          )}
        </Box>
      )}

      <Modal
        opened={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Создать отдел"
        size="md"
      >
        <SectionForm 
          onSuccess={() => {
            setCreateModalOpen(false);
            handleRefresh();
          }}
        />
      </Modal>

      <Modal
        opened={editModalOpen}
        onClose={() => {
          setEditModalOpen(false);
          setSectionToEdit(undefined);
        }}
        title="Редактировать отдел"
        size="md"
      >
        {sectionToEdit && (
          <SectionForm
            sectionToEdit={sectionToEdit}
            onSuccess={() => {
              setEditModalOpen(false);
              setSectionToEdit(undefined);
              handleRefresh();
            }}
          />
        )}
      </Modal>

      <Modal
        opened={deleteConfirmOpen}
        onClose={() => {
          setDeleteConfirmOpen(false);
          setSectionToDelete(undefined);
        }}
        title="Подтвердите удаление"
        size="sm"
      >
        <Text mb="md">Вы уверены, что хотите удалить отдел "{sectionToDelete?.name}"?</Text>
        <Group justify="flex-end">
          <Button variant="outline" onClick={() => setDeleteConfirmOpen(false)}>
            Отмена
          </Button>
          <Button color="red" onClick={handleConfirmDelete} loading={deleteSectionMutation.isPending}>
            Удалить
          </Button>
        </Group>
      </Modal>
    </Box>
  );
} 