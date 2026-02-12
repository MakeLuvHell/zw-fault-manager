import asyncio
import os
from sqlalchemy import text
from app.core.database import async_engine

async def drop_table():
    print("Dropping table brief.wx_brief_report if exists...")
    async with async_engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS brief.wx_brief_report"))
    print("Done.")

if __name__ == "__main__":
    os.environ["ENVIRONMENT"] = "dev"
    asyncio.run(drop_table())
