import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Set, Any

import httpx
from apscheduler.triggers.cron import CronTrigger
from redis.asyncio import Redis
from sqlalchemy import select, delete, text

from app.config.setting import settings
from app.core.database import async_db_session
from app.core.logger import log
from app.plugin.module_calling.model import CallTask, CallHistory, CallLog, CallingTaskConfig


class DistinctIdGenerator:
    """
    分布式流水号生成器 (基于 Redis)
    格式: YYYYMMDDHHmmss + 3位序列号 (共17位)
    """

    def __init__(self, redis: Redis):
        self.redis = redis

    async def generate(self) -> str:
        """生成唯一的17位流水号"""
        now = datetime.now()
        time_str = now.strftime("%Y%m%d%H%M%S")
        
        # 使用 Redis INCR 命令实现原子递增
        # Key 格式: calling:seq:{time_str}
        key = f"calling:seq:{time_str}"
        
        # 自增并设置过期时间（5秒后过期即可，因为只在当前秒内有效）
        seq = await self.redis.incr(key)
        if seq == 1:
            await self.redis.expire(key, 5)
            
        # 如果序列号超过 999 (同一秒超过 1000 请求)，则等待下一秒
        # 这种情况在高并发下极少发生，但在极端情况下需要保护
        if seq > 999:
            await asyncio.sleep(0.01)
            return await self.generate()
            
        return f"{time_str}{seq:03d}"


class CallingService:
    """自动外呼核心服务"""

    # 固定参数
    TARGET_OBJ_ID = "664144275936"
    TARGET_OBJ_TYPE = "1000"
    LAN_ID = "1600"
    EVENT_CODE = "EcmhZR1226"
    SVC_CODE = "6010020001"
    API_CODE = "601002000100001"
    VERSION = "1.0"
    SIGN = "主动服务触发渠道系统发送事件信息"

    @classmethod
    def get_current_time_formatted(cls):
        """获取 req_time 和 oper_time"""
        now = datetime.now()
        req_time = now.strftime("%Y%m%d%H%M%S") + "000"
        oper_time = now.strftime("%Y-%m-%d %H:%M:%S")
        return req_time, oper_time

    @classmethod
    async def build_request_body(cls, record: CallTask, redis: Redis) -> Dict:
        """构建请求体"""
        req_time, oper_time = cls.get_current_time_formatted()
        generator = DistinctIdGenerator(redis)
        distinct_id = await generator.generate()

        return {
            "contract_root": {
                "tcp_cont": {
                    "req_time": req_time,
                    "svc_code": cls.SVC_CODE,
                    "api_code": cls.API_CODE,
                    "transaction_id": "",
                    "sign": cls.SIGN,
                    "version": cls.VERSION
                },
                "svc_cont": {
                    "distinct_id": distinct_id,
                    "properties": {
                        "event_code": cls.EVENT_CODE,
                        "oper_time": oper_time,
                        "target_obj_type": cls.TARGET_OBJ_TYPE,
                        "target_obj_id": cls.TARGET_OBJ_ID,
                        "accs_nbr": record.mobile_phone,
                        "contact_nbr": record.mobile_phone,
                        "lan_id": cls.LAN_ID,
                        "cust_name": record.staff_name,
                        "busi_params": {
                            "staff_name": record.staff_name,
                            "sys_name": record.sys_name,
                            "order_type": record.order_type,
                            "order_nums": record.order_nums
                        }
                    }
                }
            }
        }

    @classmethod
    async def push_to_api(cls, client: httpx.AsyncClient, body: Dict, mobile: str) -> tuple[bool, str]:
        """调用 API 推送"""
        if not settings.CALLING_API_URL:
            log.warning("未配置 CALLING_API_URL，跳过推送")
            return False, "未配置 API URL"

        headers = {
            "Content-Type": "application/json",
            "X-APP-ID": settings.CALLING_APP_ID,
            "X-APP-KEY": settings.CALLING_APP_KEY
        }
        
        last_error = ""

        for attempt in range(settings.CALLING_RETRY_COUNT):
            try:
                # 首次尝试时记录请求体
                if attempt == 0:
                    log.info(f"推送请求体 ({mobile}): {json.dumps(body, ensure_ascii=False, indent=2)}")
                
                response = await client.post(
                    settings.CALLING_API_URL,
                    json=body,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    try:
                        resp_json = response.json()
                        resp_code = resp_json.get("contractRoot", {}).get("svcCont", {}).get("result", {}).get("resp_code")
                        result_msg = resp_json.get("contractRoot", {}).get("svcCont", {}).get("result", {}).get("result_msg", "")
                        
                        if resp_code == "0":
                            log.info(f"推送成功: {mobile}")
                            log.info(f"响应体 ({mobile}): {json.dumps(resp_json, ensure_ascii=False, indent=2)}")
                            return True, ""
                        else:
                            last_error = f"业务失败 (code={resp_code}): {result_msg}"
                            log.warning(f"推送业务失败 ({attempt + 1}/{settings.CALLING_RETRY_COUNT}): {last_error}")
                    except Exception as e:
                        last_error = f"解析响应失败: {str(e)}"
                        log.warning(f"响应解析异常 ({attempt + 1}/{settings.CALLING_RETRY_COUNT}): {last_error}")
                else:
                    last_error = f"HTTP {response.status_code} - {response.text[:200]}"
                    log.warning(f"推送失败 ({attempt + 1}/{settings.CALLING_RETRY_COUNT}): {last_error}")
            
            except httpx.RequestError as e:
                last_error = f"网络异常: {str(e)}"
                log.warning(f"网络异常 ({attempt + 1}/{settings.CALLING_RETRY_COUNT}): {last_error}")
            except Exception as e:
                last_error = f"未知异常: {str(e)}"
                log.error(f"未知异常 ({attempt + 1}/{settings.CALLING_RETRY_COUNT}): {last_error}")

            # 重试等待
            if attempt < settings.CALLING_RETRY_COUNT - 1:
                await asyncio.sleep(1)
        
        return False, last_error


    @classmethod
    async def execute_task_with_config(cls, redis: Redis, task_id: int):
        """
        根据任务配置执行外呼任务
        
        从 CallingTaskConfig 读取配置，动态查询源数据表执行外呼
        
        参数:
        - redis: Redis 连接
        - task_id: 任务配置 ID
        """
        start_time = time.time()
        log.info(f"====== 开始执行外呼任务 (配置ID: {task_id}) ======")

        # Step 1: 读取任务配置
        task_config = None
        async with async_db_session() as db:
            result = await db.execute(
                select(CallingTaskConfig).where(CallingTaskConfig.id == task_id)
            )
            task_config = result.scalar_one_or_none()
        
        if not task_config:
            log.error(f"任务配置不存在: {task_id}")
            return
        
        if not task_config.is_enabled:
            log.warning(f"任务已禁用: {task_config.name}")
            return

        # 解析字段映射
        field_mapping = json.loads(task_config.field_mapping) if isinstance(task_config.field_mapping, str) else task_config.field_mapping
        log.info(f"任务配置: {task_config.name}, 源表: {task_config.source_schema}.{task_config.source_table}")
        log.info(f"字段映射: {field_mapping}")

        # Step 2: 从配置的源表读取新增数据 (利用 SQL 过滤)
        tasks = []
        
        async with async_db_session() as db:
            # 动态构建 SQL 查询，直接在数据库层面过滤掉已存在于 call_history 的手机号
            # 使用 NOT EXISTS 子句，相比 LEFT JOIN + IS NULL 性能通常更好且逻辑更清晰
            source_table = f'"{task_config.source_schema}"."{task_config.source_table}"'
            mobile_col = f'"{field_mapping["mobile_phone"]}"'
            
            # 使用配置的 Schema
            history_table = f'"{settings.CALLING_SCHEMA}"."call_history"'
            
            query = text(f"""
                SELECT 
                    {mobile_col} as mobile_phone,
                    "{field_mapping['staff_name']}" as staff_name,
                    "{field_mapping['sys_name']}" as sys_name,
                    "{field_mapping['order_type']}" as order_type,
                    "{field_mapping['order_nums']}" as order_nums
                FROM {source_table} source_t
                WHERE NOT EXISTS (
                    SELECT 1 FROM {history_table} h 
                    WHERE h.mobile_phone = source_t.{mobile_col}::VARCHAR
                )
            """)
            
            try:
                result = await db.execute(query)
                rows = result.fetchall()
                
                # 转换为 CallTask 格式的对象
                for row in rows:
                    task = CallTask(
                        mobile_phone=str(row[0]) if row[0] else "",
                        staff_name=str(row[1]) if row[1] else "",
                        sys_name=str(row[2]) if row[2] else "",
                        order_type=str(row[3]) if row[3] else "",
                        order_nums=int(row[4]) if row[4] else 0
                    )
                    tasks.append(task)
                
                log.info(f"从源表读取到 {len(tasks)} 条新增数据(已过滤历史记录)")
            except Exception as e:
                log.error(f"查询源数据表失败: {e}")
                return

        new_tasks = tasks
        if not new_tasks:
            log.info("没有新增记录需要推送")
            return

        # Step 4: 执行推送
        success_tasks: List[CallTask] = []
        call_logs: List[CallLog] = []
        
        async with httpx.AsyncClient() as client:
            for i, task in enumerate(new_tasks):
                body = await cls.build_request_body(task, redis)
                
                is_success, error_msg = await cls.push_to_api(client, body, task.mobile_phone)
                
                # 记录日志对象
                call_log = CallLog(
                    mobile_phone=task.mobile_phone,
                    staff_name=task.staff_name,
                    sys_name=task.sys_name,
                    order_type=task.order_type,
                    order_nums=task.order_nums,
                    status=1 if is_success else 0,
                    error_msg=error_msg,
                    push_time=datetime.now()
                )
                call_logs.append(call_log)

                if is_success:
                    success_tasks.append(task)
                
                # 间隔
                if settings.CALLING_REQUEST_INTERVAL > 0 and i < len(new_tasks) - 1:
                    await asyncio.sleep(settings.CALLING_REQUEST_INTERVAL)

        # Step 5: 更新历史记录和写入日志
        if success_tasks or call_logs:
            async with async_db_session() as db:
                try:
                    # 写入流水日志
                    if call_logs:
                        db.add_all(call_logs)
                    
                    # 更新历史表 (追加成功的记录，不清空)
                    if success_tasks:
                        history_records = [
                            CallHistory(
                                mobile_phone=t.mobile_phone,
                                staff_name=t.staff_name,
                                sys_name=t.sys_name,
                                order_type=t.order_type,
                                order_nums=t.order_nums
                            ) for t in success_tasks
                        ]
                        db.add_all(history_records)
                    
                    await db.commit()
                    log.info(f"数据已回写: 新增日志 {len(call_logs)} 条, 更新历史 {len(success_tasks)} 条")
                except Exception as e:
                    await db.rollback()
                    log.error(f"回写数据库失败: {e}")
            
        duration = time.time() - start_time
        log.info(f"====== 任务执行完成，耗时 {duration:.2f} 秒 (成功: {len(success_tasks)}/{len(new_tasks)}) ======")


class CallingSchedulerService:
    """
    外呼任务调度服务
    
    负责将 CallingTaskConfig 注册到 APScheduler，
    使任务能够根据配置的 Cron 表达式自动执行
    """
    
    # 任务ID前缀，避免与其他任务冲突
    JOB_PREFIX = "calling_task_"
    
    @classmethod
    def _get_job_id(cls, task_id: int) -> str:
        """生成调度任务ID"""
        return f"{cls.JOB_PREFIX}{task_id}"
    
    @classmethod
    def _parse_cron_expr(cls, cron_expr: str) -> CronTrigger:
        """
        解析 Cron 表达式并返回 CronTrigger
        
        格式: 秒 分 时 日 月 周
        """
        fields = cron_expr.strip().split()
        if len(fields) < 6:
            raise ValueError(f"无效的 Cron 表达式: {cron_expr}")
        
        # 将 ? 替换为 * 以兼容 APScheduler
        fields = [f if f != "?" else "*" for f in fields]
        
        return CronTrigger(
            second=fields[0],
            minute=fields[1],
            hour=fields[2],
            day=fields[3],
            month=fields[4],
            day_of_week=fields[5],
            year=fields[6] if len(fields) > 6 else "*",
            timezone="Asia/Shanghai",
        )
    
    @classmethod
    async def init_calling_scheduler(cls, redis: Redis) -> None:
        """
        初始化外呼任务调度器
        
        在应用启动时调用，将所有已启用的外呼任务配置注册到调度器
        """
        from app.plugin.module_application.job.tools.ap_scheduler import scheduler
        
        log.info("🔎 开始初始化外呼任务调度...")

        # 初始化历史记录清理任务（移动到此处，确保优先初始化）
        try:
            from .api_service import CallingCleanupService
            # 从 Redis 加载配置并注册任务
            await CallingCleanupService.refresh_job(redis)
            log.info("✅ 历史记录清理任务初始化完成")
        except Exception as e:
            log.error(f"初始化历史记录清理任务失败: {e}")
        
        # 读取所有已启用的任务配置
        async with async_db_session() as db:
            result = await db.execute(
                select(CallingTaskConfig).where(CallingTaskConfig.is_enabled == True)
            )
            task_configs = result.scalars().all()
        
        if not task_configs:
            log.info("未发现已启用的外呼任务配置")
            return
        
        # 注册每个任务
        registered_count = 0
        for config in task_configs:
            try:
                cls.add_job(config, redis)
                registered_count += 1
                log.info(f"已注册外呼任务: {config.name} (ID: {config.id})")
            except Exception as e:
                log.error(f"注册外呼任务失败 [{config.name}]: {e}")
        
        log.info(f"✅ 外呼任务调度初始化完成，已注册 {registered_count} 个任务")

    
    @classmethod
    def add_job(cls, task_config: CallingTaskConfig, redis: Redis) -> None:
        """
        添加外呼任务到调度器
        
        参数:
        - task_config: 任务配置对象
        - redis: Redis 连接
        """
        from app.plugin.module_application.job.tools.ap_scheduler import scheduler
        
        job_id = cls._get_job_id(task_config.id)
        
        # 如果任务已存在，先移除
        existing_job = scheduler.get_job(job_id)
        if existing_job:
            scheduler.remove_job(job_id)
        
        try:
            trigger = cls._parse_cron_expr(task_config.cron_expr)
            
            # 添加任务
            scheduler.add_job(
                func=cls._execute_wrapper,
                trigger=trigger,
                args=[redis, task_config.id],
                id=job_id,
                name=f"外呼任务: {task_config.name}",
                jobstore="default",  # 使用内存存储，因为任务配置在数据库中
                replace_existing=True,
                misfire_grace_time=60,
            )
            
            log.info(f"外呼任务已添加到调度器: {task_config.name} ({task_config.cron_expr})")
            
        except Exception as e:
            log.error(f"添加外呼任务到调度器失败: {e}")
            raise
    
    @classmethod
    async def _execute_wrapper(cls, redis: Redis, task_id: int) -> None:
        """
        任务执行包装器
        
        被调度器调用，执行实际的外呼任务
        """
        log.info(f"调度器触发外呼任务执行: task_id={task_id}")
        try:
            await CallingService.execute_task_with_config(redis, task_id)
        except Exception as e:
            log.error(f"外呼任务执行失败 [{task_id}]: {e}")
    
    @classmethod
    def remove_job(cls, task_id: int) -> None:
        """移除外呼任务"""
        from app.plugin.module_application.job.tools.ap_scheduler import scheduler
        
        job_id = cls._get_job_id(task_id)
        existing_job = scheduler.get_job(job_id)
        if existing_job:
            scheduler.remove_job(job_id)
            log.info(f"已移除外呼任务调度: {job_id}")
    
    @classmethod
    def update_job(cls, task_config: CallingTaskConfig, redis: Redis) -> None:
        """
        更新外呼任务调度
        
        如果任务启用，则添加/更新调度；如果禁用，则移除调度
        """
        if task_config.is_enabled:
            cls.add_job(task_config, redis)
        else:
            cls.remove_job(task_config.id)
    
    @classmethod
    def pause_job(cls, task_id: int) -> None:
        """暂停外呼任务"""
        from app.plugin.module_application.job.tools.ap_scheduler import scheduler
        
        job_id = cls._get_job_id(task_id)
        existing_job = scheduler.get_job(job_id)
        if existing_job:
            scheduler.pause_job(job_id)
            log.info(f"已暂停外呼任务调度: {job_id}")
    
    @classmethod
    def resume_job(cls, task_id: int) -> None:
        """恢复外呼任务"""
        from app.plugin.module_application.job.tools.ap_scheduler import scheduler
        
        job_id = cls._get_job_id(task_id)
        existing_job = scheduler.get_job(job_id)
        if existing_job:
            scheduler.resume_job(job_id)
            log.info(f"已恢复外呼任务调度: {job_id}")

