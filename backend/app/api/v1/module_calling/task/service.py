# -*- coding: utf-8 -*-
"""外呼任务配置服务层"""
import json
from typing import Any, List
from collections.abc import Sequence

from fastapi import status
from sqlalchemy import text

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.database import async_db_session
from app.core.logger import log
from app.plugin.module_calling.model import CallingTaskConfig, CallLog
from sqlalchemy import select, desc

from .crud import CallingTaskCRUD
from .schema import (
    CallingTaskCreateSchema,
    CallingTaskUpdateSchema,
    CallingTaskOutSchema,
    FieldMappingSchema,
    SchemaInfoSchema,
    TableInfoSchema,
    ColumnInfoSchema,
    CallLogOutSchema,
)


class CallingTaskService:
    """外呼任务配置服务类"""

    @classmethod
    async def get_obj_detail_service(cls, id: int, auth: AuthSchema) -> CallingTaskOutSchema:
        """
        获取任务详情

        参数:
        - id (int): 任务ID
        - auth (AuthSchema): 认证信息

        返回:
        - CallingTaskOutSchema: 任务详情
        """
        crud = CallingTaskCRUD(auth=auth)
        obj = await crud.get_obj_by_id_crud(id=id)
        if not obj:
            raise CustomException(msg=f"任务ID {id} 不存在", status_code=status.HTTP_404_NOT_FOUND)
        return cls._model_to_schema(obj)

    @classmethod
    async def get_obj_list_service(
        cls,
        auth: AuthSchema,
        search: Any = None,
        order_by: list | None = None,
    ) -> List[CallingTaskOutSchema]:
        """
        获取任务列表

        参数:
        - auth (AuthSchema): 认证信息
        - search: 查询参数
        - order_by (list | None): 排序参数

        返回:
        - List[CallingTaskOutSchema]: 任务列表
        """
        crud = CallingTaskCRUD(auth=auth)
        search_dict = {k: v for k, v in vars(search).items() if v is not None} if search else None
        obj_list = await crud.get_obj_list_crud(search=search_dict, order_by=order_by)
        return [cls._model_to_schema(obj) for obj in obj_list]

    @classmethod
    async def create_obj_service(
        cls,
        auth: AuthSchema,
        data: CallingTaskCreateSchema,
    ) -> CallingTaskOutSchema:
        """
        创建任务

        参数:
        - auth (AuthSchema): 认证信息
        - data (CallingTaskCreateSchema): 创建数据

        返回:
        - CallingTaskOutSchema: 创建的任务
        """
        crud = CallingTaskCRUD(auth=auth)
        obj = await crud.create_obj_crud(data=data)
        log.info(f"创建外呼任务成功: {obj.name if obj else 'unknown'}")
        return cls._model_to_schema(obj)

    @classmethod
    async def update_obj_service(
        cls,
        auth: AuthSchema,
        id: int,
        data: CallingTaskUpdateSchema,
    ) -> CallingTaskOutSchema:
        """
        更新任务

        参数:
        - auth (AuthSchema): 认证信息
        - id (int): 任务ID
        - data (CallingTaskUpdateSchema): 更新数据

        返回:
        - CallingTaskOutSchema: 更新后的任务
        """
        crud = CallingTaskCRUD(auth=auth)
        
        # 检查任务是否存在
        existing = await crud.get_obj_by_id_crud(id=id)
        if not existing:
            raise CustomException(msg=f"任务ID {id} 不存在", status_code=status.HTTP_404_NOT_FOUND)
        
        obj = await crud.update_obj_crud(id=id, data=data)
        log.info(f"更新外呼任务成功: {id}")
        return cls._model_to_schema(obj)

    @classmethod
    async def delete_obj_service(cls, auth: AuthSchema, ids: list[int]) -> None:
        """
        删除任务

        参数:
        - auth (AuthSchema): 认证信息
        - ids (list[int]): 任务ID列表

        返回:
        - None
        """
        crud = CallingTaskCRUD(auth=auth)
        await crud.delete_obj_crud(ids=ids)
        log.info(f"删除外呼任务成功: {ids}")

    @classmethod
    def _model_to_schema(cls, obj: CallingTaskConfig) -> CallingTaskOutSchema:
        """将模型转换为 Schema"""
        field_mapping_dict = json.loads(obj.field_mapping) if isinstance(obj.field_mapping, str) else obj.field_mapping
        return CallingTaskOutSchema(
            id=obj.id,
            name=obj.name,
            cron_expr=obj.cron_expr,
            source_schema=obj.source_schema,
            source_table=obj.source_table,
            is_enabled=obj.is_enabled,
            remark=obj.remark,
            field_mapping=FieldMappingSchema(**field_mapping_dict),
            created_time=obj.created_time.strftime("%Y-%m-%d %H:%M:%S") if obj.created_time else "",
            updated_time=obj.updated_time.strftime("%Y-%m-%d %H:%M:%S") if obj.updated_time else "",
        )


class MetadataService:
    """数据库元数据服务类"""

    @classmethod
    async def get_schemas_service(cls) -> List[SchemaInfoSchema]:
        """
        获取所有 Schema 列表

        返回:
        - List[SchemaInfoSchema]: Schema 列表
        """
        async with async_db_session() as db:
            # PostgreSQL 查询所有非系统 schema
            result = await db.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                ORDER BY schema_name
            """))
            rows = result.fetchall()
            return [SchemaInfoSchema(schema_name=row[0]) for row in rows]

    @classmethod
    async def get_tables_service(cls, schema_name: str) -> List[TableInfoSchema]:
        """
        获取指定 Schema 下的所有表

        参数:
        - schema_name (str): Schema 名称

        返回:
        - List[TableInfoSchema]: 表列表
        """
        async with async_db_session() as db:
            result = await db.execute(text("""
                SELECT 
                    t.table_name,
                    COALESCE(pg_catalog.obj_description(
                        ('"' || t.table_schema || '"."' || t.table_name || '"')::regclass, 'pg_class'
                    ), '') as table_comment
                FROM information_schema.tables t
                WHERE t.table_schema = :schema_name
                AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name
            """), {"schema_name": schema_name})
            rows = result.fetchall()
            return [
                TableInfoSchema(
                    table_name=row[0],
                    table_comment=row[1] if row[1] else None
                ) for row in rows
            ]

    @classmethod
    async def get_columns_service(cls, schema_name: str, table_name: str) -> List[ColumnInfoSchema]:
        """
        获取指定表的所有列

        参数:
        - schema_name (str): Schema 名称
        - table_name (str): 表名称

        返回:
        - List[ColumnInfoSchema]: 列列表
        """
        async with async_db_session() as db:
            result = await db.execute(text("""
                SELECT 
                    c.column_name,
                    c.data_type,
                    COALESCE(pg_catalog.col_description(
                        ('"' || c.table_schema || '"."' || c.table_name || '"')::regclass,
                        c.ordinal_position
                    ), '') as column_comment,
                    c.is_nullable = 'YES' as is_nullable
                FROM information_schema.columns c
                WHERE c.table_schema = :schema_name
                AND c.table_name = :table_name
                ORDER BY c.ordinal_position
            """), {"schema_name": schema_name, "table_name": table_name})
            rows = result.fetchall()
            return [
                ColumnInfoSchema(
                    column_name=row[0],
                    data_type=row[1],
                    column_comment=row[2] if row[2] else None,
                    is_nullable=row[3]
                ) for row in rows
            ]


class CallLogService:
    """外呼日志服务类"""

    @classmethod
    async def get_logs_by_phones_service(
        cls,
        mobile_phones: List[str],
        limit: int = 100
    ) -> List[CallLogOutSchema]:
        """
        根据手机号列表获取日志

        参数:
        - mobile_phones (List[str]): 手机号列表
        - limit (int): 返回数量限制

        返回:
        - List[CallLogOutSchema]: 日志列表
        """
        if not mobile_phones:
            return []
            
        async with async_db_session() as db:
            result = await db.execute(
                select(CallLog)
                .where(CallLog.mobile_phone.in_(mobile_phones))
                .order_by(desc(CallLog.push_time))
                .limit(limit)
            )
            logs = result.scalars().all()
            return [
                CallLogOutSchema(
                    id=log.id,
                    mobile_phone=log.mobile_phone,
                    staff_name=log.staff_name,
                    sys_name=log.sys_name,
                    order_type=log.order_type,
                    order_nums=log.order_nums,
                    status=log.status,
                    error_msg=log.error_msg,
                    push_time=log.push_time.strftime("%Y-%m-%d %H:%M:%S") if log.push_time else ""
                ) for log in logs
            ]

    @classmethod
    async def get_recent_logs_service(cls, limit: int = 100) -> List[CallLogOutSchema]:
        """
        获取最近的日志

        参数:
        - limit (int): 返回数量限制

        返回:
        - List[CallLogOutSchema]: 日志列表
        """
        async with async_db_session() as db:
            result = await db.execute(
                select(CallLog)
                .order_by(desc(CallLog.push_time))
                .limit(limit)
            )
            logs = result.scalars().all()
            return [
                CallLogOutSchema(
                    id=log.id,
                    mobile_phone=log.mobile_phone,
                    staff_name=log.staff_name,
                    sys_name=log.sys_name,
                    order_type=log.order_type,
                    order_nums=log.order_nums,
                    status=log.status,
                    error_msg=log.error_msg,
                    push_time=log.push_time.strftime("%Y-%m-%d %H:%M:%S") if log.push_time else ""
                ) for log in logs
            ]
