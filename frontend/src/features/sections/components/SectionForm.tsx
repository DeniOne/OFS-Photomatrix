import { useEffect, useState, useMemo } from 'react';
import { Button, TextInput, Select, Textarea, Switch, Box, LoadingOverlay, Group, Stack } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { useForm, zodResolver } from '@mantine/form';
import { z } from 'zod';
import { Section, SectionCreate, SectionUpdate } from '../../../types/section'; // Типы для Section
import { Division, DivisionType } from '../../../types/division'; // Типы для Division (нужен DivisionType)
import { useCreateSection, useUpdateSection } from '../api/sectionApi'; // API для Section
import { useDivisions } from '../../divisions/api/divisionApi'; // API для Division (для списка департаментов)

// Схема валидации для формы Отдела
const sectionSchema = z.object({
  name: z.string().min(1, 'Название обязательно').max(255, 'Название слишком длинное'),
  code: z.string().min(1, 'Код обязательно').max(50, 'Код слишком длинный')
    .regex(/^[A-Za-z0-9_-]+$/, 'Код должен содержать только буквы, цифры, дефис и подчеркивание'),
  division_id: z.coerce.number().positive({ message: 'Необходимо выбрать департамент' }), // Родительский департамент
  description: z.string().max(500, 'Описание слишком длинное').nullable().optional(),
  is_active: z.boolean().default(true),
});

interface SectionFormProps {
  sectionToEdit?: Section;
  divisionId?: number | null; // Можно предустановить департамент
  onSuccess?: () => void;
}

export function SectionForm({
  sectionToEdit,
  divisionId, // Принимаем предустановленный ID департамента
  onSuccess,
}: SectionFormProps) {
  // const [isSubmitting, setIsSubmitting] = useState(false); // Будет isPending из мутаций
  const createSection = useCreateSection();
  const updateSection = useUpdateSection();

  // Загружаем список всех подразделений для выбора родительского департамента
  const { data: allDivisions = [], isLoading: isLoadingDivisions } = useDivisions();

  // Фильтруем только департаменты
  const departments = useMemo(() =>
    allDivisions.filter(d => d.type === DivisionType.DEPARTMENT),
  [allDivisions]);

  const departmentsData = useMemo(() =>
    departments.map(d => ({ value: d.id.toString(), label: d.name })),
  [departments]);

  // Общий статус загрузки/отправки
  const isProcessing = createSection.isPending || updateSection.isPending || isLoadingDivisions;

  const form = useForm({
    initialValues: {
      name: '',
      code: '',
      division_id: divisionId?.toString() || '', // Устанавливаем, если передан
      description: '',
      is_active: true,
    },
    validate: zodResolver(sectionSchema),
  });

  // Заполняем форму данными, если редактируем
  useEffect(() => {
    if (sectionToEdit) {
      form.setValues({
        name: sectionToEdit.name,
        code: sectionToEdit.code,
        division_id: sectionToEdit.division_id.toString(),
        description: sectionToEdit.description || '',
        is_active: sectionToEdit.is_active,
      });
    } else {
      // Устанавливаем division_id если он передан, но не редактируем
      form.setFieldValue('division_id', divisionId?.toString() || '');
    }
    // Сбрасываем ошибки при изменении редактируемого объекта или divisionId
    form.clearErrors();
  }, [sectionToEdit, divisionId]); // Убрали form из зависимостей

  const handleSubmit = async (values: z.infer<typeof sectionSchema>) => {
    // values уже содержит division_id как number благодаря zod

    const sectionData: SectionCreate | SectionUpdate = {
        name: values.name,
        code: values.code,
        division_id: values.division_id, // Уже number
        description: values.description || null,
        is_active: values.is_active,
    };

    try {
      if (sectionToEdit) {
        await updateSection.mutateAsync({
          id: sectionToEdit.id,
          data: sectionData as SectionUpdate, // Указываем тип явно
        });
        notifications.show({
          title: 'Успешно!',
          message: 'Отдел обновлен',
          color: 'green',
        });
      } else {
        await createSection.mutateAsync(sectionData as SectionCreate); // Указываем тип явно
        notifications.show({
          title: 'Успешно!',
          message: 'Отдел создан',
          color: 'green',
        });
        form.reset(); // Сбрасываем только при создании
        // Восстанавливаем division_id, если он был передан
        form.setFieldValue('division_id', divisionId?.toString() || '');
      }

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('Ошибка при сохранении отдела:', error);
      notifications.show({
        title: 'Ошибка',
        message: error instanceof Error ? error.message : 'Не удалось сохранить отдел.',
        color: 'red',
      });
    }
  };

  return (
    <Box pos="relative">
      <LoadingOverlay visible={isProcessing} />

      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          <TextInput
            label="Название отдела"
            placeholder="Введите название отдела"
            required
            {...form.getInputProps('name')}
            disabled={isProcessing}
          />

          <TextInput
            label="Код отдела"
            placeholder="Например: SALE_DEPT"
            required
            {...form.getInputProps('code')}
            disabled={isProcessing}
          />

          <Select
            label="Родительский департамент"
            placeholder="Выберите департамент"
            data={departmentsData}
            required
            searchable
            disabled={isProcessing || !!divisionId} // Блокируем, если ID департамента передан снаружи
            {...form.getInputProps('division_id')}
            error={form.errors.division_id} // Показываем ошибку валидации
          />

          <Textarea
            label="Описание"
            placeholder="Введите описание отдела"
            minRows={3}
            {...form.getInputProps('description')}
            disabled={isProcessing}
          />

          <Switch
            label="Активен"
            {...form.getInputProps('is_active', { type: 'checkbox' })}
            disabled={isProcessing}
          />

          <Group justify="flex-end">
            <Button type="submit" loading={isProcessing}>
              {sectionToEdit ? 'Сохранить' : 'Создать отдел'}
            </Button>
          </Group>
        </Stack>
      </form>
    </Box>
  );
} 