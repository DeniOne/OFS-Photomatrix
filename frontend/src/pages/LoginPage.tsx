// import React, { useState } from 'react'; // Убираем неиспользуемые импорты
import { useForm } from '@mantine/form';
import { TextInput, PasswordInput, Button, Title, Text, Container, Box, Center } from '@mantine/core';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/auth'; // Используем актуальную функцию login вместо loginUser
import { 
  useMantineTheme, 
  LoadingOverlay
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconX } from '@tabler/icons-react';

const LoginPage = () => {
  const navigate = useNavigate();
  const theme = useMantineTheme();

  // Форма для логина
  const form = useForm({
    initialValues: {
      email: '',
      password: '',
    },
    validate: {
      email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Неверный формат email'),
      password: (value) => (value.length < 1 ? 'Пароль не может быть пустым' : null),
    },
  });

  // Мутация для логина
  const mutation = useMutation({
    mutationFn: login,
    onSuccess: (token) => {
      console.log('Успешный вход, получен токен');
      notifications.show({
        title: 'Успех!',
        message: 'Вы успешно вошли в систему.',
        color: 'green',
        icon: <IconCheck />,
      });
      navigate('/dashboard'); // Перенаправляем на дашборд
    },
    onError: (error) => {
      console.error('Ошибка входа:', error);
      notifications.show({
        title: 'Ошибка входа!',
        message: error.message, // Используем сообщение из ошибки API
        color: 'red',
        icon: <IconX />,
      });
    },
  });

  // Обработчик сабмита формы
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); // Предотвращаем стандартное поведение формы
    const validationResult = form.validate(); // Валидируем форму
    if (validationResult.hasErrors) {
      // Если есть ошибки, ничего не делаем (Mantine покажет их)
      console.log('Validation errors:', form.errors);
      return;
    }
    // Если ошибок нет, вызываем мутацию
    mutation.mutate({ username: form.values.email, password: form.values.password });
  };

  return (
    <Box 
      style={{ 
        minHeight: '100vh', 
        backgroundColor: theme.colors.dark[8], 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative' // Для LoadingOverlay
      }}
    >
      {/* Оверлей загрузки */}
      <LoadingOverlay visible={mutation.isPending} overlayProps={{ radius: "sm", blur: 2 }} />
      
      <Container size="xs" px={0}> 
        <Box 
          component="form" 
          onSubmit={handleSubmit} // Используем наш кастомный handleSubmit
          style={{
            padding: '2rem',
            borderRadius: theme.radius.md,
            background: theme.colors.dark[7],
            boxShadow: `5px 5px 10px ${theme.colors.dark[9]}, -5px -5px 10px ${theme.colors.dark[6]}`,
            position: 'relative' // Убедимся, что оверлей не перекрывает
          }}
        >
          <Center mb="xl">
            <Title order={2} style={{ color: theme.white, fontWeight: 900 }}> 
              Photomatrix ERP
            </Title>
          </Center>
          
          <Text color="dimmed" size="sm" style={{ textAlign: 'center' }} mb="xl">
            Войдите для доступа к панели управления
          </Text>
          
          <TextInput
            label="Email"
            placeholder="your@email.com"
            required
            type="email"
            mb="md"
            {...form.getInputProps('email')} // Используем form
            styles={{
              label: { color: theme.colors.gray[5] },
              input: {
                borderRadius: theme.radius.sm,
                backgroundColor: theme.colors.dark[6],
                border: `1px solid ${theme.colors.dark[5]}`,
                color: theme.white,
                boxShadow: `inset 2px 2px 5px ${theme.colors.dark[9]}, inset -2px -2px 5px ${theme.colors.dark[5]}`,
                '&::placeholder': {
                  color: theme.colors.dark[3],
                },
                '&:focus': {
                  borderColor: theme.colors.blue[6],
                  boxShadow: `inset 2px 2px 5px ${theme.colors.dark[9]}, inset -2px -2px 5px ${theme.colors.dark[5]}`, 
                }
              }
            }}
          />
          
          <PasswordInput
            label="Пароль"
            placeholder="Ваш пароль"
            required
            mb="xl"
            {...form.getInputProps('password')} // Используем form
            styles={{
              label: { color: theme.colors.gray[5] },
              input: {
                borderRadius: theme.radius.sm,
                backgroundColor: theme.colors.dark[6],
                border: `1px solid ${theme.colors.dark[5]}`,
                color: theme.white,
                boxShadow: `inset 2px 2px 5px ${theme.colors.dark[9]}, inset -2px -2px 5px ${theme.colors.dark[5]}`,
                '&::placeholder': {
                  color: theme.colors.dark[3],
                },
                '&:focus': {
                  borderColor: theme.colors.blue[6],
                  boxShadow: `inset 2px 2px 5px ${theme.colors.dark[9]}, inset -2px -2px 5px ${theme.colors.dark[5]}`, 
                }
              }
            }}
          />
          
          <Button
            fullWidth
            type="submit"
            variant="filled"
            color="blue"
            loading={mutation.isPending} // Добавляем состояние загрузки
            styles={(theme) => ({ 
              root: {
                background: theme.colors.blue[7],
                color: theme.white,
                boxShadow: `5px 5px 10px ${theme.colors.dark[9]}, -5px -5px 10px ${theme.colors.dark[6]}`,
                border: 'none',
                borderRadius: theme.radius.md,
                padding: '12px',
                fontWeight: 700,
                transition: 'all 0.3s ease',
                '&:hover': { 
                  background: theme.colors.blue[8],
                },
                '&:active': {
                  transform: 'translateY(1px)'
                }
              }
            })}
          >
            Войти
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default LoginPage; 