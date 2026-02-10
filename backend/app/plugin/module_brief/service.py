# -*- coding: utf-8 -*-
import pandas as pd
import io
import httpx
import json
import asyncio
from typing import List, Dict, Any
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import log
from app.config.setting import settings
from app.plugin.module_brief.crud import BriefReportCRUD
from app.plugin.module_brief.model import BriefReport
from app.api.v1.module_system.auth.schema import AuthSchema


class BriefService:
    """
    智能简报业务逻辑
    """

    @staticmethod
    async def parse_excel(file_content: bytes) -> List[Dict[str, Any]]:
        """
        解析 Excel 内容并转换为 JSON 列表
        """
        try:
            # 使用 pandas 读取 Excel
            df = pd.read_excel(io.BytesIO(file_content))
            
            # 提取数据并转换为字典列表
            data = df.to_dict(orient="records")
            
            # 清理数据：处理时间格式化，处理 NaN
            cleaned_data = []
            for item in data:
                cleaned_item = {}
                for key, value in item.items():
                    # 处理 pandas 的 NaN 为 Python 的 None
                    if pd.isna(value):
                        cleaned_item[key] = None
                    elif isinstance(value, pd.Timestamp):
                        cleaned_item[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        cleaned_item[key] = value
                cleaned_data.append(cleaned_item)
                
            return cleaned_data
        except Exception as e:
            log.error(f"Excel 解析失败: {e}")
            raise ValueError(f"Excel 解析失败: {str(e)}")

    @staticmethod
    async def call_dify_workflow(report_data: List[Dict[str, Any]], focus: str) -> Dict[str, Any]:
        """
        调用 Dify 工作流 API
        """
        if not settings.DIFY_API_KEY:
            log.warning("DIFY_API_KEY 未配置，将跳过 AI 分析")
            return {"analysis": "DIFY_API_KEY 未配置，请联系管理员。", "word_count": 0}

        payload = {
            "inputs": {
                "AI_ANALYSIS_FOCUS": focus or "全面分析数据中的亮点和问题",
                "report_data": json.dumps(report_data, ensure_ascii=False),
                "MAX_WORDS": "200"
            },
            "response_mode": "blocking",
            "user": "system_admin"
        }

        headers = {
            "Authorization": f"Bearer {settings.DIFY_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    async with httpx.AsyncClient(timeout=120.0) as client:
                        log.info(f"正在调用 Dify 工作流 (尝试 {attempt + 1})... 关注点: {focus}")
                        response = await client.post(settings.DIFY_API_URL, json=payload, headers=headers)
                        response.raise_for_status()
                        res_json = response.json()
                        
                        outputs = res_json.get("data", {}).get("outputs", {})
                        return {
                            "analysis": outputs.get("analysis", "AI 未返回分析内容"),
                            "word_count": outputs.get("word_count", 0)
                        }
                except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                    if attempt == max_retries:
                        raise e
                    log.warning(f"Dify 调用失败，正在重试: {e}")
                    await asyncio.sleep(1)
        except Exception as e:
            log.error(f"Dify API 调用失败: {e}")
            return {"analysis": f"AI 分析调用失败: {str(e)}", "word_count": 0}

    @staticmethod
    async def create_analysis_report(
        auth: AuthSchema, 
        file: UploadFile, 
        focus: str
    ) -> BriefReport:
        """
        完整的业务流：解析 -> AI 分析 -> 存储
        """
        # 1. 读取并解析文件
        content = await file.read()
        report_data = await BriefService.parse_excel(content)
        
        # 2. 调用 AI 分析
        ai_result = await BriefService.call_dify_workflow(report_data, focus)
        
        # 3. 持久化存储
        snapshot_data = report_data[:100]
        
        # 使用 CRUD 类创建
        crud = BriefReportCRUD(auth)
        new_report_data = {
            "filename": file.filename,
            "focus": focus,
            "original_data": snapshot_data,
            "analysis_content": ai_result["analysis"],
            "word_count": ai_result["word_count"]
        }
        
        return await crud.create(new_report_data)

    @staticmethod
    async def get_brief_list(auth: AuthSchema, page_no: int, page_size: int):
        """
        获取历史报告列表
        """
        offset = (page_no - 1) * page_size
        crud = BriefReportCRUD(auth)
        # 使用 CRUDBase 的 page 方法进行分页
        from app.plugin.module_brief.schema import BriefReportOut
        return await crud.page(offset=offset, limit=page_size, order_by=[{"id": "desc"}], search={}, out_schema=BriefReportOut)

    @staticmethod
    async def get_brief_detail(auth: AuthSchema, report_id: int):
        """
        获取报告详情
        """
        crud = BriefReportCRUD(auth)
        return await crud.get(id=report_id)