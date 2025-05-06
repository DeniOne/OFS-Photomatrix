import React from 'react';
import { 
  IconBuildingCommunity, 
  IconBuildingPavilion, 
  IconUser, 
  IconInfoCircle,
  IconChevronUp,
  IconChevronDown
} from '@tabler/icons-react';
import { OrgChartNodeData } from '../types/orgChartTypes';
import { OrgChartSettingsValues } from '../types/orgChartSettingsTypes';

// Пропсы компонента узла
interface OrgChartNodeProps {
  nodeData: d3.HierarchyPointNode<OrgChartNodeData>;
  settings: OrgChartSettingsValues;
  onClick?: (nodeId: string) => void;
  onExpandCollapse?: (nodeId: string) => void;
  isHighlighted?: boolean;
  onShowDetails?: (data: OrgChartNodeData) => void;
}

// Компонент для отображения одного узла без зависимостей от Mantine
export function OrgChartNode({ 
  nodeData, 
  settings, 
  onClick, 
  onExpandCollapse,
  isHighlighted = false,
  onShowDetails
}: OrgChartNodeProps) {
  const data = nodeData.data;
  
  // Определяем иконку и цвет в зависимости от типа узла
  let icon;
  let bgColor; 
  let textColor = '#ffffff'; // Белый текст

  switch (data.type) {
    case 'department':
      icon = <IconBuildingCommunity size={18} />;
      bgColor = darken(settings.departmentColor, 0.2);
      break;
    case 'division':
      icon = <IconBuildingPavilion size={18} />;
      bgColor = darken(settings.divisionColor, 0.2);
      break;
    case 'position':
    default:
      icon = <IconUser size={18} />;
      bgColor = darken('#868e96', 0.2); // Серый для должностей
      break;
  }

  // Используем динамические размеры из настроек
  const { width: nodeWidth, height: nodeHeight } = getNodeDimensions(settings);
  const cardWidth = nodeWidth;
  const cardHeight = nodeHeight;

  // Обработчик клика по узлу
  const handleClick = () => {
    if (onClick) {
      onClick(data.id);
    }
  };

  // Обработчик для кнопки просмотра деталей
  const handleShowDetails = (e: React.MouseEvent) => {
    e.stopPropagation(); // Предотвращаем всплытие события
    if (onShowDetails) {
      onShowDetails(data);
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

  // Формируем подробную информацию для всплывающей подсказки
  const getDetailedInfo = () => {
    let info = `${data.name || 'Не указано'}`;
    
    if (data.title) {
      info += `\n${data.title}`;
    }
    
    if (data.code) {
      info += `\nКод: ${data.code}`;
    }
    
    if (data.staffName) {
      info += `\nСотрудник: ${data.staffName}`;
    }
    
    return info;
  };

  const borderColor = isHighlighted ? '#fcc419' : 'rgba(0, 0, 0, 0.3)';
  const borderWidth = isHighlighted ? 2 : 1;
  const transform = isHighlighted ? 'scale(1.03)' : 'scale(1)';
  
  const nodeStyles: React.CSSProperties = {
    width: cardWidth,
    height: cardHeight,
    backgroundColor: bgColor,
    color: textColor,
    cursor: onClick ? 'pointer' : 'default',
    border: `${borderWidth}px solid ${borderColor}`,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    position: 'relative',
    overflow: 'hidden',
    transition: 'all 0.2s ease',
    transform: transform,
    borderRadius: settings.nodeBorderRadius,
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
    padding: settings.compactView ? '8px' : '12px'
  };

  return (
    <div 
      style={nodeStyles}
      onClick={handleClick}
      title={getDetailedInfo()} 
    >
      {/* Основное содержимое */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: settings.compactView ? '2px' : '4px' }}>
        {/* Заголовок с иконкой */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flexWrap: 'nowrap' }}>
          {icon}
          <div 
            style={{ 
              fontSize: settings.compactView ? '12px' : '14px', 
              fontWeight: 500, 
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              maxWidth: '90%'
            }}
            title={data.name}
          >
            {data.name}
          </div>
        </div>
        
        {/* Дополнительная информация */}
        {settings.showTitle && data.title && (
          <div 
            style={{ 
              fontSize: '12px', 
              color: 'rgba(255, 255, 255, 0.7)',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              maxWidth: '90%'
            }}
            title={data.title}
          >
            {data.title}
          </div>
        )}
        
        {/* Код подразделения */}
        {settings.showDepartmentCode && data.code && (
          <div 
            style={{ 
              position: 'absolute', 
              top: 3, 
              right: 3,
              fontSize: '10px',
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              padding: '2px 4px',
              borderRadius: '4px',
              lineHeight: 1
            }}
          >
            {data.code}
          </div>
        )}
      </div>
      
      {/* Панель управления */}
      <div
        style={{
          position: 'absolute',
          bottom: 2,
          right: 2,
          display: 'flex',
          gap: '2px'
        }}
      >
        {/* Кнопка просмотра деталей */}
        {onShowDetails && (
          <div
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '4px',
              width: 20,
              height: 20,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer'
            }}
            onClick={handleShowDetails}
            title="Детали"
          >
            <IconInfoCircle size={14} />
          </div>
        )}
        
        {/* Кнопка для сворачивания/разворачивания */}
        {canToggle && (
          <div
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '4px',
              width: 20,
              height: 20,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer'
            }}
            onClick={handleToggle}
            title={hasVisibleChildren ? "Свернуть" : "Развернуть"}
          >
            {hasVisibleChildren ? <IconChevronUp size={14} /> : <IconChevronDown size={14} />}
          </div>
        )}
      </div>
    </div>
  );
}

// Вспомогательная функция получения размеров
function getNodeDimensions(settings: OrgChartSettingsValues): { width: number; height: number } {
  const width = settings.compactView ? 160 : 220;
  const height = settings.compactView ? 70 : 90;
  return { width, height };
}

// Простая функция для затемнения цвета (аналог darken из Mantine)
function darken(color: string, amount: number): string {
  // Преобразуем hex в rgb
  let r, g, b;
  if (color.startsWith('#')) {
    const hex = color.slice(1);
    r = parseInt(hex.slice(0, 2), 16);
    g = parseInt(hex.slice(2, 4), 16);
    b = parseInt(hex.slice(4, 6), 16);
  } else if (color.startsWith('rgb')) {
    const matches = color.match(/\d+/g);
    if (matches && matches.length >= 3) {
      r = parseInt(matches[0]);
      g = parseInt(matches[1]);
      b = parseInt(matches[2]);
    } else {
      r = 0; g = 0; b = 0;
    }
  } else {
    r = 0; g = 0; b = 0;
  }
  
  // Затемняем
  r = Math.max(0, Math.floor(r * (1 - amount)));
  g = Math.max(0, Math.floor(g * (1 - amount)));
  b = Math.max(0, Math.floor(b * (1 - amount)));
  
  // Возвращаем hex
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

export default OrgChartNode; 