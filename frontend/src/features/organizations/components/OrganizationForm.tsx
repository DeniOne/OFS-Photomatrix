import React from 'react';
import { Box, TextInput, Textarea, Checkbox, Button, Group, Stack } from '@mantine/core';
import { useForm } from '@mantine/form';
import { OrganizationCreateDto } from '../types/organizationTypes';
import { useCreateOrganization } from '../api/organizationApi';

type OrganizationFormProps = {
  onSuccess?: () => void;
  initialValues?: Partial<OrganizationCreateDto>; // Для предзаполнения формы (здесь org_type)
};

const OrganizationForm: React.FC<OrganizationFormProps> = ({ onSuccess, initialValues }) => {
  const createOrganizationMutation = useCreateOrganization();

  const form = useForm<OrganizationCreateDto>({ // Указываем тип для формы
    initialValues: {
      name: '',
      code: '',
      description: '',
      org_type: initialValues?.org_type || 'HOLDING', // Берем из пропсов или ставим HOLDING
      parent_id: null,
      is_active: true,
    },

    validate: {
      name: (value) => (value.trim().length > 0 ? null : 'Название обязательно'),
      code: (value) => (value.trim().length > 0 ? null : 'Код обязателен'),
      org_type: (value) => (value ? null : 'Тип организации обязателен'), // На всякий случай
    },
  });

  const handleSubmit = (values: OrganizationCreateDto) => {
    // Убедимся, что parent_id не передается для HOLDING
    const submissionData: OrganizationCreateDto = {
      ...values,
      parent_id: values.org_type === 'HOLDING' ? null : values.parent_id,
    };
    
    createOrganizationMutation.mutate(submissionData, {
        onSuccess: () => {
            form.reset(); // Сбрасываем форму
            onSuccess?.(); // Вызываем колбэк (закрытие модалки)
        }
    });
  };

  return (
    <Box component="form" onSubmit={form.onSubmit(handleSubmit)}>
      <Stack gap="md">
        <TextInput
          label="Название"
          placeholder="Введите название организации"
          required
          {...form.getInputProps('name')}
        />
        <TextInput
          label="Код"
          placeholder="Введите уникальный код (идентификатор)"
          required
          {...form.getInputProps('code')}
        />
        <Textarea
          label="Описание"
          placeholder="Введите описание"
          {...form.getInputProps('description')}
        />
        
        {/* Для Холдинга parent_id не нужен, org_type задан */}
        {/* <TextInput label="Тип" {...form.getInputProps('org_type')} disabled /> */}

        <Checkbox
          label="Активна"
          mt="sm"
          {...form.getInputProps('is_active', { type: 'checkbox' })}
        />
        
        <Group justify="flex-end" mt="lg">
          <Button 
            type="submit" 
            loading={createOrganizationMutation.isPending} // Показываем лоадер при отправке
          >
            Создать Холдинг
          </Button>
        </Group>
      </Stack>
    </Box>
  );
};

export default OrganizationForm; 