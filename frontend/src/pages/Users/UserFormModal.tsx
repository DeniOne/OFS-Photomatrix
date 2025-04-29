import React, { useEffect } from 'react';
import { Modal, TextInput, Button, Stack, Checkbox, PasswordInput, Group } from '@mantine/core';
import { useForm, zodResolver } from '@mantine/form';
import { z } from 'zod';
import { User, UserCreate, UserUpdate } from '@/types/user';
import { useCreateUser, useUpdateUser } from '@/hooks/users';

interface UserFormModalProps {
  opened: boolean;
  onClose: () => void;
  user: User | null; // null для создания, User для редактирования
}

// Схема валидации Zod
const userSchema = z.object({
  email: z.string().email({ message: 'Неверный формат email' }),
  full_name: z.string().min(1, { message: 'ФИО не может быть пустым' }).optional().or(z.literal('')),
  password: z.string().min(8, { message: 'Пароль должен быть не менее 8 символов' }).optional().or(z.literal('')),
  is_active: z.boolean(),
  is_superuser: z.boolean(),
});

const UserFormModal: React.FC<UserFormModalProps> = ({ opened, onClose, user }) => {
  const isEditing = !!user;
  const createUserMutation = useCreateUser();
  const updateUserMutation = useUpdateUser();

  const form = useForm<Partial<UserCreate & UserUpdate>>({
    // Используем Partial, т.к. не все поля обязательны при обновлении/создании
    // и пароль может отсутствовать
    mode: 'uncontrolled',
    initialValues: {
      email: '',
      full_name: '',
      password: '',
      is_active: true,
      is_superuser: false,
    },
    validate: zodResolver(userSchema),
  });

  // Заполняем форму данными при редактировании
  useEffect(() => {
    if (user && opened) {
      form.setValues({
        email: user.email,
        full_name: user.full_name || '',
        is_active: user.is_active,
        is_superuser: user.is_superuser,
        password: '' // Пароль не загружаем для редактирования
      });
    } else if (!opened) {
      form.reset(); // Сбрасываем форму при закрытии
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, opened]); // Не добавляем form в зависимости

  const handleSubmit = (values: Partial<UserCreate & UserUpdate>) => {
    const mutationData = { ...values };
    // Удаляем поле пароля, если оно пустое
    if (!mutationData.password) {
      delete mutationData.password;
    }

    if (isEditing && user) {
      updateUserMutation.mutate(
        { id: user.id, userData: mutationData as UserUpdate },
        {
          onSuccess: () => {
            onClose(); // Закрываем модалку при успехе
          },
        }
      );
    } else {
      createUserMutation.mutate(mutationData as UserCreate, {
        onSuccess: () => {
          onClose(); // Закрываем модалку при успехе
        },
      });
    }
  };

  const isLoading = createUserMutation.isPending || updateUserMutation.isPending;

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={isEditing ? 'Редактировать пользователя' : 'Добавить пользователя'}
      overlayProps={{
          backgroundOpacity: 0.55,
          blur: 3,
        }}
    >
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          <TextInput
            required
            label="Email"
            placeholder="user@example.com"
            key={form.key('email')}
            {...form.getInputProps('email')}
          />
          <TextInput
            label="ФИО"
            placeholder="Иванов Иван Иванович"
            key={form.key('full_name')}
            {...form.getInputProps('full_name')}
          />
          <PasswordInput
            label={isEditing ? "Новый пароль (если нужно изменить)" : "Пароль"}
            placeholder="********"
            key={form.key('password')}
            {...form.getInputProps('password')}
            // Обязательно только при создании, если хотим задать пароль сразу
            // required={!isEditing} 
          />
          <Checkbox
            label="Активен"
            key={form.key('is_active')}
            {...form.getInputProps('is_active', { type: 'checkbox' })}
          />
          <Checkbox
            label="Администратор (Superuser)"
            key={form.key('is_superuser')}
            {...form.getInputProps('is_superuser', { type: 'checkbox' })}
          />
          <Group justify="flex-end" mt="md">
             <Button variant="default" onClick={onClose} disabled={isLoading}>
               Отмена
             </Button>
             <Button type="submit" loading={isLoading}>
              {isEditing ? 'Сохранить изменения' : 'Создать пользователя'}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
};

export default UserFormModal; 