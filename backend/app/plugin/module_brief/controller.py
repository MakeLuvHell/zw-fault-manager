# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.encoders import jsonable_encoder

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.dependencies import AuthPermission
from app.common.response import SuccessResponse
from app.plugin.module_brief.service import BriefService
from app.plugin.module_brief.schema import BriefReportOut


router = APIRouter(tags=["智能简报分析"])


@router.post("/generate", summary="上传Excel并生成智能分析简报")
async def upload_and_analyze(
    file: UploadFile = File(...),
    focus: str = Query(None, description="分析关注点 (如: 关注处理时长过长的工单)"),
    auth: AuthSchema = Depends(AuthPermission(["module_brief:report:add"]))
):
    """
    接收 Excel 文件，进行后端统计分析，调用 AI 生成简报并存库
    """
    result = await BriefService.create_analysis_report(auth, file, focus)
    return SuccessResponse(data=jsonable_encoder({"id": result.id, "filename": result.filename}))


@router.get("/list", summary="分页获取历史分析报告列表")
async def get_report_list(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, description="每页数量"),
    auth: AuthSchema = Depends(AuthPermission(["module_brief:report:query"]))
):
    """
    获取已生成的分析报告列表
    """
    result = await BriefService.get_brief_list(auth, page_no, page_size)
    return SuccessResponse(data=jsonable_encoder(result))


@router.get("/{id}", summary="获取分析报告详细内容")
async def get_report_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_brief:report:query"]))
):
    """
    获取指定报告的 Markdown 内容及统计摘要
    """
    result = await BriefService.get_brief_detail(auth, id)
    if not result:
        return SuccessResponse(msg="报告不存在", data=None)
    
    # 转换为输出 Schema 并编码
    out_data = BriefReportOut.model_validate(result)
    return SuccessResponse(data=jsonable_encoder(out_data))