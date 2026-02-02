# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import MappedBase


class CallTask(MappedBase):
    """
    外呼任务源表
    """
    __tablename__ = "call_task"

    mobile_phone: Mapped[str] = mapped_column(String(20), primary_key=True, comment="手机号码")
    staff_name: Mapped[str] = mapped_column(String(50), comment="员工姓名")
    sys_name: Mapped[str] = mapped_column(String(50), comment="系统名称")
    order_type: Mapped[str] = mapped_column(String(50), comment="工单类型")
    order_nums: Mapped[int] = mapped_column(Integer, comment="工单数量")


class CallHistory(MappedBase):
    """
    外呼历史记录表
    """
    __tablename__ = "call_history"

    mobile_phone: Mapped[str] = mapped_column(String(20), primary_key=True, comment="手机号码")
    staff_name: Mapped[str] = mapped_column(String(50), comment="员工姓名")
    sys_name: Mapped[str] = mapped_column(String(50), comment="系统名称")
    order_type: Mapped[str] = mapped_column(String(50), comment="工单类型")
    order_nums: Mapped[int] = mapped_column(Integer, comment="工单数量")


class CallLog(MappedBase):
    """
    外呼流水日志表
    """
    __tablename__ = "call_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    mobile_phone: Mapped[str] = mapped_column(String(20), index=True, comment="手机号码")
    staff_name: Mapped[str] = mapped_column(String(50), comment="员工姓名")
    sys_name: Mapped[str] = mapped_column(String(50), comment="系统名称")
    order_type: Mapped[str] = mapped_column(String(50), comment="工单类型")
    order_nums: Mapped[int] = mapped_column(Integer, comment="工单数量")
    
    status: Mapped[int] = mapped_column(Integer, comment="状态: 1=成功, 0=失败")
    error_msg: Mapped[str | None] = mapped_column(String(2000), nullable=True, comment="错误信息")
    push_time: Mapped[datetime] = mapped_column(default=datetime.now, comment="推送时间")


class CallingTaskConfig(MappedBase):
    """
    外呼任务配置表
    用于管理外呼任务的调度配置和字段映射
    """
    __tablename__ = "calling_task_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="任务ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="任务名称")
    cron_expr: Mapped[str] = mapped_column(String(100), nullable=False, comment="Cron 表达式")
    source_schema: Mapped[str] = mapped_column(String(100), nullable=False, comment="源数据 Schema")
    source_table: Mapped[str] = mapped_column(String(100), nullable=False, comment="源数据表名")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否启用")
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="备注")
    
    # 字段映射 JSON 格式: {"mobile_phone": "col1", "staff_name": "col2", ...}
    field_mapping: Mapped[str] = mapped_column(Text, nullable=False, comment="字段映射 JSON")
    
    created_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False, comment="创建时间"
    )
    updated_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间"
    )

