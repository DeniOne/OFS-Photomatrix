import logging
import aiohttp
from typing import List, Dict, Any, Optional
from config import Config
import time
from sync_db import get_divisions_from_db, get_sections_from_db, get_positions_from_db, clear_cache, sync_all_data
import os
import json
import asyncio
import aiofiles

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

# Загрузка конфигурации
config = Config()

class ApiClient:
    """Класс для взаимодействия с API основной системы"""
    
    def __init__(self, data_dir: str = './data'):
        """
        Инициализирует API клиент.
        
        Args:
            data_dir: Директория для хранения данных (для совместимости)
        """
        self.data_dir = data_dir
        
        # Для обратной совместимости проверяем наличие директории
        if not os.path.exists(data_dir):
            logger.info(f"Создаю директорию для данных: {data_dir}")
            os.makedirs(data_dir, exist_ok=True)
        
        # Пути к файлам для обратной совместимости
        self.positions_file = os.path.join(data_dir, 'positions.json')
        self.divisions_file = os.path.join(data_dir, 'divisions.json')
        self.sections_file = os.path.join(data_dir, 'sections.json')
        
        self.base_url = config.API_URL
        self.webhook_endpoint = config.API_WEBHOOK_ENDPOINT
        self.token_validation_endpoint = config.API_TOKEN_VALIDATION_ENDPOINT
        self.organizations_endpoint = config.API_ORGANIZATIONS_ENDPOINT
        
        # Используем эндпоинты из конфигурации
        self.positions_endpoint = config.API_POSITIONS_ENDPOINT
        self.divisions_endpoint = config.API_DIVISIONS_ENDPOINT
        self.sections_endpoint = config.API_SECTIONS_ENDPOINT
        self.staff_endpoint = config.API_STAFF_ENDPOINT
        
        # Получаем API ключ из конфигурации
        self.api_key = config.API_KEY
        if self.api_key:
            logger.info("API ключ успешно загружен")
        else:
            logger.warning("API ключ не найден в конфигурации")
            
        # Кэш данных
        self._positions_cache = None
        self._positions_cache_time = 0
        self._divisions_cache = None
        self._divisions_cache_time = 0
        self._sections_cache = None
        self._sections_cache_time = 0
        self._organizations_cache = None
        
        # Время жизни кэша в секундах (1 час)
        self.cache_ttl = 3600
        
        logger.info(f"API клиент инициализирован с доступом к БД, директория для данных: {os.path.abspath(data_dir)}")
    
    def _is_cache_valid(self, cache_time: float) -> bool:
        """Проверяет, не устарел ли кэш"""
        return (time.time() - cache_time) < self.cache_ttl
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Получает список должностей из БД.
        
        Returns:
            List[Dict[str, Any]]: Список должностей
        """
        logger.info("Получаю должности из БД...")
        positions = await get_positions_from_db()
        logger.info(f"Получено {len(positions)} должностей из БД")
        return positions
    
    async def get_position_by_id(self, position_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает должность по ID.
        
        Args:
            position_id: ID должности
            
        Returns:
            Optional[Dict[str, Any]]: Должность или None, если не найдена
        """
        positions = await self.get_positions()
        for position in positions:
            if position.get('id') == position_id:
                return position
        return None
    
    async def get_divisions(self) -> List[Dict[str, Any]]:
        """
        Получает список отделов из БД.
        
        Returns:
            List[Dict[str, Any]]: Список отделов
        """
        logger.info("Получаю отделы из БД...")
        divisions = await get_divisions_from_db()
        logger.info(f"Получено {len(divisions)} отделов из БД")
        return divisions
    
    async def get_sections(self) -> List[Dict[str, Any]]:
        """
        Получает список секций из БД.
        
        Returns:
            List[Dict[str, Any]]: Список секций
        """
        logger.info("Получаю секции из БД...")
        sections = await get_sections_from_db()
        logger.info(f"Получено {len(sections)} секций из БД")
        return sections
    
    async def get_sections_for_division(self, division_id: int) -> List[Dict[str, Any]]:
        """
        Получает список секций для указанного отдела.
        
        Args:
            division_id: ID отдела
            
        Returns:
            List[Dict[str, Any]]: Список секций, относящихся к отделу
        """
        all_sections = await self.get_sections()
        return [s for s in all_sections if s.get('division_id') == division_id]
    
    async def get_organizations(self) -> List[Dict[str, Any]]:
        """Get all available organizations"""
        if self._organizations_cache is not None:
            return self._organizations_cache

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/organizations", headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._organizations_cache = data
                        return data
                    else:
                        logger.error(f"Неуспешный ответ API при получении организаций: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Ошибка при получении организаций из API: {str(e)}")
            
            # Возвращаем заглушку в случае ошибки
            return [
                {"id": 1, "name": "ОФС-Фотоматрикс", "description": "Основная организация"}
            ]
    
    async def send_employee_data(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send employee data to API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/employees", 
                    json=employee_data,
                    headers=self.headers
                ) as response:
                    if response.status == 200 or response.status == 201:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")
                        return {"error": error_text, "status": response.status}
        except Exception as e:
            logger.error(f"Error sending employee data: {str(e)}")
            return {"error": str(e), "status": 500}
    
    async def validate_token(self, token: str) -> bool:
        """Validate API token"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(f"{self.base_url}/api/validate-token", headers=headers) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return False
    
    async def create_staff(self, staff_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создает сотрудника в основной системе.
        
        Args:
            staff_data: Словарь с данными сотрудника
            
        Returns:
            Dict[str, Any]: Ответ от API
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
                async with session.post(self.staff_endpoint, json=staff_data, headers=headers) as response:
                    if response.status in (200, 201):
                        data = await response.json()
                        logger.info(f"Сотрудник успешно создан в API: {data}")
                        return {"success": True, "data": data}
                    else:
                        error = await response.text()
                        logger.error(f"Ошибка при создании сотрудника: {response.status}, {error}")
                        return {"success": False, "error": error}
        except Exception as e:
            logger.error(f"Исключение при создании сотрудника: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_invitation_code(self, employee_id: int) -> str:
        """Generate invitation code for employee"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/employees/{employee_id}/generate-code", 
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("invitation_code", "")
                    else:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")
                        return ""
        except Exception as e:
            logger.error(f"Error generating invitation code: {str(e)}")
            return ""
    
    async def validate_invitation_code(self, code: str, telegram_id: int) -> Dict[str, Any]:
        """
        Проверяет код приглашения в API.
        
        Args:
            code: Код приглашения для проверки
            telegram_id: Telegram ID пользователя
            
        Returns:
            Dict[str, Any]: Словарь с результатом проверки
        """
        try:
            endpoint = f"{self.base_url}/invitations/validate"
            payload = {
                "code": code,
                "telegram_id": telegram_id
            }
            
            async with aiohttp.ClientSession() as session:
                headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
                async with session.post(endpoint, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Код приглашения успешно проверен: {data}")
                        return {"success": True, "data": data}
                    else:
                        error = await response.text()
                        logger.error(f"Ошибка при проверке кода: {response.status}, {error}")
                        return {"success": False, "error": error}
        except Exception as e:
            error_msg = f"Исключение при проверке кода: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    async def update_data(self) -> bool:
        """
        Обновляет кеш данных из БД.
        
        Returns:
            bool: True, если данные обновлены успешно
        """
        logger.info("Обновляю кеш данных из БД...")
        return await sync_all_data()

    def clear_cache(self) -> None:
        """
        Очищает кеш данных.
        """
        logger.info("Очищаю кеш данных...")
        clear_cache()

    # Методы для обратной совместимости с JSON файлами
    async def _save_to_json(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """
        Сохраняет данные в JSON файл для обратной совместимости.
        
        Args:
            data: Данные для сохранения
            file_path: Путь к файлу
        """
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            logger.info(f"Данные сохранены в файл: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в файл {file_path}: {e}")

    async def export_data_to_json(self) -> None:
        """
        Экспортирует все данные в JSON файлы для обратной совместимости.
        """
        divisions = await self.get_divisions()
        sections = await self.get_sections()
        positions = await self.get_positions()
        
        await self._save_to_json(divisions, self.divisions_file)
        await self._save_to_json(sections, self.sections_file)
        await self._save_to_json(positions, self.positions_file)
        
        logger.info("Все данные экспортированы в JSON файлы")

# Создаем глобальный экземпляр API клиента
api_client = ApiClient() 