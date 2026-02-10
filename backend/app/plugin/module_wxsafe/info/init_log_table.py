import asyncio
from sqlalchemy import text
from app.core.database import async_engine

async def init_log_table():
    sql = """
    CREATE TABLE IF NOT EXISTS wxsafe.wxsafe_fz_log (
        id BIGSERIAL PRIMARY KEY,
        clue_number VARCHAR(100) NOT NULL,
        operator_id VARCHAR(50),
        operator_name VARCHAR(100),
        action_type VARCHAR(20) DEFAULT 'UPDATE',
        change_diff JSONB,
        created_time TIMESTAMP DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS idx_wxsafe_log_clue_number ON wxsafe.wxsafe_fz_log(clue_number);
    """
    async with async_engine.begin() as conn:
        await conn.execute(text(sql))
        print("✅ wxsafe_fz_log table created.")

if __name__ == "__main__":
    import sys
    import os
    # 添加项目根目录到 sys.path，以便能导入 app 模块
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))
    
    asyncio.run(init_log_table())
