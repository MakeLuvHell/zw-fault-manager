# -*- coding: utf-8 -*-
"""
自动外呼任务代理
由于 SchedulerUtil 强制限制了任务函数必须位于 app.plugin.module_application.job.function_task 包下，
因此我们需要在这里创建一个代理文件，指向真正的业务逻辑。
"""

from app.plugin.module_calling.tasks import execute_calling_job

__all__ = ["execute_calling_job"]
