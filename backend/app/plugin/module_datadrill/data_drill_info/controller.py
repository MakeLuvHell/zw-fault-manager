# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, Query
from app.common.response import ResponseSchema
from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.dependencies import get_current_user
from .schema import (
    PxmDataDrillInfoCreate, PxmDataDrillInfoUpdate, PxmDataDrillInfoQueryParam,
    PxmDataDrillNodeCreate, PxmDataDrillNodeUpdate,
    DrillSQLValidateRequest, DrillExecuteRequest
)
from .service import PxmDataDrillInfoService, PxmDataDrillNodeService, DrillService

router = APIRouter(prefix="/data_drill_info", tags=["下钻报表管理"])

# --- Info Endpoints ---
@router.get("/list", summary="报表列表", response_model=ResponseSchema)
async def list_info(
    page_no: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    search: PxmDataDrillInfoQueryParam = Depends(),
    auth: AuthSchema = Depends(get_current_user)
):
    data = await PxmDataDrillInfoService.list_service(auth, page_no, page_size, search)
    return ResponseSchema(data=data)

@router.post("/create", summary="创建报表", response_model=ResponseSchema)
async def create_info(
    data: PxmDataDrillInfoCreate,
    auth: AuthSchema = Depends(get_current_user)
):
    result = await PxmDataDrillInfoService.create_service(auth, data)
    return ResponseSchema(data=result)

@router.put("/update", summary="更新报表", response_model=ResponseSchema)
async def update_info(
    id: int,
    data: PxmDataDrillInfoUpdate,
    auth: AuthSchema = Depends(get_current_user)
):
    result = await PxmDataDrillInfoService.update_service(auth, id, data)
    return ResponseSchema(data=result)

@router.delete("/delete", summary="删除报表", response_model=ResponseSchema)
async def delete_info(
    ids: list[int],
    auth: AuthSchema = Depends(get_current_user)
):
    await PxmDataDrillInfoService.delete_service(auth, ids)
    return ResponseSchema()

@router.get("/detail", summary="报表详情(含节点)", response_model=ResponseSchema)
async def detail_info(
    id: int,
    auth: AuthSchema = Depends(get_current_user)
):
    result = await PxmDataDrillInfoService.detail_service(auth, id)
    return ResponseSchema(data=result)

# --- Node Endpoints ---
@router.post("/node/create", summary="创建节点", response_model=ResponseSchema)
async def create_node(
    data: PxmDataDrillNodeCreate,
    auth: AuthSchema = Depends(get_current_user)
):
    result = await PxmDataDrillNodeService.create_service(auth, data)
    return ResponseSchema(data=result)

@router.put("/node/update", summary="更新节点", response_model=ResponseSchema)
async def update_node(
    id: int,
    data: PxmDataDrillNodeUpdate,
    auth: AuthSchema = Depends(get_current_user)
):
    result = await PxmDataDrillNodeService.update_service(auth, id, data)
    return ResponseSchema(data=result)

@router.delete("/node/delete", summary="删除节点", response_model=ResponseSchema)
async def delete_node(
    ids: list[int],
    auth: AuthSchema = Depends(get_current_user)
):
    await PxmDataDrillNodeService.delete_service(auth, ids)
    return ResponseSchema()

@router.get("/node/children", summary="获取子节点", response_model=ResponseSchema)
async def get_node_children(
    parent_id: int,
    auth: AuthSchema = Depends(get_current_user)
):
    result = await PxmDataDrillNodeService.get_children_service(auth, parent_id)
    return ResponseSchema(data=result)

# --- Execute/Validate Endpoints ---
@router.post("/validate_sql", summary="SQL校验", response_model=ResponseSchema)
async def validate_sql(
    data: DrillSQLValidateRequest,
    auth: AuthSchema = Depends(get_current_user)
):
    result = await DrillService.validate_sql(auth, data)
    return ResponseSchema(data=result)

@router.post("/execute", summary="执行下钻查询", response_model=ResponseSchema)
async def execute_drill(
    data: DrillExecuteRequest,
    auth: AuthSchema = Depends(get_current_user)
):
    result = await DrillService.execute_drill(auth, data)
    return ResponseSchema(data=result)
