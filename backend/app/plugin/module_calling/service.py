import asyncio
import time
from datetime import datetime
from typing import Dict, List, Set, Any

import httpx
from redis.asyncio import Redis
from sqlalchemy import select, delete

from app.config.setting import settings
from app.core.database import async_db_session
from app.core.logger import log
from app.plugin.module_calling.model import CallTask, CallHistory, CallLog


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
                response = await client.post(
                    settings.CALLING_API_URL,
                    json=body,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    log.info(f"推送成功: {mobile}")
                    return True, ""
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
    async def execute_task(cls, redis: Redis):
        """执行外呼任务的主逻辑"""
        start_time = time.time()
        log.info("====== 开始执行自动外呼任务 ======")

        # Step 1: 读取源数据 (短事务)
        tasks = []
        history_phones = set()
        
        async with async_db_session() as db:
            result = await db.execute(select(CallTask))
            tasks = result.scalars().all()
            
            if not tasks:
                log.info("未发现任务数据，任务结束")
                return

            history_result = await db.execute(select(CallHistory.mobile_phone))
            history_phones = set(history_result.scalars().all())

        # 3. 筛选新增任务 (内存操作)
        new_tasks = [t for t in tasks if t.mobile_phone not in history_phones]
        log.info(f"读取总数: {len(tasks)}, 历史记录: {len(history_phones)}, 待推送新增: {len(new_tasks)}")

        if not new_tasks:
            log.info("没有新增记录需要推送")
            return

        # 4. 执行推送 (无 DB 操作)
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

        # 5. 更新历史记录和写入日志 (短事务)
        if success_tasks or call_logs:
            async with async_db_session() as db:
                try:
                    # 写入流水日志 (不管成功失败都要记)
                    if call_logs:
                        db.add_all(call_logs)
                    
                    # 更新历史表 (只记成功的)
                    if success_tasks:
                        await db.execute(delete(CallHistory))
                        
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
