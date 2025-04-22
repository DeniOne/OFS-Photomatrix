import { useState } from 'react';
import { Box, Button, Group, Title, JsonInput, Text, Alert, Stack, TextInput } from '@mantine/core';
import { IconRefresh, IconSend, IconKey } from '@tabler/icons-react';
import axios from 'axios';

// Тестовая страница для отладки API
const TestPage = () => {
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('access_token') || '');
  
  // URL API
  const [url, setUrl] = useState('http://localhost:8000/api/v1/auth/test-token');

  // Сохранить токен
  const saveToken = () => {
    localStorage.setItem('access_token', token);
    setResponse({ message: 'Токен сохранен!' });
    setError(null);
  };

  // Очистить токен
  const clearToken = () => {
    localStorage.removeItem('access_token');
    setToken('');
    setResponse({ message: 'Токен удален!' });
    setError(null);
  };

  // Тестовый запрос к API
  const testApi = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await axios.get(url, { headers });
      setResponse(response.data);
    } catch (err: any) {
      console.error('API error:', err);
      setError(err.response?.data?.detail || err.message || 'Неизвестная ошибка');
      setResponse(err.response?.data || null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p="md">
      <Title order={2} mb="lg">Тестирование API</Title>
      
      <Stack>
        <TextInput
          label="URL API"
          placeholder="http://localhost:8000/api/v1/..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          mb="md"
        />
        
        <TextInput
          label="Токен доступа"
          placeholder="eyJ0eXAiOiJKV1Qi..."
          value={token}
          onChange={(e) => setToken(e.target.value)}
          mb="md"
          rightSection={
            <Group gap={5}>
              <Button 
                variant="subtle" 
                size="xs"
                title="Сохранить токен" 
                onClick={saveToken}
              >
                <IconKey size={16} />
              </Button>
              <Button 
                variant="subtle" 
                color="red" 
                size="xs"
                title="Очистить токен" 
                onClick={clearToken}
              >
                ×
              </Button>
            </Group>
          }
        />
        
        <Group mb="lg">
          <Button
            leftSection={<IconSend size={16} />}
            onClick={testApi}
            loading={loading}
          >
            Отправить запрос
          </Button>
          
          <Button
            variant="outline"
            leftSection={<IconRefresh size={16} />}
            onClick={() => {
              setResponse(null);
              setError(null);
            }}
          >
            Очистить результат
          </Button>
        </Group>
        
        {error && (
          <Alert color="red" title="Ошибка" mb="md">
            {error}
          </Alert>
        )}
        
        <Box mb="lg">
          <Text fw={500} mb="xs">Ответ:</Text>
          <JsonInput
            value={response ? JSON.stringify(response, null, 2) : ''}
            readOnly
            autosize
            minRows={5}
            maxRows={20}
            styles={{ input: { fontFamily: 'monospace' } }}
          />
        </Box>
        
        <Box mt="xl">
          <Text size="sm" color="dimmed">
            Текущее состояние localStorage:
          </Text>
          <JsonInput
            value={JSON.stringify({ access_token: localStorage.getItem('access_token') }, null, 2)}
            readOnly
            autosize
            minRows={2}
            styles={{ input: { fontFamily: 'monospace' } }}
          />
        </Box>
      </Stack>
    </Box>
  );
};

export default TestPage; 