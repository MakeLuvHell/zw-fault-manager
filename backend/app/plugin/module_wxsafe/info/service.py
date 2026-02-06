# -*- coding: utf-8 -*-
from datetime import datetime
import calendar
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.plugin.module_wxsafe.info.crud import CRUDWxSafe
from app.plugin.module_wxsafe.info.model import WxSafeInfo, WxSafeDetail
from app.api.v1.module_system.auth.schema import AuthSchema
from app.plugin.module_wxsafe.info.schema import WxSafeInfoInDB


class WxSafeService:
    """
    网信安涉诈信息服务层
    """
    
    @classmethod
    async def get_wx_safe_list(cls, auth: AuthSchema, offset: int, limit: int, search: dict):
        """
        分页查询 (支持跨表属地隔离)
        """
        # 获取用户权限集合
        user_permissions = {
            menu.permission
            for role in auth.user.roles
            for menu in role.menus
            if role.status == "0" and menu.permission and menu.status == "0"
        }

        # 1. 基础查询对象 (预加载附表画像)
        query = select(WxSafeInfo).options(joinedload(WxSafeInfo.detail))

        # 2. 跨表数据隔离逻辑
        # 如果不是超级管理员，且没有全量管理权限，则必须关联附表按属地过滤
        is_admin = auth.user.is_superuser or "module_wxsafe:info:query" in user_permissions
        if not is_admin and auth.user.dept:
            clean_dept_name = auth.user.dept.name.replace("分公司", "").replace("市", "")
            query = query.join(WxSafeInfo.detail).where(WxSafeDetail.join_location.like(f"{clean_dept_name}%"))

        # 3. 处理业务过滤条件
        # 月份查询转时间范围
        if "report_month" in search:
            _, val = search.pop("report_month")
            if val and "-" in val:
                try:
                    y, m = map(int, val.split("-"))
                    last_day = calendar.monthrange(y, m)[1]
                    start_dt = datetime(y, m, 1, 0, 0, 0)
                    end_dt = datetime(y, m, last_day, 23, 59, 59)
                    query = query.where(WxSafeInfo.incident_time.between(start_dt, end_dt))
                except:
                    pass

        # 状态过滤 (待核查/已核查)
        if "status" in search:
            status = search.pop("status")
            if status == "pending":
                query = query.where(WxSafeInfo.is_compliant.is_(None))
            elif status == "verified":
                query = query.where(WxSafeInfo.is_compliant.isnot(None))

        # 其他基础字段搜索 (线索编号、手机号、入网属地等)
        if "clue_number" in search:
            query = query.where(WxSafeInfo.clue_number.like(f"%{search.pop('clue_number')[1]}%"))
        if "phone_number" in search:
            query = query.where(WxSafeInfo.phone_number.like(f"%{search.pop('phone_number')[1]}%"))
        if "join_location" in search:
            # 入网属地现在在附表
            if not is_admin: # 如果已经是 join 状态了
                query = query.where(WxSafeDetail.join_location.like(f"%{search.pop('join_location')[1]}%"))
            else:
                query = query.join(WxSafeInfo.detail).where(WxSafeDetail.join_location.like(f"%{search.pop('join_location')[1]}%"))

        # 4. 执行计数与分页
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await auth.db.execute(count_query)
        total = total_res.scalar() or 0
        
        result = await auth.db.execute(
            query.order_by(WxSafeInfo.created_time.desc()).offset(offset).limit(limit)
        )
        objs = result.scalars().all()

        return {
            "page_no": offset // limit + 1 if limit else 1,
            "page_size": limit or 10,
            "total": total,
            "has_next": offset + limit < total,
            "items": [WxSafeInfoInDB.model_validate(obj).model_dump() for obj in objs],
        }

    @classmethod
    async def get_investigation_counts(cls, auth: AuthSchema):
        """
        获取核查任务统计数量
        """
        # 基础查询，应用数据隔离
        base_query = select(func.count(WxSafeInfo.clue_number))
        
        user_permissions = {
            menu.permission
            for role in auth.user.roles
            for menu in role.menus
            if role.status == "0" and menu.permission and menu.status == "0"
        }
        
        if not auth.user.is_superuser and "module_wxsafe:info:query" not in user_permissions:
            if auth.user.dept:
                clean_dept_name = auth.user.dept.name.replace("分公司", "").replace("市", "")
                base_query = base_query.join(WxSafeInfo.detail).where(WxSafeDetail.join_location.like(f"{clean_dept_name}%"))

        # 计算待核查
        pending_sql = base_query.where(WxSafeInfo.is_compliant.is_(None))
        # 计算已核查
        verified_sql = base_query.where(WxSafeInfo.is_compliant.isnot(None))
        
        pending_res = await auth.db.execute(pending_sql)
        verified_res = await auth.db.execute(verified_sql)
        
        return {
            "pending": pending_res.scalar() or 0,
            "verified": verified_res.scalar() or 0
        }

    @classmethod
    async def create_wx_safe(cls, auth: AuthSchema, data):
        """
        单条录入
        """
        crud = CRUDWxSafe(WxSafeInfo, auth)
        existing = await crud.get(clue_number=data.clue_number)
        if existing:
            from app.core.exceptions import CustomException
            raise CustomException(msg=f"线索编号 {data.clue_number} 已存在")
        return await crud.create(data)

    @classmethod
    async def update_wx_safe_investigation(cls, auth: AuthSchema, clue_number: str, data):
        """
        核查信息补录
        """
        from app.core.exceptions import CustomException
        
        crud = CRUDWxSafe(WxSafeInfo, auth)
        existing = await crud.get(clue_number=clue_number, preload=["detail"])
        if not existing:
            raise CustomException(msg=f"线索编号 {clue_number} 不存在")
        
        # 权限检查：非超管必须校验属地 (此时 join_location 在附表)
        if not auth.user.is_superuser and auth.user.dept:
            clean_dept_name = auth.user.dept.name.replace("分公司", "").replace("市", "")
            if not existing.detail or not existing.detail.join_location or clean_dept_name not in existing.detail.join_location:
                 raise CustomException(msg=f"无权操作非本属地的数据")
        
        # 手动更新主表属性
        obj_dict = data if isinstance(data, dict) else data.model_dump(exclude_unset=True)
        for key, value in obj_dict.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        
        await auth.db.flush()
        return existing

    @classmethod
    async def import_wx_safe(cls, auth: AuthSchema, file_content: bytes):
        """
        批量导入
        """
        crud = CRUDWxSafe(WxSafeInfo, auth)
        return await crud.import_data(file_content)

    @classmethod
    async def export_wx_safe(cls, auth: AuthSchema, search: dict):
        """
        导出全量数据
        """
        from app.utils.excel_util import ExcelUtil
        
        # 1. 执行与列表查询相同的全量逻辑 (不分页)
        # 为简化逻辑，我们这里复用 get_wx_safe_list 的过滤思想但返回全量
        # 获取 10000 条作为全量限制
        result = await cls.get_wx_safe_list(auth, 0, 10000, search)
        list_data_展平 = result["items"]
        
        # 定义字段映射
        mapping_dict = {
            "clue_number": "线索编号",
            "category": "涉诈或涉案",
            "phone_number": "业务号码",
            "report_month": "月份",
            "incident_time": "涉诈（涉案）时间",
            "city": "涉诈涉案地（城市）",
            "fraud_type": "涉诈类型",
            "victim_number": "受害人号码",
            "join_date": "入网时间",
            "online_duration": "在网时长（月）",
            "install_type": "新装或存量",
            "join_location": "入网属地",
            "is_local_handle": "属地或非属地办理",
            "owner_name": "机主名称",
            "cert_address": "证件地址",
            "customer_type": "政企或个人",
            "other_phones": "名下手机号码",
            "age": "年龄",
            "agent_name": "代理商",
            "store_name": "受理厅店",
            "staff_id": "受理人工号",
            "staff_name": "受理人",
            "concurrent_cards": "与涉诈号码同时办理的卡号",
            "package_name": "所办理套餐",
            "is_fusion_package": "是否融合套餐",
            "has_broadband": "是否有宽带业务",
            "card_type": "主卡或副卡",
            "is_compliant": "是否合规受理",
            "has_resume_before": "涉诈涉案前是否有复通",
            "is_resume_compliant": "复通是否规范",
            "responsibility": "责任认定",
            "is_self_or_family": "是否本人或亲属涉诈涉案",
            "police_collab": "警企协同情况",
            "investigation_note": "调查户主备注",
            "abnormal_scene": "异常场景识别",
            "feedback": "核查情况反馈"
        }
        
        return ExcelUtil.export_list2excel(list_data_展平, mapping_dict)

    @classmethod
    async def get_template(cls):
        """
        获取导入模板
        """
        from app.utils.excel_util import ExcelUtil
        header_list = [
            "线索编号", "涉诈或涉案", "业务号码", "月份", 
            "涉诈（涉案）时间", "涉诈涉案地（城市）", "涉诈类型", "受害人号码"
        ]
        selector_header_list = ["涉诈或涉案"]
        option_list = [{"涉诈或涉案": ["涉诈", "涉案"]}]
        return ExcelUtil.get_excel_template(header_list, selector_header_list, option_list)