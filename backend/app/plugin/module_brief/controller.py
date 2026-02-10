# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, File, Query

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.dependencies import AuthPermission
from app.common.response import SuccessResponse
from app.plugin.module_brief.service import BriefService


router = APIRouter(tags=["智能简报分析"])


@router.post("/upload", summary="上传Excel并生成智能简报")
async def upload_and_analyze(
    file: UploadFile = File(...),
    focus: str = Query(None, description="分析关注点"),
    auth: AuthSchema = Depends(AuthPermission(["module_brief:report:add"]))
):
    """
    接收 Excel 文件，解析数据，调用 AI 生成简报并存库
    """
    result = await BriefService.create_analysis_report(auth, file, focus)
    return SuccessResponse(data={"id": result.id, "filename": result.filename})


@router.get("/list", summary="分页获取历史分析报告列表")
async def get_report_list(
    page_no: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    auth: AuthSchema = Depends(AuthPermission(["module_brief:report:query"]))
):
    """
    获取已生成的分析报告列表
    """
    result = await BriefService.get_brief_list(auth, page_no, page_size)
    return SuccessResponse(data=result)


@router.get("/{id}", summary="获取分析报告详细内容")
async def get_report_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_brief:report:query"]))
):
    """
    获取指定报告的 Markdown 内容及原始快照
    """
    result = await BriefService.get_brief_detail(auth, id)
    if not result:
        return SuccessResponse(msg="报告不存在", data=None)
    return SuccessResponse(data=result)