import { useState } from 'react';
import { Modal, Button, Box, Text } from '@mantine/core';

function TestModalPage() {
  const [opened, setOpened] = useState(false);

  return (
    <Box p="xl">
      <Text mb="md">Тестовая страница для проверки Modal</Text>
      <Button onClick={() => setOpened(true)}>Открыть модалку</Button>

      <Modal
        opened={opened}
        onClose={() => setOpened(false)}
        title="Тестовая Модалка"
      >
        <Text>Если ты видишь это окно, значит, базовый Modal работает!</Text>
      </Modal>
    </Box>
  );
}

export default TestModalPage; 