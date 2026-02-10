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
        从 Excel 导入数据 (批量优化版)
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
        valid_masters = []
        valid_details = []
        
        # 1. 预处理：获取所有 Excel 中的线索编号，用于批量查重
        xls_clue_numbers = []
        if "线索编号" in df.columns:
             # 转为字符串并去重，防止 Excel 内部重复导致查询条件冗余（虽然 in 查询不在乎）
             xls_clue_numbers = df["线索编号"].dropna().astype(str).unique().tolist()
        
        # 批量查询数据库中已存在的线索编号
        existing_clue_set = set()
        if xls_clue_numbers:
            # 分批查询防止参数过多 (按 1000 条分批)
            batch_size = 1000
            for i in range(0, len(xls_clue_numbers), batch_size):
                batch = xls_clue_numbers[i:i + batch_size]
                stmt = select(WxSafeInfo.clue_number).where(WxSafeInfo.clue_number.in_(batch))
                db_res = await self.auth.db.execute(stmt)
                existing_clue_set.update(db_res.scalars().all())

        from app.plugin.module_wxsafe.info.model import WxSafeDetail

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
                        val_str = str(val)
                        if val_str.endswith('.0'):
                             val_str = val_str[:-2]
                        item_data[en_name] = val_str
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
                # 2. 验证数据格式 (利用 Pydantic Schema)
                schema_data = WxSafeInfoCreate(**item_data)
                
                # 3. 查重 (数据库已存在 或 Excel 前序行已出现)
                if schema_data.clue_number in existing_clue_set:
                    results.append(ImportResultDetail(
                        clue_number=clue_num,
                        status="失败",
                        reason="线索编号已存在或重复"
                    ))
                    continue
                
                # 标记为已存在，防止 Excel 内部后续重复
                existing_clue_set.add(schema_data.clue_number)
                
                # 4. 构建对象 (不入库)
                obj_dict = schema_data.model_dump()
                
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
                
                # 补全关联键
                detail_data["clue_number"] = obj_dict["clue_number"]
                detail_data["phone_number"] = obj_dict["phone_number"]
                
                # 实例化 Master
                master_obj = WxSafeInfo(**master_data)
                if self.auth.user:
                    if hasattr(master_obj, "created_id"): setattr(master_obj, "created_id", self.auth.user.id)
                    if hasattr(master_obj, "updated_id"): setattr(master_obj, "updated_id", self.auth.user.id)
                
                # 实例化 Detail
                detail_obj = WxSafeDetail(**detail_data)

                valid_masters.append(master_obj)
                valid_details.append(detail_obj)

                results.append(ImportResultDetail(
                    clue_number=clue_num,
                    status="成功"
                ))
            except ValidationError as ve:
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

        # 5. 批量执行插入
        success_count = 0
        if valid_masters:
            try:
                self.auth.db.add_all(valid_masters)
                self.auth.db.add_all(valid_details)
                await self.auth.db.flush()
                success_count = len(valid_masters)
            except Exception as e:
                # 批量插入失败，回滚并更新状态
                # 注意：这里可能需要更精细的错误处理，但通常预查重后极少失败
                await self.auth.db.rollback()
                success_count = 0
                error_msg = f"数据库写入异常: {e!s}"
                for res in results:
                    if res.status == "成功":
                        res.status = "失败"
                        res.reason = error_msg

        return WxSafeImportResponse(
            total=len(df),
            success_count=success_count,
            fail_count=len(df) - success_count,
            details=results
        )
