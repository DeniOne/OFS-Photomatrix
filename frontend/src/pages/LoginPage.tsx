import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  TextInput, 
  PasswordInput, 
  Button, 
  Box, 
  Title, 
  Text,
  Container,
  Center,
  useMantineTheme 
} from '@mantine/core';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const theme = useMantineTheme();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Добавить реальную логику авторизации
    console.log('Login attempt:', { email, password });
    // Пока просто переходим на дашборд
    navigate('/dashboard');
  };

  return (
    <Box 
      style={{ 
        minHeight: '100vh', 
        backgroundColor: theme.colors.dark[8], 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      <Container size="xs" px={0}>
        <Box 
          component="form" 
          onSubmit={handleSubmit}
          style={{
            padding: '2rem',
            borderRadius: theme.radius.md,
            background: theme.colors.dark[7],
            boxShadow: `5px 5px 10px ${theme.colors.dark[9]}, -5px -5px 10px ${theme.colors.dark[6]}`,
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
            type="email" // Добавим тип email
            value={email}
            onChange={(e) => setEmail(e.currentTarget.value)}
            mb="md"
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
            value={password}
            onChange={(e) => setPassword(e.currentTarget.value)}
            mb="xl"
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