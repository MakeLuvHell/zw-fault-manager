# -*- coding: utf-8 -*-
"""外呼任务配置 CRUD 数据层"""
import json
from collections.abc import Sequence

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.plugin.module_calling.model import CallingTaskConfig

from .schema import CallingTaskCreateSchema, CallingTaskUpdateSchema


class CallingTaskCRUD(CRUDBase[CallingTaskConfig, CallingTaskCreateSchema, CallingTaskUpdateSchema]):
    """外呼任务配置数据层"""

    def __init__(self, auth: AuthSchema | None = None) -> None:
        """
        初始化外呼任务CRUD

        参数:
        - auth (AuthSchema | None): 认证信息模型
        """
        self.auth = auth
        super().__init__(model=CallingTaskConfig, auth=auth)

    async def get_obj_by_id_crud(self, id: int) -> CallingTaskConfig | None:
        """
        获取外呼任务详情

        参数:
        - id (int): 任务ID

        返回:
        - CallingTaskConfig | None: 外呼任务模型实例
        """
        return await self.get(id=id)

    async def get_obj_list_crud(
        self,
        search: dict | None = None,
        order_by: list | None = None,
    ) -> Sequence[CallingTaskConfig]:
        """
        获取外呼任务列表

        参数:
        - search (dict | None): 查询参数对象
        - order_by (list | None): 排序参数列表

        返回:
        - Sequence[CallingTaskConfig]: 外呼任务模型实例列表
        """
        return await self.list(search=search, order_by=order_by)

    async def create_obj_crud(self, data: CallingTaskCreateSchema) -> CallingTaskConfig | None:
        """
        创建外呼任务

        参数:
        - data (CallingTaskCreateSchema): 创建外呼任务负载模型

        返回:
        - CallingTaskConfig | None: 外呼任务模型实例
        """
        # 将 field_mapping 转换为 JSON 字符串
        data_dict = data.model_dump()
        data_dict["field_mapping"] = json.dumps(data_dict["field_mapping"], ensure_ascii=False)
        return await self.create(data=data_dict)

    async def update_obj_crud(self, id: int, data: CallingTaskUpdateSchema) -> CallingTaskConfig | None:
        """
        更新外呼任务

        参数:
        - id (int): 任务ID
        - data (CallingTaskUpdateSchema): 更新外呼任务负载模型

        返回:
        - CallingTaskConfig | None: 外呼任务模型实例
        """
        # 将 field_mapping 转换为 JSON 字符串
        data_dict = data.model_dump()
        data_dict["field_mapping"] = json.dumps(data_dict["field_mapping"], ensure_ascii=False)
        return await self.update(id=id, data=data_dict)

    async def delete_obj_crud(self, ids: list[int]) -> None:
        """
        删除外呼任务

        参数:
        - ids (list[int]): 任务ID列表

        返回:
        - None
        """
        return await self.delete(ids=ids)

    async def get_enabled_tasks_crud(self) -> Sequence[CallingTaskConfig]:
        """
        获取所有启用的任务

        返回:
        - Sequence[CallingTaskConfig]: 启用的外呼任务列表
        """
        return await self.list(search={"is_enabled": ("eq", True)})
