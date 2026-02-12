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
    async def parse_excel(file_content: bytes) -> pd.DataFrame:
        """
        解析 Excel 内容并返回 DataFrame，进行基本校验
        """
        try:
            # 使用 pandas 读取 Excel
            df = pd.read_excel(io.BytesIO(file_content))
            
            # 校验必要列
            required_cols = ["自分类", "问题描述"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Excel 缺少必要列: {', '.join(missing_cols)}")
                
            return df
        except Exception as e:
            log.error(f"Excel 解析失败: {e}")
            raise ValueError(f"Excel 解析失败: {str(e)}")

    @staticmethod
    def generate_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """
        后端预计算：生成统计摘要 (Pandas)
        """
        total_count = len(df)
        
        # 1. 统计自分类 Top 10
        type_stats = df["自分类"].value_counts().head(10).to_dict()
        
        # 2. 统计一线人员身份分布
        identity_stats = {}
        if "一线人员身份" in df.columns:
            identity_stats = df["一线人员身份"].value_counts().to_dict()
            
        # 3. 统计平均时长 (如果有相关列)
        duration_stats = {}
        duration_col = "整单办结时长"
        if duration_col in df.columns:
            # 尝试转换为数值，过滤掉非数值
            df[duration_col] = pd.to_numeric(df[duration_col], errors='coerce')
            duration_stats = {
                "avg_duration": round(float(df[duration_col].mean()), 2) if not df[duration_col].empty else 0,
                "max_duration": float(df[duration_col].max()) if not df[duration_col].empty else 0
            }

        # 4. 提取关键词 (简单词频分析，基于问题描述)
        top_keywords = []
        if "问题描述" in df.columns:
            # 这里简单演示，实际可用 jieba
            text = " ".join(df["问题描述"].astype(str).tolist()[:500]) # 仅取前500条分析以保性能
            # 简单模拟分词：这里暂不做复杂分词，直接由 Dify 处理描述或后续引入 jieba
            # 暂且只传递统计数据
            
        summary = {
            "total_count": total_count,
            "type_distribution": type_stats,
            "identity_distribution": identity_stats,
            "duration_metrics": duration_stats,
            "data_sample": df[["自分类", "问题描述"]].head(5).to_dict(orient="records")
        }
        return summary

    @staticmethod
    async def call_dify_workflow(summary_data: Dict[str, Any], focus: str) -> Dict[str, Any]:
        """
        调用 Dify 工作流 API，传递统计摘要
        """
        # --- 调试输出：方便手动搬运 ---
        log.info("\n" + "="*50 + "\n[DIFY 待发送数据摘要 - 请复制下方 JSON]\n" + "="*50)
        print(json.dumps(summary_data, indent=2, ensure_ascii=False))
        log.info("\n" + "="*50)

        if not settings.DIFY_API_KEY:
            log.warning("DIFY_API_KEY 未配置，将跳过 AI 分析")
            return {"analysis": "DIFY_API_KEY 未配置，请从控制台复制数据到 Dify 测试。", "word_count": 0}

        payload = {
            "inputs": {
                "AI_ANALYSIS_FOCUS": focus or "全面分析数据中的亮点和问题",
                "statistical_summary": json.dumps(summary_data, ensure_ascii=False),
                "MAX_WORDS": "800"
            },
            "response_mode": "blocking",
            "user": "system_admin"
        }

        headers = {
            "Authorization": f"Bearer {settings.DIFY_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client: # 缩短超时，方便测试
                log.info(f"正在尝试调用 Dify 工作流... 关注点: {focus}")
                response = await client.post(settings.DIFY_API_URL, json=payload, headers=headers)
                response.raise_for_status()
                res_json = response.json()
                
                # Dify Workflow API 响应结构通常在 data.outputs 中
                outputs = res_json.get("data", {}).get("outputs", {})
                return {
                    "analysis": outputs.get("analysis") or outputs.get("text") or "AI 未返回分析内容",
                    "word_count": len(outputs.get("analysis", ""))
                }
        except Exception as e:
            log.error(f"Dify API 调用不可达 (网络环境限制): {e}")
            return {
                "analysis": f"⚠️ **网络环境受限，无法自动连接 Dify**\n\n请从后端控制台复制统计摘要 JSON 到 Dify 进行手动测试。\n\n**错误信息**: `{str(e)}`",
                "word_count": 0
            }

    @staticmethod
    async def create_analysis_report(
        auth: AuthSchema, 
        file: UploadFile, 
        focus: str
    ) -> BriefReport:
        """
        完整的业务流：解析 -> 统计 -> AI 分析 -> 存储
        """
        # 1. 读取并解析文件
        content = await file.read()
        df = await BriefService.parse_excel(content)
        
        # 2. 后端预计算
        summary_data = BriefService.generate_summary(df)
        
        # 3. 调用 AI 分析
        ai_result = await BriefService.call_dify_workflow(summary_data, focus)
        
        # 4. 持久化存储
        # 尝试从文件名提取日期 (如 202511)
        import re
        from datetime import datetime
        report_date = datetime.now()
        date_match = re.search(r"(\d{4})(\d{2})", file.filename)
        if date_match:
            try:
                report_date = datetime(int(date_match.group(1)), int(date_match.group(2)), 1)
            except:
                pass

        crud = BriefReportCRUD(auth)
        new_report_data = {
            "filename": file.filename,
            "focus": focus,
            "summary_data": summary_data,
            "report_content": ai_result["analysis"],
            "report_date": report_date,
            "creator_id": auth.user.id if auth and auth.user else None
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