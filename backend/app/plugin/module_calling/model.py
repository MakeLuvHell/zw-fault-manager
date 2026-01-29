# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import String, Integer
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
