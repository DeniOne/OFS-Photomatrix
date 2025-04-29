import { OrgChartNode } from './components/OrgChart';

// Тестовые данные для визуализации оргструктуры
export const mockOrgChartData: OrgChartNode = {
  id: '1',
  name: 'Генеральный директор',
  title: 'CEO',
  type: 'position',
  children: [
    {
      id: '2',
      name: 'Финансовый директор',
      title: 'CFO',
      type: 'position',
      children: [
        {
          id: '3',
          name: 'Бухгалтерия',
          code: 'BUH',
          type: 'department',
          children: [
            { id: '4', name: 'Главный бухгалтер', type: 'position' },
            { id: '5', name: 'Бухгалтер-экономист', type: 'position' }
          ]
        },
        {
          id: '6',
          name: 'Финансовый отдел',
          code: 'FIN',
          type: 'division',
          children: [
            { id: '7', name: 'Начальник финансового отдела', type: 'position' },
            { id: '8', name: 'Финансовый аналитик', type: 'position' }
          ]
        }
      ]
    },
    {
      id: '9',
      name: 'Технический директор',
      title: 'CTO',
      type: 'position',
      children: [
        {
          id: '10',
          name: 'Отдел разработки',
          code: 'DEV',
          type: 'division',
          children: [
            { id: '11', name: 'Руководитель разработки', type: 'position' },
            { id: '12', name: 'Frontend-разработчики', type: 'position' },
            { id: '13', name: 'Backend-разработчики', type: 'position' }
          ]
        },
        {
          id: '14',
          name: 'Отдел тестирования',
          code: 'QA',
          type: 'division',
          children: [
            { id: '15', name: 'QA Lead', type: 'position' },
            { id: '16', name: 'QA Engineers', type: 'position' }
          ]
        }
      ]
    },
    {
      id: '17',
      name: 'HR-директор',
      type: 'position',
      children: [
        { 
          id: '18', 
          name: 'Отдел кадров', 
          code: 'HR',
          type: 'department',
          children: [
            { id: '20', name: 'HR-менеджеры', type: 'position' }
          ]
        },
        { 
          id: '19', 
          name: 'Рекрутеры', 
          type: 'position'
        }
      ]
    }
  ]
}; 