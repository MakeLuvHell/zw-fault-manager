# -*- coding: utf-8 -*-
from datetime import datetime
from pydantic import Field, ConfigDict, BaseModel
from app.core.validator import Telephone, DateTimeStr


class WxSafeInfoBase(BaseModel):
    """
    网信安信息基础 Schema
    用于定义字段名和基础类型（Python 原生类型）
    """
    model_config = ConfigDict(from_attributes=True)
    
    category: str | None = Field(None, description="涉诈或涉案")
    phone_number: Telephone = Field(..., description="业务号码")
    report_month: str | None = Field(None, description="月份")
    # Input 使用 datetime，Pydantic 会自动尝试解析字符串
    incident_time: datetime | None = Field(None, description="涉诈（涉案）时间")
    city: str | None = Field(None, description="涉诈涉案地（城市）")
    fraud_type: str | None = Field(None, description="涉诈类型")
    victim_number: str | None = Field(None, description="受害人号码")
    
    # 后续字段
    join_date: datetime | None = Field(None, description="入网时间")
    online_duration: int | None = Field(None, description="在网时长（月）")
    install_type: str | None = Field(None, description="新装或存量")
    join_location: str | None = Field(None, description="入网属地")
    is_local_handle: str | None = Field(None, description="属地或非属地办理")
    owner_name: str | None = Field(None, description="机主名称")
    cert_address: str | None = Field(None, description="证件地址")
    customer_type: str | None = Field(None, description="政企或个人")
    other_phones: str | None = Field(None, description="名下手机号码")
    age: int | None = Field(None, description="年龄")
    agent_name: str | None = Field(None, description="代理商")
    store_name: str | None = Field(None, description="受理厅店")
    staff_id: str | None = Field(None, description="受理人工号")
    staff_name: str | None = Field(None, description="受理人")
    concurrent_cards: str | None = Field(None, description="与涉诈号码同时办理的卡号")
    package_name: str | None = Field(None, description="所办理套餐")
    is_fusion_package: str | None = Field(None, description="是否融合套餐")
    has_broadband: str | None = Field(None, description="是否有宽带业务")
    card_type: str | None = Field(None, description="主卡或副卡")
    is_compliant: str | None = Field(None, description="是否合规受理")
    has_resume_before: str | None = Field(None, description="涉诈涉案前是否有复通")
    is_resume_compliant: str | None = Field(None, description="复通是否规范")
    responsibility: str | None = Field(None, description="责任认定")
    is_self_or_family: str | None = Field(None, description="是否本人或亲属涉诈涉案")
    police_collab: str | None = Field(None, description="警企协同情况")
    investigation_note: str | None = Field(None, description="调查户主备注")
    abnormal_scene: str | None = Field(None, description="异常场景识别")
    feedback: str | None = Field(None, description="核查情况反馈")


class WxSafeInfoCreate(WxSafeInfoBase):
    """
    创建网信安信息
    """
    clue_number: str = Field(..., description="线索编号")


class WxSafeInfoUpdate(WxSafeInfoBase):
    """
    更新网信安信息
    """
    pass


class WxSafeInfoInvestigationUpdate(BaseModel):
    """
    涉诈信息核查更新 (9个字段)
    """
    is_compliant: str | None = Field(None, description="是否合规受理")
    has_resume_before: str | None = Field(None, description="涉诈涉案前是否有复通")
    is_resume_compliant: str | None = Field(None, description="复通是否规范")
    responsibility: str | None = Field(None, description="责任认定")
    is_self_or_family: str | None = Field(None, description="是否本人或亲属涉诈涉案")
    police_collab: str | None = Field(None, description="警企协同情况")
    investigation_note: str | None = Field(None, description="调查户主备注")
    abnormal_scene: str | None = Field(None, description="异常场景识别")
    feedback: str | None = Field(None, description="核查情况反馈")


class WxSafeInfoInDB(WxSafeInfoBase):
    """
    数据库中的网信安信息 (Output Schema)
    覆写时间字段为 DateTimeStr 以便 JSON 序列化
    """
    clue_number: str
    incident_time: DateTimeStr | None = None
    join_date: DateTimeStr | None = None
    
    created_time: DateTimeStr
    updated_time: DateTimeStr


class ImportResultDetail(BaseModel):
    """
    导入结果详情
    """
    clue_number: str | None = None
    status: str = Field(..., description="状态: 成功/失败")
    reason: str | None = Field(None, description="失败原因")


class WxSafeImportResponse(BaseModel):
    """
    批量导入响应
    """
    total: int = Field(0, description="总条数")
    success_count: int = Field(0, description="成功条数")
    fail_count: int = Field(0, description="失败条数")
    details: list[ImportResultDetail] = Field([], description="结果明细")
