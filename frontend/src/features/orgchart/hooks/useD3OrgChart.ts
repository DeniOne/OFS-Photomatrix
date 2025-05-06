import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import * as d3 from 'd3';
import { OrgChartNodeData } from '../types/orgChartTypes';
import { OrgChartSettingsValues } from '../components/OrgChartSettings';
import { getNodeDimensions } from '../utils/dimensions';

interface UseD3OrgChartProps {
  data: OrgChartNodeData | null;
  settings: OrgChartSettingsValues;
  width: number;
  height: number;
}

export const useD3OrgChart = ({
  data,
  settings,
  width,
  height,
}: UseD3OrgChartProps) => {
  const [rootNode, setRootNode] = useState<d3.HierarchyPointNode<OrgChartNodeData> | null>(null);
  const [nodes, setNodes] = useState<d3.HierarchyPointNode<OrgChartNodeData>[]>([]);
  const [links, setLinks] = useState<d3.HierarchyPointLink<OrgChartNodeData>[]>([]);
  
  // Создаем рефы без инициализации в D3 
  const svgRef = useRef<SVGSVGElement>(null);
  const gRef = useRef<SVGGElement>(null);
  
  // Храним зум-поведение в реф
  const zoomBehaviorRef = useRef<d3.ZoomBehavior<SVGElement, unknown> | null>(null);
  const initializedRef = useRef(false);

  // Получаем размеры узлов из настроек
  const { width: nodeWidth, height: nodeHeight } = useMemo(() => getNodeDimensions(settings), [settings]);

  // Рассчитываем базовые отступы
  const margin = useMemo(() => ({
    top: 40,
    right: nodeWidth, 
    bottom: 40,
    left: nodeWidth,
  }), [nodeWidth]);

  // Функция для создания и расчета дерева
  const calculateTree = useCallback(() => {
    if (!data) {
      setRootNode(null);
      setNodes([]);
      setLinks([]);
      return;
    }

    try {
      // Создаем иерархию из данных
      const hierarchy = d3.hierarchy(data);
      
      // Настройка генератора макета
      let treeLayout;
      const layoutNodeSize: [number, number] = settings.layout === 'horizontal'
        ? [nodeHeight + settings.siblingGap, nodeWidth + settings.levelGap]
        : [nodeWidth + settings.siblingGap, nodeHeight + settings.levelGap];

      if (settings.layout === 'horizontal') {
        treeLayout = d3.tree<OrgChartNodeData>()
          .nodeSize(layoutNodeSize)
          .separation((a, b) => (a.parent === b.parent ? 1 : 1.2));
      } else if (settings.layout === 'radial') {
        const radius = Math.min(width, height) / 2 - Math.max(margin.top, margin.right);
        treeLayout = d3.tree<OrgChartNodeData>()
          .size([2 * Math.PI, radius])
          .separation((a, b) => (a.parent === b.parent ? 1 : 2) / (a.depth + 1));
      } else { // вертикальный по умолчанию
        treeLayout = d3.tree<OrgChartNodeData>()
          .nodeSize(layoutNodeSize)
          .separation((a, b) => (a.parent === b.parent ? 1 : 1.2));
      }

      // Применяем функцию расчета layout для получения координат
      const root = treeLayout(hierarchy) as d3.HierarchyPointNode<OrgChartNodeData>;

      // Нормализуем координаты для разных типов layout
      if (settings.layout !== 'radial') {
        root.descendants().forEach(d => {
          if (settings.layout === 'horizontal') {
            d.y = d.depth * (nodeWidth + settings.levelGap);
          } else {
            d.y = d.depth * (nodeHeight + settings.levelGap);
          }
        });
      }

      // Обновляем состояния
      setRootNode(root);
      setNodes(root.descendants());
      setLinks(root.links());
      
    } catch (err) {
      console.error('Ошибка при расчете дерева:', err);
      // В случае ошибки сбрасываем состояния
      setRootNode(null);
      setNodes([]);
      setLinks([]);
    }
  }, [data, settings, width, height, margin, nodeWidth, nodeHeight]);

  // Эффект для расчета дерева при изменении данных или настроек
  useEffect(() => {
    calculateTree();
  }, [calculateTree]);

  // Функция для инициализации D3 и зум-поведения
  const initializeD3 = useCallback(() => {
    // Проверяем наличие DOM-элементов
    if (!svgRef.current) return;
    
    try {
      const svg = d3.select(svgRef.current);
      
      // Если еще не инициализировано зум-поведение, создаем его
      if (!zoomBehaviorRef.current) {
        // Создаем зум-поведение
        const zoom = d3.zoom<SVGElement, unknown>()
          .scaleExtent([0.1, 3]) // мин. и макс. масштаб
          .on('zoom', (event) => {
            // Эта функция вызывается при зуме/перемещении
            d3.select(gRef.current)
              .attr('transform', event.transform.toString());
          });
        
        // Сохраняем зум-поведение в ref
        zoomBehaviorRef.current = zoom;
        
        // Применяем зум к SVG
        svg.call(zoom);
        
        // Начальная трансформация
        const initialTransform = d3.zoomIdentity
          .translate(width / 2, height / 2)
          .scale(settings.zoom || 0.8);
        
        svg.call(zoom.transform, initialTransform);
      }
      
      initializedRef.current = true;
    } catch (err) {
      console.error('Ошибка при инициализации D3:', err);
    }
  }, [width, height, settings.zoom]);

  // Эффект для инициализации D3 один раз после монтирования
  useEffect(() => {
    if (svgRef.current && !initializedRef.current) {
      initializeD3();
    }
  }, [initializeD3]);

  // Функция для зума к указанному узлу
  const zoomToNode = useCallback((nodeId: string) => {
    if (!svgRef.current || !zoomBehaviorRef.current || !rootNode) return;
    
    try {
      // Найдем узел по id
      let targetNode = null;
      rootNode.each(node => {
        if (node.data && node.data.id === nodeId) {
          targetNode = node;
        }
      });
      
      if (!targetNode) {
        console.warn(`Узел с id ${nodeId} не найден`);
        return;
      }
      
      // Получаем координаты целевого узла
      const x = settings.layout === 'horizontal' ? targetNode.x : targetNode.x;
      const y = settings.layout === 'horizontal' ? targetNode.y : targetNode.y;
      
      // Создаем трансформацию для центрирования
      const transform = d3.zoomIdentity
        .translate(width / 2 - y, height / 2 - x)
        .scale(settings.zoom || 0.8);
      
      // Применяем трансформацию с анимацией
      d3.select(svgRef.current)
        .transition()
        .duration(500)
        .call(zoomBehaviorRef.current.transform, transform);
    } catch (err) {
      console.error('Ошибка при зуме к узлу:', err);
    }
  }, [rootNode, settings.layout, settings.zoom, width, height]);

  // Функция для сброса зума
  const resetZoom = useCallback(() => {
    if (!svgRef.current || !zoomBehaviorRef.current) return;
    
    try {
      // Создаем начальную трансформацию
      const initialTransform = d3.zoomIdentity
        .translate(width / 2, height / 2)
        .scale(settings.zoom || 0.8);
      
      // Применяем трансформацию с анимацией
      d3.select(svgRef.current)
        .transition()
        .duration(500)
        .call(zoomBehaviorRef.current.transform, initialTransform);
    } catch (err) {
      console.error('Ошибка при сбросе зума:', err);
    }
  }, [width, height, settings.zoom]);

  // Функция для масштабирования
  const zoom = useCallback((scale: number) => {
    if (!svgRef.current || !zoomBehaviorRef.current) return;
    
    try {
      // Получаем текущую трансформацию
      const currentTransform = d3.zoomTransform(svgRef.current);
      
      // Создаем новую трансформацию с измененным масштабом
      const newTransform = d3.zoomIdentity
        .translate(currentTransform.x, currentTransform.y)
        .scale(currentTransform.k * scale);
      
      // Применяем трансформацию с анимацией
      d3.select(svgRef.current)
        .transition()
        .duration(300)
        .call(zoomBehaviorRef.current.transform, newTransform);
    } catch (err) {
      console.error('Ошибка при масштабировании:', err);
    }
  }, []);

  // Функции для увеличения и уменьшения
  const zoomIn = useCallback(() => zoom(1.2), [zoom]);
  const zoomOut = useCallback(() => zoom(0.8), [zoom]);

  return {
    svgRef,
    gRef,
    nodes,
    links,
    zoomToNode,
    resetZoom,
    zoomIn,
    zoomOut,
    rootNode
  };
}; 