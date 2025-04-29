import asyncio
import pandas as pd
import re
import os
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.db.session import async_session
from app.models.function import Function
from app.models.section import Section
from app.models.division import Division
from app.schemas.function import FunctionCreate

# Словарь для преобразования названий функций
FUNCTION_NAME_MAPPING = {
    'функция найма': 'Найм сотрудников',
    'функция аудита': 'Аудит бизнес-процессов',
    'функция продаж': 'Продажи продуктов и услуг',
    'функция маркетинга': 'Маркетинг и продвижение',
    'функция hr': 'Управление персоналом',
    'функция учета': 'Бухгалтерский учет',
    'функция зарплаты': 'Расчет заработной платы',
    'функция финансов': 'Финансовое планирование',
    'функция it поддержки': 'ИТ поддержка пользователей',
    'функция разработки': 'Разработка программного обеспечения',
    'функция закупок': 'Закупка товаров и услуг',
    'функция логистики': 'Логистика и доставка',
    'функция контроля': 'Контроль качества',
    'функция анализа': 'Аналитика и отчетность',
    'функция проектирования': 'Проектирование и разработка',
    'функция клиентской поддержки': 'Поддержка клиентов',
    'функция обеспечение приемной': 'Обеспечение работы приемной',
    'функция введения в должность': 'Введение в должность',
    'функция офс': 'ОФС',
    # Добавьте другие соответствия по необходимости
}

# Возможные названия колонок в Excel
POSSIBLE_NAME_COLUMNS = ['название', 'наименование', 'имя', 'name', 'title']
POSSIBLE_SECTION_COLUMNS = ['отдел', 'подразделение', 'section', 'отделение']
POSSIBLE_DIVISION_COLUMNS = ['департамент', 'division', 'дивизион']
POSSIBLE_DESCRIPTION_COLUMNS = ['описание', 'description', 'комментарий', 'comment']

def clean_and_generate_code(name):
    """Генерирует код функции из названия"""
    # Удаляем спецсимволы и приводим к нижнему регистру
    clean = re.sub(r'[^\w\s]', '', name).lower()
    # Берем первые буквы каждого слова для кода
    code = ''.join([word[0] for word in clean.split() if word])
    # Если код слишком короткий, добавляем первые 3 буквы первого слова
    if len(code) < 3 and len(clean.split()) > 0:
        first_word = clean.split()[0]
        code = first_word[:min(3, len(first_word))] + code
    # Добавляем префикс 'F_'
    return f'F_{code.upper()}'

# Счетчик для нумерации функций
function_counter = 0

def generate_function_code():
    """Генерирует код функции в формате FUN_01, FUN_02, FUN_03 и т.д."""
    global function_counter
    function_counter += 1
    return f"FUN_{function_counter:02d}"

async def find_section_by_name(db: AsyncSession, name: str):
    """Находит отдел по имени"""
    if not name:
        return None
    
    # Нормализуем имя
    name = name.strip().lower()
    
    # Пробуем точное совпадение
    query = select(Section).where(Section.name.ilike(f'{name}'))
    result = await db.execute(query)
    section = result.scalars().first()
    if section:
        return section
    
    # Пробуем частичное совпадение
    query = select(Section).where(Section.name.ilike(f'%{name}%'))
    result = await db.execute(query)
    return result.scalars().first()

async def find_division_by_name(db: AsyncSession, name: str):
    """Находит департамент по имени"""
    if not name:
        return None
        
    # Нормализуем имя
    name = name.strip().lower()
    
    # Пробуем точное совпадение
    query = select(Division).where(Division.name.ilike(f'{name}'))
    result = await db.execute(query)
    division = result.scalars().first()
    if division:
        return division
    
    # Пробуем частичное совпадение
    query = select(Division).where(Division.name.ilike(f'%{name}%'))
    result = await db.execute(query)
    return result.scalars().first()

def find_column_by_possible_names(df, possible_names):
    """Ищет колонку в DataFrame по списку возможных имен"""
    for column in df.columns:
        if column.lower() in possible_names:
            return column
    return None

async def import_functions(excel_path, start_counter=0):
    """Импортирует функции из Excel файла в базу данных"""
    
    # Устанавливаем начальное значение счетчика
    global function_counter
    function_counter = start_counter
    
    if not os.path.exists(excel_path):
        print(f"❌ Файл {excel_path} не найден!")
        return
    
    print(f"Загрузка файла: {excel_path}")
    
    try:
        # Пытаемся загрузить Excel файл с разными настройками
        dfs = []
        try:
            # Пробуем разные листы и настройки
            excel = pd.ExcelFile(excel_path)
            for sheet_name in excel.sheet_names:
                try:
                    df = pd.read_excel(excel, sheet_name=sheet_name)
                    print(f"✅ Загружен лист '{sheet_name}'")
                    dfs.append(df)
                except:
                    continue
        except Exception as e:
            print(f"❌ Ошибка при чтении Excel-файла: {str(e)}")
            return
        
        if not dfs:
            print("❌ Не удалось загрузить ни один лист из Excel-файла")
            return
        
        # Создаем список для хранения функций
        functions_to_create = []
        
        # Для каждого датафрейма (листа Excel)
        for df_index, df in enumerate(dfs):
            print(f"\nОбработка листа {df_index+1}")
            
            # Преобразуем все заголовки и данные к строковому типу для безопасного поиска
            try:
                df = df.astype(str)
            except:
                # Игнорируем ошибки преобразования - просто продолжим с тем что есть
                pass
            
            # Ищем ячейки, содержащие "Функция" где угодно в датафрейме
            functions_found = False
            
            # Перебираем все ячейки датафрейма
            for row_idx, row in df.iterrows():
                for col_idx, value in enumerate(row):
                    # Пропускаем пустые значения или NaN
                    if not isinstance(value, str) or pd.isna(value):
                        continue
                    
                    # Ищем строки с "Функция"
                    if "функция" in value.lower() or "Функция" in value:
                        functions_found = True
                        
                        # Используем это значение как имя функции
                        function_name = value.strip()
                        
                        # Ищем возможное описание в ячейках справа или снизу
                        description = ""
                        try:
                            # Проверяем ячейку справа
                            if col_idx + 1 < len(row) and isinstance(row[col_idx + 1], str):
                                description = row[col_idx + 1]
                        except:
                            pass
                        
                        # Ищем отдел/департамент в соседних ячейках по строке
                        parent_section_name = None
                        parent_division_name = None
                        try:
                            # Ищем в строке человека с должностью (обычно это глава отдела)
                            for i in range(len(row)):
                                if i != col_idx and isinstance(row[i], str) and len(row[i]) > 3:
                                    section_text = row[i]
                                    if "управление" in section_text.lower():
                                        parent_section_name = section_text
                                        break
                        except:
                            pass
                        
                        # Преобразуем имя функции
                        function_name_lower = function_name.lower()
                        if function_name_lower in FUNCTION_NAME_MAPPING:
                            transformed_name = FUNCTION_NAME_MAPPING[function_name_lower]
                        else:
                            # Убираем слово "Функция" и обрабатываем остаток
                            name_parts = re.split(r'функция\s+', function_name.lower(), flags=re.IGNORECASE)
                            if len(name_parts) > 1 and name_parts[1]:
                                transformed_name = name_parts[1].strip().capitalize()
                            else:
                                transformed_name = function_name.capitalize()
                        
                        print(f"Найдена функция: {function_name} -> {transformed_name}")
                        
                        # Добавляем функцию в список для создания
                        functions_to_create.append({
                            'name': transformed_name,
                            'parent_section': parent_section_name,
                            'parent_division': parent_division_name,
                            'description': description,
                            'code': generate_function_code()
                        })
                        
            if not functions_found:
                print(f"⚠️ На листе {df_index+1} не найдено функций")
        
        if not functions_to_create:
            print("❌ Не найдено ни одной функции во всем файле Excel")
            return
        
        # Вывод предпросмотра функций перед импортом
        print(f"\nНайдено {len(functions_to_create)} функций для импорта:")
        for i, func in enumerate(functions_to_create):
            print(f"{i+1}. {func['name']} (код: {func['code']})")
            if func['parent_section']:
                print(f"   Отдел: {func['parent_section']}")
            if func['parent_division']:
                print(f"   Департамент: {func['parent_division']}")
        
        confirm = input("\nПродолжить импорт? (y/n): ")
        if confirm.lower() != 'y':
            print("Импорт отменен.")
            return
        
        # Подключаемся к БД и создаем функции
        async with async_session() as db:
            total_created = 0
            
            for func_data in functions_to_create:
                section_id = None
                
                # Ищем связанный отдел
                if func_data['parent_section']:
                    section = await find_section_by_name(db, func_data['parent_section'])
                    if section:
                        section_id = section.id
                        print(f"✓ Найден отдел '{section.name}' (ID: {section.id})")
                    else:
                        print(f"⚠️ Отдел '{func_data['parent_section']}' не найден")
                        
                        # Если отдел не найден, ищем по департаменту
                        if func_data['parent_division']:
                            division = await find_division_by_name(db, func_data['parent_division'])
                            if division:
                                print(f"✓ Найден департамент '{division.name}' (ID: {division.id})")
                                # Поиск подходящего отдела в департаменте
                                query = select(Section).where(Section.division_id == division.id)
                                result = await db.execute(query)
                                sections = result.scalars().all()
                                if sections:
                                    # Берем первый отдел из найденных
                                    section_id = sections[0].id
                                    print(f"✓ Используем отдел '{sections[0].name}' (ID: {sections[0].id}) из департамента")
                
                # Создаем функцию с найденным section_id
                function_data = FunctionCreate(
                    name=func_data['name'],
                    code=func_data['code'],
                    section_id=section_id,
                    description=func_data.get('description', ''),
                    is_active=True
                )
                
                # Проверяем, существует ли уже такая функция
                query = select(Function).where(
                    Function.name == function_data.name
                )
                result = await db.execute(query)
                existing_function = result.scalars().first()
                
                if not existing_function:
                    try:
                        # Создаем новую функцию
                        db_function = Function(**function_data.dict())
                        db.add(db_function)
                        await db.commit()
                        await db.refresh(db_function)
                        print(f"✅ Создана функция: {function_data.name}")
                        total_created += 1
                    except Exception as e:
                        print(f"❌ Ошибка при создании функции '{function_data.name}': {str(e)}")
                        await db.rollback()
                else:
                    print(f"⚠️ Функция '{function_data.name}' уже существует, пропускаем")
            
            print(f"\n✅ Импорт завершен! Создано {total_created} новых функций.")
    
    except Exception as e:
        print(f"❌ Ошибка импорта: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Путь к Excel файлу
    excel_file = "functions.xlsx"
    
    # Получаем начальное значение счетчика из аргументов командной строки, если оно есть
    start_counter = 0
    if len(sys.argv) > 1:
        try:
            start_counter = int(sys.argv[1])
            print(f"Начинаем нумерацию функций с: FUN_{start_counter+1:02d}")
        except ValueError:
            print(f"⚠️ Неверный формат начального счетчика: {sys.argv[1]}, используем 0")
    
    # Запускаем импорт
    asyncio.run(import_functions(excel_file, start_counter)) 