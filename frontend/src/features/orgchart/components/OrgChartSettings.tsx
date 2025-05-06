import { useState, useEffect } from 'react';
import { 
  Box, 
  Title, 
  Paper, 
  Stack, 
  Slider, 
  Group, 
  Text,
  Switch,
  SegmentedControl, 
  ColorInput,
  Collapse,
  Button,
  NumberInput,
  ActionIcon,
  Divider
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { 
  IconDownload, 
  IconZoomIn,
  IconZoomOut,
  IconRefresh, 
  IconLayoutGrid, 
  IconLayoutColumns, 
  IconLayoutRows,
  IconChevronUp,
  IconChevronDown
} from '@tabler/icons-react';
import { OrgChartSettingsValues, defaultOrgChartSettings, nodeSizePresets } from '../types/orgChartSettingsTypes';

// Интерфейс для пропсов компонента
interface OrgChartSettingsProps {
  settings: OrgChartSettingsValues;
  userSettings?: Partial<OrgChartSettingsValues>;
  onSettingsChange: (values: OrgChartSettingsValues) => void;
  onExport?: (format: 'svg' | 'png') => void;
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onReset?: () => void;
}

// Компонент настроек
export default function OrgChartSettings({
  settings,
  userSettings,
  onSettingsChange,
  onExport,
  onZoomIn,
  onZoomOut,
  onReset,
}: OrgChartSettingsProps) {
  const [activeSection, setActiveSection] = useState<string | null>('layout');
  
  // Инициализация формы с переданными настройками
  const form = useForm<OrgChartSettingsValues>({
    initialValues: {
      ...defaultOrgChartSettings,
      ...settings,
      ...userSettings
    },
  });
  
  // Устанавливаем правильный пресет в зависимости от размеров
  useEffect(() => {
    const { nodeWidth, nodeHeight } = form.values;
    
    // Ищем подходящий пресет
    const preset = Object.entries(nodeSizePresets).find(
      ([key, value]) => key !== 'custom' && value.width === nodeWidth && value.height === nodeHeight
    );
    
    if (preset) {
      form.setFieldValue('nodeSizePreset', preset[0] as 'small' | 'medium' | 'large');
    } else {
      form.setFieldValue('nodeSizePreset', 'custom');
    }
  }, [form.values.nodeWidth, form.values.nodeHeight]);

  // Обработчик изменений в форме
  useEffect(() => {
    // Вызываем callback при изменении любого поля
    onSettingsChange(form.values);
  }, [form.values, onSettingsChange]);

  const toggleSection = (section: string) => {
    setActiveSection(activeSection === section ? null : section);
  };
  
  const handlePresetChange = (preset: string) => {
    if (preset === 'custom') return;
    
    const { width, height } = nodeSizePresets[preset as keyof typeof nodeSizePresets];
    form.setFieldValue('nodeWidth', width);
    form.setFieldValue('nodeHeight', height);
    form.setFieldValue('nodeSizePreset', preset as 'small' | 'medium' | 'large' | 'custom');
  };

  return (
    <Paper p="md" radius="md" withBorder>
      <Stack gap="xs">
        <Title order={3} size="h4">Настройки организационной диаграммы</Title>
        
        {/* Кнопки управления */}
        <Group justify="space-between" mb="xs">
          <Group gap="xs">
            <ActionIcon 
              variant="light" 
              color="blue" 
              onClick={onZoomIn} 
              title="Увеличить"
            >
              <IconZoomIn size={18} />
            </ActionIcon>
            <ActionIcon 
              variant="light" 
              color="blue" 
              onClick={onZoomOut} 
              title="Уменьшить"
            >
              <IconZoomOut size={18} />
            </ActionIcon>
            <ActionIcon 
              variant="light" 
              color="gray" 
              onClick={onReset} 
              title="Сбросить настройки"
            >
              <IconRefresh size={18} />
            </ActionIcon>
          </Group>
          
          <Group gap="xs">
            <Button 
              variant="light" 
              size="xs" 
              onClick={() => onExport && onExport('svg')}
            >
              <Group gap={6} justify="center">
                <IconDownload size={16} />
                <span>SVG</span>
              </Group>
            </Button>
            <Button 
              variant="light" 
              size="xs" 
              onClick={() => onExport && onExport('png')}
            >
              <Group gap={6} justify="center">
                <IconDownload size={16} />
                <span>PNG</span>
              </Group>
            </Button>
          </Group>
        </Group>

        <Divider />

        {/* Раздел макета */}
        <Box>
          <Group justify="space-between" onClick={() => toggleSection('layout')} style={{ cursor: 'pointer' }}>
            <Text fw={500}>Макет и масштаб</Text>
            <ActionIcon>
              {activeSection === 'layout' ? <IconChevronUp size={16} /> : <IconChevronDown size={16} />}
            </ActionIcon>
          </Group>
          
          <Collapse in={activeSection === 'layout'}>
            <Box mt="xs">
              <Text fw={500} size="sm" mb={5}>Тип макета</Text>
                <SegmentedControl
                fullWidth
                value={form.values.layout}
                onChange={(value) => form.setFieldValue('layout', value as 'horizontal' | 'vertical' | 'radial')}
                  data={[
                  { value: 'vertical', label: <Box><IconLayoutRows size={16} /><Box>Вертик.</Box></Box> },
                  { value: 'horizontal', label: <Box><IconLayoutColumns size={16} /><Box>Гориз.</Box></Box> },
                  { value: 'radial', label: <Box><IconLayoutGrid size={16} /><Box>Радиал.</Box></Box> },
                ]}
              />
              
              <Text fw={500} size="sm" mt="md" mb={5}>Масштаб по умолчанию</Text>
              <Slider
                min={0.3}
                max={1.5}
                step={0.1}
                label={(value) => `${Math.round(value * 100)}%`}
                value={form.values.zoom}
                onChange={(value) => form.setFieldValue('zoom', value)}
                marks={[
                  { value: 0.5, label: '50%' },
                  { value: 1, label: '100%' },
                  { value: 1.5, label: '150%' },
                ]}
              />
            </Box>
          </Collapse>
        </Box>
        
        {/* Раздел размеров */}
        <Box>
          <Group justify="space-between" onClick={() => toggleSection('sizes')} style={{ cursor: 'pointer' }}>
            <Text fw={500}>Размеры и отступы</Text>
            <ActionIcon>
              {activeSection === 'sizes' ? <IconChevronUp size={16} /> : <IconChevronDown size={16} />}
            </ActionIcon>
          </Group>
          
          <Collapse in={activeSection === 'sizes'}>
            <Box mt="xs">
              <Text fw={500} size="sm" mb={5}>Размер узлов</Text>
                <SegmentedControl
                fullWidth
                value={form.values.nodeSizePreset}
                onChange={handlePresetChange}
                  data={[
                  { value: 'small', label: 'S' },
                  { value: 'medium', label: 'M' },
                  { value: 'large', label: 'L' },
                  { value: 'custom', label: 'Custom' },
                ]}
              />
              
              <Group grow mt="xs">
                <NumberInput
                  label="Ширина"
                  value={form.values.nodeWidth}
                  onChange={(value) => form.setFieldValue('nodeWidth', Number(value) || 100)}
                  min={80}
                  max={300}
                  disabled={form.values.nodeSizePreset !== 'custom'}
                />
                <NumberInput
                  label="Высота"
                  value={form.values.nodeHeight}
                  onChange={(value) => form.setFieldValue('nodeHeight', Number(value) || 50)}
                  min={40}
                  max={200}
                  disabled={form.values.nodeSizePreset !== 'custom'}
                />
              </Group>
              
              <Text fw={500} size="sm" mt="md" mb={5}>Отступ между соседними узлами</Text>
                <Slider
                  min={10}
                  max={100}
                  step={5}
                label={(value) => `${value}px`}
                value={form.values.siblingGap}
                onChange={(value) => form.setFieldValue('siblingGap', value)}
                  marks={[
                  { value: 20, label: '20px' },
                  { value: 60, label: '60px' },
                  { value: 100, label: '100px' },
                ]}
              />
              
              <Text fw={500} size="sm" mt="md" mb={5}>Отступ между уровнями</Text>
                <Slider
                  min={20}
                max={150}
                  step={5}
                label={(value) => `${value}px`}
                value={form.values.levelGap}
                onChange={(value) => form.setFieldValue('levelGap', value)}
                  marks={[
                  { value: 40, label: '40px' },
                  { value: 100, label: '100px' },
                  { value: 150, label: '150px' },
                ]}
              />
              
              <Text fw={500} size="sm" mt="md" mb={5}>Скругление углов</Text>
                <Slider
                  min={0}
                max={16}
                  step={1}
                label={(value) => `${value}px`}
                value={form.values.nodeBorderRadius}
                onChange={(value) => form.setFieldValue('nodeBorderRadius', value)}
                  marks={[
                  { value: 0, label: '0px' },
                  { value: 8, label: '8px' },
                  { value: 16, label: '16px' },
                ]}
              />
            </Box>
          </Collapse>
        </Box>
        
        {/* Раздел отображения */}
        <Box>
          <Group justify="space-between" onClick={() => toggleSection('display')} style={{ cursor: 'pointer' }}>
            <Text fw={500}>Отображение</Text>
            <ActionIcon>
              {activeSection === 'display' ? <IconChevronUp size={16} /> : <IconChevronDown size={16} />}
            </ActionIcon>
          </Group>
          
          <Collapse in={activeSection === 'display'}>
            <Box mt="xs">
              <Switch
                label="Компактный вид"
                checked={form.values.compactView}
                onChange={(event) => form.setFieldValue('compactView', event.currentTarget.checked)}
                mt="xs"
              />
              
              <Switch
                label="Показывать должность/описание"
                checked={form.values.showTitle}
                onChange={(event) => form.setFieldValue('showTitle', event.currentTarget.checked)}
                mt="xs"
              />
              
              <Switch
                label="Показывать код подразделения"
                checked={form.values.showDepartmentCode}
                onChange={(event) => form.setFieldValue('showDepartmentCode', event.currentTarget.checked)}
                mt="xs"
              />
              
                  <Switch
                label="Цвет по типу узла"
                checked={form.values.colorByType}
                onChange={(event) => form.setFieldValue('colorByType', event.currentTarget.checked)}
                mt="xs"
              />
              
              {form.values.colorByType && (
                <Group grow mt="xs">
                  <ColorInput
                    label="Цвет подразделений"
                    format="hex"
                    value={form.values.departmentColor}
                    onChange={(value) => form.setFieldValue('departmentColor', value)}
                    withEyeDropper={false}
                    swatches={['#1971c2', '#2b8a3e', '#5f3dc4', '#e67700', '#c92a2a']}
                  />
                  <ColorInput
                    label="Цвет отделов"
                    format="hex"
                    value={form.values.divisionColor}
                    onChange={(value) => form.setFieldValue('divisionColor', value)}
                    withEyeDropper={false}
                    swatches={['#2f9e44', '#1c7ed6', '#862e9c', '#f08c00', '#e03131']}
                  />
                </Group>
              )}
              
              <NumberInput
                label="Максимальная глубина (пусто - без ограничений)"
                value={form.values.maxDepth === null ? undefined : form.values.maxDepth}
                onChange={(value) => form.setFieldValue('maxDepth', value === undefined ? null : Number(value))}
                min={1}
                max={10}
                mt="xs"
                placeholder="Без ограничений"
              />
            </Box>
          </Collapse>
        </Box>
      </Stack>
    </Paper>
  );
}