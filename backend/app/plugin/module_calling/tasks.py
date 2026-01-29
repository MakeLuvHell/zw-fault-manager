from app.plugin.module_application.job.tools.ap_scheduler import SchedulerUtil
from app.plugin.module_calling.service import CallingService
from app.core.logger import log


async def execute_calling_job(*args, **kwargs):
    """
    自动外呼定时任务入口
    """
    log.info(">>>>>> [Debug] 进入 execute_calling_job <<<<<<")
    
    # 从 SchedulerUtil 获取 Redis 实例
    redis = SchedulerUtil.redis_instance
    if not redis:
        log.error("Redis 实例未初始化，无法执行外呼任务")
        return

    log.info(f">>>>>> [Debug] Redis 实例获取成功: {redis}")
    await CallingService.execute_task(redis)
