import { useState, useEffect, useRef, forwardRef, useImperativeHandle, useCallback } from 'react';
import ReactDOM from 'react-dom/client';
import * as d3 from 'd3';
import { Modal, Text, Group, Stack, Paper, Title, Grid, Badge, Button, ActionIcon } from '@mantine/core';
import { defaultOrgChartSettings } from '../types/orgChartSettingsTypes';
import { OrgChartHandle, OrgChartProps, OrgChartNodeData, OrgChartViewType } from '../types/orgChartTypes';
import { getNodeDimensions } from '../utils/dimensions';
import { IconZoomIn, IconZoomOut, IconFocus2 } from '@tabler/icons-react';
import OrgChartNode from './OrgChartNode';

// Тип для хранения смещений узлов
type NodeOffsets = Map<string, { dx: number, dy: number }>;

// Вспомогательное хранилище для отслеживания позиций при перетаскивании
const dragState = {
  initialPositions: new Map<string, { x: number, y: number }>(),
  isDragging: false,
  draggedNodeId: '',
  movedEnough: false, // Флаг, показывающий, было ли смещение
  startX: 0, // Начальная координата X для определения клика
  startY: 0, // Начальная координата Y для определения клика
  currentDx: 0, // Текущее смещение X во время drag
  currentDy: 0, // Текущее смещение Y во время drag
  reset() {
    this.initialPositions.clear();
    this.isDragging = false;
    this.draggedNodeId = '';
    this.movedEnough = false;
    this.startX = 0;
    this.startY = 0;
    this.currentDx = 0;
    this.currentDy = 0;
  }
};

// Компонент организационной диаграммы с поддержкой разных типов визуализации
const OrgChart = forwardRef<OrgChartHandle, OrgChartProps>(({
  data,
  settings: userSettings = {},
  onNodeClick,
  searchTerm = '',
  viewType = 'business',
  width: containerWidth = 800,
  height: containerHeight = 600,
}, ref) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const [rootNode, setRootNode] = useState<d3.HierarchyNode<OrgChartNodeData> | null>(null);
  const [selectedNode, setSelectedNode] = useState<OrgChartNodeData | null>(null);
  const [nodeDetailsOpen, setNodeDetailsOpen] = useState<boolean>(false);
  const [focusedNode, setFocusedNode] = useState<string | null>(null);
  
  // Хранилище React корней для всех ForeignObject элементов
  const reactRootsRef = useRef(new Map<Element, ReactDOM.Root>());
  
  // Объединяем настройки
  const settings = {
    ...defaultOrgChartSettings,
    ...userSettings
  };
  
  // Размеры узлов
  const { width: nodeWidth, height: nodeHeight } = getNodeDimensions(settings);
  
  const [nodeOffsets, setNodeOffsets] = useState<NodeOffsets>(new Map());
  const svgGRef = useRef<SVGGElement | null>(null); // Реф для группы <g>
  
  // Очистка React корней ТОЛЬКО при размонтировании или смене data
  const cleanupReactRoots = useCallback((nodesToRemove: Set<string> = new Set()) => {
    reactRootsRef.current.forEach((root, element) => {
      // Проверяем, связан ли корень с удаляемым узлом по data-id родительского <g>
      const parentG = element.closest('g.node');
      const nodeId = parentG?.getAttribute('data-id');
      if (nodesToRemove.size === 0 || (nodeId && nodesToRemove.has(nodeId))) {
        try {
          root.unmount();
        } catch (e) { console.warn('Ошибка при размонтировании React корня:', e); }
        reactRootsRef.current.delete(element);
      }
    });
  }, []);
  
  // Обработчик для переключения состояния узла (свернут/развернут)
  const toggleNode = useCallback((nodeId: string) => {
    if (!rootNode || !data) return;
    
    // Клонируем данные для не мутирования источника
    const newRoot = d3.hierarchy(data);
    
    // Находим нужный узел
    const targetNode = newRoot.descendants().find(node => node.data.id === nodeId);
    if (!targetNode) return;
    
    // Переключаем видимость потомков
    if (targetNode.children) {
      // Если узел раскрыт - сворачиваем его
      // @ts-ignore - _children используется d3 для скрытых узлов
      targetNode._children = targetNode.children;
      // @ts-ignore
      targetNode.children = undefined;
    } else {
      // Если узел свернут - раскрываем его
      // @ts-ignore
      targetNode.children = targetNode._children;
      // @ts-ignore
      targetNode._children = undefined;
    }
    
    // Обновляем дерево с изменениями
    setRootNode(newRoot);
  }, [data, rootNode]);
  
  // Обработчик для просмотра деталей узла
  const showNodeDetails = useCallback((nodeData: OrgChartNodeData) => {
    setSelectedNode(nodeData);
    setNodeDetailsOpen(true);
  }, []);
  
  // Функция для фокусировки (масштабирования) на узле
  const focusOnNode = useCallback((nodeId: string) => {
    if (!rootNode || !svgRef.current || !zoomRef.current) return;
    
    // Находим нужный узел
    const targetNode = rootNode.descendants().find(node => node.data.id === nodeId);
    if (!targetNode) return;
    
    // Устанавливаем фокус
    setFocusedNode(nodeId);
    
    // Трансформируем вид для центрирования на узле
    const scale = 1.2; // Масштаб приближения
    
    // Получаем координаты узла
    const x = targetNode.x || 0;
    const y = targetNode.y || 0;
    
    // Центрируем узел
    const tx = containerWidth / 2 - x * scale;
    const ty = containerHeight / 3 - y * scale;
    
    // Применяем трансформацию
    zoomRef.current.transform(
      d3.select(svgRef.current),
      d3.zoomIdentity.translate(tx, ty).scale(scale)
    );
  }, [containerWidth, containerHeight, rootNode]);
  
  // Функция для сброса фокуса
  const resetFocus = useCallback(() => {
    if (!rootNode || !svgRef.current || !zoomRef.current) return;
    
    setFocusedNode(null);
    
    // Определяем масштаб в зависимости от количества узлов
    const nodeCount = rootNode.descendants().length;
    const dynamicScale = Math.min(Math.max(0.3, 4 / Math.sqrt(nodeCount)), 1);
    
    // Возвращаем общий вид
    zoomRef.current.transform(
      d3.select(svgRef.current),
      d3.zoomIdentity.translate(containerWidth / 4, containerHeight / 6).scale(dynamicScale)
    );
  }, [containerWidth, containerHeight, rootNode]);
  
  // Создаем иерархию из данных при их изменении
  useEffect(() => {
    if (!data) return;
    
    // Создаем иерархическую структуру для D3
    const root = d3.hierarchy(data);
    setRootNode(root);
    
  }, [data]);
  
  // Экспортируем API для внешнего управления
  useImperativeHandle(ref, () => ({
    zoomIn: () => {
      if (!zoomRef.current || !svgRef.current) return;
      zoomRef.current.scaleBy(d3.select(svgRef.current), 1.2);
    },
    zoomOut: () => {
      if (!zoomRef.current || !svgRef.current) return;
      zoomRef.current.scaleBy(d3.select(svgRef.current), 0.8);
    },
    resetZoom: () => {
      if (!zoomRef.current || !svgRef.current) return;
      zoomRef.current.transform(
        d3.select(svgRef.current),
        d3.zoomIdentity.translate(containerWidth / 4, containerHeight / 6).scale(0.8)
      );
    },
    fitToScreen: () => {
      if (!zoomRef.current || !svgRef.current || !rootNode) return;
      
      // Определяем масштаб в зависимости от количества узлов
      const nodeCount = rootNode.descendants().length;
      const dynamicScale = Math.min(Math.max(0.3, 4 / Math.sqrt(nodeCount)), 1);
      
      zoomRef.current.transform(
        d3.select(svgRef.current),
        d3.zoomIdentity.translate(containerWidth / 4, containerHeight / 6).scale(dynamicScale)
      );
    },
    // Добавляем функцию для сворачивания/разворачивания узла
    toggleNode,
    // Добавляем функцию для фокусировки на узле
    focusOnNode,
    // Сброс фокуса
    resetFocus,
    // Заглушки для совместимости с интерфейсом OrgChartHandle
    zoomToNode: focusOnNode,
    exportAsImage: async (): Promise<string | null> => {
      // Здесь в будущем можно добавить код для экспорта изображения
      return Promise.resolve(null);
    }
  } as OrgChartHandle));
  
  // Получение имени типа узла для отображения
  const getNodeTypeName = (type?: string, id?: string, viewType: OrgChartViewType = 'business') => {
    // Для юридической структуры используем другие наименования
    if (viewType === 'legal') {
      if (id?.startsWith('org-')) return 'Юридическое лицо';
      if (id?.startsWith('div-')) return 'Подразделение юрлица';
    }
    
    // Для локационной структуры
    if (viewType === 'location') {
      if (id?.startsWith('org-')) return 'Локация';
      if (id?.startsWith('div-')) return 'Подразделение локации';
    }
    
    // Для бизнес-структуры
    if (id?.startsWith('org-')) {
      if (type === 'board' || id.includes('board-')) return 'Совет директоров';
      return 'Организация';
    }
    if (id?.startsWith('div-')) return 'Подразделение';
    if (id?.startsWith('sec-')) return 'Секция';
    if (id?.startsWith('func-') || type === 'function') return 'Функция';
    if (id?.startsWith('pos-') || type === 'position') return 'Должность';
    
    switch(type) {
      case 'department': return 'Подразделение';
      case 'division': return 'Отдел';
      case 'section': return 'Секция';
      case 'position': return 'Должность';
      case 'function': return 'Функция';
      case 'board': return 'Совет директоров';
      default: return 'Неизвестный тип';
    }
  };
  
  // Добавляем функцию для определения цвета связи между узлами
  const getLinkColor = (source: d3.HierarchyPointNode<OrgChartNodeData>, target: d3.HierarchyPointNode<OrgChartNodeData>): string => {
    // Для связей между узлами разных типов
    if (source.data.type === 'function' && target.data.type) {
      return '#ff9800'; // Оранжевый для функциональных связей
    }
    
    // Если это связь между должностью и сотрудником
    if (source.data.type === 'position' && target.data.staffId) {
      return '#9c27b0'; // Фиолетовый для назначений сотрудников
    }

    // Для обычной иерархии - цвет зависит от уровня в дереве
    const sourceLevelData = source.data.level || source.data.position_level || source.depth;
    const targetLevelData = target.data.level || target.data.position_level || target.depth;
    
    // Определяем разницу уровней
    const levelDiff = Math.abs(sourceLevelData - targetLevelData);
    
    // Выбираем цвет в зависимости от разницы уровней
    switch (levelDiff) {
      case 0: // Узлы на одном уровне (равноправные)
        return '#78909c'; // Серый
      case 1: // Прямое подчинение
        return '#4285f4'; // Синий Google
      case 2: // Через уровень
        return '#0f9d58'; // Зеленый Google
      case 3: // Дальнее подчинение
        return '#db4437'; // Красный Google
      default: // Очень дальнее подчинение
        return '#a2a2a2'; // Светло-серый
    }
  };

  // Функция для расчета толщины линии связи
  const getLinkWidth = (source: d3.HierarchyPointNode<OrgChartNodeData>, target: d3.HierarchyPointNode<OrgChartNodeData>): number => {
    // Более толстые линии для близких уровней, более тонкие для дальних
    const sourceLevelData = source.data.level || source.data.position_level || source.depth;
    const targetLevelData = target.data.level || target.data.position_level || target.depth;
    const levelDiff = Math.abs(sourceLevelData - targetLevelData);
    
    return Math.max(3 - levelDiff * 0.5, 1); // От 3px до 1px
  };
  
  // --- Drag Handler ---
  const dragThreshold = 3; // Порог смещения для начала перетаскивания

  const dragHandler = d3.drag<SVGGElement, d3.HierarchyPointNode<OrgChartNodeData>>()
    .on('start', function(event, d) {
        dragState.startX = event.x;
        dragState.startY = event.y;
        dragState.movedEnough = false;
        const currentOffset = nodeOffsets.get(d.data.id) || { dx: 0, dy: 0 };
        dragState.currentDx = currentOffset.dx;
        dragState.currentDy = currentOffset.dy;

        d3.select(this).raise(); // Поднимаем узел наверх
        event.sourceEvent.stopPropagation(); // Останавливаем всплытие для предотвращения зума

        dragState.isDragging = true; 
        dragState.draggedNodeId = d.data.id;

        // Сохраняем НАЧАЛЬНЫЕ layout-позиции (БЕЗ текущего смещения)
        const initialLayoutPos = { x: d.x - dragState.currentDx, y: d.y - dragState.currentDy };
        dragState.initialPositions.clear(); // Очищаем перед новым драгом
        dragState.initialPositions.set(d.data.id, initialLayoutPos);

        // Сохраняем начальные layout-позиции потомков
        d.descendants().slice(1).forEach(node => {
            const offset = nodeOffsets.get(node.data.id) || { dx: 0, dy: 0 };
            // Сохраняем позицию без учета сохраненного смещения
            dragState.initialPositions.set(node.data.id, { x: node.x - offset.dx, y: node.y - offset.dy });
        });
    })
    .on('drag', function(event, d) {
        if (!dragState.isDragging) return;

        const dxMoved = Math.abs(event.x - dragState.startX);
        const dyMoved = Math.abs(event.y - dragState.startY);

        // Если двигаем достаточно - помечаем как реальный драг
        if (!dragState.movedEnough && (dxMoved > dragThreshold || dyMoved > dragThreshold)) {
            dragState.movedEnough = true;
        }

        // Если не двигали достаточно, выходим (это еще может быть клик)
        if (!dragState.movedEnough) return;

        // Смещение относительно НАЧАЛА ПЕРЕТАСКИВАНИЯ
        const dragDx = event.x - dragState.startX;
        const dragDy = event.y - dragState.startY;

        // --- Обновляем данные узлов (d.x, d.y) ---
        dragState.initialPositions.forEach((initialLayoutPos, nodeId) => {
            const nodeData = (nodeId === d.data.id) ? d : d.descendants().find(n => n.data.id === nodeId);
            if (nodeData) {
                const nodeCurrentOffset = nodeOffsets.get(nodeId) || { dx: 0, dy: 0 };
                // Новое общее смещение для этого узла
                const nodeNewTotalDx = nodeCurrentOffset.dx + dragDx;
                const nodeNewTotalDy = nodeCurrentOffset.dy + dragDy;
                // Обновляем координаты в данных D3
                nodeData.x = initialLayoutPos.x + nodeNewTotalDx;
                nodeData.y = initialLayoutPos.y + nodeNewTotalDy;
            }
        });

        // --- Обновляем DOM ---
        // Двигаем текущий узел (<g>)
        d3.select(this).attr('transform', `translate(${d.x},${d.y})`);

        // Двигаем потомков (<g>)
        if (svgGRef.current) {
             const svgGSelection = d3.select(svgGRef.current);
             d.descendants().slice(1).forEach(node => {
                const nodeElementSelection = svgGSelection.select<SVGGElement>(`g[data-id="${node.data.id}"]`);
                if (!nodeElementSelection.empty()) {
                    nodeElementSelection.attr('transform', `translate(${node.x},${node.y})`);
                }
            });

            // Обновляем связанные линии (<path>)
            svgGSelection.selectAll<SVGPathElement, d3.HierarchyPointLink<OrgChartNodeData>>('path.link')
                .filter(linkData =>
                    dragState.initialPositions.has(linkData.source.data.id) ||
                    dragState.initialPositions.has(linkData.target.data.id)
                )
                .attr('d', d3.linkVertical<d3.HierarchyPointLink<OrgChartNodeData>, d3.HierarchyPointNode<OrgChartNodeData>>()
                    .x(n => n.x).y(n => n.y) // Используем обновленные n.x, n.y
                );
        }
    })
    .on('end', function(event, d) {
        if (!dragState.movedEnough) {
            // --- Клик ---
            console.log('Drag interpreted as click for node:', d.data.id);
            // Вызываем обработчик клика, переданный в пропсах
            if (onNodeClick) {
                 onNodeClick(d.data.id);
            } else {
                 // Фоллбэк: показать детали, если onNodeClick не задан
                 showNodeDetails(d.data);
            }
        } else {
            // --- Успешное перетаскивание ---
            console.log('Drag ended successfully for node:', d.data.id);
            // Сохраняем новые смещения в стейт React
            setNodeOffsets(prevOffsets => {
                const newOffsets = new Map(prevOffsets);
                const dragDx = event.x - dragState.startX;
                const dragDy = event.y - dragState.startY;

                dragState.initialPositions.forEach((_, nodeId) => {
                    const currentOffset = prevOffsets.get(nodeId) || { dx: 0, dy: 0 };
                    newOffsets.set(nodeId, { dx: currentOffset.dx + dragDx, dy: currentOffset.dy + dragDy });
                });
                return newOffsets;
            });
        }
        // Сбрасываем состояние драга
        dragState.reset();
    });

  // Основной useEffect для рендеринга и обновлений D3
  useEffect(() => {
    console.log("OrgChart: useEffect triggered");
    
    if (!data || !svgRef.current) {
        console.log("OrgChart: No data or svgRef, exiting useEffect");
        return;
    }
    
    console.log("OrgChart: Starting render/update");

    // Создаем иерархию D3
    const root = d3.hierarchy(data);
    const nodeCount = root.descendants().length; // Считаем узлы
    
    // Очищаем предыдущие React корни при перерисовке
    cleanupReactRoots();
    
    // Отладочная информация
    console.log(`OrgChart: Rendering ${viewType} view with ${nodeCount} nodes`);
    console.log("OrgChart: Container dimensions:", { width: containerWidth, height: containerHeight });
    
    try {
      // Очищаем предыдущее содержимое
      d3.select(svgRef.current).selectAll('*').remove();
      
      // Создаем SVG и группу для графа
      const svg = d3.select(svgRef.current);
      const g = svg.append('g');
      svgGRef.current = g.node();
      
      // Определяем масштаб в зависимости от количества узлов
      const dynamicScale = Math.min(Math.max(0.3, 4 / Math.sqrt(nodeCount)), 1);
      
      // Выбираем и настраиваем генератор дерева в зависимости от типа схемы
      let treeLayout: d3.TreeLayout<OrgChartNodeData>;
      
      // Для разных типов схем используем разные настройки
      if (viewType === 'legal' || viewType === 'location') {
        // Для юридической и территориальной - более кластеризованное отображение
        treeLayout = d3.tree<OrgChartNodeData>()
          .size([containerWidth * 0.85, containerHeight * 0.7])
          .nodeSize([nodeWidth * 1.8, nodeHeight * 3]);
      } else {
        // Для бизнес-структуры - более вытянутое иерархическое отображение
        treeLayout = d3.tree<OrgChartNodeData>()
          .size([containerWidth, containerHeight * 0.85])
          .nodeSize([nodeWidth * 2.5, nodeHeight * 4]);
      }
      
      // Применяем генератор для получения координат
      const treeData = treeLayout(root);
      
      // Применяем сохраненные смещения к позициям из layout
      treeData.each(node => {
        const offset = nodeOffsets.get(node.data.id);
        if (offset) {
          node.x += offset.dx;
          node.y += offset.dy;
        }
      });
      
      // Центрируем дерево
      const svgG = g.attr('transform', `translate(${containerWidth / 2}, 50)`);
      
      // Создаем генератор линий для связей
      const linkGenerator = d3.linkVertical<d3.HierarchyPointLink<OrgChartNodeData>, d3.HierarchyPointNode<OrgChartNodeData>>()
        .x((d) => d.x)
        .y((d) => d.y);
      
      // Добавляем узлы
      const nodes = svgG.selectAll<SVGGElement, d3.HierarchyPointNode<OrgChartNodeData>>('.node')
        .data(treeData.descendants())
        .enter()
        .append('g')
        .attr('class', 'node')
        .attr('data-id', d => d.data.id)
        .attr('transform', d => `translate(${d.x},${d.y})`)
        .attr('opacity', 0)
        .call(dragHandler)
        .call(enter => enter.transition().duration(300).attr('opacity', 1));
      
      // Для каждого узла создаем React-компонент
      nodes.each(function(d) {
        const groupElement = this;
        // Проверяем, есть ли уже foreignObject и React корень
        let foSelection = d3.select(groupElement).select<SVGForeignObjectElement>('foreignObject');
        let reactRoot = reactRootsRef.current.get(groupElement);

        if (foSelection.empty()) {
            // Создаем, если нет
            const { width: nodeW, height: nodeH } = getNodeDimensions(settings);
            foSelection = d3.select(groupElement).append('foreignObject')
                .attr('x', -nodeW / 2)
                .attr('y', -nodeH / 2)
                .attr('width', nodeW)
                .attr('height', nodeH);
            
            const container = document.createElement('div');
            foSelection.node()!.appendChild(container);
            reactRoot = ReactDOM.createRoot(container);
            reactRootsRef.current.set(groupElement, reactRoot);
        }

        // Рендерим/обновляем React компонент
        reactRoot?.render(
            <OrgChartNode 
                nodeData={d}
                settings={settings}
                onExpandCollapse={toggleNode}
                isHighlighted={focusedNode === d.data.id || Boolean(searchTerm && (
                  (d.data.name?.toLowerCase().includes(searchTerm.toLowerCase())) ||
                  (d.data.title?.toLowerCase().includes(searchTerm.toLowerCase())) ||
                  (d.data.staffName?.toLowerCase().includes(searchTerm.toLowerCase()))
                ))}
                onShowDetails={showNodeDetails}
            />
        );
      });
      
      // Обновляем все связи (перемещаем этот блок ПОСЛЕ создания узлов)
      const links = svgG.selectAll<SVGPathElement, d3.HierarchyPointLink<OrgChartNodeData>>('.link')
        .data(treeData.links(), d => `${d.source.data.id}-${d.target.data.id}`)
        .join(
            enter => enter.append('path')
                .attr('class', 'link')
                .attr('fill', 'none')
                .attr('opacity', 0)
                .attr('stroke', d => getLinkColor(d.source, d.target))
                .attr('stroke-width', d => getLinkWidth(d.source, d.target))
                .attr('d', linkGenerator)
                .call(enter => enter.transition().duration(300).attr('opacity', 0.7)),
            update => update
                .call(update => update.transition().duration(300)
                    .attr('stroke', d => getLinkColor(d.source, d.target)) 
                    .attr('stroke-width', d => getLinkWidth(d.source, d.target))
                    .attr('d', linkGenerator)),
            exit => exit
                .call(exit => exit.transition().duration(300).attr('opacity', 0).remove())
        )
        .on('mouseover', function(event, d) {
          d3.select(this)
            .attr('stroke-width', getLinkWidth(d.source, d.target) + 1)
            .attr('opacity', 1);
        })
        .on('mouseout', function(event, d) {
          d3.select(this)
            .attr('stroke-width', getLinkWidth(d.source, d.target))
            .attr('opacity', 0.7);
        });
      
      // Создаем зум-поведение
      const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.1, 2])
        .on('zoom', (event) => {
          g.attr('transform', event.transform);
        });
      
      // Сохраняем зум в реф
      zoomRef.current = zoom;
      
      // Применяем зум к SVG
      svg.call(zoom);
      
      // Устанавливаем начальный масштаб для всего дерева
      svg.call(
        zoom.transform, 
        d3.zoomIdentity.translate(containerWidth / 4, containerHeight / 6).scale(dynamicScale)
      );
      
    } catch (err) {
      console.error('Ошибка при создании графа:', err);
    }
    
  }, [data, settings, containerWidth, containerHeight, viewType, nodeOffsets, searchTerm, focusedNode, cleanupReactRoots, toggleNode, showNodeDetails, nodeWidth, nodeHeight, onNodeClick]);

  // useEffect для очистки React корней при размонтировании
  useEffect(() => {
    return () => cleanupReactRoots();
  }, [cleanupReactRoots]);
  
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden' }}>
      <svg
        ref={svgRef}
        width="100%" 
        height="100%" 
        style={{
          background: '#1a1b1e',
          borderRadius: '8px',
          display: 'block',
        }}
      />
      
      {/* Кнопки для управления фокусом */}
      {focusedNode && (
        <div style={{
          position: 'absolute',
          bottom: 10,
          right: 10,
          display: 'flex',
          gap: 5,
          backgroundColor: 'rgba(0,0,0,0.5)',
          padding: '5px',
          borderRadius: '5px',
          zIndex: 10
        }}>
          <ActionIcon variant="filled" color="blue" onClick={resetFocus} title="Вернуться к общему виду">
            <IconFocus2 size={16} />
          </ActionIcon>
          <ActionIcon variant="filled" color="green" onClick={() => zoomRef.current?.scaleBy(d3.select(svgRef.current!), 1.2)} title="Приблизить">
            <IconZoomIn size={16} />
          </ActionIcon>
          <ActionIcon variant="filled" color="yellow" onClick={() => zoomRef.current?.scaleBy(d3.select(svgRef.current!), 0.8)} title="Отдалить">
            <IconZoomOut size={16} />
          </ActionIcon>
        </div>
      )}
      
      {/* Модальное окно для просмотра подробной информации узла */}
      <Modal
        opened={nodeDetailsOpen}
        onClose={() => setNodeDetailsOpen(false)}
        title={<Title order={4}>{selectedNode?.name}</Title>}
        size="lg"
        zIndex={20}
      >
        {selectedNode && (
          <Stack>
            <Paper p="md" withBorder>
              <Grid>
                {selectedNode.type && (
                  <Grid.Col span={6}><Group><Text fw={500}>Тип:</Text><Text>{getNodeTypeName(selectedNode.type, selectedNode.id, viewType)}</Text></Group></Grid.Col>
                )}
                {selectedNode.code && (
                  <Grid.Col span={6}><Group><Text fw={500}>Код:</Text><Badge>{selectedNode.code}</Badge></Group></Grid.Col>
                )}
                {selectedNode.title && (
                   <Grid.Col span={12}><Group><Text fw={500}>Должность/Описание:</Text><Text>{selectedNode.title}</Text></Group></Grid.Col>
                )}
                {selectedNode.staffId && (
                   <Grid.Col span={12}><Group><Text fw={500}>Сотрудник:</Text><Text>{selectedNode.staffName || selectedNode.staffId}</Text></Group></Grid.Col>
                )}
                {selectedNode.level !== undefined && (
                   <Grid.Col span={6}><Group><Text fw={500}>Уровень:</Text><Text>{selectedNode.level}</Text></Group></Grid.Col>
                )}
                {selectedNode.has_ckp !== undefined && (
                   <Grid.Col span={6}>
                    <Group>
                      <Text fw={500}>ЦКП:</Text>
                      <Badge color={selectedNode.has_ckp ? "green" : "gray"}>
                        {selectedNode.has_ckp ? "Имеет" : "Отсутствует"}
                      </Badge>
                    </Group>
                   </Grid.Col>
                )}
              </Grid>
            </Paper>
            <Group justify="space-between" w="100%">
              <Button 
                variant="outline" 
                color="blue" 
                onClick={() => {
                  setNodeDetailsOpen(false);
                  focusOnNode(selectedNode.id);
                }}
              >
                Сфокусировать
              </Button>
              <Button onClick={() => setNodeDetailsOpen(false)}>Закрыть</Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </div>
  );
});

export default OrgChart; 