import React, { useEffect, useState } from 'react';
import { Box, TextInput, Textarea, Checkbox, Button, Group, Stack, Select, Alert } from '@mantine/core';
import { Organization } from '@/types/organization';
import { useCreateOrganization, useUpdateOrganization } from '../api/organizationApi';
import { IconAlertCircle, IconCheck } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';

type OrganizationFormProps = {
  onSuccess?: () => void;
  organizationToEdit?: Organization | null;
};

const OrganizationForm: React.FC<OrganizationFormProps> = ({ onSuccess, organizationToEdit }) => {
  const createOrganizationMutation = useCreateOrganization();
  const updateOrganizationMutation = useUpdateOrganization();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Форма
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [orgType, setOrgType] = useState<'HOLDING' | 'LEGAL_ENTITY' | 'LOCATION'>('HOLDING');
  const [description, setDescription] = useState('');
  const [isActive, setIsActive] = useState(true);
  
  // Заполнение формы при редактировании
  useEffect(() => {
    if (organizationToEdit) {
      setName(organizationToEdit.name);
      setCode(organizationToEdit.code);
      setOrgType(organizationToEdit.org_type);
      setDescription(organizationToEdit.description || '');
      setIsActive(organizationToEdit.is_active);
    }
  }, [organizationToEdit]);
  
  // Валидация
  const validateForm = () => {
    setError(null);
    
    if (!name.trim()) {
      setError('Название обязательно');
      return false;
    }
    
    if (!code.trim()) {
      setError('Код обязателен');
      return false;
    }
    
    if (!/^[A-Za-z0-9_-]+$/.test(code)) {
      setError('Код может содержать только латинские буквы, цифры, тире и подчеркивания');
      return false;
    }
    
    return true;
  };
  
  // Обработка отправки формы
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const formData = {
        name,
        code,
        org_type: orgType,
        description: description.trim() ? description : null,
        is_active: isActive,
        parent_id: orgType === 'HOLDING' ? null : null, // Пока не реализовано родительское поле
      };
      
      console.log('Submitting organization data:', formData);
      
      if (organizationToEdit) {
        await updateOrganizationMutation.mutateAsync({
          id: organizationToEdit.id,
          data: formData
        });
        
        notifications.show({
          title: 'Успех!',
          message: `Организация "${name}" успешно обновлена`,
          color: 'green',
          icon: <IconCheck size="1.1rem" />,
        });
        
        onSuccess?.();
      } else {
        await createOrganizationMutation.mutateAsync(formData);
        
        notifications.show({
          title: 'Успех!',
          message: `Организация "${name}" успешно создана`,
          color: 'green',
          icon: <IconCheck size="1.1rem" />,
        });
        
        // Очищаем форму
        setName('');
        setCode('');
        setOrgType('HOLDING');
        setDescription('');
        setIsActive(true);
        
        onSuccess?.();
      }
    } catch (error) {
      console.error('Form submission error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Неизвестная ошибка';
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <Box>
      <form onSubmit={handleSubmit}>
        {error && (
          <Alert 
            icon={<IconAlertCircle size="1rem" />} 
            title="Ошибка!" 
            color="red" 
            mb="md"
          >
            {error}
          </Alert>
        )}
        
        <Stack gap="md">
          <TextInput
            label="Название"
            placeholder="Введите название организации"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={isSubmitting}
            error={!name.trim() && 'Название обязательно'}
          />
          
          <TextInput
            label="Код"
            placeholder="Введите уникальный код (например, MAIN-HQ)"
            required
            value={code}
            onChange={(e) => setCode(e.target.value)}
            disabled={isSubmitting || !!organizationToEdit}
            error={!code.trim() && 'Код обязателен'}
          />
          
          <Select
            label="Тип организации"
            placeholder="Выберите тип"
            required
            data={[
              { value: 'HOLDING', label: 'Холдинг' },
              { value: 'LEGAL_ENTITY', label: 'Юридическое лицо' },
              { value: 'LOCATION', label: 'Локация' }
            ]}
            value={orgType}
            onChange={(val) => setOrgType(val as 'HOLDING' | 'LEGAL_ENTITY' | 'LOCATION')}
            disabled={isSubmitting || !!organizationToEdit}
          />
          
          <Textarea
            label="Описание"
            placeholder="Введите описание"
            autosize
            minRows={3}
            maxRows={5}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isSubmitting}
          />
          
          <Checkbox
            label="Активна"
            checked={isActive}
            onChange={(e) => setIsActive(e.currentTarget.checked)}
            disabled={isSubmitting}
          />
          
          <Group justify="flex-end" mt="md">
            <Button 
              type="submit" 
              loading={isSubmitting}
              size="md"
            >
              {organizationToEdit ? 'Сохранить' : 'Создать'}
            </Button>
          </Group>
        </Stack>
      </form>
    </Box>
  );
};

export default OrganizationForm; 