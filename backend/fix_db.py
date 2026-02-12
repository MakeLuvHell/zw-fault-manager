import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config.setting import settings

async def fix_database():
    print(f"Connecting to database: {settings.DATABASE_HOST}")
    engine = create_async_engine(settings.ASYNC_DB_URI)
    
    async with engine.begin() as conn:
        # 1. 确保 schema 存在
        print("Ensuring schema 'brief' exists...")
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS brief"))
        
        # 2. 检查并创建表/添加列
        print("Checking table 'brief.wx_brief_report'...")
        # 尝试创建表
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS brief.wx_brief_report (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                focus VARCHAR(500),
                summary_data JSON,
                report_content TEXT,
                report_date TIMESTAMP,
                creator_id INTEGER,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """))
        
        # 3. 针对可能已存在但缺少列的情况，尝试添加列 (PostgreSQL ALTER TABLE IF NOT EXISTS 类似实现)
        columns_to_add = [
            ("summary_data", "JSON"),
            ("report_content", "TEXT"),
            ("report_date", "TIMESTAMP"),
            ("focus", "VARCHAR(500)")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                print(f"Attempting to add column {col_name} to brief.wx_brief_report...")
                await conn.execute(text(f"ALTER TABLE brief.wx_brief_report ADD COLUMN {col_name} {col_type}"))
                print(f"Column {col_name} added.")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"Column {col_name} already exists, skipping.")
                else:
                    print(f"Error adding {col_name}: {e}")

    await engine.dispose()
    print("Database fix completed.")

if __name__ == "__main__":
    # 设置环境变量以加载正确的配置
    os.environ["ENVIRONMENT"] = "dev"
    asyncio.run(fix_database())
