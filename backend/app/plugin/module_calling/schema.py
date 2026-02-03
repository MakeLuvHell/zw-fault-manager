# -*- coding: utf-8 -*-
"""外呼任务配置 Schema 定义"""
from typing import Optional
from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field


class FieldMappingSchema(BaseModel):
    """字段映射配置"""
    mobile_phone: str = Field(..., description="手机号字段映射")
    staff_name: str = Field(..., description="员工姓名字段映射")
    sys_name: str = Field(..., description="系统名称字段映射")
    order_type: str = Field(..., description="工单类型字段映射")
    order_nums: str = Field(..., description="工单数量字段映射")


class CallingTaskCreateSchema(BaseModel):
    """外呼任务创建模型"""
    name: str = Field(..., max_length=100, description="任务名称")
    cron_expr: str = Field(..., max_length=100, description="Cron 表达式")
    source_schema: str = Field(..., max_length=100, description="源数据 Schema")
    source_table: str = Field(..., max_length=100, description="源数据表名")
    is_enabled: bool = Field(default=True, description="是否启用")
    remark: Optional[str] = Field(default=None, max_length=500, description="备注")
    field_mapping: FieldMappingSchema = Field(..., description="字段映射配置")


class CallingTaskUpdateSchema(CallingTaskCreateSchema):
    """外呼任务更新模型"""
    pass


class CallingTaskOutSchema(BaseModel):
    """外呼任务响应模型"""
    id: int = Field(..., description="任务ID")
    name: str = Field(..., description="任务名称")
    cron_expr: str = Field(..., description="Cron 表达式")
    source_schema: str = Field(..., description="源数据 Schema")
    source_table: str = Field(..., description="源数据表名")
    is_enabled: bool = Field(..., description="是否启用")
    remark: Optional[str] = Field(default=None, description="备注")
    field_mapping: FieldMappingSchema = Field(..., description="字段映射配置")
    created_time: str = Field(..., description="创建时间")
    updated_time: str = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class CallingTaskQueryParam:
    """外呼任务查询参数"""

    def __init__(
        self,
        name: Optional[str] = Query(None, description="任务名称"),
        source_table: Optional[str] = Query(None, description="源数据表"),
        is_enabled: Optional[bool] = Query(None, description="启用状态"),
    ) -> None:
        if name:
            self.name = ("like", name)
        if source_table:
            self.source_table = ("like", source_table)
        if is_enabled is not None:
            self.is_enabled = ("eq", is_enabled)


# ============ 元数据相关 Schema ============

class SchemaInfoSchema(BaseModel):
    """Schema 信息"""
    schema_name: str = Field(..., description="Schema 名称")


class TableInfoSchema(BaseModel):
    """表信息"""
    table_name: str = Field(..., description="表名称")
    table_comment: Optional[str] = Field(default=None, description="表注释")


class ColumnInfoSchema(BaseModel):
    """列信息"""
    column_name: str = Field(..., description="列名称")
    data_type: str = Field(..., description="数据类型")
    column_comment: Optional[str] = Field(default=None, description="列注释")
    is_nullable: bool = Field(default=True, description="是否可为空")


# ============ 日志相关 Schema ============

class CallLogOutSchema(BaseModel):
    """外呼日志响应模型"""
    id: int = Field(..., description="日志ID")
    mobile_phone: str = Field(..., description="手机号码")
    staff_name: str = Field(..., description="员工姓名")
    sys_name: str = Field(..., description="系统名称")
    order_type: str = Field(..., description="工单类型")
    order_nums: int = Field(..., description="工单数量")
    status: int = Field(..., description="状态: 1=成功, 0=失败")
    error_msg: Optional[str] = Field(default=None, description="错误信息")
    push_time: str = Field(..., description="推送时间")

    model_config = ConfigDict(from_attributes=True)


# ============ 预览数据相关 Schema ============

class PreviewDataItemSchema(BaseModel):
    """待推送数据项"""
    mobile_phone: str = Field(..., description="手机号码")
    staff_name: str = Field(..., description="员工姓名")
    sys_name: str = Field(..., description="系统名称")
    order_type: str = Field(..., description="工单类型")
    order_nums: int = Field(..., description="工单数量")


class PreviewDataResultSchema(BaseModel):
    """待推送数据预览结果"""
    total: int = Field(..., description="待推送总数")
    items: list[PreviewDataItemSchema] = Field(..., description="数据列表")
    page_no: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
