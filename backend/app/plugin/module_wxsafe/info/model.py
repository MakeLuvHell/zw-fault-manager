# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

from app.core.base_model import MappedBase
from app.config.setting import settings


class WxSafeBase(MappedBase):
    """
    网信安模块基类，统一指定 schema
    """
    __abstract__ = True

    @declared_attr.directive
    def __table_args__(cls):
        return {"schema": settings.WXSAFE_SCHEMA}


class WxSafeInfo(WxSafeBase):
    """
    网信安涉诈信息表
    """
    __tablename__ = "t_wx_safe_info"

    # 1-8 核心字段
    clue_number: Mapped[str] = mapped_column(String(100), primary_key=True, comment="线索编号")
    category: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="涉诈或涉案")
    phone_number: Mapped[str] = mapped_column(String(20), index=True, comment="业务号码")
    report_month: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="月份")
    incident_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="涉诈（涉案）时间")
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="涉诈涉案地（城市）")
    fraud_type: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="涉诈类型")
    victim_number: Mapped[str | None] = mapped_column(Text, nullable=True, comment="受害人号码")

    # 9-36 后续字段
    join_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="入网时间")
    online_duration: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="在网时长（月）")
    install_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="新装或存量")
    join_location: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="入网属地")
    is_local_handle: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="属地或非属地办理")
    owner_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="机主名称")
    cert_address: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="证件地址")
    customer_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="政企或个人")
    other_phones: Mapped[str | None] = mapped_column(Text, nullable=True, comment="名下手机号码")
    age: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="年龄")
    agent_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="代理商")
    store_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="受理厅店")
    staff_id: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="受理人工号")
    staff_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="受理人")
    concurrent_cards: Mapped[str | None] = mapped_column(Text, nullable=True, comment="与涉诈号码同时办理的卡号")
    package_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="所办理套餐")
    is_fusion_package: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="是否融合套餐")
    has_broadband: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="是否有宽带业务")
    card_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="主卡或副卡")
    is_compliant: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="是否合规受理")
    has_resume_before: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="涉诈涉案前是否有复通")
    is_resume_compliant: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="复通是否规范")
    responsibility: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="责任认定")
    is_self_or_family: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="是否本人或亲属涉诈涉案")
    police_collab: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="警企协同情况")
    investigation_note: Mapped[str | None] = mapped_column(Text, nullable=True, comment="调查户主备注")
    abnormal_scene: Mapped[str | None] = mapped_column(Text, nullable=True, comment="异常场景识别")
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True, comment="核查情况反馈")

    created_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False, comment="数据入库时间"
    )
    updated_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="数据最后更新时间"
    )
