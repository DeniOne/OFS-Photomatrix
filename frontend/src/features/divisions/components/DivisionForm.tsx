import { useEffect, useState } from 'react';
import { Button, TextInput, Select, Textarea, Switch, Box, LoadingOverlay, Group, Stack, SegmentedControl, Text } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { useForm, zodResolver } from '@mantine/form';
import { z } from 'zod';
import { Division, DivisionCreate, DivisionType } from '../../../types/division';
import { useCreateDivision, useUpdateDivision } from '../api/divisionApi';
import { useOrganizations } from '../../organizations/api/organizationApi';

// Префиксы для кодов подразделений
const DEPARTMENT_PREFIX = 'DEP_';
const DIVISION_PREFIX = 'OTD_';

// Схема валидации для формы подразделения
const divisionSchema = z.object({
  name: z.string().min(1, 'Название обязательно').max(100, 'Название слишком длинное'),
  code: z.string().min(1, 'Код обязательно').max(50, 'Код слишком длинный')
    .regex(/^[A-Za-z0-9_-]+$/, 'Код должен содержать только буквы, цифры, дефис и подчеркивание'),
  description: z.string().max(500, 'Описание слишком длинное').optional(),
  organization_id: z.number().nullable(),
  parent_id: z.number().nullable().optional(),
  is_active: z.boolean().default(true),
  type: z.enum([DivisionType.DEPARTMENT, DivisionType.DIVISION]),
});

interface DivisionFormProps {
  divisionToEdit?: Division;
  organizationId?: number | null;
  parentId?: number | null;
  onSuccess?: () => void;
  availableParents?: Division[];
  defaultType?: DivisionType;
}

export function DivisionForm({ 
  divisionToEdit, 
  organizationId, 
  parentId, 
  onSuccess, 
  availableParents = [],
  defaultType = DivisionType.DEPARTMENT 
}: DivisionFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { data: organizations = [] } = useOrganizations();
  const createDivision = useCreateDivision();
  const updateDivision = useUpdateDivision();

  const [showParentField, setShowParentField] = useState(defaultType === DivisionType.DIVISION);

  // Находим организацию типа HOLDING (Фотоматрица)
  const holdingOrganization = organizations.find(org => org.org_type === 'HOLDING');

  // Автоматически используем ID холдинга если он доступен
  const defaultOrganizationId = organizationId || (holdingOrganization?.id || null);

  // Получаем начальный префикс на основе типа
  const getInitialPrefix = (type: DivisionType) => {
    return type === DivisionType.DEPARTMENT ? DEPARTMENT_PREFIX : DIVISION_PREFIX;
  };

  const form = useForm({
    initialValues: {
      name: '',
      code: getInitialPrefix(defaultType),
      description: '',
      organization_id: defaultOrganizationId,
      parent_id: parentId || null,
      is_active: true,
      type: defaultType,
    },
    validate: zodResolver(divisionSchema),
  });

  // Обработчик изменения значения поля кода с сохранением префикса
  const handleCodeChange = (value: string) => {
    if (divisionToEdit) {
      // Не меняем префикс при редактировании
      form.setFieldValue('code', value);
      return;
    }

    const currentPrefix = form.values.type === DivisionType.DEPARTMENT 
      ? DEPARTMENT_PREFIX 
      : DIVISION_PREFIX;
    
    if (!value.startsWith(currentPrefix)) {
      // Если пользователь пытается удалить префикс, восстанавливаем его
      form.setFieldValue('code', currentPrefix + value.replace(currentPrefix, ''));
    } else {
      form.setFieldValue('code', value);
    }
  };

  useEffect(() => {
    if (divisionToEdit) {
      form.setValues({
        name: divisionToEdit.name,
        code: divisionToEdit.code,
        description: divisionToEdit.description || '',
        organization_id: divisionToEdit.organization_id,
        parent_id: divisionToEdit.parent_id,
        is_active: divisionToEdit.is_active,
        type: divisionToEdit.type || defaultType,
      });
      setShowParentField(divisionToEdit.type === DivisionType.DIVISION);
    } else {
      form.setValues({
        name: '',
        code: getInitialPrefix(defaultType),
        description: '',
        organization_id: defaultOrganizationId,
        parent_id: parentId || null,
        is_active: true,
        type: defaultType,
      });
      setShowParentField(defaultType === DivisionType.DIVISION);
    }
  }, [divisionToEdit, defaultOrganizationId, parentId, defaultType]);

  const handleTypeChange = (value: DivisionType) => {
    form.setFieldValue('type', value);
    
    const isSection = value === DivisionType.DIVISION;
    setShowParentField(isSection);
    
    if (!isSection) {
      form.setFieldValue('parent_id', null);
    }

    // Если не редактируем существующее подразделение, меняем префикс при смене типа
    if (!divisionToEdit) {
      const newPrefix = isSection ? DIVISION_PREFIX : DEPARTMENT_PREFIX;
      const codeWithoutPrefix = form.values.code
        .replace(DEPARTMENT_PREFIX, '')
        .replace(DIVISION_PREFIX, '');
      form.setFieldValue('code', newPrefix + codeWithoutPrefix);
    }
  };

  const filteredAvailableParents = availableParents.filter(
    p => p.type === DivisionType.DEPARTMENT && 
    (!divisionToEdit || p.id !== divisionToEdit.id)
  );

  const handleSubmit = async (values: typeof form.values) => {
    try {
      setIsSubmitting(true);
      
      // Проверяем, что код содержит что-то помимо префикса
      const prefix = values.type === DivisionType.DEPARTMENT 
        ? DEPARTMENT_PREFIX 
        : DIVISION_PREFIX;
      
      if (!divisionToEdit && values.code === prefix) {
        form.setFieldError('code', `Необходимо добавить код после префикса ${prefix}`);
        setIsSubmitting(false);
        return;
      }
      
      const finalValues = {
        ...values,
        parent_id: values.type === DivisionType.DEPARTMENT ? null : values.parent_id
      };
      
      const divisionData: DivisionCreate = {
        name: finalValues.name,
        code: finalValues.code,
        description: finalValues.description || undefined,
        organization_id: finalValues.organization_id!,
        parent_id: finalValues.parent_id,
        is_active: finalValues.is_active,
        type: finalValues.type,
      };

      if (divisionToEdit) {
        await updateDivision.mutateAsync({
          id: divisionToEdit.id,
          ...divisionData
        });
        notifications.show({
          title: 'Успешно!',
          message: divisionData.type === DivisionType.DEPARTMENT ? 
            'Департамент обновлен' : 'Отдел обновлен',
          color: 'green',
        });
      } else {
        await createDivision.mutateAsync(divisionData);
        form.reset();
        // Сбрасываем форму с правильным префиксом
        form.setFieldValue('code', getInitialPrefix(values.type));
        notifications.show({
          title: 'Успешно!',
          message: divisionData.type === DivisionType.DEPARTMENT ? 
            'Департамент создан' : 'Отдел создан',
          color: 'green',
        });
      }
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('Ошибка при сохранении подразделения:', error);
      notifications.show({
        title: 'Ошибка',
        message: 'Не удалось сохранить. Пожалуйста, попробуйте снова.',
        color: 'red',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Получаем текущий префикс на основе выбранного типа
  const currentPrefix = form.values.type === DivisionType.DEPARTMENT 
    ? DEPARTMENT_PREFIX 
    : DIVISION_PREFIX;

  return (
    <Box pos="relative">
      <LoadingOverlay visible={isSubmitting} />
      
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          <Box>
            <Text size="sm" fw={500} mb={5}>Тип подразделения</Text>
            <SegmentedControl
              data={[
                { label: 'Департамент', value: DivisionType.DEPARTMENT },
                { label: 'Отдел', value: DivisionType.DIVISION }
              ]}
              value={form.values.type}
              onChange={(value) => handleTypeChange(value as DivisionType)}
              disabled={isSubmitting || !!divisionToEdit}
              fullWidth
            />
          </Box>
          
          <TextInput
            label="Название"
            placeholder={`Введите название ${form.values.type === DivisionType.DEPARTMENT ? 'департамента' : 'отдела'}`}
            required
            {...form.getInputProps('name')}
            disabled={isSubmitting}
          />
          
          <TextInput
            label="Код"
            placeholder={`${currentPrefix}123`}
            description={`Код автоматически начинается с ${currentPrefix}`}
            required
            value={form.values.code}
            onChange={(e) => handleCodeChange(e.target.value)}
            error={form.errors.code || (form.values.code === currentPrefix && !divisionToEdit ? `Необходимо добавить код после префикса ${currentPrefix}` : '')}
            disabled={isSubmitting || !!divisionToEdit}
          />
          
          <Select
            label="Организация"
            placeholder="Выберите организацию"
            data={organizations.map(org => ({ value: String(org.id), label: org.name }))}
            required
            searchable
            value={form.values.organization_id ? String(form.values.organization_id) : null}
            onChange={(value) => form.setFieldValue('organization_id', value ? Number(value) : null)}
            disabled={isSubmitting || !!organizationId}
          />
          
          {showParentField && form.values.organization_id && (
            <Select
              label="Родительский департамент"
              placeholder="Выберите департамент"
              data={filteredAvailableParents.map(div => ({ value: String(div.id), label: div.name }))}
              searchable
              required={form.values.type === DivisionType.DIVISION}
              value={form.values.parent_id ? String(form.values.parent_id) : null}
              onChange={(value) => form.setFieldValue('parent_id', value ? Number(value) : null)}
              disabled={isSubmitting || !!parentId}
              error={form.values.type === DivisionType.DIVISION && !form.values.parent_id ? 
                'Для отдела необходимо выбрать родительский департамент' : undefined}
            />
          )}
          
          <Textarea
            label="Описание"
            placeholder={`Введите описание ${form.values.type === DivisionType.DEPARTMENT ? 'департамента' : 'отдела'}`}
            minRows={3}
            {...form.getInputProps('description')}
            disabled={isSubmitting}
          />
          
          <Switch
            label="Активно"
            checked={form.values.is_active}
            onChange={(event) => form.setFieldValue('is_active', event.currentTarget.checked)}
            disabled={isSubmitting}
          />
          
          <Group justify="flex-end">
            <Button type="submit" loading={isSubmitting}>
              {divisionToEdit ? 'Сохранить' : 'Создать'}
            </Button>
          </Group>
        </Stack>
      </form>
    </Box>
  );
} 