import { OrgChartNodeData } from './types/orgChartTypes';

// Тестовые данные для визуализации оргструктуры
export const mockOrgChartData: OrgChartNodeData = {
  id: 'root',
  name: 'Организационная структура',
  title: 'Демонстрационная схема',
  type: 'department',
  children: [
    {
      id: 'pos-1',
      name: 'Генеральный директор',
      title: 'CEO',
      type: 'position',
      level: 1,
      children: [
        {
          id: 'pos-2',
          name: 'Финансовый директор',
          title: 'CFO',
          type: 'position',
          level: 2,
          children: [
            {
              id: 'org-3',
              name: 'Бухгалтерия',
              code: 'BUH',
              type: 'department',
              children: [
                { id: 'pos-4', name: 'Главный бухгалтер', level: 3, type: 'position' },
                { id: 'pos-5', name: 'Бухгалтер-экономист', level: 5, type: 'position' }
              ]
            },
            {
              id: 'org-6',
              name: 'Финансовый отдел',
              code: 'FIN',
              type: 'division',
              children: [
                { id: 'pos-7', name: 'Начальник финансового отдела', level: 3, type: 'position' },
                { id: 'pos-8', name: 'Финансовый аналитик', level: 5, type: 'position' }
              ]
            }
          ]
        },
        {
          id: 'pos-9',
          name: 'Технический директор',
          title: 'CTO',
          type: 'position',
          level: 2,
          children: [
            {
              id: 'org-10',
              name: 'Отдел разработки',
              code: 'DEV',
              type: 'division',
              children: [
                { id: 'pos-11', name: 'Руководитель разработки', level: 3, type: 'position' },
                { id: 'pos-12', name: 'Frontend-разработчики', level: 5, type: 'position' },
                { id: 'pos-13', name: 'Backend-разработчики', level: 5, type: 'position' }
              ]
            },
            {
              id: 'org-14',
              name: 'Отдел тестирования',
              code: 'QA',
              type: 'division',
              children: [
                { id: 'pos-15', name: 'QA Lead', level: 3, type: 'position' },
                { id: 'pos-16', name: 'QA Engineers', level: 5, type: 'position' }
              ]
            }
          ]
        },
        {
          id: 'pos-17',
          name: 'HR-директор',
          type: 'position',
          level: 2,
          children: [
            { 
              id: 'org-18', 
              name: 'Отдел кадров', 
              code: 'HR',
              type: 'department',
              children: [
                { id: 'pos-20', name: 'HR-менеджеры', level: 4, type: 'position' }
              ]
            },
            { 
              id: 'pos-19', 
              name: 'Рекрутеры', 
              level: 5,
              type: 'position'
            }
          ]
        }
      ]
    }
  ]
};

// Альтернативный формат данных, соответствующий API
export const mockApiData = {
  id: 1,
  name: "ООО Рога и Копыта",
  org_type: "HOLDING",
  children: [
    {
      id: 2,
      name: "Директорат",
      org_type: "DEPARTMENT",
      children: [
        {
          id: 3,
          name: "Генеральный директор",
          level: 1,
          children: []
        },
        {
          id: 4, 
          name: "Финансовый директор",
          level: 2,
          children: []
        }
      ]
    },
    {
      id: 5,
      name: "ИТ-Департамент",
      org_type: "DEPARTMENT",
      children: [
        {
          id: 6,
          name: "Руководитель ИТ",
          level: 3,
          children: []
        },
        {
          id: 7,
          name: "Отдел разработки",
          org_type: "DIVISION",
          children: [
            {
              id: 8,
              name: "Ведущий программист",
              level: 4,
              children: []
            }
          ]
        }
      ]
    }
  ]
}; 