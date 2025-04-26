from app.db.base import engine
from app.models.staff_organization import StaffOrganization
import asyncio

async def drop_table():
    async with engine.begin() as conn:
        await conn.run_sync(StaffOrganization.__table__.drop, checkfirst=True)
        print('Таблица staff_organization удалена!')

if __name__ == "__main__":
    asyncio.run(drop_table()) 