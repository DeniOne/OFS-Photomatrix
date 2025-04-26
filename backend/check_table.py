import asyncio
from app.db.base import engine

async def check_table():
    async with engine.connect() as conn:
        result = await conn.execute('SELECT * FROM staff_organization')
        rows = result.fetchall()
        print(f'Found {len(rows)} rows in staff_organization:')
        for row in rows:
            print(row)

if __name__ == "__main__":
    asyncio.run(check_table()) 