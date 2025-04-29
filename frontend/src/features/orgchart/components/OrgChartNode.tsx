import React from 'react';
import { Paper, Avatar, Text, Stack, Group, Badge, useMantineTheme, Box } from '@mantine/core';
import { 
  IconBuildingCommunity, 
  IconBuildingPavilion, 
  IconUser, 
  IconDots,
  IconChevronUp
} from '@tabler/icons-react';
import { OrgChartNode as OrgChartNodeData } from './OrgChart';
import { OrgChartSettingsValues } from './OrgChartSettings';

// Пропсы компонента узла
interface OrgChartNodeProps {
  nodeData: d3.HierarchyPointNode<OrgChartNodeData>;
  settings: OrgChartSettingsValues;
  onClick?: (nodeId: string) => void;
  onExpandCollapse?: (nodeId: string) => void;
  isHighlighted?: boolean;
}

// Компонент для отображения одного узла
export function OrgChartNode({ 
  nodeData, 
  settings, 
  onClick, 
  onExpandCollapse,
  isHighlighted = false
}: OrgChartNodeProps) {
  const theme = useMantineTheme();
  const data = nodeData.data;
  
  // Определяем иконку и цвет в зависимости от типа узла
  let icon;
  let bgColor = settings.colorByType ? (data.type === 'department' ? settings.departmentColor : settings.divisionColor) : theme.colors.blue[6];
  let textColor = theme.white; // Default text color

  switch (data.type) {
    case 'department':
      icon = <IconBuildingCommunity size={18} />;
      break;
    case 'division':
      icon = <IconBuildingPavilion size={18} />;
      break;
    case 'position':
    default:
      icon = <IconUser size={18} />;
      bgColor = theme.colors.gray[7]; // Specific color for positions
      break;
  }

  // Динамические размеры карточки
  const cardWidth = settings.compactView ? 120 : 160;
  const cardHeight = settings.compactView ? 60 : 80;

  // Обработчик клика по узлу (для будущей интерактивности)
  const handleClick = () => {
    if (onClick) {
      onClick(data.id);
    }
  };

  // Обработчик для кнопки расширения/сворачивания
  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation(); // Предотвращаем всплытие события до onClick узла
    if (onExpandCollapse) {
      onExpandCollapse(data.id);
    }
  };
  
  // Определяем, есть ли у узла скрытые потомки
  // @ts-ignore - _children используется d3 для скрытых узлов
  const hasHiddenChildren = nodeData._children && nodeData._children.length > 0;
  const hasVisibleChildren = nodeData.children && nodeData.children.length > 0;
  const canToggle = hasHiddenChildren || hasVisibleChildren;

  return (
    <Paper
      shadow="sm"
      radius={settings.nodeBorderRadius}
      p={settings.compactView ? "xs" : "sm"}
      sx={(theme) => ({
        width: cardWidth,
        height: cardHeight,
        backgroundColor: bgColor,
        color: textColor,
        cursor: onClick ? 'pointer' : 'default',
        border: isHighlighted 
            ? `2px solid ${theme.colors.yellow[5]}` 
            : `1px solid ${theme.fn.rgba(theme.black, 0.3)}`,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
        transition: 'border 0.2s ease',
        transform: isHighlighted ? 'scale(1.03)' : 'scale(1)',
      })}
      onClick={handleClick}
    >
      <Stack spacing={settings.compactView ? 2 : 4} align="center">
        <Group spacing="xs" noWrap align="center">
          {icon}
          <Text 
            size={settings.compactView ? "xs" : "sm"} 
            weight={500} 
            lineClamp={1} 
            title={data.name}
          >
            {data.name}
          </Text>
        </Group>
        
        {settings.showTitle && data.title && (
          <Text 
            size="xs" 
            color="dimmed" 
            lineClamp={1}
            title={data.title}
          >
            {data.title}
          </Text>
        )}
        
        {settings.showDepartmentCode && data.code && (
          <Badge 
            size="xs" 
            variant="light" 
            color="gray"
            sx={{ position: 'absolute', top: 3, right: 3 }}
          >
            {data.code}
          </Badge>
        )}
      </Stack>
      
      {/* Кнопка для сворачивания/разворачивания */}
      {canToggle && (
        <Box
          sx={{
            position: 'absolute',
            bottom: -1, // Slightly overlap border
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: theme.fn.darken(bgColor, 0.2),
            color: theme.white,
            width: '20px',
            height: '10px',
            borderRadius: '3px 3px 0 0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            border: `1px solid ${theme.fn.rgba(theme.black, 0.3)}`,
            borderBottom: 'none'
          }}
          onClick={handleToggle}
          title={hasVisibleChildren ? "Свернуть" : "Развернуть"}
        >
          {hasVisibleChildren ? <IconChevronUp size={10} /> : <IconDots size={10} />}
        </Box>
      )}
    </Paper>
  );
}

export default OrgChartNode; 