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
    original_data: list | dict | None = Field(None, description="原始数据快照")
    analysis_content: str | None = Field(None, description="AI分析报告内容")
    word_count: int | None = Field(None, description="报告字数")
    creator_id: int | None = Field(None, description="创建者ID")


class BriefReportOut(BriefReportBase):
    """
    分析报告输出 Schema
    """
    id: int
    analysis_content: str | None = Field(None, description="AI分析报告内容")
    word_count: int | None = Field(None, description="报告字数")
    created_time: DateTimeStr
    updated_time: DateTimeStr
