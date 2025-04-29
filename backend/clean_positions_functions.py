import asyncio
from sqlalchemy import text
from app.db.session import async_session

async def clean_tables():
    """Очищает таблицы, связанные с должностями и функциями"""
    
    print("Начинаю очистку...")
    
    async with async_session() as session:
        # Отключаем внешние ключи для удаления без проблем
        await session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
        
        # Используем DELETE CASCADE из SQL напрямую
        
        # 1. Удаляем связи staff_position 
        await session.execute(text("DELETE FROM staff_position"))
        print("✅ Удалены связи staff_position")
        
        # 2. Удаляем функциональные назначения
        await session.execute(text("DELETE FROM functional_assignment"))
        print("✅ Удалены функциональные назначения")
        
        # 3. Удаляем функциональные отношения
        await session.execute(text("DELETE FROM functional_relation"))
        print("✅ Удалены функциональные отношения")
        
        # 4. Удаляем должности
        await session.execute(text("DELETE FROM position"))
        print("✅ Удалены должности")
        
        # 5. Удаляем функции
        await session.execute(text("DELETE FROM function"))
        print("✅ Удалены функции")
        
        # Фиксируем изменения
        await session.commit()
        print("✅ Изменения сохранены")
        
        # Восстанавливаем проверку внешних ключей
        await session.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
        
    print("🎉 Очистка завершена!")

if __name__ == "__main__":
    asyncio.run(clean_tables()) 