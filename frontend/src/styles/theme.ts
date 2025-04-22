import { MantineThemeOverride, MantineTheme } from '@mantine/core';

// Цвета для темной темы
const darkColors = {
  // Основной фиолетовый/синий для акцентов
  primary: [
    '#ede9fe', // Светлее
    '#ddd6fe',
    '#c4b5fd',
    '#a78bfa',
    '#8b5cf6', // Основной
    '#7c3aed',
    '#6d28d9',
    '#5b21b6', // Темнее
    '#4c1d95',
    '#3b0764'
  ] as [string, string, string, string, string, string, string, string, string, string],
  // Темно-серые/синие для фона и карточек
  dark: [
    '#C1C2C5', // Светлее для текста/границ
    '#A6A7AB',
    '#909296',
    '#5c5f66',
    '#373A40',
    '#2C2E33', // Фон карточек
    '#25262b',
    '#1A1B1E', // Основной фон
    '#141517',
    '#101113'  // Самый темный
  ] as [string, string, string, string, string, string, string, string, string, string],
  // Дополнительные цвета (если нужны)
  green: [
    '#d1fae5', '#a7f3d0', '#6ee7b7', '#34d399', '#10b981', 
    '#059669', '#047857', '#065f46', '#064e3b', '#022c22'
  ] as [string, string, string, string, string, string, string, string, string, string],
  red: [
    '#fee2e2', '#fecaca', '#fca5a5', '#f87171', '#ef4444', 
    '#dc2626', '#b91c1c', '#991b1b', '#7f1d1d', '#450a0a'
  ] as [string, string, string, string, string, string, string, string, string, string],
};

// Тени для темного неоморфизма (пример)
export const neumorphicShadows = {
  dark: '5px 5px 10px #141517, -5px -5px 10px #25262b', // Выпуклый
  darkInset: 'inset 4px 4px 8px #141517, inset -4px -4px 8px #25262b', // Вогнутый
};

// Основная тема
export const theme: MantineThemeOverride = {
  // colorScheme: 'dark', // Убрали, т.к. Mantine сам определяет по цветам
  colors: {
    ...darkColors,
    // Переопределяем стандартные цвета, если нужно
    blue: darkColors.primary, 
  },
  primaryColor: 'primary', // Используем наш ключ 'primary'
  primaryShade: {
    light: 4, // Индекс для светлых оттенков
    dark: 6,  // Индекс для темных оттенков (основной - 4)
  },
  
  // Шрифты (можно настроить)
  fontFamily: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif, Apple Color Emoji, Segoe UI Emoji',
  headings: { fontFamily: 'inherit' },

  // Округления
  radius: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
  },
  
  // Настройка компонентов (примеры)
  components: {
    Button: {
      defaultProps: {
        radius: 'md',
      },
      styles: (_theme: MantineTheme) => ({
        root: {
          // Стили для кнопок
        }
      }),
    },
    Card: {
      defaultProps: {
        radius: 'md',
        padding: 'xl',
        shadow: 'none',
        withBorder: false,
      },
      styles: (theme: MantineTheme) => ({
        root: {
          backgroundColor: theme.colors.dark[6],
          border: `1px solid ${theme.colors.dark[5]}`
        }
      }),
    },
    TextInput: {
      styles: (_theme: MantineTheme) => ({
        input: {
          backgroundColor: 'var(--mantine-color-dark-6)',
          borderColor: 'var(--mantine-color-dark-4)',
          color: 'var(--mantine-color-gray-0)',
          '&::placeholder': {
            color: 'var(--mantine-color-dark-3)',
          },
        },
        label: {
          color: 'var(--mantine-color-gray-5)',
          marginBottom: '4px',
        },
      }),
    },
  },
};

export default theme; 