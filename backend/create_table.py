from app.db.base import engine
from app.models.staff_organization import StaffOrganization
import asyncio

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(StaffOrganization.__table__.create, checkfirst=True)
        print('Таблица staff_organization создана!')

if __name__ == "__main__":
    asyncio.run(create_table()) 