# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

from app.core.base_model import MappedBase
from app.config.setting import settings


class BriefBase(MappedBase):
    """
    智能简报模块基类，统一指定 schema
    """
    __abstract__ = True

    @declared_attr.directive
    def __table_args__(cls):
        # 兼容 MySQL (无 schema) 和 PostgreSQL
        if settings.DATABASE_TYPE == "postgres":
            return {"schema": settings.BRIEF_SCHEMA}
        return None


class BriefReport(BriefBase):
    """
    智能简报记录表
    """
    __tablename__ = "wx_brief_report"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键ID")
    filename: Mapped[str] = mapped_column(String(255), comment="原始文件名")
    focus: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="分析关注点")
    
    # 统计摘要数据 (JSON 格式)
    summary_data: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="统计摘要数据(JSON)")
    
    # AI 分析结果 (Markdown 格式)
    report_content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="AI分析报告内容")
    
    # 报告所属月份/日期
    report_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="报告所属日期")
    
    creator_id: Mapped[int | None] = mapped_column(nullable=True, comment="创建者ID")
    
    created_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False, comment="创建时间"
    )
    updated_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间"
    )
