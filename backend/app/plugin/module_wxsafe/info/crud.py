# -*- coding: utf-8 -*-
import pandas as pd
import io
from typing import Any
from sqlalchemy import select
from app.core.base_crud import CRUDBase
from app.plugin.module_wxsafe.info.model import WxSafeInfo
from app.plugin.module_wxsafe.info.schema import (
    WxSafeInfoCreate, 
    WxSafeInfoUpdate, 
    WxSafeImportResponse, 
    ImportResultDetail
)
from app.core.exceptions import CustomException
from pydantic import ValidationError


class CRUDWxSafe(CRUDBase[WxSafeInfo, WxSafeInfoCreate, WxSafeInfoUpdate]):
    """
    网信安涉诈信息数据操作层
    """

    async def create(self, data: WxSafeInfoCreate | dict) -> WxSafeInfo:
        """
        重写创建方法，处理主附表
        """
        from app.plugin.module_wxsafe.info.model import WxSafeDetail
        obj_dict = data if isinstance(data, dict) else data.model_dump()
        
        # 1. 提取字段
        master_fields = [
            "clue_number", "category", "phone_number", "report_month", 
            "incident_time", "city", "fraud_type", "victim_number",
            "is_compliant", "has_resume_before", 
            "is_resume_compliant", "responsibility", "is_self_or_family", 
            "police_collab", "investigation_note", "abnormal_scene", "feedback"
        ]
        detail_fields = [
            "join_date", "online_duration", "install_type", "join_location",
            "is_local_handle", "owner_name", "cert_address", "customer_type", 
            "other_phones", "age", "agent_name", "store_name", "staff_id", 
            "staff_name", "concurrent_cards", "package_name", "is_fusion_package", 
            "has_broadband", "card_type"
        ]
        
        master_data = {k: v for k, v in obj_dict.items() if k in master_fields}
        detail_data = {k: v for k, v in obj_dict.items() if k in detail_fields}
        
        # 2. 创建主表对象
        obj = self.model(**master_data)
        if self.auth.user:
            if hasattr(obj, "created_id"): setattr(obj, "created_id", self.auth.user.id)
            if hasattr(obj, "updated_id"): setattr(obj, "updated_id", self.auth.user.id)
        
        self.auth.db.add(obj)
        
        # 3. 创建附表对象
        detail_data["clue_number"] = obj_dict["clue_number"]
        detail_data["phone_number"] = obj_dict["phone_number"]
        detail_obj = WxSafeDetail(**detail_data)
        self.auth.db.add(detail_obj)
        
        await self.auth.db.flush()
        await self.auth.db.refresh(obj)
        return obj
    
    async def import_data(self, file_content: bytes) -> WxSafeImportResponse:
        """
        从 Excel 导入数据
        """
        try:
            df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            raise CustomException(msg=f"Excel 文件解析失败: {e!s}")

        # 字段映射 (中文 -> 英文) - 仅保留 8 个核心字段
        mapping = {
            "线索编号": "clue_number",
            "涉诈或涉案": "category",
            "业务号码": "phone_number",
            "月份": "report_month",
            "涉诈（涉案）时间": "incident_time",
            "涉诈涉案地（城市）": "city",
            "涉诈类型": "fraud_type",
            "受害人号码": "victim_number"
        }

        # 检查必要列
        must_cols = ["线索编号", "业务号码"]
        missing_cols = [col for col in mapping.keys() if col not in df.columns]
        if missing_cols:
            raise CustomException(msg=f"导入失败，缺少必要列: {', '.join(missing_cols)}")

        results: list[ImportResultDetail] = []
        success_count = 0
        
        for _, row in df.iterrows():
            # 提取数据并清洗 (处理 NaN)
            item_data = {}
            for cn_name, en_name in mapping.items():
                val = row[cn_name]
                if pd.isna(val):
                    item_data[en_name] = None
                else:
                    # 特殊处理业务号码和受害人号码，防止被读成浮点数
                    if en_name in ["phone_number", "victim_number", "clue_number"]:
                        item_data[en_name] = str(val).split('.')[0] if isinstance(val, float) else str(val)
                    # 处理时间字段
                    elif en_name == "incident_time":
                        if isinstance(val, pd.Timestamp):
                            item_data[en_name] = val.to_pydatetime()
                        elif isinstance(val, str):
                            try:
                                # 尝试多种格式解析
                                from dateutil import parser
                                item_data[en_name] = parser.parse(val)
                            except:
                                item_data[en_name] = val # 让 Pydantic 报错
                        else:
                            item_data[en_name] = val
                    # 强制转换月份为字符串
                    elif en_name == "report_month":
                        item_data[en_name] = str(val) if val is not None else None
                    else:
                        item_data[en_name] = val

            clue_num = str(item_data.get("clue_number", "未知"))
            
            try:
                # 1. 验证数据格式 (利用 Pydantic Schema，包含 11位号码校验)
                # 注意：clue_number 也是必填的
                schema_data = WxSafeInfoCreate(**item_data)
                
                # 2. 检查唯一性 (线索编号)
                existing = await self.get(clue_number=schema_data.clue_number)
                if existing:
                    results.append(ImportResultDetail(
                        clue_number=clue_num,
                        status="失败",
                        reason="线索编号已存在"
                    ))
                    continue
                
                # 3. 入库
                await self.create(schema_data)
                success_count += 1
                results.append(ImportResultDetail(
                    clue_number=clue_num,
                    status="成功"
                ))
            except ValidationError as ve:
                # 提取 Pydantic 校验错误
                errors = ve.errors()
                error_msg = "; ".join([f"{e['loc'][-1]}: {e['msg']}" for e in errors])
                results.append(ImportResultDetail(
                    clue_number=clue_num,
                    status="失败",
                    reason=f"格式校验失败: {error_msg}"
                ))
            except Exception as e:
                results.append(ImportResultDetail(
                    clue_number=clue_num,
                    status="失败",
                    reason=f"系统错误: {e!s}"
                ))

        return WxSafeImportResponse(
            total=len(df),
            success_count=success_count,
            fail_count=len(df) - success_count,
            details=results
        )
