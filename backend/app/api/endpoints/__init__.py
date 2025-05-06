# Инициализация пакета endpoints
"""
Этот файл экспортирует модули роутеров для доступа по имени
"""

try:
    # Импортируем модули вручную
    from app.api.endpoints.auth import router as login
    from app.api.endpoints.users import router as users
    from app.api.endpoints.organizations import router as organizations
    from app.api.endpoints.divisions import router as divisions
    from app.api.endpoints.positions import router as positions
    from app.api.endpoints.staff import router as staff
    from app.api.endpoints.value_products import router as value_products
    from app.api.endpoints.functions import router as functions
    from app.api.endpoints.sections import router as sections
    from app.api.endpoints.orgchart import router as orgchart

    # Экспортируем имена
    __all__ = [
        "login", "users", "organizations", "divisions", 
        "positions", "staff", "value_products", "functions",
        "sections", "orgchart"
    ]

    print("Успешно импортированы роутеры в endpoints/__init__.py:", __all__)

except ImportError as e:
    import sys
    print(f"! Ошибка импорта в endpoints/__init__.py: {e}", file=sys.stderr)
    print(f"Проверьте наличие всех файлов роутеров: {__all__ if '__all__' in locals() else 'список не определен'}", file=sys.stderr)
    raise
