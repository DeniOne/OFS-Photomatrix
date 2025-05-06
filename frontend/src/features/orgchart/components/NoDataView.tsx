import { Box, Text, Group, Button, ThemeIcon, Code } from '@mantine/core';
import { IconAlertTriangle, IconReload } from '@tabler/icons-react';
import { useState } from 'react';

interface NoDataViewProps {
  message: string;
  onRetry?: () => void;
}

export function NoDataView({ message, onRetry }: NoDataViewProps) {
  const [showDetails, setShowDetails] = useState(false);
  
  // Проверка наличия JSON объекта в сообщении
  const hasJsonObject = message.includes('[object Object]');
  
  return (
    <Box
      style={{
        backgroundColor: 'var(--mantine-color-dark-6)',
        padding: 'var(--mantine-spacing-xl)',
        borderRadius: 'var(--mantine-radius-md)',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
      }}
    >
      <ThemeIcon 
        size={60} 
        radius="xl" 
        variant="light" 
        color="yellow"
        mb="md"
      >
        <IconAlertTriangle size={34} />
      </ThemeIcon>
      
      <Text size="xl" fw={500} mb="sm">
        Данные недоступны
      </Text>
      
      <Text color="dimmed" mb="xl" size="md" maw={500}>
        {message}
      </Text>
      
      {hasJsonObject && (
        <Box mb="md">
          <Button 
            variant="subtle" 
            size="compact-sm"
            onClick={() => setShowDetails(!showDetails)}
          >
            {showDetails ? 'Скрыть техническую информацию' : 'Показать техническую информацию'}
          </Button>
          
          {showDetails && (
            <Code block mt="xs">
              Возможная ошибка в обработке данных API. Проверьте консоль браузера (F12) для подробностей.
            </Code>
          )}
        </Box>
      )}
      
      {onRetry && (
        <Group justify="center">
          <Button 
            onClick={onRetry} 
            leftSection={<IconReload size={16} />}
            variant="outline"
          >
            Повторить попытку
          </Button>
        </Group>
      )}
    </Box>
  );
}

export default NoDataView; 