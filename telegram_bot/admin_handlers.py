import re
import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from typing import Dict, Any, List
import asyncio
import os
import json

from database import BotDatabase
from states import AdminStates
import keyboards
from api_client import ApiClient, sync_all_data, clear_cache
from config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация роутера
router = Router()

# Инициализация зависимостей
db = BotDatabase()
api_client = ApiClient()
config = Config()

# Фильтр для проверки прав админа
def is_admin_filter(message: Message) -> bool:
    """Фильтр для проверки, является ли пользователь админом"""
    user_id = message.from_user.id  # Получаем ID как число
    user_id_str = str(user_id)  # Строковое представление для логов и БД
    username = message.from_user.username
    logger.info(f"⚙️ Проверка прав админа для пользователя ID: {user_id} (тип: {type(user_id)}), Username: @{username}")
    
    # Проверка в конфиге
    logger.info(f"📋 Список админов в конфиге: {config.ADMIN_IDS}")
    logger.info(f"📋 Типы данных в списке админов: {[type(x) for x in config.ADMIN_IDS]}")
    
    # Сначала проверяем через метод is_admin из config
    is_admin_in_config = config.is_admin(user_id)
    logger.info(f"Пользователь {user_id} {'является' if is_admin_in_config else 'не является'} админом по конфигу")
    
    # Проверка в базе данных
    is_admin_in_db = db.is_admin(user_id_str)
    logger.info(f"Пользователь {user_id_str} {'является' if is_admin_in_db else 'не является'} админом по данным БД")
    
    # Пользователь админ, если он найден в конфиге ИЛИ в базе данных
    is_admin = is_admin_in_config or is_admin_in_db
    
    if is_admin:
        logger.info(f"✅ Пользователь {user_id} (@{username}) успешно прошел проверку прав админа")
    else:
        logger.warning(f"❌ Пользователь {user_id} (@{username}) не имеет прав админа")
    
    return is_admin

def is_superadmin_filter(message: Message) -> bool:
    """Фильтр для проверки, является ли пользователь супер-админом"""
    user_id = str(message.from_user.id)
    username = message.from_user.username
    logger.info(f"⚙️ Проверка прав суперадмина для пользователя ID: {user_id}, Username: @{username}")
    
    # Проверка в конфиге
    is_superadmin_config = message.from_user.id in config.ADMIN_IDS
    logger.info(f"📋 Проверка в конфиге: ID {user_id} {'найден в списке' if is_superadmin_config else 'отсутствует в списке'} админов")
    logger.info(f"📋 Список админов в конфиге: {config.ADMIN_IDS}")
    
    # Проверка в БД
    is_superadmin_db = db.is_superadmin(user_id)
    logger.info(f"🗄️ Проверка в БД: ID {user_id} {'найден' if is_superadmin_db else 'не найден'} в таблице суперадминов")
    
    # Итоговый результат
    result = is_superadmin_config or is_superadmin_db
    logger.info(f"🔑 Результат проверки прав суперадмина для {user_id}: {'✅ Доступ разрешен' if result else '❌ Доступ запрещен'}")
    return result

# Полностью переделываем команду admin
@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Отображает панель администратора"""
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени пользователя"
    logger.info(f"🔷 Запрос админ-панели от пользователя ID: {user_id} (тип: {type(user_id)}), Username: @{username}")
    
    # Проверяем, есть ли пользователь в списке админов из конфига
    admins_config = config.ADMIN_IDS
    logger.info(f"📋 Список админов в конфиге: {admins_config}")
    logger.info(f"📋 Типы данных в списке админов: {[type(x) for x in admins_config]}")
    
    # Проверка типов данных для более точной диагностики
    admin_config_details = [f"{x} (тип: {type(x)})" for x in admins_config]
    logger.info(f"🔍 Детальный список админов в конфиге: {admin_config_details}")
    
    # Проверяем наличие пользователя в конфиге
    try:
        is_in_config = user_id in admins_config
        logger.info(f"🔎 Проверка наличия {user_id} в списке админов конфига: {is_in_config}")
        
        if is_in_config:
            logger.info(f"✅ Пользователь {user_id} найден в списке админов по ID в конфиге")
            
            try:
                # Пытаемся очистить предыдущие сообщения
                logger.info(f"🧹 Пытаемся удалить предыдущее сообщение пользователя")
                await message.delete()
                logger.info(f"✅ Предыдущее сообщение успешно удалено")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось удалить старые сообщения: {str(e)}")
                logger.exception("Подробная ошибка при удалении сообщения:")
            
            logger.info(f"🛠️ Создаем инлайн-клавиатуру панели администратора")
            # Создаем инлайн-клавиатуру для панели администратора
            kb = [
                [
                    InlineKeyboardButton(text="📋 Заявки", callback_data="admin_requests"),
                    InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
                ],
                [
                    InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_management"),
                    InlineKeyboardButton(text="👨‍💼 Сотрудники", callback_data="admin_staff")
                ],
                [
                    InlineKeyboardButton(text="🔄 Обновить должности", callback_data="admin_update_positions")
                ],
                [
                    InlineKeyboardButton(text="🏠 Главное меню", callback_data="admin_main_menu")
                ]
            ]
            admin_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
            
            # Удаляем клавиатуру снизу
            from aiogram.types import ReplyKeyboardRemove
            logger.info(f"⌨️ Удаляем стандартную клавиатуру снизу")
            
            logger.info(f"📤 Отправляем панель администратора пользователю")
            await message.answer(
                "👨‍💼 <b>Панель администратора</b>\n\n"
                "Ваши права администратора подтверждены.\n"
                "Выберите действие:",
                reply_markup=admin_keyboard
            )
            logger.info(f"✅ Панель администратора успешно отправлена пользователю {user_id}")
        else:
            logger.warning(f"⚠️ Пользователь {user_id} не найден в списке админов в конфиге, проверяем в БД")
            
            # Подробное логирование проверки в БД
            try:
                # Проверяем, может быть админ есть в БД
                # Преобразуем ID в строку для БД
                user_id_str = str(user_id)
                logger.info(f"🔄 Преобразуем ID для проверки в БД: {user_id} -> '{user_id_str}'")
                
                is_admin_in_db = db.is_admin(user_id_str)
                logger.info(f"🔎 Результат проверки админа в БД: {is_admin_in_db}")
                
                if is_admin_in_db:
                    logger.info(f"✅ Пользователь {user_id} найден в базе данных как админ")
                    
                    logger.info(f"🛠️ Создаем инлайн-клавиатуру панели администратора")
                    # Создаем инлайн-клавиатуру для панели администратора
                    kb = [
                        [
                            InlineKeyboardButton(text="📋 Заявки", callback_data="admin_requests"),
                            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
                        ],
                        [
                            InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_management"),
                            InlineKeyboardButton(text="👨‍💼 Сотрудники", callback_data="admin_staff")
                        ],
                        [
                            InlineKeyboardButton(text="🔄 Обновить должности", callback_data="admin_update_positions")
                        ],
                        [
                            InlineKeyboardButton(text="🏠 Главное меню", callback_data="admin_main_menu")
                        ]
                    ]
                    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
                    
                    # Удаляем клавиатуру снизу
                    from aiogram.types import ReplyKeyboardRemove
                    logger.info(f"⌨️ Удаляем стандартную клавиатуру снизу")
                    
                    logger.info(f"📤 Отправляем панель администратора пользователю")
                    await message.answer(
                        "👨‍💼 <b>Панель администратора</b>\n\n"
                        "Ваши права администратора подтверждены.\n"
                        "Выберите действие:",
                        reply_markup=admin_keyboard
                    )
                    logger.info(f"✅ Панель администратора успешно отправлена пользователю {user_id}")
                else:
                    logger.warning(f"❌ Пользователь {user_id} не найден в базе данных как админ - доступ запрещен")
                    await message.answer(
                        "⛔ У вас недостаточно прав для доступа к панели администратора."
                    )
                    logger.info(f"📤 Отправлено сообщение об отказе в доступе пользователю {user_id}")
            except Exception as e:
                logger.error(f"❌ Ошибка при проверке админа в БД: {e}")
                logger.exception("Подробная ошибка при проверке админа:")
                await message.answer(
                    "⚠️ Произошла ошибка при проверке ваших прав администратора. Попробуйте позже или обратитесь к разработчику."
                )
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке наличия пользователя в конфиге: {e}")
        logger.exception("Подробная ошибка при проверке наличия в конфиге:")
        await message.answer(
            "⚠️ Произошла ошибка при проверке ваших прав администратора. Попробуйте позже или обратитесь к разработчику."
        )

# Обработчик кнопки "Заявки"
@router.message(F.text == "📋 Заявки", is_admin_filter)
async def show_requests(message: Message):
    """Отображает список заявок на регистрацию"""
    requests = db.get_pending_registration_requests()
    
    if not requests:
        # Создаем инлайн-клавиатуру для возврата к админ-панели
        kb = [
            [InlineKeyboardButton(text="◀️ Назад к админке", callback_data="admin_menu")]
        ]
        admin_back_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        
        await message.answer(
            "📭 На данный момент нет заявок на регистрацию.",
            reply_markup=admin_back_keyboard
        )
        return
    
    await message.answer(
        f"📋 <b>Заявки на регистрацию ({len(requests)})</b>\n\n"
        f"Выбери заявку для обработки:",
        reply_markup=keyboards.get_pending_requests_keyboard(requests)
    )

# Добавляем новый обработчик для кнопки "Заявки на регистрацию"
@router.message(F.text == "📋 Заявки на регистрацию")
async def show_registration_requests(message: Message):
    """Отображает список заявок на регистрацию (альтернативная кнопка)"""
    # Перенаправляем на существующий обработчик
    await show_requests(message)

# Обработчик запроса обновления списка заявок
@router.callback_query(F.data == "refresh_requests")
async def refresh_requests(callback: CallbackQuery):
    """Обновляет список заявок"""
    requests = db.get_pending_registration_requests()
    
    if not requests:
        await callback.message.edit_text(
            "📭 На данный момент нет заявок на регистрацию."
        )
        return
    
    await callback.message.edit_text(
        f"📋 <b>Заявки на регистрацию ({len(requests)})</b>\n\n"
        f"Выбери заявку для обработки:",
        reply_markup=keyboards.get_pending_requests_keyboard(requests)
    )
    
    await callback.answer("Список обновлен")

# Обработчик для кнопки "Назад к админке"
@router.callback_query(F.data.in_(["admin_menu", "back_to_admin"]))
async def admin_menu_callback(callback: CallbackQuery):
    """Возвращает к админ-меню"""
    kb = [
        [
            InlineKeyboardButton(text="📋 Заявки", callback_data="admin_requests"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_management"),
            InlineKeyboardButton(text="👨‍💼 Сотрудники", callback_data="admin_staff")
        ],
        [
            InlineKeyboardButton(text="🔄 Обновить должности", callback_data="admin_update_positions")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="admin_main_menu")
        ]
    ]
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await callback.message.edit_text(
        "👨‍💼 <b>Панель администратора</b>\n\n"
        "Ваши права администратора подтверждены.\n"
        "Выберите действие:",
        reply_markup=admin_keyboard
    )
    
    await callback.answer()

# Обработчик выбора заявки из списка
@router.callback_query(F.data.startswith("request_"))
async def select_request(callback: CallbackQuery):
    """Отображает данные конкретной заявки"""
    request_id = int(callback.data.split("_")[1])
    request = db.get_registration_request(request_id)
    
    if not request:
        await callback.message.edit_text(
            "❌ Заявка не найдена или уже обработана.",
            reply_markup=keyboards.get_back_to_main_keyboard()
        )
        await callback.answer("Заявка не найдена")
        return
    
    # Формируем текст с данными заявки
    username = request.get('telegram_username', 'Нет данных')
    username_text = f"@{username}" if username and not username.startswith('@') else username
    
    text = (
        f"📝 <b>Заявка #{request['id']}</b>\n\n"
        f"<b>Telegram ID:</b> {request['telegram_id']}\n"
        f"<b>Username:</b> {username_text}\n"
        f"<b>Имя пользователя:</b> {request.get('user_full_name', 'Нет данных')}\n"
        f"<b>Примерная должность:</b> {request.get('approximate_position', 'Не указана')}\n"
        f"<b>Дата создания:</b> {request['created_at']}\n\n"
        f"Выберите действие:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboards.get_request_action_keyboard(request_id)
    )
    
    await callback.answer()

# Обработчик кнопки "Назад к списку заявок"
@router.callback_query(F.data == "back_to_requests")
async def back_to_requests(callback: CallbackQuery):
    """Возврат к списку заявок"""
    requests = db.get_pending_registration_requests()
    
    if not requests:
        await callback.message.edit_text(
            "📭 На данный момент нет заявок на регистрацию."
        )
        return
    
    await callback.message.edit_text(
        f"📋 <b>Заявки на регистрацию ({len(requests)})</b>\n\n"
        f"Выбери заявку для обработки:",
        reply_markup=keyboards.get_pending_requests_keyboard(requests)
    )
    
    await callback.answer()

# Обработчик кнопки "Отклонить заявку"
@router.callback_query(F.data.startswith("reject_request_"))
async def reject_request(callback: CallbackQuery):
    """Отклоняет заявку на регистрацию"""
    request_id = int(callback.data.split("_")[2])
    
    # Обновляем статус заявки
    success = db.process_registration_request(
        request_id=request_id,
        status="rejected",
        admin_id=str(callback.from_user.id)
    )
    
    if not success:
        await callback.message.edit_text(
            "❌ Не удалось отклонить заявку. Попробуйте позже.",
            reply_markup=keyboards.get_back_to_main_keyboard()
        )
        await callback.answer("Ошибка")
        return
    
    # Получаем данные заявки
    request = db.get_registration_request(request_id)
    
    await callback.message.edit_text(
        f"✅ Заявка #{request_id} успешно отклонена.",
        reply_markup=keyboards.get_back_to_main_keyboard()
    )
    
    # Отправляем уведомление пользователю
    bot = callback.bot
    await bot.send_message(
        chat_id=request['telegram_id'],
        text="❌ <b>Заявка отклонена</b>\n\n"
             "Ваша заявка на регистрацию была отклонена администратором.\n"
             "Возможно, вы указали неверные данные или не являетесь сотрудником организации.\n\n"
             "Если вы считаете, что произошла ошибка, свяжитесь с администрацией."
    )
    
    await callback.answer("Заявка отклонена")

# Обработчик кнопки "Одобрить заявку"
@router.callback_query(F.data.startswith("approve_request_"))
async def approve_request(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс одобрения заявки"""
    request_id = int(callback.data.split("_")[2])
    
    # Получаем данные заявки
    request = db.get_registration_request(request_id)
    
    if not request:
        await callback.message.edit_text(
            "❌ Заявка не найдена или уже обработана.",
            reply_markup=keyboards.get_back_to_main_keyboard()
        )
        await callback.answer("Заявка не найдена")
        return
    
    # Сохраняем ID заявки в состоянии
    await state.update_data(request_id=request_id)
    
    # Получаем список должностей из API
    try:
        # Запрашиваем должности через API
        positions = await api_client.get_positions()
        
        if not positions:
            # Сообщаем об ошибке получения должностей
            logger.error("API не вернул должности")
            await callback.message.edit_text(
                f"❌ <b>Ошибка при получении должностей из API</b>\n\n"
                f"Невозможно обработать заявку №{request_id}, так как не удалось получить список должностей. "
                f"Пожалуйста, проверьте соединение с API или обратитесь к системному администратору.",
                reply_markup=keyboards.get_back_to_request_keyboard(request_id)
            )
            await callback.answer("Ошибка получения должностей")
            return
        
        # Даже если API недоступен, мы получим фиктивные должности,
        # так что продолжаем обработку в любом случае
        
        # Сохраняем список позиций в состоянии
        await state.update_data(positions=positions)
        
        # Устанавливаем состояние ожидания выбора должности
        await state.set_state(AdminStates.waiting_for_position_selection)
        
        # Меняем сообщение на выбор должности
        await callback.message.edit_text(
            f"👨‍💼 <b>Выбор должности для заявки #{request_id}</b>\n\n"
            f"<b>Пользователь:</b> {request.get('user_full_name', 'Нет данных')}\n"
            f"<b>Примерная должность:</b> {request.get('approximate_position', 'Не указана')}\n\n"
            f"Выберите должность из списка или вернитесь к заявке:",
            reply_markup=keyboards.get_positions_keyboard(positions, request_id)
        )
        
        # Также запрашиваем список отделов, чтобы потом можно было выбрать
        divisions = await api_client.get_divisions()
        if divisions:
            await state.update_data(divisions=divisions)
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при получении должностей: {e}")
        await callback.message.edit_text(
            f"❌ <b>Произошла ошибка при получении списка должностей:</b> {str(e)}\n\n"
            f"Пожалуйста, попробуйте позже или обратитесь к администратору системы.",
            reply_markup=keyboards.get_back_to_request_keyboard(request_id)
        )
        await callback.answer("Ошибка")

# Обработчик выбора должности
@router.callback_query(StateFilter(AdminStates.waiting_for_position_selection), F.data.startswith("position_"))
async def select_position(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор должности и генерирует код приглашения"""
    position_id = int(callback.data.split("_")[1])
    
    # Получаем данные из состояния
    data = await state.get_data()
    request_id = data.get("request_id")
    positions = data.get("positions", [])
    divisions = data.get("divisions", [])
    
    # Получаем данные заявки
    request = db.get_registration_request(request_id)
    
    if not request:
        await callback.message.edit_text(
            "❌ Заявка не найдена или уже обработана.",
            reply_markup=keyboards.get_back_to_main_keyboard()
        )
        await callback.answer("Заявка не найдена")
        await state.clear()
        return
    
    # Находим выбранную должность в списке
    selected_position = None
    for position in positions:
        if position.get('id') == position_id or str(position.get('id')) == str(position_id):
            selected_position = position
            break
    
    if not selected_position:
        await callback.message.edit_text(
            "❌ Выбранная должность не найдена. Попробуйте еще раз.",
            reply_markup=keyboards.get_back_to_request_keyboard(request_id)
        )
        await callback.answer("Должность не найдена")
        await state.clear()
        return
    
    # Сохраняем выбранную должность в состоянии
    await state.update_data(
        selected_position_id=position_id,
        selected_position_name=selected_position.get('name', selected_position.get('title', 'Неизвестная должность')),
        selected_position=selected_position
    )
    
    # Если есть отделы, предлагаем выбрать отдел
    if divisions:
        await state.set_state(AdminStates.waiting_for_division_selection)
        
        # Формируем клавиатуру с отделами
        await callback.message.edit_text(
            f"🏢 <b>Выбор отдела для заявки #{request_id}</b>\n\n"
            f"<b>Пользователь:</b> {request.get('user_full_name', 'Нет данных')}\n"
            f"<b>Выбранная должность:</b> {selected_position.get('name', selected_position.get('title', 'Неизвестная должность'))}\n\n"
            f"Выберите отдел из списка или пропустите этот шаг:",
            reply_markup=keyboards.get_api_divisions_keyboard(divisions, request_id)
        )
        
        await callback.answer()
        return
    
    # Если отделов нет, генерируем код приглашения
    await generate_invitation_code(callback, state)

# Обработчик выбора отдела
@router.callback_query(StateFilter(AdminStates.waiting_for_division_selection), F.data.startswith("division_"))
async def select_division(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор отдела и генерирует код приглашения"""
    division_id = int(callback.data.split("_")[1])
    
    # Получаем данные из состояния
    data = await state.get_data()
    divisions = data.get("divisions", [])
    
    # Находим выбранный отдел в списке
    selected_division = None
    for division in divisions:
        if division.get('id') == division_id or str(division.get('id')) == str(division_id):
            selected_division = division
            break
    
    if not selected_division:
        await callback.answer("Отдел не найден")
        return
    
    # Сохраняем выбранный отдел в состоянии
    await state.update_data(
        selected_division_id=division_id,
        selected_division_name=selected_division.get('name', 'Неизвестный отдел'),
        selected_division=selected_division
    )
    
    # Генерируем код приглашения
    await generate_invitation_code(callback, state)

# Обработчик пропуска выбора отдела
@router.callback_query(StateFilter(AdminStates.waiting_for_division_selection), F.data == "skip_division")
async def skip_division(callback: CallbackQuery, state: FSMContext):
    """Пропускает выбор отдела и генерирует код приглашения"""
    # Генерируем код приглашения
    await generate_invitation_code(callback, state)

# Обработчик возврата к выбору должности
@router.callback_query(F.data == "back_to_position_selection")
async def back_to_position_selection(callback: CallbackQuery, state: FSMContext):
    """Возвращает к выбору должности"""
    # Получаем данные из состояния
    data = await state.get_data()
    request_id = data.get("request_id")
    positions = data.get("positions", [])
    request = db.get_registration_request(request_id)
    
    # Устанавливаем состояние выбора должности
    await state.set_state(AdminStates.waiting_for_position_selection)
    
    # Отображаем список должностей
    await callback.message.edit_text(
        f"👨‍💼 <b>Выбор должности для заявки #{request_id}</b>\n\n"
        f"<b>Пользователь:</b> {request.get('user_full_name', 'Нет данных')}\n"
        f"<b>Примерная должность:</b> {request.get('approximate_position', 'Не указана')}\n\n"
        f"Выберите должность из списка или вернитесь к заявке:",
        reply_markup=keyboards.get_positions_keyboard(positions, request_id)
    )
    
    await callback.answer()

# Функция для генерации кода приглашения
async def generate_invitation_code(callback: CallbackQuery, state: FSMContext):
    """Генерирует код приглашения на основе выбранной должности и отдела"""
    # Получаем данные из состояния
    data = await state.get_data()
    request_id = data.get("request_id")
    request = db.get_registration_request(request_id)
    
    # Получаем данные о выбранной должности
    selected_position = data.get("selected_position")
    position_id = selected_position.get('id')
    position_name = selected_position.get('name', selected_position.get('title', 'Неизвестная должность'))
    
    # Получаем данные о выбранном отделе (если есть)
    selected_division = data.get("selected_division")
    division_id = None
    division_name = "Не указан"
    
    if selected_division:
        division_id = selected_division.get('id')
        division_name = selected_division.get('name', 'Неизвестный отдел')
    
    # Данные для API
    invite_code_data = {
        "position_id": position_id,
        "division_id": division_id,
        "telegram_id": request.get('telegram_id'),
        "user_full_name": request.get('user_full_name', 'Нет данных'),
        "organization_id": 1  # По умолчанию используем первую организацию
    }
    
    # Генерируем код через API
    api_result = await api_client.generate_invitation_code(invite_code_data)
    
    if api_result.get("success"):
        # Код успешно сгенерирован через API
        invitation_code = api_result.get("code")
        expires_at = api_result.get("expires_at", "неизвестно")
        
        # Сохраняем код в БД
        db.save_invitation_code(
            request_id=request_id,
            code=invitation_code,
            position_id=position_id,
            position_name=position_name,
            division_id=division_id,
            division_name=division_name,
            expires_at=expires_at
        )
        
        # Отправляем код пользователю
        await send_invitation_to_user(
            request_id, 
            invitation_code, 
            position_name, 
            division_name if division_id else None
        )
        
        # Отображаем сообщение админу о успешной генерации кода
        await callback.message.edit_text(
            f"✅ <b>Код приглашения сгенерирован для заявки #{request_id}</b>\n\n"
            f"<b>Код:</b> <code>{invitation_code}</code>\n"
            f"<b>Действителен до:</b> {expires_at}\n"
            f"<b>Пользователь:</b> {request.get('user_full_name', 'Нет данных')}\n"
            f"<b>Должность:</b> {position_name}\n"
            f"<b>Отдел:</b> {division_name}\n\n"
            f"Код был отправлен пользователю.",
            reply_markup=keyboards.get_back_to_request_keyboard(request_id)
        )
    else:
        # Ошибка при генерации кода через API
        error_message = api_result.get("message", "Неизвестная ошибка")
        
        await callback.message.edit_text(
            f"❌ <b>Ошибка при генерации кода приглашения</b>\n\n"
            f"<b>Заявка:</b> #{request_id}\n"
            f"<b>Пользователь:</b> {request.get('user_full_name', 'Нет данных')}\n"
            f"<b>Должность:</b> {position_name}\n"
            f"<b>Отдел:</b> {division_name}\n\n"
            f"<b>Ошибка:</b> {error_message}",
            reply_markup=keyboards.get_back_to_request_keyboard(request_id)
        )
    
    # Обновляем состояние заявки
    db.update_registration_request(request_id, status="approved")
    
    # Очищаем состояние
    await state.clear()
    
    await callback.answer()

# Обработчик кнопки "Назад" при выборе должности
@router.callback_query(F.data.startswith("back_to_request_"))
async def back_to_request(callback: CallbackQuery, state: FSMContext):
    """Возврат к просмотру заявки"""
    request_id = int(callback.data.split("_")[3])
    request = db.get_registration_request(request_id)
    
    await state.clear()
    
    if not request:
        await callback.message.edit_text(
            "❌ Заявка не найдена или уже обработана.",
            reply_markup=keyboards.get_back_to_main_keyboard()
        )
        await callback.answer("Заявка не найдена")
        return
    
    # Формируем текст с данными заявки
    username = request.get('telegram_username', 'Нет данных')
    username_text = f"@{username}" if username and not username.startswith('@') else username
    
    text = (
        f"📝 <b>Заявка #{request['id']}</b>\n\n"
        f"<b>Telegram ID:</b> {request['telegram_id']}\n"
        f"<b>Username:</b> {username_text}\n"
        f"<b>Имя пользователя:</b> {request.get('user_full_name', 'Нет данных')}\n"
        f"<b>Примерная должность:</b> {request.get('approximate_position', 'Не указана')}\n"
        f"<b>Дата создания:</b> {request['created_at']}\n\n"
        f"Выберите действие:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboards.get_request_action_keyboard(request_id)
    )
    
    await callback.answer()

# Обработчик кнопки "Статистика"
@router.message(F.text == "📊 Статистика", is_admin_filter)
async def show_stats(message: Message):
    """Показывает статистику бота и админа"""
    admin_id = str(message.from_user.id)
    
    # Получаем статистику админа
    admin_stats = db.get_admin_stats(admin_id)
    
    # Получаем общую статистику
    staff = db.get_all_staff()
    requests = db.get_pending_registration_requests()
    
    # Создаем инлайн-клавиатуру для возврата к админ-панели
    kb = [
        [InlineKeyboardButton(text="◀️ Назад к админке", callback_data="admin_menu")]
    ]
    admin_back_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    # Формируем текст со статистикой
    text = (
        f"📊 <b>Статистика</b>\n\n"
        f"<b>Общая статистика:</b>\n"
        f"• Всего сотрудников: {len(staff)}\n"
        f"• Ожидающих заявок: {len(requests)}\n\n"
        f"<b>Ваша статистика:</b>\n"
        f"• Обработано заявок: {admin_stats['processed_requests']}\n"
        f"• Одобрено заявок: {admin_stats['approved_requests']}\n"
        f"• Отклонено заявок: {admin_stats['rejected_requests']}\n"
        f"• Сгенерировано кодов: {admin_stats['generated_codes']}\n"
        f"• Использовано кодов: {admin_stats['used_codes']}"
    )
    
    await message.answer(
        text,
        reply_markup=admin_back_keyboard
    )

# Обработчик кнопки "Управление админами"
@router.callback_query(F.data == "admin_management")
async def handle_admin_management(callback: CallbackQuery):
    """Обработчик инлайн-кнопки 'Управление админами'"""
    # Создаем инлайн-клавиатуру управления админами
    kb = [
        [
            InlineKeyboardButton(text="➕ Добавить админа", callback_data="add_admin"),
            InlineKeyboardButton(text="➖ Удалить админа", callback_data="remove_admin")
        ],
        [
            InlineKeyboardButton(text="📜 Список админов", callback_data="list_admins")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад к админке", callback_data="admin_menu")
        ]
    ]
    admin_management_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    # Изменяем ТЕКУЩЕЕ сообщение вместо создания нового
    await callback.message.edit_text(
        "👥 <b>Управление администраторами</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_management_keyboard
    )
    
    await callback.answer()

# Добавляем новый обработчик для кнопки "Управление пользователями"
@router.message(F.text == "👤 Управление пользователями")
async def user_management(message: Message):
    """Отображает меню управления пользователями"""
    # Создаем клавиатуру для возврата к админ-панели
    kb = [
        [
            InlineKeyboardButton(text="➕ Добавить админа", callback_data="add_admin"),
            InlineKeyboardButton(text="➖ Удалить админа", callback_data="remove_admin")
        ],
        [
            InlineKeyboardButton(text="📜 Список админов", callback_data="list_admins")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад к админке", callback_data="admin_menu")
        ]
    ]
    admin_management_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await message.answer(
        "👥 <b>Управление администраторами</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_management_keyboard
    )

# Обработчик для кнопки "Удалить админа"
@router.callback_query(F.data == "remove_admin")
async def handle_remove_admin(callback: CallbackQuery):
    """Упрощенный обработчик кнопки 'Удалить админа'"""
    text = "Функция удаления админа отключена."
    
    # Возвращаемся к панели администратора
    kb = [
        [
            InlineKeyboardButton(text="📋 Заявки", callback_data="admin_requests"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_management"),
            InlineKeyboardButton(text="👨‍💼 Сотрудники", callback_data="admin_staff")
        ],
        [
            InlineKeyboardButton(text="🔄 Обновить должности", callback_data="admin_update_positions")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="admin_main_menu")
        ]
    ]
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await callback.message.edit_text(text, reply_markup=admin_keyboard)
    await callback.answer()

# Обработчик для кнопки "Список админов"
@router.callback_query(F.data == "list_admins")
async def handle_list_admins(callback: CallbackQuery):
    """Упрощенный обработчик кнопки 'Список админов'"""
    # Получаем ID текущего пользователя
    user_id = callback.from_user.id
    username = callback.from_user.username or "Unknown"
    
    # Текст со списком админов
    text = f"👨‍💼 <b>Список администраторов</b>\n\n"
    text += f"<b>Вы:</b> {user_id} (@{username})\n\n"
    text += f"<b>Все админы:</b> {config.ADMIN_IDS}"
    
    # Кнопка назад к управлению админами
    kb = [[InlineKeyboardButton(text="◀️ Назад", callback_data="admin_management")]]
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await callback.message.edit_text(text, reply_markup=back_keyboard)
    await callback.answer()

# Обработчик кнопки "Назад к управлению админами"
@router.callback_query(F.data == "back_to_admin_management")
async def back_to_admin_management(callback: CallbackQuery):
    """Возврат к меню управления админами"""
    await callback.message.edit_text(
        "👥 <b>Управление админами</b>\n\n"
        "Выберите действие из меню ниже:"
    )
    await callback.message.answer(
        "Выбери действие:",
        reply_markup=keyboards.get_admin_management_keyboard()
    )
    
    await callback.answer()

# Обработчик кнопки "Добавить админа"
@router.callback_query(F.data == "add_admin")
async def handle_add_admin(callback: CallbackQuery):
    """Обработчик кнопки 'Добавить админа' (инлайн)"""
    # Добавляем текущего пользователя как админа напрямую
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username or "Unknown"
        
        # Добавляем пользователя в БД как админа
        success = db.add_admin(
            telegram_id=str(user_id),
            full_name=callback.from_user.full_name or username,
            created_by="system"
        )
        
        if success:
            text = f"✅ Вы успешно добавлены как админ!\nID: {user_id}\nUsername: @{username}"
        else:
            text = f"⚠️ Не удалось добавить вас как админа. Возможно, вы уже добавлены."
        
        # Добавляем текущего пользователя в конфиг (для перестраховки)
        if user_id not in config.ADMIN_IDS:
            config.ADMIN_IDS.append(user_id)
            
        # Создаем инлайн-клавиатуру для возврата к панели администратора
        kb = [
            [
                InlineKeyboardButton(text="📋 Заявки", callback_data="admin_requests"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_management"),
                InlineKeyboardButton(text="👨‍💼 Сотрудники", callback_data="admin_staff")
            ],
            [
                InlineKeyboardButton(text="🔄 Обновить должности", callback_data="admin_update_positions")
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="admin_main_menu")
            ]
        ]
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        
        # Отправляем ответ с результатом
        await callback.message.edit_text(text, reply_markup=admin_keyboard)
    except Exception as e:
        # В случае ошибки выводим информацию для отладки
        error_text = f"❌ Ошибка при добавлении админа: {str(e)}\n\nID: {callback.from_user.id}"
        await callback.message.edit_text(error_text)
    
    await callback.answer()

# Обработчик ввода Telegram ID нового админа
@router.message(StateFilter(AdminStates.waiting_for_admin_id))
async def process_admin_id(message: Message, state: FSMContext):
    """Обрабатывает ввод Telegram ID нового админа"""
    admin_id = message.text.strip()
    
    # Проверяем формат (ID или username)
    if admin_id.isdigit():
        # Это числовой ID
        telegram_id = admin_id
    elif admin_id.startswith('@'):
        # Это username - предупреждаем, что нужен ID
        await message.answer(
            "⚠️ К сожалению, добавление админа по username не поддерживается. "
            "Введите числовой Telegram ID пользователя."
        )
        return
    else:
        await message.answer(
            "❌ Некорректный формат. Введите числовой Telegram ID пользователя."
        )
        return
    
    # Проверяем, существует ли уже такой админ
    existing_admin = db.get_admin_by_telegram_id(telegram_id)
    if existing_admin and existing_admin['is_active']:
        await message.answer(
            "❌ Этот пользователь уже является админом.",
            reply_markup=keyboards.get_admin_management_keyboard()
        )
        await state.clear()
        return
    
    # Сохраняем ID в состоянии
    await state.update_data(admin_telegram_id=telegram_id)
    
    # Переходим к вводу имени
    await state.set_state(AdminStates.waiting_for_admin_name)
    
    await message.answer(
        "👤 Введите имя нового админа:"
    )

# Обработчик ввода имени нового админа
@router.message(StateFilter(AdminStates.waiting_for_admin_name))
async def process_admin_name(message: Message, state: FSMContext):
    """Обрабатывает ввод имени нового админа"""
    admin_name = message.text.strip()
    
    if not admin_name:
        await message.answer("❌ Имя не может быть пустым. Введите имя админа:")
        return
    
    # Сохраняем имя в состоянии
    await state.update_data(admin_name=admin_name)
    
    # Переходим к подтверждению
    await state.set_state(AdminStates.waiting_for_admin_confirmation)
    
    # Получаем данные для подтверждения
    data = await state.get_data()
    
    await message.answer(
        f"👤 <b>Подтверждение добавления админа</b>\n\n"
        f"<b>Telegram ID:</b> {data['admin_telegram_id']}\n"
        f"<b>Имя:</b> {data['admin_name']}\n\n"
        f"Подтвердите добавление нового админа:",
        reply_markup=keyboards.get_confirm_keyboard()
    )

# Обработчик подтверждения добавления админа
@router.callback_query(StateFilter(AdminStates.waiting_for_admin_confirmation))
async def confirm_add_admin(callback: CallbackQuery, state: FSMContext):
    """Подтверждает добавление нового админа"""
    if callback.data == "confirm":
        # Получаем данные из состояния
        data = await state.get_data()
        
        # Добавляем нового админа
        success = db.add_admin(
            telegram_id=data['admin_telegram_id'],
            full_name=data['admin_name'],
            created_by=str(callback.from_user.id)
        )
        
        if success:
            # Отправляем уведомление новому админу
            try:
                await callback.bot.send_message(
                    chat_id=data['admin_telegram_id'],
                    text=f"🎉 <b>Поздравляем!</b>\n\n"
                         f"Вы назначены администратором бота OFS Global.\n"
                         f"Для входа в панель администратора отправьте команду /admin"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления новому админу: {e}")
            
            await callback.message.edit_text(
                f"✅ Админ успешно добавлен!\n\n"
                f"<b>Telegram ID:</b> {data['admin_telegram_id']}\n"
                f"<b>Имя:</b> {data['admin_name']}"
            )
            
            await callback.message.answer(
                "Выбери дальнейшее действие:",
                reply_markup=keyboards.get_admin_management_keyboard()
            )
        else:
            await callback.message.edit_text(
                "❌ Не удалось добавить админа. Попробуйте позже."
            )
    else:  # cancel
        await callback.message.edit_text(
            "❌ Добавление админа отменено."
        )
        
        await callback.message.answer(
            "Выбери дальнейшее действие:",
            reply_markup=keyboards.get_admin_management_keyboard()
        )
    
    # Очищаем состояние
    await state.clear()
    await callback.answer()

# Обработчик кнопки "Главное меню"
@router.message(F.text == "🏠 Главное меню")
async def main_menu_from_admin(message: Message):
    """Возвращает в главное меню из админ-панели"""
    from aiogram.types import ReplyKeyboardRemove
    
    # Удаляем нижнюю клавиатуру
    await message.answer(
        "Возвращаемся в главное меню...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Вызываем функцию главного меню
    from telegram_bot.handlers import main_menu
    await main_menu(message)

# Обработчик кнопки "Сотрудники"
@router.message(F.text == "🧑‍💼 Сотрудники", is_admin_filter)
async def show_staff(message: Message):
    """Отображает список сотрудников"""
    staff = db.get_all_staff()
    
    if not staff:
        await message.answer(
            "📭 Список сотрудников пуст.",
            reply_markup=keyboards.get_admin_keyboard()
        )
        return
    
    await message.answer(
        f"👥 <b>Список сотрудников ({len(staff)})</b>\n\n"
        f"Выберите сотрудника для просмотра деталей:",
        reply_markup=keyboards.get_staff_list_keyboard(staff)
    )

# Обработчик выбора админа для действий
@router.callback_query(F.data.startswith("admin_"))
async def admin_callback_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопок админ-панели"""
    # Получаем действие из колбэка
    action = callback.data.split("_")[1]
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    logger.info(f"👤 Админ {user_id} (@{username}) выполнил действие: {action}")
    
    # Логика обработки различных действий админа
    if action == "view_requests":
        logger.info(f"📊 Админ {user_id} запросил просмотр заявок на регистрацию")
        # Получаем список заявок
        registration_requests = db.get_registration_requests()
        
        if registration_requests:
            count = len(registration_requests)
            logger.info(f"📋 Найдено {count} заявок на регистрацию")
            await callback.message.edit_text(
                f"📝 Найдено {count} заявок на регистрацию\n\n"
                "Выберите действие:",
                reply_markup=keyboards.get_requests_keyboard(registration_requests)
            )
        else:
            logger.info("📋 Заявок на регистрацию не найдено")
            await callback.message.edit_text(
                "📝 Заявок на регистрацию не найдено\n\n"
                "Когда пользователи будут регистрироваться, их заявки появятся здесь.",
                reply_markup=keyboards.get_back_to_admin_keyboard()
            )
    
    elif action == "manage_admins":
        logger.info(f"👥 Админ {user_id} запросил управление администраторами")
        # Получаем список админов
        admins = db.get_admins()
        
        if admins:
            count = len(admins)
            logger.info(f"👥 Найдено {count} администраторов в системе")
            await callback.message.edit_text(
                f"👥 Администраторы ({count}):\n\n" + 
                "\n".join([f"{i+1}. {admin['full_name']} (ID: {admin['telegram_id']})" 
                          for i, admin in enumerate(admins)]),
                reply_markup=keyboards.get_admins_keyboard()
            )
        else:
            logger.info("👥 Администраторы не найдены в системе")
            await callback.message.edit_text(
                "👥 Администраторы не найдены\n\n"
                "Вы можете добавить новых администраторов.",
                reply_markup=keyboards.get_admins_keyboard()
            )
    
    elif action == "add_admin":
        logger.info(f"➕ Админ {user_id} инициировал добавление нового администратора")
        await state.set_state(AdminStates.waiting_for_admin_id)
        await callback.message.edit_text(
            "👤 Введите Telegram ID нового администратора:",
            reply_markup=keyboards.get_cancel_keyboard()
        )
    
    elif action == "sync_data":
        logger.info(f"🔄 Админ {user_id} запустил синхронизацию данных")
        await callback.message.edit_text(
            "🔄 Синхронизация данных...",
            reply_markup=None
        )
        
        try:
            # Импорт функции синхронизации (переделана на прямое подключение к БД)
            from sync_db import sync_all_data
            
            # Выполняем синхронизацию
            success = sync_all_data()
            
            if success:
                logger.info("✅ Синхронизация данных успешно завершена")
                await callback.message.edit_text(
                    "✅ Синхронизация данных успешно завершена!",
                    reply_markup=keyboards.get_back_to_admin_keyboard()
                )
            else:
                logger.error("❌ Ошибка при синхронизации данных")
                await callback.message.edit_text(
                    "❌ Произошла ошибка при синхронизации данных.",
                    reply_markup=keyboards.get_back_to_admin_keyboard()
                )
        except Exception as e:
            error_message = str(e)
            logger.error(f"❌ Ошибка при синхронизации данных: {error_message}")
            await callback.message.edit_text(
                f"❌ Произошла ошибка при синхронизации данных:\n{error_message}",
                reply_markup=keyboards.get_back_to_admin_keyboard()
            )
    
    elif action == "back":
        logger.info(f"🔙 Админ {user_id} вернулся в главное меню администратора")
        # Возвращаемся в главное меню админа
        await callback.message.edit_text(
            "🛠️ Панель администратора\n\n"
            "Выберите действие:",
            reply_markup=keyboards.get_admin_keyboard()
        )
    
    # Обработка остальных действий...
    await callback.answer()

# Обработчик подтверждения заявки на регистрацию
@router.callback_query(F.data.startswith("approve_"))
async def approve_registration(callback: CallbackQuery):
    """Обработчик подтверждения заявки на регистрацию"""
    user_id = callback.data.split("_")[1]
    admin_id = callback.from_user.id
    admin_username = callback.from_user.username
    
    logger.info(f"✅ Админ {admin_id} (@{admin_username}) одобрил заявку пользователя {user_id}")
    
    # Логика подтверждения заявки
    if db.approve_registration(user_id):
        # Получаем данные пользователя
        user_data = db.get_user_data(user_id)
        logger.info(f"📋 Заявка пользователя {user_id} ({user_data.get('full_name', 'Неизвестно')}) успешно одобрена")
        
        # Отправляем уведомление пользователю
        try:
            from aiogram import Bot
            from config import Config
            config = Config()
            bot = Bot(token=config.BOT_TOKEN)
            
            await bot.send_message(
                chat_id=user_id,
                text="✅ Ваша заявка на регистрацию была одобрена администратором! Теперь вы можете пользоваться всеми функциями бота."
            )
            logger.info(f"📩 Уведомление об одобрении успешно отправлено пользователю {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке уведомления пользователю {user_id}: {e}")
        
        # Обновляем сообщение в интерфейсе админа
        await callback.message.edit_text(
            f"✅ Заявка пользователя {user_data.get('full_name', 'Неизвестно')} (ID: {user_id}) успешно одобрена!",
            reply_markup=keyboards.get_back_to_admin_keyboard()
        )
    else:
        logger.error(f"❌ Ошибка при одобрении заявки пользователя {user_id}")
        await callback.message.edit_text(
            f"❌ Произошла ошибка при одобрении заявки пользователя (ID: {user_id}).",
            reply_markup=keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Обработчик отклонения заявки на регистрацию
@router.callback_query(F.data.startswith("reject_"))
async def reject_registration(callback: CallbackQuery, state: FSMContext):
    """Обработчик отклонения заявки на регистрацию"""
    user_id = callback.data.split("_")[1]
    admin_id = callback.from_user.id
    admin_username = callback.from_user.username
    
    logger.info(f"❌ Админ {admin_id} (@{admin_username}) отклонил заявку пользователя {user_id}")
    
    # Сохраняем ID пользователя в состоянии
    await state.update_data(rejected_user_id=user_id)
    
    # Запрашиваем причину отклонения
    await state.set_state(AdminStates.waiting_for_rejection_reason)
    await callback.message.edit_text(
        "Пожалуйста, укажите причину отклонения заявки:",
        reply_markup=keyboards.get_cancel_keyboard()
    )
    
    await callback.answer()

def register_admin_handlers(dispatcher: Router):
    """Регистрирует все обработчики админских команд"""
    dispatcher.include_router(router)

# Добавляем обработчики для инлайн-кнопок админ-панели

@router.callback_query(F.data == "admin_requests")
async def admin_show_requests(callback: CallbackQuery):
    """Показать список заявок на регистрацию"""
    await callback.answer()
    await show_requests(callback.message)

@router.callback_query(F.data == "admin_stats")
async def admin_show_stats(callback: CallbackQuery):
    """Показать статистику"""
    await callback.answer()
    await show_stats(callback.message)

@router.callback_query(F.data == "admin_management")
async def admin_show_management(callback: CallbackQuery):
    """Показать управление админами"""
    await callback.answer()
    kb = [
        [
            InlineKeyboardButton(text="➕ Добавить админа", callback_data="add_admin"),
            InlineKeyboardButton(text="➖ Удалить админа", callback_data="remove_admin")
        ],
        [
            InlineKeyboardButton(text="📋 Список админов", callback_data="list_admins")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin")
        ]
    ]
    manage_admins_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.edit_text(
        "👥 <b>Управление администраторами</b>\n\n"
        "Выберите действие:",
        reply_markup=manage_admins_kb
    )

@router.callback_query(F.data == "admin_staff")
async def admin_show_staff(callback: CallbackQuery):
    """Показать список сотрудников"""
    await callback.answer()
    # Получаем список всех подтвержденных сотрудников
    employees = db.get_all_employees()
    
    if not employees:
        kb = [[InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin")]]
        back_kb = InlineKeyboardMarkup(inline_keyboard=kb)
        await callback.message.edit_text(
            "👨‍💼 <b>Список сотрудников</b>\n\n"
            "В системе пока нет подтвержденных сотрудников.",
            reply_markup=back_kb
        )
        return
    
    # Создаем текст со списком сотрудников
    staff_text = "👨‍💼 <b>Список сотрудников</b>\n\n"
    for i, employee in enumerate(employees, 1):
        staff_text += f"{i}. {employee.full_name} - {employee.position}\n"
        staff_text += f"    📱 {employee.phone or 'Не указан'}\n"
        staff_text += f"    📧 {employee.email or 'Не указан'}\n\n"
    
    # Добавляем кнопку назад
    kb = [[InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin")]]
    back_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    
    # Разбиваем на части, если текст слишком длинный
    if len(staff_text) > 4000:
        await callback.message.edit_text(
            "👨‍💼 <b>Список сотрудников</b>\n\n"
            "Список слишком большой. Будет отправлено несколько сообщений.",
            reply_markup=back_kb
        )
        
        # Отправляем по частям
        chunks = [staff_text[i:i+4000] for i in range(0, len(staff_text), 4000)]
        for chunk in chunks[:-1]:
            await callback.message.answer(chunk)
        
        # Последний чанк с кнопкой назад
        await callback.message.answer(chunks[-1], reply_markup=back_kb)
    else:
        await callback.message.edit_text(staff_text, reply_markup=back_kb)

@router.callback_query(F.data == "admin_main_menu")
async def admin_main_menu(callback: CallbackQuery):
    """Вернуться в главное меню"""
    await callback.answer()
    
    # Отправляем сообщение с удалением клавиатуры
    from aiogram.types import ReplyKeyboardRemove
    await callback.message.answer(
        "Возвращаемся в главное меню...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Удаляем сообщение с админской клавиатурой
    await callback.message.delete()
    
    # Вызываем главное меню из другого модуля
    from telegram_bot.handlers import main_menu
    await main_menu(callback.message)

@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    """Вернуться к главной панели администратора"""
    await callback.answer()
    
    # Создаем инлайн-клавиатуру для панели администратора
    kb = [
        [
            InlineKeyboardButton(text="📋 Заявки", callback_data="admin_requests"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_management"),
            InlineKeyboardButton(text="👨‍💼 Сотрудники", callback_data="admin_staff")
        ],
        [
            InlineKeyboardButton(text="🔄 Обновить должности", callback_data="admin_update_positions")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="admin_main_menu")
        ]
    ]
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await callback.message.edit_text(
        "👨‍💼 <b>Панель администратора</b>\n\n"
        "Ваши права администратора подтверждены.\n"
        "Выберите действие:",
        reply_markup=admin_keyboard
    ) 