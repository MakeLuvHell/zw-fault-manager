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
    
    async def import_data(self, file_content: bytes) -> WxSafeImportResponse:
        """
        从 Excel 导入数据
        """
        try:
            df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            raise CustomException(msg=f"Excel 文件解析失败: {e!s}")

        # 字段映射 (中文 -> 英文)
        mapping = {
            "线索编号": "clue_number",
            "涉诈或涉案": "category",
            "业务号码": "phone_number",
            "月份": "report_month",
            "涉诈（涉案）时间": "incident_time",
            "涉诈涉案地（城市）": "city",
            "涉诈类型": "fraud_type",
            "受害人号码": "victim_number",
            "入网时间": "join_date",
            "在网时长（月）": "online_duration",
            "新装或存量": "install_type",
            "入网属地": "join_location",
            "属地或非属地办理": "is_local_handle",
            "机主名称": "owner_name",
            "证件地址": "cert_address",
            "政企或个人": "customer_type",
            "名下手机号码": "other_phones",
            "年龄": "age",
            "代理商": "agent_name",
            "受理厅店": "store_name",
            "受理人工号": "staff_id",
            "受理人": "staff_name",
            "与涉诈号码同时办理的卡号": "concurrent_cards",
            "所办理套餐": "package_name",
            "是否融合套餐": "is_fusion_package",
            "是否有宽带业务": "has_broadband",
            "主卡或副卡": "card_type",
            "是否合规受理": "is_compliant",
            "涉诈涉案前是否有复通": "has_resume_before",
            "复通是否规范": "is_resume_compliant",
            "责任认定": "responsibility",
            "是否本人或亲属涉诈涉案": "is_self_or_family",
            "警企协同情况": "police_collab",
            "调查户主备注": "investigation_note",
            "异常场景识别": "abnormal_scene",
            "核查情况反馈": "feedback"
        }

        # 检查必要列
        must_cols = ["线索编号", "业务号码"]
        missing_cols = [col for col in must_cols if col not in df.columns]
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
