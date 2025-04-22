import { useState } from 'react';
import { Box, Text, Button, Group, Collapse, ActionIcon, Badge, Tooltip } from '@mantine/core';
import { IconChevronRight, IconChevronDown, IconEdit, IconTrash, IconPlus } from '@tabler/icons-react';
import { Division, DivisionWithChildren } from '../../../types/division';

// Функция для преобразования плоского списка в дерево
export const buildDivisionTree = (divisions: Division[]): DivisionWithChildren[] => {
  const divisionMap: Record<number, DivisionWithChildren> = {};
  const rootDivisions: DivisionWithChildren[] = [];

  // Сначала создаем карту всех подразделений с пустым массивом children
  divisions.forEach(division => {
    divisionMap[division.id] = { ...division, children: [] };
  });

  // Затем выстраиваем иерархию
  divisions.forEach(division => {
    const divisionWithChildren = divisionMap[division.id];
    
    if (division.parent_id === null) {
      // Если нет родителя, это корневое подразделение
      rootDivisions.push(divisionWithChildren);
    } else if (divisionMap[division.parent_id]) {
      // Если есть родитель, добавляем как дочернее
      divisionMap[division.parent_id].children.push(divisionWithChildren);
    } else {
      // Если родителя нет в списке (ошибка данных), добавляем как корневое
      rootDivisions.push(divisionWithChildren);
    }
  });

  return rootDivisions;
};

interface DivisionNodeProps {
  division: DivisionWithChildren;
  level: number;
  onEdit: (division: Division) => void;
  onDelete: (id: number) => void;
  onAddChild: (parentId: number) => void;
}

function DivisionNode({ division, level, onEdit, onDelete, onAddChild }: DivisionNodeProps) {
  const [isOpen, setIsOpen] = useState(level < 1); // Автоматически раскрываем первый уровень
  const hasChildren = division.children.length > 0;
  
  return (
    <Box>
      <Group gap="xs" mb={5} style={{ paddingLeft: level * 20 }}>
        {hasChildren ? (
          <ActionIcon 
            size="sm" 
            variant="subtle" 
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <IconChevronDown size="1rem" /> : <IconChevronRight size="1rem" />}
          </ActionIcon>
        ) : (
          <Box style={{ width: 24 }} />
        )}
        
        <Box style={{ flexGrow: 1 }}>
          <Group gap="xs">
            <Text weight={500}>
              {division.name}
            </Text>
            <Text size="xs" color="dimmed">
              ({division.code})
            </Text>
            <Badge
              size="xs"
              color={division.is_active ? 'green' : 'red'}
            >
              {division.is_active ? 'Активно' : 'Неактивно'}
            </Badge>
          </Group>
        </Box>
        
        <Group gap="xs">
          <Tooltip label="Добавить подразделение">
            <ActionIcon 
              size="sm" 
              variant="subtle" 
              color="blue"
              onClick={() => onAddChild(division.id)}
            >
              <IconPlus size="1rem" />
            </ActionIcon>
          </Tooltip>
          <Tooltip label="Редактировать">
            <ActionIcon 
              size="sm" 
              variant="subtle" 
              color="blue"
              onClick={() => onEdit(division)}
            >
              <IconEdit size="1rem" />
            </ActionIcon>
          </Tooltip>
          <Tooltip label="Удалить">
            <ActionIcon 
              size="sm" 
              variant="subtle" 
              color="red"
              onClick={() => onDelete(division.id)}
            >
              <IconTrash size="1rem" />
            </ActionIcon>
          </Tooltip>
        </Group>
      </Group>
      
      {hasChildren && (
        <Collapse in={isOpen}>
          <Box>
            {division.children.map(child => (
              <DivisionNode
                key={child.id}
                division={child}
                level={level + 1}
                onEdit={onEdit}
                onDelete={onDelete}
                onAddChild={onAddChild}
              />
            ))}
          </Box>
        </Collapse>
      )}
    </Box>
  );
}

interface DivisionsTreeProps {
  divisions: Division[];
  onEdit: (division: Division) => void;
  onDelete: (id: number) => void;
  onAddChild: (parentId: number) => void;
  onAddRoot: () => void;
  organizationId?: number | null;
}

export function DivisionsTree({ 
  divisions, 
  onEdit, 
  onDelete,
  onAddChild,
  onAddRoot,
  organizationId 
}: DivisionsTreeProps) {
  // Фильтруем подразделения по организации, если указан ID организации
  const filteredDivisions = organizationId
    ? divisions.filter(div => div.organization_id === organizationId)
    : divisions;
  
  // Строим дерево из отфильтрованных подразделений
  const divisionTree = buildDivisionTree(filteredDivisions);
  
  return (
    <Box>
      <Group justify="flex-end" mb="md">
        <Button 
          leftSection={<IconPlus size="1rem" />}
          onClick={onAddRoot}
        >
          Новое корневое подразделение
        </Button>
      </Group>
      
      {divisionTree.length === 0 ? (
        <Text ta="center" py="lg">
          Подразделения не найдены
        </Text>
      ) : (
        <Box style={{ border: '1px solid #373A40', borderRadius: '4px', padding: '10px' }}>
          {divisionTree.map(division => (
            <DivisionNode
              key={division.id}
              division={division}
              level={0}
              onEdit={onEdit}
              onDelete={onDelete}
              onAddChild={onAddChild}
            />
          ))}
        </Box>
      )}
    </Box>
  );
} 