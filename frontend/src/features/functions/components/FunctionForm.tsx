import React, { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { TextInput, Textarea, Select, Checkbox, Button, Stack, Group, LoadingOverlay, Alert, Box } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';

import { Function, FunctionCreate, FunctionUpdate } from '../../../types/function';
import { Section } from '../../../types/section';
// Используем хук для загрузки секций
import { useSections } from '../../../features/sections/api/sectionApi';

// Схема валидации Zod
const functionSchema = z.object({
  name: z.string().min(1, 'Название обязательно'),
  code: z.string().min(1, 'Код обязателен'),
  section_id: z.string().min(1, 'Секция обязательна'), // Используем string, т.к. Select возвращает string
  description: z.string().nullable().optional(),
  is_active: z.boolean(),
});

// Тип для данных формы
type FunctionFormData = z.infer<typeof functionSchema>;

// Пропсы компонента
interface FunctionFormProps {
  onSubmit: (data: FunctionCreate | FunctionUpdate) => void;
  onCancel: () => void;
  initialData?: Function | null; // Данные для редактирования
  isLoading?: boolean; // Состояние загрузки для внешнего управления (например, при сабмите)
}

const FunctionForm: React.FC<FunctionFormProps> = ({
  onSubmit,
  onCancel,
  initialData = null,
  isLoading = false,
}) => {
  // Загружаем все секции, передавая null, чтобы не фильтровать по division_id
  // enabled: true - чтобы хук выполнил запрос даже с null
  const {
    data: sections = [], // Дефолт - пустой массив, чтобы избежать undefined
    isLoading: isLoadingSections,
    isError: isErrorSections,
    error: sectionsError,
  } = useSections(null);

  // Настройка react-hook-form
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FunctionFormData>({
    resolver: zodResolver(functionSchema),
    defaultValues: {
      name: initialData?.name || '',
      code: initialData?.code || '',
      section_id: initialData?.section_id?.toString() || '', // Преобразуем в строку для Select
      description: initialData?.description || '',
      is_active: initialData?.is_active ?? true, // По умолчанию активна
    },
  });

  // Сброс формы при изменении initialData (для редактирования)
  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        code: initialData.code,
        section_id: initialData.section_id.toString(),
        description: initialData.description || '',
        is_active: initialData.is_active,
      });
    } else {
      // Сброс к значениям по умолчанию при создании
      reset({
        name: '',
        code: '',
        section_id: '',
        description: '',
        is_active: true,
      });
    }
  }, [initialData, reset]);

  // Обработчик отправки формы
  const handleFormSubmit = (formData: FunctionFormData) => {
    const dataToSubmit: FunctionCreate | FunctionUpdate = {
      ...formData,
      section_id: parseInt(formData.section_id, 10), // Преобразуем ID секции обратно в число
      description: formData.description || null, // Убедимся, что пустое описание - null
    };
    onSubmit(dataToSubmit);
  };

  // Формирование опций для Select
  const sectionOptions = sections.map((section) => ({
    value: section.id.toString(),
    label: section.name,
  }));

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <div style={{ position: 'relative' }}>
        <LoadingOverlay visible={isLoading || isSubmitting || isLoadingSections} overlayProps={{ radius: 'sm', blur: 2 }} />
        <Stack gap="md">
          {isErrorSections && (
            <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка загрузки секций" color="red">
              Не удалось загрузить список секций: {sectionsError?.message || 'Неизвестная ошибка'}
            </Alert>
          )}

          <Controller
            name="name"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="Название функции"
                placeholder="Введите название"
                required
                error={errors.name?.message}
              />
            )}
          />

          <Controller
            name="code"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="Код функции"
                placeholder="Введите уникальный код"
                required
                error={errors.code?.message}
              />
            )}
          />

          <Controller
            name="section_id"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                label="Секция"
                placeholder={isLoadingSections ? "Загрузка..." : "Выберите секцию"}
                data={sectionOptions}
                required
                searchable
                nothingFoundMessage="Секции не найдены"
                disabled={isLoadingSections || isErrorSections}
                error={errors.section_id?.message}
              />
            )}
          />

          <Controller
            name="description"
            control={control}
            render={({ field }) => (
              <Textarea
                {...field}
                value={field.value ?? ''} // Убедимся, что значение не null/undefined
                label="Описание"
                placeholder="Добавьте описание (необязательно)"
                minRows={3}
              />
            )}
          />

          <Controller
            name="is_active"
            control={control}
            render={({ field }) => (
              <Checkbox
                label="Активна"
                checked={field.value}
                onChange={(event) => field.onChange(event.currentTarget.checked)}
                onBlur={field.onBlur}
                name={field.name}
              />
            )}
          />

          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={onCancel} disabled={isLoading || isSubmitting}>
              Отмена
            </Button>
            <Button type="submit" loading={isLoading || isSubmitting}>
              {initialData ? 'Сохранить изменения' : 'Создать функцию'}
            </Button>
          </Group>
        </Stack>
      </div>
    </form>
  );
};

export default FunctionForm; 