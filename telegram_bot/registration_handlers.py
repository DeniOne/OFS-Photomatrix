import logging
import re
from typing import Dict, Union, Any, Optional

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from database import BotDatabase
from states import RegistrationStates
import keyboards
from api_client import ApiClient
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

# Команда начала работы с ботом
@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = str(message.from_user.id)
    
    # Проверяем, зарегистрирован ли пользователь
    staff = db.get_employee_by_telegram_id(user_id)
    
    if staff:
        # Пользователь уже зарегистрирован
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Ты уже зарегистрирован в системе как сотрудник.\n"
            f"<b>Должность:</b> {staff.get('position_name', 'Не указана')}\n\n"
            f"Используй меню для навигации.",
            reply_markup=keyboards.get_main_keyboard()
        )
        return
    
    # Проверяем, есть ли активная заявка на регистрацию
    pending_request = db.get_pending_request_by_telegram_id(user_id)
    
    if pending_request:
        # У пользователя уже есть заявка на рассмотрении
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Твоя заявка на регистрацию уже отправлена и ожидает рассмотрения администратором.\n"
            f"Пожалуйста, дождись ответа. Тебе придет уведомление, как только заявка будет рассмотрена.",
            reply_markup=keyboards.get_main_keyboard()
        )
        return
    
    # Проверяем, есть ли код приглашения для этого пользователя
    invitation_code = db.get_active_invitation_code(user_id)
    
    if invitation_code:
        # У пользователя есть активный код, переходим к вводу кода
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Для тебя уже был сгенерирован код приглашения. Пожалуйста, введи его для завершения регистрации.",
            reply_markup=keyboards.get_reset_keyboard()
        )
        
        # Устанавливаем состояние ожидания ввода кода
        await message.bot.set_state(message.from_user.id, RegistrationStates.waiting_for_code, message.chat.id)
        return
    
    # Начинаем процесс регистрации - используем инлайн клавиатуру вместо обычной клавиатуры
    
    # Сначала удаляем нижнюю клавиатуру
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Создаем инлайн-клавиатуру
    kb = [
        [InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="start_registration")],
        [InlineKeyboardButton(text="🔑 У меня есть код", callback_data="have_code")],
        [InlineKeyboardButton(text="🔍 Проверить статус", callback_data="check_status")],
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about_bot")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="show_help")]
    ]
    inline_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await message.answer(
        f"Добро пожаловать в бот OFS Global для регистрации сотрудников.\n\n"
        f"Для начала процесса регистрации, пожалуйста, выберите вариант ниже:",
        reply_markup=inline_kb
    )

@router.callback_query(F.data == "start_registration")
async def callback_registration_start(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс регистрации через инлайн-кнопку"""
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    
    # Проверяем, зарегистрирован ли пользователь
    staff = db.get_employee_by_telegram_id(user_id)
    
    if staff:
        await callback.message.edit_text(
            "✅ Ты уже зарегистрирован в системе как сотрудник."
        )
        return
    
    # Проверяем, есть ли активная заявка на регистрацию
    pending_request = db.get_pending_request_by_telegram_id(user_id)
    
    if pending_request:
        await callback.message.edit_text(
            "⏳ Твоя заявка на регистрацию уже отправлена и ожидает рассмотрения администратором.\n"
            "Пожалуйста, дождись ответа."
        )
        return
    
    # Проверяем, есть ли код приглашения для этого пользователя
    invitation_code = db.get_active_invitation_code(user_id)
    
    if invitation_code:
        await callback.message.edit_text(
            "👨‍💼 Для тебя уже был сгенерирован код приглашения.\n"
            "Пожалуйста, введи его для завершения регистрации:"
        )
        
        # Устанавливаем состояние ожидания ввода кода
        await state.set_state(RegistrationStates.waiting_for_code)
        return
    
    # Сохраняем telegram_id в состоянии
    await state.update_data(telegram_id=user_id)
    
    # Если у пользователя есть username, сохраняем его
    if callback.from_user.username:
        await state.update_data(telegram_username=callback.from_user.username)
    
    # Сохраняем полное имя пользователя из Telegram
    full_name = f"{callback.from_user.first_name}"
    if callback.from_user.last_name:
        full_name += f" {callback.from_user.last_name}"
    
    await state.update_data(user_full_name=full_name)
    
    # Переходим к запросу подтверждения имени
    await state.set_state(RegistrationStates.waiting_for_name_confirmation)
    
    # Создаем инлайн-клавиатуру для подтверждения имени
    kb = [
        [
            InlineKeyboardButton(text="✅ Да", callback_data="confirm_name"),
            InlineKeyboardButton(text="❌ Нет", callback_data="reject_name")
        ]
    ]
    confirmation_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await callback.message.edit_text(
        f"👤 Твое имя в Telegram: <b>{full_name}</b>\n\n"
        f"Использовать это имя для регистрации?",
        reply_markup=confirmation_kb
    )

@router.callback_query(F.data == "confirm_name", StateFilter(RegistrationStates.waiting_for_name_confirmation))
async def callback_confirm_name(callback: CallbackQuery, state: FSMContext):
    """Подтверждение имени через инлайн-кнопку"""
    await callback.answer()
    
    # Имя подтверждено, переходим к выбору организации
    await state.set_state(RegistrationStates.waiting_for_organization)
    
    # Получаем список организаций из API
    organizations = await api_client.get_organizations()
    
    await callback.message.edit_text(
        "🏢 Выберите организацию, в которой вы работаете:",
        reply_markup=keyboards.get_organizations_keyboard(organizations)
    )

@router.callback_query(F.data.startswith("org_"), StateFilter(RegistrationStates.waiting_for_organization))
async def process_organization_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора организации"""
    await callback.answer()
    
    # Получаем ID организации из callback.data
    organization_id = int(callback.data.split("_")[1])
    
    # Получаем список организаций для поиска выбранной
    organizations = await api_client.get_organizations()
    
    # Ищем выбранную организацию
    selected_organization = None
    for org in organizations:
        if org.get('id') == organization_id:
            selected_organization = org
            break
    
    if not selected_organization:
        await callback.message.edit_text(
            "❌ Организация не найдена. Пожалуйста, попробуйте снова."
        )
        return
    
    # Сохраняем выбранную организацию в состоянии
    await state.update_data(
        organization_id=organization_id,
        organization_name=selected_organization.get('name', 'Неизвестная организация')
    )
    
    # Переходим к вводу должности (текстом)
    await state.set_state(RegistrationStates.waiting_for_position)
    
    await callback.message.edit_text(
        "Пожалуйста, введите вашу должность:"
    )

@router.callback_query(F.data == "reject_name", StateFilter(RegistrationStates.waiting_for_name_confirmation))
async def callback_reject_name(callback: CallbackQuery, state: FSMContext):
    """Отклонение имени через инлайн-кнопку"""
    await callback.answer()
    
    # Пользователь хочет ввести другое имя
    await state.set_state(RegistrationStates.waiting_for_name)
    
    await callback.message.edit_text(
        "👤 Пожалуйста, введи свое полное имя (ФИО):"
    )

@router.callback_query(F.data == "have_code")
async def callback_have_code(callback: CallbackQuery, state: FSMContext):
    """Обработчик нажатия на кнопку 'У меня есть код'"""
    await callback.answer()
    
    await callback.message.edit_text(
        "🔑 Пожалуйста, введи код приглашения, который ты получил:"
    )
    
    # Устанавливаем состояние ожидания ввода кода
    await state.set_state(RegistrationStates.waiting_for_code)

@router.callback_query(F.data == "check_status")
async def callback_check_status(callback: CallbackQuery):
    """Обработчик нажатия на кнопку 'Проверить статус'"""
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    
    # Проверяем, зарегистрирован ли пользователь
    staff = db.get_employee_by_telegram_id(user_id)
    
    if staff:
        await callback.message.edit_text(
            f"✅ <b>Статус проверки:</b>\n\n"
            f"Вы зарегистрированы в системе как сотрудник.\n"
            f"<b>Имя:</b> {staff.get('full_name', 'Не указано')}\n"
            f"<b>Должность:</b> {staff.get('position_name', 'Не указана')}\n\n"
            f"🏠 <a href='tg://bot_command?command=start'>Вернуться в главное меню</a>"
        )
        return
    
    # Проверяем, есть ли активная заявка на регистрацию
    pending_request = db.get_pending_request_by_telegram_id(user_id)
    
    if pending_request:
        await callback.message.edit_text(
            f"⏳ <b>Статус проверки:</b>\n\n"
            f"У вас есть активная заявка на регистрацию.\n"
            f"<b>Дата создания:</b> {pending_request.get('created_at', 'Не указана')}\n"
            f"<b>Статус:</b> Ожидает рассмотрения\n\n"
            f"Пожалуйста, дождитесь, когда администратор рассмотрит вашу заявку.\n"
            f"🏠 <a href='tg://bot_command?command=start'>Вернуться в главное меню</a>"
        )
        return
    
    # Проверяем, есть ли код приглашения для этого пользователя
    invitation_code = db.get_active_invitation_code(user_id)
    
    if invitation_code:
        await callback.message.edit_text(
            f"🔑 <b>Статус проверки:</b>\n\n"
            f"Для вас создан код приглашения, который ожидает активации.\n"
            f"<b>Срок действия до:</b> {invitation_code.get('expires_at', 'Не указан')}\n\n"
            f"Для завершения регистрации введите код.\n"
            f"🏠 <a href='tg://bot_command?command=start'>Вернуться в главное меню</a>"
        )
        return
    
    await callback.message.edit_text(
        "❌ <b>Статус проверки:</b>\n\n"
        "У вас нет активных заявок на регистрацию или приглашений.\n"
        "Чтобы начать процесс регистрации, выберите пункт '📝 Зарегистрироваться'.\n\n"
        "🏠 <a href='tg://bot_command?command=start'>Вернуться в главное меню</a>"
    )

@router.callback_query(F.data == "about_bot")
async def callback_about_bot(callback: CallbackQuery):
    """Обработчик нажатия на кнопку 'О боте'"""
    await callback.answer()
    
    await callback.message.edit_text(
        "ℹ️ <b>О боте</b>\n\n"
        "Этот бот предназначен для регистрации сотрудников компании OFS Global.\n"
        "Версия: 1.0.0\n"
        "Разработчик: OFS Development Team\n\n"
        "🏠 <a href='tg://bot_command?command=start'>Вернуться в главное меню</a>"
    )

@router.callback_query(F.data == "show_help")
async def callback_show_help(callback: CallbackQuery):
    """Обработчик нажатия на кнопку 'Помощь'"""
    await callback.answer()
    
    await callback.message.edit_text(
        "❓ <b>Справка</b>\n\n"
        "Как использовать бота:\n"
        "1. Нажмите на кнопку '📝 Зарегистрироваться'\n"
        "2. Следуйте инструкциям для заполнения данных\n"
        "3. Дождитесь проверки администратором\n"
        "4. Если у вас уже есть код приглашения, нажмите '🔑 У меня есть код'\n\n"
        "По вопросам поддержки обращайтесь к администратору системы.\n\n"
        "🏠 <a href='tg://bot_command?command=start'>Вернуться в главное меню</a>"
    )

def register_registration_handlers(dispatcher: Router):
    """Регистрирует все обработчики регистрации"""
    dispatcher.include_router(router) 