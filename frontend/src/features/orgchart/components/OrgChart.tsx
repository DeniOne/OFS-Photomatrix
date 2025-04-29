import React, { useRef, useEffect, useState, useCallback, forwardRef, useImperativeHandle } from 'react';
import ReactDOM from 'react-dom/client';
import * as d3 from 'd3';
import { Box, Text, useMantineTheme } from '@mantine/core';
import { OrgChartSettingsValues, defaultOrgChartSettings } from './OrgChartSettings';
import OrgChartNodeComponent, { OrgChartNode as OrgChartNodeData } from './OrgChartNode';
import { OrgChartHandle } from './OrgChart';

const getNodeDimensions = (settings: OrgChartSettingsValues) => {
  const width = settings.compactView ? 120 : 160;
  const height = settings.compactView ? 60 : 80;
  return { width, height };
};

export interface OrgChartHandle {
  centerOnNode: (nodeId: string) => void;
  resetZoom: () => void; 
}

const OrgChart = forwardRef<OrgChartHandle, OrgChartProps>(({
  width,
  height,
  initialData,
  userSettings,
  onNodeClick,
  searchTerm
}, ref) => {
  const theme = useMantineTheme();
  const svgRef = useRef<SVGSVGElement>(null);
  const gRef = useRef<SVGGElement>(null);
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown>>();
  const rootRef = useRef<d3.HierarchyPointNode<OrgChartNodeData>>();
  const [nodes, setNodes] = useState<d3.HierarchyPointNode<OrgChartNodeData>[]>([]);
  const [links, setLinks] = useState<d3.HierarchyPointLink<OrgChartNodeData>[]>([]);
  
  const [chartData, setChartData] = useState<OrgChartNodeData>(initialData);

  const [highlightedNodeIds, setHighlightedNodeIds] = useState<Set<string>>(new Set()); 

  const settings: OrgChartSettingsValues = {
    ...defaultOrgChartSettings,
    ...userSettings
  };

  const { width: nodeWidth, height: nodeHeight } = getNodeDimensions(settings);

  const margin = {
    top: 40,
    right: nodeWidth,
    bottom: 40,
    left: nodeWidth,
  };

  const updateChart = useCallback((sourceNode: d3.HierarchyPointNode<OrgChartNodeData> | null = null) => {
    if (!rootRef.current) return;

    const root = rootRef.current;
    const duration = sourceNode ? 500 : 0;

    const layoutNodeSize: [number, number] = settings.layout === 'horizontal' 
      ? [nodeHeight + settings.siblingGap, nodeWidth + settings.levelGap] 
      : [nodeWidth + settings.siblingGap, nodeHeight + settings.levelGap];

    let treeLayout;
    if (settings.layout === 'horizontal') {
      treeLayout = d3.tree<OrgChartNodeData>()
        .nodeSize(layoutNodeSize)
        .separation((a, b) => (a.parent === b.parent ? 1 : 1.2));
    } else if (settings.layout === 'radial') {
      const radius = Math.min(width, height) / 2 - Math.max(margin.top, margin.right, margin.bottom, margin.left);
      treeLayout = d3.tree<OrgChartNodeData>()
        .size([2 * Math.PI, radius])
        .separation((a, b) => (a.parent === b.parent ? 1 : 2) / (a.depth + 1));
    } else {
      treeLayout = d3.tree<OrgChartNodeData>()
        .nodeSize(layoutNodeSize)
        .separation((a, b) => (a.parent === b.parent ? 1 : 1.2));
    }
    
    const newRootWithCoords = treeLayout(root as d3.HierarchyNode<OrgChartNodeData>);
    const newNodes = newRootWithCoords.descendants();
    const newLinks = newRootWithCoords.links();
    
    if (settings.layout !== 'radial') {
      newNodes.forEach(d => {
        if (settings.layout === 'horizontal') {
          d.y = d.depth * (nodeWidth + settings.levelGap);
        } else {
          d.y = d.depth * (nodeHeight + settings.levelGap);
        }
      });
    }

    setNodes(newNodes);
    setLinks(newLinks);

    const enterNodeTransform = (d: d3.HierarchyPointNode<OrgChartNodeData>) => {
      const parentCoords = sourceNode || root;
       if (settings.layout === 'radial') {
          const x = parentCoords.y * Math.cos(parentCoords.x - Math.PI / 2);
          const y = parentCoords.y * Math.sin(parentCoords.x - Math.PI / 2);
          return `translate(${x},${y})`;
        } else if (settings.layout === 'horizontal') {
          return `translate(${parentCoords.y},${parentCoords.x})`;
        } else {
          return `translate(${parentCoords.x},${parentCoords.y})`;
        }
    };

    const nodeSelection = d3.select(gRef.current).selectAll<SVGGElement, d3.HierarchyPointNode<OrgChartNodeData>>('g.node')
      .data(newNodes, d => d.data.id);

    const nodeEnter = nodeSelection.enter().append('g')
      .attr('class', 'node')
      .attr('transform', enterNodeTransform)
      .attr('opacity', 0)
      .on('click', (event, d) => {
          if (onNodeClick) {
              onNodeClick(d.data.id);
          }
      });
      
    nodeEnter.append('foreignObject')
        .attr('width', nodeWidth)
        .attr('height', nodeHeight)
        .attr('x', -nodeWidth / 2)
        .attr('y', -nodeHeight / 2)
        .style('overflow', 'visible')
      .append('xhtml:div')
        .style('width', `${nodeWidth}px`)
        .style('height', `${nodeHeight}px`)
        .style('display', 'flex')
        .style('align-items', 'center')
        .style('justify-content', 'center');

    const nodeUpdate = nodeEnter.merge(nodeSelection);

    nodeUpdate.select<HTMLDivElement>('foreignObject > div')
      .html(d => {
        return `<div id="node-${d.data.id}"></div>`; 
      });

    nodeUpdate.transition()
      .duration(duration)
      .attr('transform', d => {
         if (settings.layout === 'radial') {
          const x = d.y * Math.cos(d.x - Math.PI / 2);
          const y = d.y * Math.sin(d.x - Math.PI / 2);
          return `translate(${x},${y})`;
        } else if (settings.layout === 'horizontal') {
          return `translate(${d.y},${d.x})`;
        } else {
          return `translate(${d.x},${d.y})`;
        }
      })
      .attr('opacity', 1);

    const nodeExit = nodeSelection.exit();
      
    nodeExit.transition()
      .duration(duration)
      .attr('transform', enterNodeTransform)
      .attr('opacity', 0)
      .remove();

    const linkSelection = d3.select(gRef.current).selectAll<SVGPathElement, d3.HierarchyPointLink<OrgChartNodeData>>('path.link')
      .data(newLinks, d => d.target.data.id);

    let linkGenerator: any;
    if (settings.layout === 'horizontal') {
      linkGenerator = d3.linkHorizontal<any, d3.HierarchyPointNode<OrgChartNodeData>>()
        .x(d => d.y)
        .y(d => d.x);
    } else if (settings.layout === 'radial') {
      linkGenerator = d3.linkRadial<any, d3.HierarchyPointNode<OrgChartNodeData>>()
        .angle(d => d.x)
        .radius(d => d.y);
    } else {
      linkGenerator = d3.linkVertical<any, d3.HierarchyPointNode<OrgChartNodeData>>()
        .x(d => d.x)
        .y(d => d.y);
    }

    const linkEnter = linkSelection.enter().insert('path', 'g')
      .attr('class', 'link')
      .attr('d', d => {
        const o = { x: (sourceNode || root).x, y: (sourceNode || root).y };
        return linkGenerator({ source: o, target: o });
      })
      .attr('fill', 'none')
      .attr('stroke', theme.colors.dark[3])
      .attr('stroke-width', 1.5)
      .attr('opacity', 0);

    const linkUpdate = linkEnter.merge(linkSelection);

    linkUpdate.transition()
      .duration(duration)
      .attr('d', linkGenerator)
      .attr('opacity', 1);

    linkSelection.exit().transition()
      .duration(duration)
      .attr('d', d => {
        const o = { x: (sourceNode || root).x, y: (sourceNode || root).y };
        return linkGenerator({ source: o, target: o });
      })
      .attr('opacity', 0)
      .remove();
      
  }, [settings, width, height, margin, theme, nodeWidth, nodeHeight, onNodeClick]);

  useEffect(() => {
    if (!svgRef.current || !chartData) return;

    const svg = d3.select(svgRef.current);

    if (!gRef.current) {
      gRef.current = svg.append('g')
        .attr('class', 'org-chart-container')
        .node();
      
      if (settings.showGrid) {
        const grid = d3.select(gRef.current).insert('g', ':first-child').attr('class', 'grid');
        
        for (let i = -height * 2; i < height * 2; i += 50) {
          grid.append('line')
            .attr('x1', -width * 2) .attr('y1', i)
            .attr('x2', width * 2) .attr('y2', i)
            .attr('stroke', theme.colors.dark[4]) .attr('stroke-width', 0.5) .attr('opacity', 0.3);
        }
        
        for (let i = -width * 2; i < width * 2; i += 50) {
          grid.append('line')
            .attr('x1', i) .attr('y1', -height * 2)
            .attr('x2', i) .attr('y2', height * 2)
            .attr('stroke', theme.colors.dark[4]) .attr('stroke-width', 0.5) .attr('opacity', 0.3);
        }
      }

      zoomRef.current = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.2, 3])
        .on('zoom', (event) => {
          if (gRef.current) {
            d3.select(gRef.current).attr('transform', event.transform);
          }
        });

      svg.call(zoomRef.current);

      const initialTransform = d3.zoomIdentity
        .translate(width / 2, settings.layout === 'vertical' ? margin.top + nodeHeight : height / 2)
        .scale(settings.zoom || 0.6);
      
      svg.call(zoomRef.current.transform, initialTransform);
    }
    
    d3.select(gRef.current).select('.grid').remove();
    if (settings.showGrid) {
      const grid = d3.select(gRef.current).insert('g', ':first-child').attr('class', 'grid');
      
      for (let i = -height * 2; i < height * 2; i += 50) {
        grid.append('line')
          .attr('x1', -width * 2) .attr('y1', i)
          .attr('x2', width * 2) .attr('y2', i)
          .attr('stroke', theme.colors.dark[4]) .attr('stroke-width', 0.5) .attr('opacity', 0.3);
      }
      
      for (let i = -width * 2; i < width * 2; i += 50) {
        grid.append('line')
          .attr('x1', i) .attr('y1', -height * 2)
          .attr('x2', i) .attr('y2', height * 2)
          .attr('stroke', theme.colors.dark[4]) .attr('stroke-width', 0.5) .attr('opacity', 0.3);
      }
    }

    const hierarchyRoot = d3.hierarchy(chartData); 
    
    if (settings.maxDepth !== null) {
      hierarchyRoot.descendants().forEach(d => {
        if (d.depth >= (settings.maxDepth as number)) {
          if (d.children) {
            d._children = d.children;
            d.children = undefined; 
          }
        } else {
          if(d._children && d.depth < settings.maxDepth) {
            d.children = d._children;
            d._children = undefined;
          }
        }
      });
    }
    
    rootRef.current = hierarchyRoot as d3.HierarchyPointNode<OrgChartNodeData>;

    updateChart();

  }, [chartData, width, height, settings, theme, updateChart]);

  const handleExpandCollapse = useCallback((nodeId: string) => {
    if (!rootRef.current) return;

    let clickedNode: d3.HierarchyPointNode<OrgChartNodeData> | null = null;

    rootRef.current.each((node) => {
      if (node.data.id === nodeId) {
        clickedNode = node as d3.HierarchyPointNode<OrgChartNodeData>;
      }
    });

    if (clickedNode) {
      if (clickedNode.children) {
         clickedNode._children = clickedNode.children;
        clickedNode.children = undefined;
      } 
      else if (clickedNode._children) {
        clickedNode.children = clickedNode._children;
        clickedNode._children = undefined;
      }
      
      updateChart(clickedNode); 
    }
  }, [updateChart]);

  const centerNode = useCallback((nodeId: string) => {
    if (!svgRef.current || !zoomRef.current || !rootRef.current) return;

    let targetNode: d3.HierarchyPointNode<OrgChartNodeData> | null = null;
    rootRef.current.each(node => {
        if (node.data.id === nodeId) {
            targetNode = node as d3.HierarchyPointNode<OrgChartNodeData>;
        }
    });

    if (targetNode) {
        const svg = d3.select(svgRef.current);
        const zoomBehavior = zoomRef.current;
        
        let targetX = 0;
        let targetY = 0;

        if (settings.layout === 'horizontal') {
            targetX = targetNode.y;
            targetY = targetNode.x;
        } else {
            targetX = targetNode.x;
            targetY = targetNode.y;
        }

        const currentTransform = d3.zoomTransform(svgRef.current);
        
        svg.transition().duration(750)
           .call(
               zoomBehavior.translateTo, 
               targetX, 
               targetY, 
            ); 
            
    }
  }, [settings.layout, width, height]);

  const resetZoomAndPosition = useCallback(() => {
      if (!svgRef.current || !zoomRef.current) return;
       const svg = d3.select(svgRef.current);
       const zoomBehavior = zoomRef.current;
       const initialTransform = d3.zoomIdentity
        .translate(width / 2, settings.layout === 'vertical' ? margin.top + nodeHeight : height / 2) 
        .scale(settings.zoom || 0.6); 
       svg.transition().duration(750).call(zoomBehavior.transform, initialTransform);
  }, [width, height, settings.layout, settings.zoom, margin.top, nodeHeight]);

  useImperativeHandle(ref, () => ({
    centerOnNode: centerNode,
    resetZoom: resetZoomAndPosition
  }));

  useEffect(() => {
    if (!rootRef.current || !searchTerm) {
        setHighlightedNodeIds(new Set());
        return;
    }

    const term = searchTerm.toLowerCase().trim();
    const newHighlightedIds = new Set<string>();

    rootRef.current.each(node => {
        const nodeName = node.data.name?.toLowerCase() || '';
        const nodeTitle = node.data.title?.toLowerCase() || '';
        
        if (nodeName.includes(term) || nodeTitle.includes(term)) {
            newHighlightedIds.add(node.data.id);
        }
    });

    setHighlightedNodeIds(newHighlightedIds);

  }, [searchTerm, chartData]);

  useEffect(() => {
    nodes.forEach(node => {
      const container = document.getElementById(`node-${node.data.id}`);
      if (container) {
        const root = ReactDOM.createRoot(container); 
        root.render(
          <OrgChartNodeComponent 
            nodeData={node} 
            settings={settings}
            onClick={onNodeClick ? () => onNodeClick(node.data.id) : undefined} 
            onExpandCollapse={handleExpandCollapse} 
            isHighlighted={highlightedNodeIds.has(node.data.id)}
          />
        );
      }
    });
    
    const nodeIds = new Set(nodes.map(n => `node-${n.data.id}`));
    const rootsToUnmount = document.querySelectorAll('[id^="node-"]');
    rootsToUnmount.forEach(container => {
        if (!nodeIds.has(container.id)) {
            container.innerHTML = ''; 
        }
    });

  }, [nodes, settings, onNodeClick, handleExpandCollapse, highlightedNodeIds]);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = "https://unpkg.com/react-dom@18/umd/react-dom.development.js";
    script.async = true;
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);


  return (
    <Box sx={{ 
        width: '100%', 
        height: '100%', 
        backgroundColor: theme.colors.dark[8], 
        borderRadius: theme.radius.md,
        overflow: 'hidden'
    }}>
      {!chartData ? (
        <Text p="md" align="center" color="dimmed">Нет данных для отображения</Text>
      ) : (
        <svg 
          ref={svgRef} 
          width="100%" 
          height="100%" 
        />
      )}
    </Box>
  );
});

export default OrgChart;
