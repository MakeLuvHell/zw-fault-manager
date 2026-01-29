import asyncio
from sqlalchemy import select, update
from app.core.database import async_db_session
from app.plugin.module_application.job.model import JobModel

async def fix_job_cron():
    print("正在连接数据库...")
    async with async_db_session() as db:
        # 查询任务
        result = await db.execute(select(JobModel).where(JobModel.name == "自动外呼任务"))
        job = result.scalars().first()
        
        if job:
            print(f"找到任务: {job.name}, 当前参数: {job.trigger_args}")
            # 强制更新为合法的 Cron 表达式
            new_cron = "0 0,15,30,45 15-17 * * 1-5"
            job.trigger = "cron"
            job.trigger_args = new_cron
            job.week = "1-5" # 即使模型没这个字段，只要 trigger_args 对了就行
            
            await db.commit()
            print(f"✅ 任务参数已修复为: {new_cron}")
        else:
            print("❌ 未找到任务 '自动外呼任务'")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fix_job_cron())
