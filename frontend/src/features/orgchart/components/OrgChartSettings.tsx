import { useState } from 'react';
import { 
  Box, 
  Title, 
  SegmentedControl, 
  Slider, 
  ColorPicker, 
  Checkbox, 
  Group, 
  Stack, 
  Select, 
  Button, 
  Divider,
  Accordion,
  Paper,
  Text,
  Switch,
  NumberInput,
  useMantineTheme
} from '@mantine/core';
import { 
  IconDownload, 
  IconArrowsMaximize, 
  IconArrowsMinimize,
  IconLayoutList,
  IconZoomIn,
  IconZoomOut,
  IconRotate,
  IconChevronUp,
  IconChevronRight
} from '@tabler/icons-react';

// Интерфейс для настроек
export interface OrgChartSettingsValues {
  layout: 'vertical' | 'horizontal' | 'radial';
  nodeSize: number;
  levelGap: number;
  siblingGap: number;
  nodeBorderRadius: number;
  showTitle: boolean;
  showDepartmentCode: boolean;
  colorByType: boolean;
  linkStyle: 'curved' | 'straight' | 'step';
  zoom: number;
  maxDepth: number | null;
  showGrid: boolean;
  compactView: boolean;
  departmentColor: string;
  divisionColor: string;
}

// Пропсы компонента
interface OrgChartSettingsProps {
  settings: OrgChartSettingsValues;
  onSettingsChange: (settings: OrgChartSettingsValues) => void;
  onExport: (format: 'svg' | 'png') => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onReset: () => void;
}

// Компонент настроек
export function OrgChartSettings({
  settings,
  onSettingsChange,
  onExport,
  onZoomIn,
  onZoomOut,
  onReset
}: OrgChartSettingsProps) {
  const theme = useMantineTheme();
  
  // Обработчик изменения отдельного поля
  const handleChange = <K extends keyof OrgChartSettingsValues>(
    key: K, 
    value: OrgChartSettingsValues[K]
  ) => {
    onSettingsChange({
      ...settings,
      [key]: value
    });
  };

  return (
    <Paper 
      p="md" 
      radius="md" 
      shadow="sm"
      sx={{
        backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[7] : theme.colors.gray[0]
      }}
    >
      <Stack spacing="md">
        <Group position="apart">
          <Title order={4}>Настройки диаграммы</Title>
          <Group spacing="xs">
            <Button 
              variant="light" 
              size="xs" 
              leftIcon={<IconZoomIn size={16} />}
              onClick={onZoomIn}
            >
              Увеличить
            </Button>
            <Button 
              variant="light" 
              size="xs" 
              leftIcon={<IconZoomOut size={16} />}
              onClick={onZoomOut}
            >
              Уменьшить
            </Button>
            <Button 
              variant="subtle" 
              size="xs"
              onClick={onReset}
            >
              Сбросить
            </Button>
          </Group>
        </Group>

        <Divider />

        <Accordion defaultValue="layout" radius="md">
          <Accordion.Item value="layout">
            <Accordion.Control>
              <Group spacing="xs">
                <IconLayoutList size={16} />
                <Text>Макет</Text>
              </Group>
            </Accordion.Control>
            <Accordion.Panel>
              <Stack spacing="xs">
                <Text size="sm" weight={500}>Ориентация</Text>
                <SegmentedControl
                  value={settings.layout}
                  onChange={(value) => handleChange('layout', value as OrgChartSettingsValues['layout'])}
                  data={[
                    { label: 'Вертикальная', value: 'vertical' },
                    { label: 'Горизонтальная', value: 'horizontal' },
                    { label: 'Радиальная', value: 'radial' }
                  ]}
                  fullWidth
                />

                <Text size="sm" weight={500} mt="xs">Стиль соединений</Text>
                <SegmentedControl
                  value={settings.linkStyle}
                  onChange={(value) => handleChange('linkStyle', value as OrgChartSettingsValues['linkStyle'])}
                  data={[
                    { label: 'Изогнутые', value: 'curved' },
                    { label: 'Прямые', value: 'straight' },
                    { label: 'Ступенчатые', value: 'step' }
                  ]}
                  fullWidth
                />

                <Text size="sm" weight={500} mt="xs">Расстояние между уровнями</Text>
                <Slider
                  value={settings.levelGap}
                  onChange={(value) => handleChange('levelGap', value)}
                  min={30}
                  max={200}
                  step={10}
                  marks={[
                    { value: 30, label: '30' },
                    { value: 100, label: '100' },
                    { value: 200, label: '200' }
                  ]}
                />

                <Text size="sm" weight={500} mt="xs">Расстояние между элементами</Text>
                <Slider
                  value={settings.siblingGap}
                  onChange={(value) => handleChange('siblingGap', value)}
                  min={10}
                  max={100}
                  step={5}
                  marks={[
                    { value: 10, label: '10' },
                    { value: 50, label: '50' },
                    { value: 100, label: '100' }
                  ]}
                />

                <Group mt="xs">
                  <Switch
                    label="Компактный вид"
                    checked={settings.compactView}
                    onChange={(event) => handleChange('compactView', event.currentTarget.checked)}
                  />
                  <Switch
                    label="Показать сетку"
                    checked={settings.showGrid}
                    onChange={(event) => handleChange('showGrid', event.currentTarget.checked)}
                  />
                </Group>
              </Stack>
            </Accordion.Panel>
          </Accordion.Item>

          <Accordion.Item value="nodes">
            <Accordion.Control>
              <Group spacing="xs">
                <IconRotate size={16} />
                <Text>Узлы</Text>
              </Group>
            </Accordion.Control>
            <Accordion.Panel>
              <Stack spacing="xs">
                <Text size="sm" weight={500}>Размер узлов</Text>
                <Slider
                  value={settings.nodeSize}
                  onChange={(value) => handleChange('nodeSize', value)}
                  min={20}
                  max={100}
                  step={5}
                  marks={[
                    { value: 20, label: '20' },
                    { value: 60, label: '60' },
                    { value: 100, label: '100' }
                  ]}
                />

                <Text size="sm" weight={500} mt="xs">Скругление углов</Text>
                <Slider
                  value={settings.nodeBorderRadius}
                  onChange={(value) => handleChange('nodeBorderRadius', value)}
                  min={0}
                  max={20}
                  step={1}
                  marks={[
                    { value: 0, label: '0' },
                    { value: 10, label: '10' },
                    { value: 20, label: '20' }
                  ]}
                />

                <Text size="sm" weight={500} mt="xs">Максимальная глубина</Text>
                <NumberInput
                  value={settings.maxDepth ?? undefined}
                  onChange={(value) => handleChange('maxDepth', value !== '' ? Number(value) : null)}
                  placeholder="Все уровни"
                  min={1}
                  max={10}
                  step={1}
                />

                <Group mt="xs">
                  <Switch
                    label="Показать должность"
                    checked={settings.showTitle}
                    onChange={(event) => handleChange('showTitle', event.currentTarget.checked)}
                  />
                  <Switch
                    label="Показать код"
                    checked={settings.showDepartmentCode}
                    onChange={(event) => handleChange('showDepartmentCode', event.currentTarget.checked)}
                  />
                </Group>
              </Stack>
            </Accordion.Panel>
          </Accordion.Item>

          <Accordion.Item value="colors">
            <Accordion.Control>
              <Group spacing="xs">
                <IconArrowsMaximize size={16} />
                <Text>Цвета</Text>
              </Group>
            </Accordion.Control>
            <Accordion.Panel>
              <Stack spacing="xs">
                <Switch
                  label="Разделять цветом по типу"
                  checked={settings.colorByType}
                  onChange={(event) => handleChange('colorByType', event.currentTarget.checked)}
                />

                <Text size="sm" weight={500} mt="xs">Цвет департаментов</Text>
                <ColorPicker
                  format="hex"
                  value={settings.departmentColor}
                  onChange={(color) => handleChange('departmentColor', color)}
                  swatches={[
                    theme.colors.blue[6],
                    theme.colors.indigo[6],
                    theme.colors.purple[6],
                    theme.colors.teal[6],
                    theme.colors.green[6],
                    theme.colors.yellow[6],
                    theme.colors.orange[6],
                    theme.colors.red[6],
                  ]}
                />

                <Text size="sm" weight={500} mt="xs">Цвет отделов</Text>
                <ColorPicker
                  format="hex"
                  value={settings.divisionColor}
                  onChange={(color) => handleChange('divisionColor', color)}
                  swatches={[
                    theme.colors.blue[4],
                    theme.colors.indigo[4],
                    theme.colors.purple[4],
                    theme.colors.teal[4],
                    theme.colors.green[4],
                    theme.colors.yellow[4],
                    theme.colors.orange[4],
                    theme.colors.red[4],
                  ]}
                />
              </Stack>
            </Accordion.Panel>
          </Accordion.Item>
        </Accordion>

        <Divider />

        <Group position="apart">
          <Button 
            variant="filled" 
            leftIcon={<IconDownload size={16} />}
            onClick={() => onExport('svg')}
          >
            Экспорт SVG
          </Button>
          <Button 
            variant="light" 
            leftIcon={<IconDownload size={16} />}
            onClick={() => onExport('png')}
          >
            Экспорт PNG
          </Button>
        </Group>
      </Stack>
    </Paper>
  );
}

// Дефолтные настройки
export const defaultOrgChartSettings: OrgChartSettingsValues = {
  layout: 'vertical',
  nodeSize: 50,
  levelGap: 100,
  siblingGap: 40,
  nodeBorderRadius: 5,
  showTitle: true,
  showDepartmentCode: false,
  colorByType: true,
  linkStyle: 'curved',
  zoom: 1,
  maxDepth: null,
  showGrid: false,
  compactView: false,
  departmentColor: '#228be6', // blue.6
  divisionColor: '#4dabf7', // blue.4
};

export default OrgChartSettings; 