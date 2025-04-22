import React, { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { TextInput, Textarea, Select, Checkbox, Button, Stack, Group, LoadingOverlay, Alert, Box } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';

import { Function, FunctionCreate, FunctionUpdate } from '../../../types/function';
import { Section } from '../../../types/section';
// Используем хук для загрузки отделов
import { useSections } from '../../../features/sections/api/sectionApi';

// Константа для префикса кода функции
const FUNCTION_PREFIX = 'FUN_';

// Схема валидации Zod
const functionSchema = z.object({
  name: z.string().min(1, 'Название обязательно'),
  code: z.string().min(1, 'Код обязателен'),
  section_id: z.string().min(1, 'Отдел обязателен'), // Используем string, т.к. Select возвращает string
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
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FunctionFormData>({
    resolver: zodResolver(functionSchema),
    defaultValues: {
      name: initialData?.name || '',
      code: initialData?.code || FUNCTION_PREFIX,
      section_id: initialData?.section_id?.toString() || '', // Преобразуем в строку для Select
      description: initialData?.description || '',
      is_active: initialData?.is_active ?? true, // По умолчанию активна
    },
  });

  // Отслеживаем текущее значение поля code
  const currentCode = watch('code');

  // Обработчик изменения поля кода для сохранения префикса
  const handleCodeChange = (value: string) => {
    if (initialData) {
      // При редактировании не меняем код
      return value;
    }
    
    // Для новой функции всегда сохраняем префикс
    if (!value.startsWith(FUNCTION_PREFIX)) {
      return FUNCTION_PREFIX + value.replace(FUNCTION_PREFIX, '');
    }
    return value;
  };

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
        code: FUNCTION_PREFIX,
        section_id: '',
        description: '',
        is_active: true,
      });
    }
  }, [initialData, reset]);

  // Обработчик отправки формы
  const handleFormSubmit = (formData: FunctionFormData) => {
    // Проверка на наличие символов после префикса
    if (!initialData && formData.code === FUNCTION_PREFIX) {
      // Устанавливаем ошибку, если код равен только префиксу
      setValue('code', FUNCTION_PREFIX, { shouldValidate: true });
      return;
    }
    
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

  // Валидация кода на наличие символов после префикса
  const validateCode = (value: string) => {
    if (!initialData && value === FUNCTION_PREFIX) {
      return 'Необходимо добавить код после префикса ' + FUNCTION_PREFIX;
    }
    return true;
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <div style={{ position: 'relative' }}>
        <LoadingOverlay visible={isLoading || isSubmitting || isLoadingSections} overlayProps={{ radius: 'sm', blur: 2 }} />
        <Stack gap="md">
          {isErrorSections && (
            <Alert icon={<IconAlertCircle size="1rem" />} title="Ошибка загрузки отделов" color="red">
              Не удалось загрузить список отделов: {sectionsError?.message || 'Неизвестная ошибка'}
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
            rules={{ validate: validateCode }}
            render={({ field }) => (
              <TextInput
                value={field.value}
                onChange={(e) => {
                  const newValue = handleCodeChange(e.target.value);
                  field.onChange(newValue);
                }}
                onBlur={field.onBlur}
                name={field.name}
                label="Код функции"
                placeholder={`${FUNCTION_PREFIX}123`}
                description="Код автоматически начинается с FUN_"
                required
                error={errors.code?.message}
                disabled={!!initialData}
              />
            )}
          />

          <Controller
            name="section_id"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                label="Отдел"
                placeholder={isLoadingSections ? "Загрузка..." : "Выберите отдел"}
                data={sectionOptions}
                required
                searchable
                nothingFoundMessage="Отделы не найдены"
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