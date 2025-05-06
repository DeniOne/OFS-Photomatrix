import { useState, useRef, useCallback } from 'react';
import { Box, Title, Text, Stack, Breadcrumbs, Group, Grid, ActionIcon, LoadingOverlay, TextInput, Paper, SegmentedControl } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { IconSitemap, IconSettings, IconSearch, IconZoomIn, IconZoomOut, IconZoomReset, IconDownload, IconBuilding, IconMapPin, IconHierarchy } from '@tabler/icons-react';
import OrgChart from '../components/OrgChart';
import { OrgChartHandle, OrgChartViewType } from '../types/orgChartTypes';
import OrgChartSettings from '../components/OrgChartSettings';
import { OrgChartSettingsValues, defaultOrgChartSettings } from '../types/orgChartSettingsTypes';
import { useOrgChartData } from '../hooks/useOrgChartData';
import NoDataView from '../components/NoDataView';

export function OrgChartPage() {
  const navigate = useNavigate();
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState<OrgChartSettingsValues>({
    ...defaultOrgChartSettings
  });
  
  // Тип отображаемой схемы (по умолчанию - бизнес-схема)
  const [viewType, setViewType] = useState<OrgChartViewType>('business');
  
  // Используем хук с передачей типа схемы
  const { isLoading, error, data, refetch } = useOrgChartData(viewType);
  
  const orgChartRef = useRef<OrgChartHandle>(null);
  
  const [searchTerm, setSearchTerm] = useState('');
  
  const items = [
    { title: 'Главная', href: '/' },
    { title: 'Оргструктура', href: '#' },
  ].map((item, index) => (
    <Text key={index} onClick={() => item.href !== '#' && navigate(item.href)}>
      {item.title}
    </Text>
  ));

  const handleExport = (format: 'svg' | 'png') => {
    if (format === 'svg') {
      const svgElement = document.querySelector('.org-chart-container')?.parentElement;
      if (svgElement) {
        // Код для сохранения SVG - исправлено приведение типов
        const svgData = new XMLSerializer().serializeToString(svgElement as unknown as SVGElement);
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'org-chart.svg';
        link.click();
        URL.revokeObjectURL(url);
      }
    } else if (format === 'png') {
      // Экспорт в PNG (требует дополнительной библиотеки)
      console.log('Экспорт в PNG не реализован');
    }
  };

  const handleZoomIn = useCallback(() => {
    if (orgChartRef.current) {
      orgChartRef.current.zoomIn();
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    if (orgChartRef.current) {
      orgChartRef.current.zoomOut();
    }
  }, []);

  const handleReset = useCallback(() => {
    if (orgChartRef.current) {
      orgChartRef.current.resetZoom();
    }
  }, []);

  const handleNodeClick = useCallback((nodeId: string) => {
    if (orgChartRef.current) {
      orgChartRef.current.zoomToNode(nodeId);
    }
  }, []);

  // Обработчик смены типа схемы
  const handleViewTypeChange = useCallback((value: string) => {
    const newType = value as OrgChartViewType;
    setViewType(newType);
    
    // Сбрасываем зум при смене представления
    setTimeout(() => {
      if (orgChartRef.current) {
        orgChartRef.current.resetZoom();
      }
    }, 300);
  }, []);

  // Получаем заголовок в зависимости от типа схемы
  const getViewTitle = () => {
    switch (viewType) {
      case 'business':
        return 'Бизнес-структура';
      case 'legal':
        return 'Юридическая структура';
      case 'location':
        return 'Территориальная структура';
      default:
        return 'Оргструктура';
    }
  };

  return (
    <Box p="md">
      <Stack>
        <Group justify="space-between">
          <Breadcrumbs>{items}</Breadcrumbs>
          <ActionIcon 
            variant="light" 
            size="lg" 
            onClick={() => setShowSettings(!showSettings)}
            color={showSettings ? "blue" : "gray"}
          >
            <IconSettings size={20} />
          </ActionIcon>
        </Group>
        
        <Group justify="space-between">
          <Group>
             <IconSitemap size={28} stroke={1.5} />
             <Title order={1}>{getViewTitle()}</Title>
          </Group>
          
          <Group>
            <SegmentedControl
              value={viewType}
              onChange={handleViewTypeChange}
              data={[
                { 
                  value: 'business', 
                  label: (
                    <Group gap={6} wrap="nowrap">
                      <IconHierarchy size={16} />
                      <Text size="sm">Бизнес</Text>
                    </Group>
                  ) 
                },
                { 
                  value: 'legal', 
                  label: (
                    <Group gap={6} wrap="nowrap">
                      <IconBuilding size={16} />
                      <Text size="sm">Юрлица</Text>
                    </Group>
                  ) 
                },
                { 
                  value: 'location', 
                  label: (
                    <Group gap={6} wrap="nowrap">
                      <IconMapPin size={16} />
                      <Text size="sm">Локации</Text>
                    </Group>
                  ) 
                },
              ]}
            />
            
            <TextInput
              placeholder="Поиск по имени или должности"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.currentTarget.value)}
              style={{ width: 300 }}
              rightSection={<IconSearch size={16} />}
            />
          </Group>
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
            <div style={{ 
              position: 'relative', 
              height: 'calc(100vh - 120px)',
              width: '100%',
              overflow: 'hidden',
              border: '1px solid #30363d',
              borderRadius: '8px'
            }}>
              {isLoading && <LoadingOverlay visible={true} />}
              
              {error && (
                <NoDataView 
                  message={`Произошла ошибка при загрузке организационной структуры: ${error}`}
                  onRetry={refetch}
                />
              )}
              
              {!isLoading && !error && !data && (
                <NoDataView 
                  message="Данные организационной структуры отсутствуют или недоступны."
                  onRetry={refetch}
                />
              )}
              
              {data && (
                <>
                  {/* Контрольная панель масштабирования */}
                  <Paper
                    style={{
                      position: 'absolute',
                      right: '20px',
                      top: '20px',
                      zIndex: 100,
                      padding: '8px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px',
                      background: 'rgba(39, 43, 55, 0.8)',
                      backdropFilter: 'blur(4px)',
                      borderRadius: '8px',
                    }}
                  >
                    <ActionIcon onClick={handleZoomIn}>
                      <IconZoomIn size={20} />
                    </ActionIcon>
                    <ActionIcon onClick={handleZoomOut}>
                      <IconZoomOut size={20} />
                    </ActionIcon>
                    <ActionIcon onClick={handleReset}>
                      <IconZoomReset size={20} />
                    </ActionIcon>
                    <ActionIcon onClick={() => handleExport('svg')}>
                      <IconDownload size={20} />
                    </ActionIcon>
                  </Paper>
                  
                  <OrgChart
                    ref={orgChartRef}
                    data={data}
                    settings={settings}
                    searchTerm={searchTerm}
                    viewType={viewType}
                    onNodeClick={handleNodeClick}
                    width={window.innerWidth * (showSettings ? 0.75 : 0.95)}
                    height={window.innerHeight - 150}
                  />
                </>
              )}
            </div>
          </Grid.Col>
        </Grid>
      </Stack>
    </Box>
  );
}

export default OrgChartPage;
