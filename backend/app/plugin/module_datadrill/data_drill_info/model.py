# -*- coding: utf-8 -*-

from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from app.core.base_model import ModelMixin, UserMixin

class PxmDataDrillInfoModel(ModelMixin, UserMixin):
    """
    下钻报表主表
    """
    __tablename__: str = 'data_drill_info'
    __table_args__: dict[str, str] = {'comment': '下钻报表定义'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    report_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='报表名称')
    
    # Relationship to nodes
    nodes: Mapped[list["PxmDataDrillNodeModel"]] = relationship(
        "PxmDataDrillNodeModel", back_populates="info", cascade="all, delete-orphan", lazy="selectin"
    )

class PxmDataDrillNodeModel(ModelMixin):
    """
    下钻报表节点表
    """
    __tablename__: str = 'data_drill_node'
    __table_args__: dict[str, str] = {'comment': '下钻报表节点'}

    info_id: Mapped[int] = mapped_column(Integer, ForeignKey('data_drill_info.id', ondelete="CASCADE"), nullable=False, comment='主表ID')
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('data_drill_node.id'), nullable=True, comment='父节点ID')
    node_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='节点名称')
    sql_text: Mapped[str | None] = mapped_column(Text, nullable=True, comment='查询SQL')
    link_field: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='父级关联字段')
    param_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='参数名')

    # Relationships
    info: Mapped["PxmDataDrillInfoModel"] = relationship("PxmDataDrillInfoModel", back_populates="nodes")
    parent: Mapped["PxmDataDrillNodeModel"] = relationship(
        "PxmDataDrillNodeModel", 
        remote_side="[PxmDataDrillNodeModel.id]", 
        backref=backref("children", lazy="selectin")
    )
