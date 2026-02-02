# -*- coding: utf-8 -*-
"""外呼任务配置 API 路由"""
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi.responses import JSONResponse
from redis.asyncio.client import Redis

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.request import PaginationService
from app.common.response import SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.dependencies import AuthPermission, redis_getter
from app.core.logger import log
from app.core.router_class import OperationLogRoute
from app.core.router_class import OperationLogRoute
from .service import CallingService, CallingSchedulerService

from .schema import (
    CallingTaskCreateSchema,
    CallingTaskUpdateSchema,
    CallingTaskOutSchema,
    CallingTaskQueryParam,
    SchemaInfoSchema,
    TableInfoSchema,
    ColumnInfoSchema,
    CallLogOutSchema,
)
from .api_service import CallingTaskService, MetadataService, CallLogService


CallingTaskRouter = APIRouter(route_class=OperationLogRoute, prefix="/task", tags=["外呼任务管理"])


@CallingTaskRouter.get(
    "/detail/{id}",
    summary="获取任务详情",
    description="获取外呼任务配置详情",
    response_model=CallingTaskOutSchema,
)
async def get_task_detail_controller(
    id: Annotated[int, Path(description="任务ID")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_calling:task:detail"]))],
) -> JSONResponse:
    """获取任务详情"""
    result = await CallingTaskService.get_obj_detail_service(id=id, auth=auth)
    log.info(f"获取外呼任务详情成功 {id}")
    return SuccessResponse(data=result, msg="获取任务详情成功")


@CallingTaskRouter.get(
    "/list",
    summary="获取任务列表",
    description="获取外呼任务配置列表",
    response_model=list[CallingTaskOutSchema],
)
async def get_task_list_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_calling:task:query"]))],
    page: Annotated[PaginationQueryParam, Depends()],
    search: Annotated[CallingTaskQueryParam, Depends()],
) -> JSONResponse:
    """获取任务列表"""
    result_list = await CallingTaskService.get_obj_list_service(
        auth=auth, search=search, order_by=page.order_by
    )
    result = await PaginationService.paginate(
        data_list=result_list,
        page_no=page.page_no,
        page_size=page.page_size,
    )
    log.info("获取外呼任务列表成功")
    return SuccessResponse(data=result, msg="查询任务列表成功")


@CallingTaskRouter.post(
    "/create",
    summary="创建任务",
    description="创建外呼任务配置",
    response_model=CallingTaskOutSchema,
)
async def create_task_controller(
    data: CallingTaskCreateSchema,
    redis: Annotated[Redis, Depends(redis_getter)],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_calling:task:create"]))],
) -> JSONResponse:
    """创建任务"""
    result = await CallingTaskService.create_obj_service(auth=auth, data=data)
    
    # 如果任务启用，添加到调度器
    if result.is_enabled:
        task_config = await CallingTaskService.get_obj_detail_service(id=result.id, auth=auth)
        CallingSchedulerService.add_job(task_config, redis)
    
    log.info(f"创建外呼任务成功: {result.name}")
    return SuccessResponse(data=result, msg="创建任务成功")


@CallingTaskRouter.put(
    "/update/{id}",
    summary="修改任务",
    description="修改外呼任务配置",
    response_model=CallingTaskOutSchema,
)
async def update_task_controller(
    data: CallingTaskUpdateSchema,
    id: Annotated[int, Path(description="任务ID")],
    redis: Annotated[Redis, Depends(redis_getter)],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_calling:task:update"]))],
) -> JSONResponse:
    """修改任务"""
    result = await CallingTaskService.update_obj_service(auth=auth, id=id, data=data)
    
    # 同步更新调度器
    task_config = await CallingTaskService.get_obj_detail_service(id=id, auth=auth)
    CallingSchedulerService.update_job(task_config, redis)
    
    log.info(f"更新外呼任务成功 {id}")
    return SuccessResponse(data=result, msg="更新任务成功")


@CallingTaskRouter.delete(
    "/delete",
    summary="删除任务",
    description="删除外呼任务配置",
)
async def delete_task_controller(
    ids: Annotated[list[int], Body(description="任务ID列表")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_calling:task:delete"]))],
) -> JSONResponse:
    """删除任务"""
    # 先从调度器移除
    for task_id in ids:
        CallingSchedulerService.remove_job(task_id)
    
    await CallingTaskService.delete_obj_service(auth=auth, ids=ids)
    log.info(f"删除外呼任务成功: {ids}")
    return SuccessResponse(msg="删除任务成功")


@CallingTaskRouter.post(
    "/execute/{id}",
    summary="立即执行任务",
    description="立即异步执行外呼任务，不等待定时调度",
)
async def execute_task_controller(
    id: Annotated[int, Path(description="任务ID")],
    redis: Annotated[Redis, Depends(redis_getter)],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_calling:task:execute"]))],
) -> JSONResponse:
    """
    立即执行任务
    
    异步触发外呼任务执行，前端立即收到反馈，不阻塞界面
    """
    # 检查任务是否存在
    task = await CallingTaskService.get_obj_detail_service(id=id, auth=auth)
    
    # 异步触发任务执行（后台运行）
    # 使用新的 execute_task_with_config 方法，根据任务配置动态读取源表数据
    import asyncio
    asyncio.create_task(CallingService.execute_task_with_config(redis, id))
    
    log.info(f"触发外呼任务执行: {task.name} (ID: {id})")
    return SuccessResponse(msg=f"任务 '{task.name}' 已触发执行，请点击日志按钮查看结果")


@CallingTaskRouter.get(
    "/logs",
    summary="获取执行日志",
    description="获取最近的外呼执行日志",
    response_model=list[CallLogOutSchema],
)
async def get_logs_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_calling:task:query"]))],
    limit: Annotated[int, Query(description="返回数量限制", ge=1, le=500)] = 100,
) -> JSONResponse:
    """获取最近的执行日志"""
    result = await CallLogService.get_recent_logs_service(limit=limit)
    log.info(f"获取外呼日志成功，共 {len(result)} 条")
    return SuccessResponse(data=result, msg="获取日志成功")


# ============ 元数据 API ============

MetadataRouter = APIRouter(prefix="/metadata", tags=["数据库元数据"])


@MetadataRouter.get(
    "/schemas",
    summary="获取 Schema 列表",
    description="获取数据库所有可用的 Schema",
    response_model=list[SchemaInfoSchema],
)
async def get_schemas_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_calling:task:query"]))],
) -> JSONResponse:
    """获取 Schema 列表"""
    result = await MetadataService.get_schemas_service()
    return SuccessResponse(data=result, msg="获取 Schema 列表成功")


@MetadataRouter.get(
    "/tables",
    summary="获取表列表",
    description="获取指定 Schema 下的所有表",
    response_model=list[TableInfoSchema],
)
async def get_tables_controller(
    schema_name: Annotated[str, Query(description="Schema 名称")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_calling:task:query"]))],
) -> JSONResponse:
    """获取表列表"""
    result = await MetadataService.get_tables_service(schema_name=schema_name)
    return SuccessResponse(data=result, msg="获取表列表成功")


@MetadataRouter.get(
    "/columns",
    summary="获取列列表",
    description="获取指定表的所有列信息",
    response_model=list[ColumnInfoSchema],
)
async def get_columns_controller(
    schema_name: Annotated[str, Query(description="Schema 名称")],
    table_name: Annotated[str, Query(description="表名称")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_calling:task:query"]))],
) -> JSONResponse:
    """获取列列表"""
    result = await MetadataService.get_columns_service(schema_name=schema_name, table_name=table_name)
    return SuccessResponse(data=result, msg="获取列列表成功")
