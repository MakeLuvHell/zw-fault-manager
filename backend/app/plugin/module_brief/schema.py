# -*- coding: utf-8 -*-
from datetime import datetime
from pydantic import Field, ConfigDict, BaseModel
from app.core.validator import DateTimeStr


class BriefReportBase(BaseModel):
    """
    智能简报基础 Schema
    """
    model_config = ConfigDict(from_attributes=True)
    
    filename: str = Field(..., description="原始文件名")
    focus: str | None = Field(None, description="分析关注点")


class BriefReportCreate(BriefReportBase):
    """
    创建分析报告 (通常由系统内部调用)
    """
    summary_data: dict | None = Field(None, description="统计摘要数据")
    report_content: str | None = Field(None, description="AI分析报告内容")
    report_date: datetime | None = Field(None, description="报告所属日期")
    creator_id: int | None = Field(None, description="创建者ID")


class BriefReportOut(BriefReportBase):
    """
    分析报告输出 Schema
    """
    id: int
    report_content: str | None = Field(None, description="AI分析报告内容")
    report_date: datetime | None = Field(None, description="报告所属日期")
    created_time: DateTimeStr
    updated_time: DateTimeStr
