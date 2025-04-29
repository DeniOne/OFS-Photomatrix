import os
import json
import logging
import sqlite3
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import random
import string
import time

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

class BotDatabase:
    """Класс для работы с базой данных бота"""
    
    def __init__(self, db_path: str = "bot_data.db", storage_path: str = "./data"):
        """Инициализация базы данных"""
        self.storage_path = storage_path
        self.db_path = os.path.join(storage_path, db_path)
        self.staff_file = os.path.join(storage_path, "staff.json")
        self.conn = None
        self.cursor = None
        self.ensure_storage_exists()
        self._create_tables()
    
    def ensure_storage_exists(self):
        """Проверяет и создает директорию для хранения данных если она не существует"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            logger.info(f"Создана директория хранилища: {self.storage_path}")
        
        # Создаем файл с сотрудниками, если он не существует
        if not os.path.exists(self.staff_file):
            with open(self.staff_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            logger.info(f"Создан файл для хранения сотрудников: {self.staff_file}")
    
    def _connect(self):
        """Устанавливает соединение с БД"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def _disconnect(self):
        """Закрывает соединение с БД"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def _create_tables(self):
        """Создает необходимые таблицы в БД"""
        self._connect()
        
        # Таблица для хранения сотрудников
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT NOT NULL UNIQUE,
            telegram_username TEXT,
            full_name TEXT NOT NULL,
            position_id INTEGER NOT NULL,
            position_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
        ''')
        
        # Таблица для хранения админов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT NOT NULL UNIQUE,
            username TEXT,
            full_name TEXT NOT NULL,
            permission_level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            is_active INTEGER DEFAULT 1
        )
        ''')
        
        # Таблица для хранения заявок на регистрацию
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS registration_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT NOT NULL,
            telegram_username TEXT,
            user_full_name TEXT NOT NULL,
            approximate_position TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            processed_at TIMESTAMP,
            processed_by TEXT
        )
        ''')
        
        # Таблица для хранения кодов приглашений
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitation_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            telegram_id TEXT NOT NULL,
            position_id INTEGER NOT NULL,
            position_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            created_by TEXT,
            is_used INTEGER DEFAULT 0,
            used_at TIMESTAMP
        )
        ''')
        
        # Создаем индексы для ускорения поиска
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_staff_telegram_id ON staff(telegram_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_admins_telegram_id ON admins(telegram_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_registration_requests_telegram_id ON registration_requests(telegram_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_invitation_codes_telegram_id ON invitation_codes(telegram_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_invitation_codes_code ON invitation_codes(code)')
        
        # Проверяем, есть ли суперадмин в системе
        self.cursor.execute('SELECT COUNT(*) as count FROM admins WHERE permission_level = 2')
        if self.cursor.fetchone()['count'] == 0:
            # Добавляем суперадмина по умолчанию
            from config import Config
            config = Config()
            if config.ADMIN_IDS:
                admin_id = config.ADMIN_IDS[0]
                self.cursor.execute('''
                INSERT INTO admins (telegram_id, full_name, permission_level)
                VALUES (?, ?, 2)
                ''', (admin_id, "Суперадмин"))
                logger.info(f"Создан суперадмин с ID: {admin_id}")
        
        self.conn.commit()
        self._disconnect()
    
    def init_db(self):
        """Инициализирует базу данных и создает необходимые таблицы"""
        logger.info("Инициализация базы данных")
        self.ensure_storage_exists()
        self._create_tables()
        logger.info("База данных инициализирована")
        return True
    
    def create_employee(self, employee_data: Dict[str, Any]) -> int:
        """Создает нового сотрудника в БД"""
        try:
            self._connect()
            self.cursor.execute('''
            INSERT INTO staff (
                telegram_id,
                telegram_username,
                full_name,
                position_id,
                position_name
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                employee_data['telegram_id'],
                employee_data.get('telegram_username', ''),
                employee_data['full_name'],
                employee_data['position_id'],
                employee_data['position_name']
            ))
            self.conn.commit()
            new_id = self.cursor.lastrowid
            logger.info(f"Создан новый сотрудник: {employee_data['full_name']} (ID: {new_id})")
            return new_id
        except Exception as e:
            logger.error(f"Ошибка при создании сотрудника: {e}")
            return 0
        finally:
            self._disconnect()
    
    def get_employee_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Получает данные сотрудника по его Telegram ID"""
        try:
            self._connect()
            self.cursor.execute('''
            SELECT * FROM staff WHERE telegram_id = ? AND is_active = 1
            ''', (telegram_id,))
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Ошибка при получении данных сотрудника: {e}")
            return None
        finally:
            self._disconnect()
    
    def get_all_staff(self) -> List[Dict[str, Any]]:
        """Получает список всех сотрудников"""
        try:
            self._connect()
            self.cursor.execute('SELECT * FROM staff WHERE is_active = 1 ORDER BY created_at DESC')
            staff = [dict(row) for row in self.cursor.fetchall()]
            return staff
        except Exception as e:
            logger.error(f"Ошибка при получении списка сотрудников: {e}")
            return []
        finally:
            self._disconnect()
    
    def update_employee(self, employee_id: int, data: Dict[str, Any]) -> bool:
        """Обновляет данные сотрудника"""
        try:
            self._connect()
            
            # Формируем запрос динамически на основе переданных данных
            fields = []
            values = []
            
            for key, value in data.items():
                fields.append(f"{key} = ?")
                values.append(value)
            
            query = f"UPDATE staff SET {', '.join(fields)} WHERE id = ?"
            values.append(employee_id)
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных сотрудника: {e}")
            return False
        finally:
            self._disconnect()
    
    def delete_employee(self, telegram_id: str) -> bool:
        """Удаляет сотрудника (отмечает как неактивного)"""
        try:
            self._connect()
            self.cursor.execute('''
            UPDATE staff SET is_active = 0 WHERE telegram_id = ?
            ''', (telegram_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении сотрудника: {e}")
            return False
        finally:
            self._disconnect()
    
    def add_admin(self, telegram_id: str, full_name: str, created_by: str = None) -> bool:
        """Добавляет нового администратора"""
        try:
            self._connect()
            
            # Проверяем, существует ли уже этот админ
            self.cursor.execute('SELECT * FROM admins WHERE telegram_id = ?', (telegram_id,))
            existing_admin = self.cursor.fetchone()
            
            if existing_admin:
                # Если админ уже существует, но деактивирован, активируем его
                if not existing_admin['is_active']:
                    self.cursor.execute('''
                    UPDATE admins SET 
                        is_active = 1,
                        full_name = ?,
                        created_by = ?
                    WHERE telegram_id = ?
                    ''', (full_name, created_by, telegram_id))
                    self.conn.commit()
                    logger.info(f"Администратор с ID {telegram_id} активирован")
                    return True
                else:
                    # Админ уже существует и активен
                    logger.warning(f"Администратор с ID {telegram_id} уже существует")
                    return False
            
            # Добавляем нового админа
            self.cursor.execute('''
            INSERT INTO admins (
                telegram_id,
                full_name,
                permission_level,
                created_by
            ) VALUES (?, ?, 1, ?)
            ''', (telegram_id, full_name, created_by))
            
            self.conn.commit()
            logger.info(f"Добавлен новый администратор: {full_name} (ID: {telegram_id})")
            return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении администратора: {e}")
            return False
        finally:
            self._disconnect()
    
    def remove_admin(self, telegram_id: str) -> bool:
        """Удаляет администратора (отмечает как неактивного)"""
        try:
            self._connect()
            self.cursor.execute('''
            UPDATE admins SET is_active = 0 WHERE telegram_id = ?
            ''', (telegram_id,))
            self.conn.commit()
            logger.info(f"Администратор с ID {telegram_id} деактивирован")
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении администратора: {e}")
            return False
        finally:
            self._disconnect()
    
    def is_admin(self, telegram_id: str) -> bool:
        """Проверяет, является ли пользователь администратором"""
        try:
            self._connect()
            
            # Конвертируем telegram_id в строку для сравнения
            telegram_id_str = str(telegram_id)
            logger.info(f"👤 Проверка прав администратора для ID: {telegram_id_str}")
            
            # Проверяем сначала по telegram_id
            logger.info(f"🔍 Выполняем SQL-запрос по telegram_id: {telegram_id_str}")
            self.cursor.execute('''
            SELECT COUNT(*) as count FROM admins 
            WHERE telegram_id = ? AND is_active = 1
            ''', (telegram_id_str,))
            
            result = self.cursor.fetchone()
            count_by_id = result['count'] if result else 0
            logger.info(f"📊 Результат SQL-запроса по ID: найдено {count_by_id} записей")
            
            # Проверяем, найден ли админ по ID
            if count_by_id > 0:
                logger.info(f"✅ Пользователь {telegram_id_str} найден в таблице admins по ID и является активным админом")
                return True
            
            logger.info(f"⚠️ Пользователь {telegram_id_str} не найден в таблице admins по ID")
                
            # Если по ID не найден, и ID начинается с @, проверяем также по username
            if telegram_id_str.startswith('@'):
                username = telegram_id_str.lstrip('@')
                logger.info(f"🔍 ID начинается с @, проверяем по username: {username}")
                
                self.cursor.execute('''
                SELECT COUNT(*) as count FROM admins 
                WHERE username = ? AND is_active = 1
                ''', (username,))
                
                result = self.cursor.fetchone()
                count_by_username = result['count'] if result else 0
                
                logger.info(f"📊 Результат SQL-запроса по username: найдено {count_by_username} записей")
                
                if count_by_username > 0:
                    logger.info(f"✅ Пользователь {telegram_id_str} найден в таблице admins по username и является активным админом")
                    return True
                
                logger.info(f"⚠️ Пользователь {telegram_id_str} не найден в таблице admins по username")
            
            logger.info(f"❌ Пользователь {telegram_id_str} не является администратором")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке прав администратора: {e}")
            return False
        finally:
            self._disconnect()
    
    def is_superadmin(self, telegram_id: str) -> bool:
        """Проверяет, является ли пользователь супер-администратором"""
        try:
            self._connect()
            
            # Конвертируем telegram_id в строку для сравнения
            telegram_id_str = str(telegram_id)
            logger.info(f"👑 Проверка прав суперадмина для ID: {telegram_id_str}")
            
            # Проверяем наличие суперадмина в БД
            logger.info(f"🔍 Выполняем SQL-запрос на наличие суперадмина: {telegram_id_str}")
            self.cursor.execute('''
            SELECT COUNT(*) as count FROM admins 
            WHERE telegram_id = ? AND permission_level = 2 AND is_active = 1
            ''', (telegram_id_str,))
            
            result = self.cursor.fetchone()
            count = result['count'] if result else 0
            
            logger.info(f"📊 Результат SQL-запроса суперадмина: найдено {count} записей")
            
            if count > 0:
                logger.info(f"✅ Пользователь {telegram_id_str} найден в таблице admins как суперадмин (permission_level=2)")
                return True
            
            logger.info(f"❌ Пользователь {telegram_id_str} не является суперадмином")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке прав суперадмина: {e}")
            return False
        finally:
            self._disconnect()
    
    def get_all_admins(self) -> List[Dict[str, Any]]:
        """Получает список всех администраторов"""
        try:
            self._connect()
            self.cursor.execute('SELECT * FROM admins ORDER BY permission_level DESC, created_at DESC')
            admins = [dict(row) for row in self.cursor.fetchall()]
            return admins
        except Exception as e:
            logger.error(f"Ошибка при получении списка администраторов: {e}")
            return []
        finally:
            self._disconnect()
    
    def get_admin_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Получает данные администратора по его Telegram ID"""
        try:
            self._connect()
            self.cursor.execute('SELECT * FROM admins WHERE telegram_id = ?', (telegram_id,))
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Ошибка при получении данных администратора: {e}")
            return None
        finally:
            self._disconnect()
    
    def get_admin_stats(self, admin_id: str) -> Dict[str, int]:
        """Получает статистику по действиям администратора"""
        try:
            self._connect()
            
            # Статистика по обработанным заявкам
            self.cursor.execute('''
            SELECT 
                COUNT(*) as processed_requests,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_requests,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_requests
            FROM registration_requests 
            WHERE processed_by = ? AND status != 'pending'
            ''', (admin_id,))
            
            requests_stats = dict(self.cursor.fetchone())
            
            # Статистика по сгенерированным кодам
            self.cursor.execute('''
            SELECT 
                COUNT(*) as generated_codes,
                SUM(CASE WHEN is_used = 1 THEN 1 ELSE 0 END) as used_codes
            FROM invitation_codes 
            WHERE created_by = ?
            ''', (admin_id,))
            
            codes_stats = dict(self.cursor.fetchone())
            
            return {
                'processed_requests': requests_stats['processed_requests'] or 0,
                'approved_requests': requests_stats['approved_requests'] or 0,
                'rejected_requests': requests_stats['rejected_requests'] or 0,
                'generated_codes': codes_stats['generated_codes'] or 0,
                'used_codes': codes_stats['used_codes'] or 0
            }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики администратора: {e}")
            return {
                'processed_requests': 0,
                'approved_requests': 0,
                'rejected_requests': 0,
                'generated_codes': 0,
                'used_codes': 0
            }
        finally:
            self._disconnect()
    
    def create_registration_request(self, telegram_id: str = None, user_full_name: str = None,
                                   telegram_username: str = '', approximate_position: str = '',
                                   request_data: Dict[str, Any] = None) -> int:
        """
        Создает новую заявку на регистрацию
        
        Args:
            telegram_id: ID пользователя в Telegram
            user_full_name: Имя пользователя
            telegram_username: Имя пользователя в Telegram (опционально)
            approximate_position: Примерная должность (опционально)
            request_data: Словарь с данными запроса (альтернативный вариант передачи данных)
            
        Returns:
            int: ID созданной заявки или 0 в случае ошибки
        """
        try:
            self._connect()
            
            # Если передан словарь с данными, используем его
            if request_data:
                telegram_id = request_data.get('telegram_id', telegram_id)
                user_full_name = request_data.get('user_full_name', user_full_name)
                telegram_username = request_data.get('telegram_username', telegram_username)
                approximate_position = request_data.get('approximate_position', approximate_position)
            
            # Проверяем обязательные поля
            if not telegram_id or not user_full_name:
                logger.error(f"Не заполнены обязательные поля для создания заявки: telegram_id={telegram_id}, user_full_name={user_full_name}")
                return 0
            
            # Проверяем, есть ли уже активная заявка от этого пользователя
            self.cursor.execute('''
            SELECT COUNT(*) as count FROM registration_requests 
            WHERE telegram_id = ? AND status = 'pending'
            ''', (telegram_id,))
            
            if self.cursor.fetchone()['count'] > 0:
                logger.warning(f"У пользователя {telegram_id} уже есть активная заявка")
                return 0
            
            # Создаем новую заявку
            self.cursor.execute('''
            INSERT INTO registration_requests (
                telegram_id,
                telegram_username,
                user_full_name,
                approximate_position
            ) VALUES (?, ?, ?, ?)
            ''', (telegram_id, telegram_username, user_full_name, approximate_position))
            
            self.conn.commit()
            new_id = self.cursor.lastrowid
            logger.info(f"Создана новая заявка на регистрацию от пользователя {user_full_name} (ID: {new_id})")
            return new_id
        except Exception as e:
            logger.error(f"Ошибка при создании заявки на регистрацию: {e}")
            return 0
        finally:
            self._disconnect()
    
    def get_registration_request(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Получает данные заявки по её ID"""
        try:
            self._connect()
            self.cursor.execute('SELECT * FROM registration_requests WHERE id = ?', (request_id,))
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Ошибка при получении данных заявки: {e}")
            return None
        finally:
            self._disconnect()
    
    def get_pending_registration_requests(self) -> List[Dict[str, Any]]:
        """Получает список всех ожидающих заявок на регистрацию"""
        try:
            self._connect()
            self.cursor.execute('''
            SELECT * FROM registration_requests 
            WHERE status = 'pending' 
            ORDER BY created_at ASC
            ''')
            requests = [dict(row) for row in self.cursor.fetchall()]
            return requests
        except Exception as e:
            logger.error(f"Ошибка при получении списка заявок: {e}")
            return []
        finally:
            self._disconnect()
    
    def get_pending_request_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Получает активную заявку пользователя по его Telegram ID"""
        try:
            self._connect()
            self.cursor.execute('''
            SELECT * FROM registration_requests 
            WHERE telegram_id = ? AND status IN ('pending', 'approved')
            ORDER BY created_at DESC LIMIT 1
            ''', (telegram_id,))
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Ошибка при получении заявки по Telegram ID: {e}")
            return None
        finally:
            self._disconnect()
    
    def process_registration_request(self, request_id: int, status: str, admin_id: str, position_id: int = None, position_name: str = None, invitation_code: str = None) -> bool:
        """Обновляет статус заявки на регистрацию"""
        try:
            self._connect()
            self.cursor.execute('''
            UPDATE registration_requests 
            SET status = ?, processed_at = CURRENT_TIMESTAMP, processed_by = ?
            WHERE id = ?
            ''', (status, admin_id, request_id))
            self.conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса заявки: {e}")
            return False
        finally:
            self._disconnect()
    
    def update_registration_request(self, request_id: int, **kwargs) -> bool:
        """Обновляет данные заявки на регистрацию"""
        try:
            self._connect()
            
            # Формируем запрос динамически на основе переданных данных
            fields = []
            values = []
            
            for key, value in kwargs.items():
                fields.append(f"{key} = ?")
                values.append(value)
            
            query = f"UPDATE registration_requests SET {', '.join(fields)} WHERE id = ?"
            values.append(request_id)
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных заявки: {e}")
            return False
        finally:
            self._disconnect()
    
    def save_invitation_code(self, request_id: int, code: str, position_id: int, position_name: str, 
                             division_id: int = None, division_name: str = None, expires_at: str = None) -> bool:
        """
        Сохраняет код приглашения, полученный от API
        
        Args:
            request_id: ID заявки
            code: Код приглашения
            position_id: ID должности
            position_name: Название должности
            division_id: ID отдела (опционально)
            division_name: Название отдела (опционально)
            expires_at: Дата и время истечения срока действия кода (опционально)
            
        Returns:
            bool: True если код успешно сохранен, False в противном случае
        """
        try:
            self._connect()
            
            # Получаем данные заявки
            request = self.get_registration_request(request_id)
            if not request:
                logger.error(f"Не удалось найти заявку с ID {request_id}")
                return False
            
            # Добавляем запись о коде приглашения
            self.cursor.execute('''
            INSERT INTO invitation_codes (
                code, 
                telegram_id, 
                position_id, 
                position_name, 
                expires_at,
                created_by
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                code,
                request.get('telegram_id'),
                position_id,
                position_name,
                expires_at,
                request.get('processed_by')
            ))
            
            # Обновляем запись о заявке - добавляем отдел если есть
            if division_id and division_name:
                self.cursor.execute('''
                UPDATE registration_requests 
                SET division_id = ?, division_name = ? 
                WHERE id = ?
                ''', (division_id, division_name, request_id))
            
            self.conn.commit()
            logger.info(f"Сохранен код приглашения {code} для пользователя {request.get('telegram_id')}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении кода приглашения: {e}")
            return False
        finally:
            self._disconnect()
    
    def generate_position_code(self, telegram_id: str, position_id: int, position_name: str, admin_id: str) -> str:
        """Генерирует уникальный код для должности"""
        try:
            # Генерируем случайный код из 6 символов
            code_length = 6
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length))
            
            # Добавляем таймстамп для уникальности
            timestamp = int(time.time()) % 10000
            code = f"{code}{timestamp:04d}"
            
            # Устанавливаем срок действия кода (24 часа)
            expires_at = datetime.now() + timedelta(hours=24)
            
            self._connect()
            self.cursor.execute('''
            INSERT INTO invitation_codes (
                code,
                telegram_id,
                position_id,
                position_name,
                created_by,
                expires_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (code, telegram_id, position_id, position_name, admin_id, expires_at))
            
            self.conn.commit()
            logger.info(f"Сгенерирован код {code} для пользователя {telegram_id} (должность: {position_name})")
            return code
        except Exception as e:
            logger.error(f"Ошибка при генерации кода: {e}")
            return ""
        finally:
            self._disconnect()
    
    def validate_invitation_code(self, telegram_id: str, code: str) -> Optional[Dict[str, Any]]:
        """Проверяет валидность кода приглашения"""
        try:
            self._connect()
            
            # Проверяем код на существование, срок действия и принадлежность пользователю
            self.cursor.execute('''
            SELECT * FROM invitation_codes 
            WHERE code = ? AND telegram_id = ? AND is_used = 0 AND expires_at > CURRENT_TIMESTAMP
            ''', (code, telegram_id))
            
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Ошибка при проверке кода приглашения: {e}")
            return None
        finally:
            self._disconnect()
    
    def mark_invitation_code_used(self, code: str) -> bool:
        """Отмечает код приглашения как использованный"""
        try:
            self._connect()
            self.cursor.execute('''
            UPDATE invitation_codes 
            SET is_used = 1, used_at = CURRENT_TIMESTAMP
            WHERE code = ?
            ''', (code,))
            
            self.conn.commit()
            logger.info(f"Код {code} отмечен как использованный")
            return True
        except Exception as e:
            logger.error(f"Ошибка при отметке кода как использованного: {e}")
            return False
        finally:
            self._disconnect()
    
    def get_active_invitation_code(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Получает активный код приглашения для пользователя"""
        try:
            self._connect()
            self.cursor.execute('''
            SELECT * FROM invitation_codes 
            WHERE telegram_id = ? AND is_used = 0 AND expires_at > CURRENT_TIMESTAMP
            ORDER BY created_at DESC LIMIT 1
            ''', (telegram_id,))
            
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Ошибка при получении активного кода приглашения: {e}")
            return None
        finally:
            self._disconnect() 