import React, { useEffect, useState } from 'react';
import { 
  TextInput, Button, Group, Select, Textarea, 
  Box, Switch, Stack, LoadingOverlay, MultiSelect
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useSections } from '../../sections/api/sectionApi';
import { Position, PositionCreate, PositionUpdate } from '../../../types/position';
import { useQuery } from '@tanstack/react-query';
import { functionApi } from '../../../api/functionApi';
import { useDivisions } from '../../divisions/api/divisionApi';

// Префикс для кода должности
const POSITION_PREFIX = 'POS_';

// Предопределенные уровни должностей
const POSITION_LEVELS = [
  { value: 'DIRECTOR', label: 'Директор' },
  { value: 'HEAD', label: 'Руководитель' },
  { value: 'LEAD', label: 'Ведущий специалист' },
  { value: 'SPECIALIST', label: 'Специалист' },
  { value: 'ASSISTANT', label: 'Ассистент' },
];

// Константы для проверки уровней должностей
const LEVEL_DIRECTOR = 'DIRECTOR';
const LEVEL_HEAD = 'HEAD';
const LEVEL_LEAD = 'LEAD';

// Тип для опций секций
interface SectionOption {
  value: string;
  label: string;
  division_id?: number;
}

interface PositionFormProps {
  initialData?: Position | null;
  onSubmit: (data: PositionCreate | PositionUpdate) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const PositionForm: React.FC<PositionFormProps> = ({
  initialData = null,
  onSubmit,
  onCancel,
  isLoading,
}) => {
  // Получаем список департаментов
  const { data: divisions = [], isLoading: loadingDivisions } = useDivisions();
  const [divisionOptions, setDivisionOptions] = useState<{ value: string; label: string }[]>([]);

  // Получаем список отделов для выбора
  const { data: sections = [], isLoading: loadingSections } = useSections(null);
  const [sectionOptions, setSectionOptions] = useState<SectionOption[]>([]);
  const [filteredSectionOptions, setFilteredSectionOptions] = useState<SectionOption[]>([]);

  // Получаем список функций для мультиселекта
  const { data: functions = [], isLoading: loadingFunctions } = useQuery({
    queryKey: ['functions'],
    queryFn: () => functionApi.getAll({ limit: 1000 }),
  });
  
  const [functionOptions, setFunctionOptions] = useState<{ value: string; label: string }[]>([]);

  const [showDivision, setShowDivision] = useState(true);
  const [showSection, setShowSection] = useState(true);

  // Преобразуем департаменты в опции для селекта
  useEffect(() => {
    if (divisions && divisions.length > 0) {
      const options = divisions.map((division) => ({
        value: String(division.id),
        label: division.name,
      }));
      setDivisionOptions(options);
    }
  }, [divisions]);

  useEffect(() => {
    if (sections && sections.length > 0) {
      const options = sections.map((section) => ({
        value: String(section.id),
        label: `${section.name} (${section.division?.name || 'Без подразделения'})`,
        division_id: section.division_id,
      }));
      setSectionOptions(options);
      
      // Изначально установим все отделы
      setFilteredSectionOptions(options);
    }
  }, [sections]);

  // Преобразуем функции в опции для мультиселекта
  useEffect(() => {
    if (functions && functions.length > 0) {
      const options = functions.map((func) => ({
        value: String(func.id),
        label: `${func.name} (${func.code})`,
      }));
      setFunctionOptions(options);
    }
  }, [functions]);

  const form = useForm({
    initialValues: {
      name: initialData?.name || '',
      code: initialData?.code || POSITION_PREFIX,
      division_id: initialData?.division_id ? String(initialData.division_id) : '',
      section_id: initialData?.section_id ? String(initialData.section_id) : '',
      attribute: initialData?.attribute || '',
      description: initialData?.description || '',
      is_active: initialData?.is_active ?? true,
      function_ids: initialData?.function_ids?.map(id => String(id)) || [],
    },
    validate: {
      name: (value) => (value.trim().length < 3 ? 'Название должно содержать минимум 3 символа' : null),
      code: (value) => {
        if (value.trim().length < 2) {
          return 'Код должен содержать минимум 2 символа';
        }
        if (!initialData && value === POSITION_PREFIX) {
          return 'Необходимо добавить код после префикса ' + POSITION_PREFIX;
        }
        return null;
      },
      section_id: (value, values) => {
        // Отдел обязателен только если он отображается (т.е. должность не директор и не руководитель)
        const positionLevel = values.attribute;
        if (positionLevel !== LEVEL_DIRECTOR && positionLevel !== LEVEL_HEAD) {
          return !value ? 'Необходимо выбрать отдел' : null;
        }
        return null;
      },
    },
  });

  // Обработчик изменения поля кода для сохранения префикса
  const handleCodeChange = (value: string) => {
    if (initialData) {
      // При редактировании не меняем код
      return;
    }
    
    // Для новой должности всегда сохраняем префикс
    if (!value.startsWith(POSITION_PREFIX)) {
      form.setFieldValue('code', POSITION_PREFIX + value.replace(POSITION_PREFIX, ''));
    } else {
      form.setFieldValue('code', value);
    }
  };

  // Фильтруем список отделов при выборе департамента
  useEffect(() => {
    const divisionId = form.values.division_id;
    if (divisionId) {
      const filtered = sectionOptions.filter(
        section => section.division_id === Number(divisionId)
      );
      setFilteredSectionOptions(filtered);
      
      // Если выбран отдел, который не принадлежит выбранному департаменту, сбрасываем его
      const currentSectionId = form.values.section_id;
      if (currentSectionId) {
        const sectionExists = filtered.some(s => s.value === currentSectionId);
        if (!sectionExists) {
          form.setFieldValue('section_id', '');
        }
      }
    } else {
      // Если департамент не выбран, показываем все отделы
      setFilteredSectionOptions(sectionOptions);
    }
  }, [form.values.division_id, sectionOptions]);

  useEffect(() => {
    // Проверяем уровень должности, чтобы определить видимость полей
    const positionLevel = form.values.attribute;
    
    // Если уровень "Директор", не показываем ни департамент, ни отдел
    if (positionLevel === LEVEL_DIRECTOR) {
      setShowDivision(false);
      setShowSection(false);
      // Очищаем поля, если они заполнены
      form.setFieldValue('division_id', '');
      form.setFieldValue('section_id', '');
    } 
    // Если уровень "Руководитель", показываем только департамент, но не отдел
    else if (positionLevel === LEVEL_HEAD) {
      setShowDivision(true);
      setShowSection(false);
      // Очищаем поле отдела, если оно заполнено
      form.setFieldValue('section_id', '');
    } 
    // В остальных случаях показываем оба поля
    else {
      setShowDivision(true);
      setShowSection(true);
    }
  }, [form.values.attribute]);

  // Изменяем валидацию в зависимости от видимости полей
  useEffect(() => {
    // Если поле отдела скрыто, убираем его обязательность
    if (!showSection) {
      form.clearFieldError('section_id');
    }
  }, [showSection]);

  const handleSubmit = (values: typeof form.values) => {
    // Проверка на наличие кода после префикса
    if (!initialData && values.code === POSITION_PREFIX) {
      form.setFieldError('code', 'Необходимо добавить код после префикса ' + POSITION_PREFIX);
      return;
    }
    
    // В зависимости от уровня должности, определяем, какие поля отправлять
    const positionLevel = values.attribute;
    let divisionId = null;
    let sectionId = undefined; // По умолчанию undefined для корректной типизации
    
    // Для директора не отправляем ни департамент, ни отдел
    if (positionLevel === LEVEL_DIRECTOR) {
      divisionId = null;
      sectionId = undefined;
    }
    // Для руководителя отправляем только департамент
    else if (positionLevel === LEVEL_HEAD) {
      divisionId = values.division_id ? Number(values.division_id) : null;
      sectionId = undefined;
    }
    // Для остальных отправляем и департамент, и отдел
    else {
      divisionId = values.division_id ? Number(values.division_id) : null;
      sectionId = values.section_id ? Number(values.section_id) : undefined;
    }
    
    const formData = {
      ...values,
      division_id: divisionId,
      section_id: sectionId,
      function_ids: values.function_ids?.map(id => Number(id)) || [],
      description: values.description || null,
      attribute: values.attribute || null,
    };
    
    onSubmit(formData);
  };

  return (
    <Box pos="relative">
      <LoadingOverlay visible={isLoading || loadingSections || loadingFunctions || loadingDivisions} />
      
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          <TextInput
            label="Название должности"
            placeholder="Менеджер по продажам"
            withAsterisk
            {...form.getInputProps('name')}
          />
          
          <TextInput
            label="Код должности"
            placeholder={`${POSITION_PREFIX}123`}
            description="Код автоматически начинается с POS_"
            withAsterisk
            value={form.values.code}
            onChange={(e) => handleCodeChange(e.currentTarget.value)}
            error={form.errors.code}
            disabled={!!initialData} // Запрещаем менять код при редактировании
          />

          <Select
            label="Уровень должности"
            placeholder="Выберите уровень должности"
            data={POSITION_LEVELS}
            clearable
            {...form.getInputProps('attribute')}
          />

          {showDivision && (
            <Select
              label="Департамент"
              placeholder="Выберите департамент"
              data={divisionOptions}
              searchable
              clearable
              {...form.getInputProps('division_id')}
            />
          )}
          
          {showSection && (
            <Select
              label="Отдел"
              placeholder="Выберите отдел"
              data={filteredSectionOptions}
              withAsterisk={showSection}
              searchable
              {...form.getInputProps('section_id')}
            />
          )}

          <MultiSelect
            label="Функции"
            placeholder="Выберите функции должности"
            data={functionOptions}
            searchable
            clearable
            nothingFoundMessage="Функции не найдены"
            {...form.getInputProps('function_ids')}
          />
          
          <Textarea
            label="Описание"
            placeholder="Краткое описание должности и обязанностей"
            minRows={3}
            {...form.getInputProps('description')}
          />
          
          <Switch
            label="Активна"
            checked={form.values.is_active}
            onChange={(event) => form.setFieldValue('is_active', event.currentTarget.checked)}
          />
          
          <Group justify="flex-end" mt="xl">
            <Button variant="outline" onClick={onCancel} disabled={isLoading}>
              Отмена
            </Button>
            <Button type="submit" loading={isLoading}>
              {initialData ? 'Сохранить' : 'Создать'}
            </Button>
          </Group>
        </Stack>
      </form>
    </Box>
  );
};

export default PositionForm; 