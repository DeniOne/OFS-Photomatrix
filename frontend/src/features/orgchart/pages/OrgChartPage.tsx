import React, { useState, useRef } from 'react';
import { Box, Title, Text, Stack, Breadcrumbs, Group, Grid, ActionIcon, LoadingOverlay, Alert, TextInput } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { IconSitemap, IconSettings, IconAlertCircle, IconSearch, IconX } from '@tabler/icons-react';
import OrgChart, { OrgChartHandle } from '../components/OrgChart';
import OrgChartSettings, { OrgChartSettingsValues, defaultOrgChartSettings } from '../components/OrgChartSettings';
import { useOrgChartData } from '../api/useOrgChartData';

export function OrgChartPage() {
  const navigate = useNavigate();
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState<OrgChartSettingsValues>(defaultOrgChartSettings);
  
  const { data: orgChartData, isLoading, error } = useOrgChartData();
  
  // Создаем ref для доступа к методам OrgChart
  const orgChartRef = useRef<OrgChartHandle>(null);
  
  // Состояние для поискового запроса
  const [searchTerm, setSearchTerm] = useState('');
  
  // Хлебные крошки для навигации
  const items = [
    { title: 'Главная', href: '/' },
    { title: 'Оргструктура', href: '#' },
  ].map((item, index) => (
    <Text key={index} onClick={() => item.href !== '#' && navigate(item.href)}>
      {item.title}
    </Text>
  ));

  // Обработчики для экспорта и масштабирования
  const handleExport = (format: 'svg' | 'png') => {
    // TODO: Вызвать метод экспорта из OrgChart через ref, если он будет реализован
    console.log(`Экспорт в формате ${format}`);
  };

  const handleZoomIn = () => {
    // TODO: Вызвать метод зума из OrgChart через ref
    console.log("Zoom In (not implemented via ref yet)");
  };

  const handleZoomOut = () => {
    // TODO: Вызвать метод зума из OrgChart через ref
    console.log("Zoom Out (not implemented via ref yet)");
  };

  // Используем метод сброса из OrgChart через ref
  const handleReset = () => {
    // Сбрасываем настройки в родительском компоненте
    setSettings(defaultOrgChartSettings);
    // Вызываем сброс зума/положения в дочернем компоненте
    orgChartRef.current?.resetZoom();
  };

  // Обработчик клика на узел, который вызывает центрирование
  const handleNodeClick = (nodeId: string) => {
    console.log('Node clicked in Page:', nodeId);
    orgChartRef.current?.centerOnNode(nodeId); // Вызываем центрирование
  };

  return (
    <Box p="md">
      <Stack>
        <Group>
          <Group>
            <Breadcrumbs>{items}</Breadcrumbs>
          </Group>
          <ActionIcon 
            variant="light" 
            size="lg" 
            onClick={() => setShowSettings(!showSettings)}
            color={showSettings ? "blue" : "gray"}
          >
            <IconSettings size={20} />
          </ActionIcon>
        </Group>
        
        <Group>
          <Group>
             <IconSitemap size={28} stroke={1.5} />
             <Title order={1}>Оргструктура</Title>
          </Group>
          {/* Поле поиска */}
          <TextInput
            placeholder="Поиск по названию/должности..."
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.currentTarget.value)}
            icon={<IconSearch size={16} />}
            rightSection={
              searchTerm ? (
                <ActionIcon onClick={() => setSearchTerm('')} title="Очистить">
                  <IconX size={16} />
                </ActionIcon>
              ) : null
            }
            sx={{ flexGrow: 1, maxWidth: '400px' }} // Растягиваем, но ограничиваем
          />
        </Group>
        
        <Grid gutter="md">
          {showSettings && (
            <Grid.Col span={3}>
              <OrgChartSettings
                settings={settings}
                onSettingsChange={setSettings}
                onExport={handleExport}
                onZoomIn={handleZoomIn}
                onZoomOut={handleZoomOut}
                onReset={handleReset}
              />
            </Grid.Col>
          )}
          
          <Grid.Col span={showSettings ? 9 : 12}>
            <Box sx={{ height: 'calc(100vh - 220px)', position: 'relative' }}> {/* Уменьшил высоту из-за поиска */}
              <LoadingOverlay visible={isLoading} overlayBlur={2} />
              {error && (
                <Alert color="red" title="Ошибка">
                  {error.message}
                </Alert>
              )}
              {!isLoading && !error && orgChartData && (
                <OrgChart 
                  ref={orgChartRef}
                  data={orgChartData} 
                  settings={settings}
                  onNodeClick={handleNodeClick}
                  searchTerm={searchTerm} // Передаем поисковый запрос
                />
              )}
            </Box>
          </Grid.Col>
        </Grid>
      </Stack>
    </Box>
  );
}

export default OrgChartPage;
