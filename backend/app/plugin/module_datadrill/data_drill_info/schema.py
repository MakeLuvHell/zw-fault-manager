# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from fastapi import Query
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr

# --- Node Schemas ---
class PxmDataDrillNodeBase(BaseModel):
    parent_id: Optional[int] = Field(None, description="父节点ID")
    node_name: str = Field(..., description="节点名称")
    sql_text: Optional[str] = Field(None, description="查询SQL")
    link_field: Optional[str] = Field(None, description="父级关联字段")
    param_name: Optional[str] = Field(None, description="参数名")
    status: Optional[str] = Field("0", description="状态")
    description: Optional[str] = Field(None, description="备注")

class PxmDataDrillNodeCreate(PxmDataDrillNodeBase):
    info_id: int = Field(..., description="关联主表ID")

class PxmDataDrillNodeUpdate(PxmDataDrillNodeBase):
    pass

class PxmDataDrillNodeOut(PxmDataDrillNodeBase):
    id: int
    info_id: int
    # children: List["PxmDataDrillNodeOut"] = []
    
    model_config = ConfigDict(from_attributes=True)

# --- Info Schemas ---
class PxmDataDrillInfoBase(BaseModel):
    report_name: str = Field(..., description="报表名称")
    status: Optional[str] = Field("0", description="状态")
    description: Optional[str] = Field(None, description="备注")

class PxmDataDrillInfoCreate(PxmDataDrillInfoBase):
    pass

class PxmDataDrillInfoUpdate(PxmDataDrillInfoBase):
    pass

class PxmDataDrillInfoSimpleOut(PxmDataDrillInfoBase, BaseSchema, UserBySchema):
    model_config = ConfigDict(from_attributes=True)

class PxmDataDrillInfoOut(PxmDataDrillInfoBase, BaseSchema, UserBySchema):
    nodes: List[PxmDataDrillNodeOut] = []
    model_config = ConfigDict(from_attributes=True)

class PxmDataDrillInfoQueryParam:
    def __init__(
        self,
        report_name: str | None = Query(None, description="报表名称"),
        status: str | None = Query(None, description="状态"),
    ):
        self.report_name = ("like", report_name)
        self.status = status

# --- Execute/Validate Schemas ---
class DrillSQLValidateRequest(BaseModel):
    sql_text: str = Field(..., description="SQL语句")

class DrillSQLValidateResponse(BaseModel):
    valid: bool
    message: str
    columns: List[str] = []
    params: List[str] = []
    sql: Optional[str] = None

class DrillExecuteRequest(BaseModel):
    report_id: int
    node_id: int
    params: dict = Field(default_factory=dict, description="查询参数")
    page_no: int = 1
    page_size: int = 10

class DrillExecuteResponse(BaseModel):
    columns: List[str]
    data: List[dict]
    total: int
