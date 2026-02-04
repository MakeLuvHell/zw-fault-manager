# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import Response
from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.dependencies import get_current_user
from app.plugin.module_wxsafe.info.service import WxSafeService
from app.plugin.module_wxsafe.info.schema import WxSafeInfoCreate, WxSafeImportResponse
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

@router.get("/list", summary="分页获取涉诈信息列表")
async def get_list(
    page_no: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    clue_number: str = Query(None),
    phone_number: str = Query(None),
    auth: AuthSchema = Depends(get_current_user)
):
    search = {}
    if clue_number:
        search["clue_number"] = ("like", clue_number)
    if phone_number:
        search["phone_number"] = ("like", phone_number)
        
    offset = (page_no - 1) * page_size
    result = await WxSafeService.get_wx_safe_list(auth, offset, page_size, search)
    return SuccessResponse(data=result)

@router.post("/create", summary="单条录入涉诈信息")
async def create(
    data: WxSafeInfoCreate,
    auth: AuthSchema = Depends(get_current_user)
):
    result = await WxSafeService.create_wx_safe(auth, data)
    return SuccessResponse(data={"clue_number": result.clue_number})

@router.post("/import", summary="批量导入涉诈信息", response_model=ResponseSchema)
async def import_data(
    file: UploadFile = File(...),
    auth: AuthSchema = Depends(get_current_user)
):
    content = await file.read()
    result = await WxSafeService.import_wx_safe(auth, content)
    return SuccessResponse(data=result)