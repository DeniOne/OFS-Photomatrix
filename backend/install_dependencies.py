import subprocess
import sys
import os

def install_dependencies():
    """Устанавливает необходимые зависимости для работы с Excel"""
    
    print("Установка зависимостей для импорта данных из Excel...")
    
    # Определяем, активировано ли виртуальное окружение
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("⚠️ ВНИМАНИЕ: Вы не в виртуальном окружении Python!")
        print("Рекомендуется использовать виртуальное окружение для установки зависимостей.")
        proceed = input("Продолжить установку глобально? (y/n): ")
        if proceed.lower() != 'y':
            print("Установка отменена.")
            sys.exit(0)
    
    # Список пакетов для установки
    packages = [
        "pandas",
        "openpyxl",  # Для работы с Excel файлами
        "xlrd"       # Для старых форматов Excel (.xls)
    ]
    
    try:
        # Устанавливаем каждый пакет
        for package in packages:
            print(f"Установка {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {package} успешно установлен")
            else:
                print(f"❌ Ошибка при установке {package}:")
                print(result.stderr)
        
        print("\n🎉 Установка зависимостей завершена!")
        print("Теперь вы можете запустить скрипт импорта: python import_functions_from_excel.py")
        
    except Exception as e:
        print(f"❌ Произошла ошибка при установке зависимостей: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies() 