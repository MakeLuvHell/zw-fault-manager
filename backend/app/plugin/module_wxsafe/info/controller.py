# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import Response
from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.dependencies import get_current_user, AuthPermission
from app.plugin.module_wxsafe.info.service import WxSafeService
from app.plugin.module_wxsafe.info.schema import WxSafeInfoCreate, WxSafeImportResponse, WxSafeInfoInvestigationUpdate
from app.common.response import SuccessResponse, ResponseSchema

router = APIRouter(prefix="/info", tags=["网信安涉诈信息管理"])

@router.get("/template", summary="下载涉诈信息导入模板")
async def download_template():
    result = await WxSafeService.get_template()
    return Response(
        content=result,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=wx_safe_import_template.xlsx"}
    )

@router.get("/list", summary="[管理]分页获取涉诈信息列表")
async def get_list(
    page_no: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    clue_number: str = Query(None),
    phone_number: str = Query(None),
    join_location: str = Query(None),
    report_month: str = Query(None),
    auth: AuthSchema = Depends(AuthPermission(["module_wxsafe:info:query"]))
):
    search = {}
    if clue_number:
        search["clue_number"] = ("like", clue_number)
    if phone_number:
        search["phone_number"] = ("like", phone_number)
    if join_location:
        search["join_location"] = ("like", join_location)
    if report_month:
        search["report_month"] = ("like", report_month)
        
    offset = (page_no - 1) * page_size
    result = await WxSafeService.get_wx_safe_list(auth, offset, page_size, search)
    return SuccessResponse(data=result)

@router.get("/investigation/list", summary="[核查]分页获取涉诈信息列表")
async def get_investigation_list(
    page_no: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    clue_number: str = Query(None),
    phone_number: str = Query(None),
    join_location: str = Query(None),
    report_month: str = Query(None),
    status: str = Query(None, description="状态: pending-待核查, verified-已核查"),
    auth: AuthSchema = Depends(AuthPermission(["module_wxsafe:investigation:query"]))
):
    search = {}
    if clue_number:
        search["clue_number"] = ("like", clue_number)
    if phone_number:
        search["phone_number"] = ("like", phone_number)
    if join_location:
        search["join_location"] = ("like", join_location)
    if report_month:
        search["report_month"] = ("like", report_month)
    if status:
        search["status"] = status
        
    offset = (page_no - 1) * page_size
    result = await WxSafeService.get_wx_safe_list(auth, offset, page_size, search)
    return SuccessResponse(data=result)

@router.get("/investigation/counts", summary="获取核查任务统计数量")
async def get_investigation_counts(
    auth: AuthSchema = Depends(AuthPermission(["module_wxsafe:investigation:query"]))
):
    result = await WxSafeService.get_investigation_counts(auth)
    return SuccessResponse(data=result)

@router.post("/create", summary="单条录入涉诈信息")
async def create(
    data: WxSafeInfoCreate,
    auth: AuthSchema = Depends(AuthPermission(["module_wxsafe:info:add"]))
):
    result = await WxSafeService.create_wx_safe(auth, data)
    return SuccessResponse(data={"clue_number": result.clue_number})

@router.put("/investigation/{clue_number}", summary="核查信息补录")
async def update_investigation(
    clue_number: str,
    data: WxSafeInfoInvestigationUpdate,
    auth: AuthSchema = Depends(AuthPermission(["module_wxsafe:investigation:update"]))
):
    await WxSafeService.update_wx_safe_investigation(auth, clue_number, data)
    return SuccessResponse(msg="核查信息保存成功")

@router.post("/import", summary="批量导入涉诈信息", response_model=ResponseSchema)

async def import_data(

    file: UploadFile = File(...),

    auth: AuthSchema = Depends(AuthPermission(["module_wxsafe:info:import"]))

):

    content = await file.read()

    result = await WxSafeService.import_wx_safe(auth, content)

    return SuccessResponse(data=result)



@router.post("/export", summary="导出涉诈信息")

async def export_data(

    clue_number: str = Query(None),

    phone_number: str = Query(None),

    join_location: str = Query(None),

    report_month: str = Query(None),

    auth: AuthSchema = Depends(AuthPermission(["module_wxsafe:info:export"]))

):

    search = {}

    if clue_number:

        search["clue_number"] = ("like", clue_number)

    if phone_number:

        search["phone_number"] = ("like", phone_number)

    if join_location:

        search["join_location"] = ("like", join_location)

    if report_month:

        search["report_month"] = ("like", report_month)

        

    result = await WxSafeService.export_wx_safe(auth, search)

    return Response(

        content=result,

        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

        headers={"Content-Disposition": f"attachment; filename=wx_safe_data.xlsx"}

    )
