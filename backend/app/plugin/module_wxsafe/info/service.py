# -*- coding: utf-8 -*-
from datetime import datetime
import calendar
from app.plugin.module_wxsafe.info.crud import CRUDWxSafe
from app.plugin.module_wxsafe.info.model import WxSafeInfo
from app.api.v1.module_system.auth.schema import AuthSchema


class WxSafeService:
    """
    网信安涉诈信息服务层
    """
    
    @classmethod
    async def get_wx_safe_list(cls, auth: AuthSchema, offset: int, limit: int, search: dict):
        """
        分页查询
        """
        from app.plugin.module_wxsafe.info.schema import WxSafeInfoInDB
        
        # 获取用户权限集合
        user_permissions = {
            menu.permission
            for role in auth.user.roles
            for menu in role.menus
            if role.status == "0" and menu.permission and menu.status == "0"
        }

        # 数据隔离逻辑：
        # 1. 如果是超级管理员，或者拥有管理岗全量查询权限 (module_wxsafe:info:query)，则不进行过滤
        # 2. 否则，如果用户有部门信息，则根据部门进行属地前缀匹配
        if auth.user.is_superuser or "module_wxsafe:info:query" in user_permissions:
            pass
        elif auth.user.dept:
            clean_dept_name = auth.user.dept.name.replace("分公司", "").replace("市", "")
            search["join_location"] = ("like", f"{clean_dept_name}%")

        # 兼容性处理：如果搜索条件包含 report_month
        if "report_month" in search:
            field_name, val = search.pop("report_month")
            if val and "-" in val:
                # 将 YYYY-MM 转换为当月的起始和结束时间戳，查询 incident_time 字段
                try:
                    y, m = map(int, val.split("-"))
                    last_day = calendar.monthrange(y, m)[1]
                    start_dt = datetime(y, m, 1, 0, 0, 0)
                    end_dt = datetime(y, m, last_day, 23, 59, 59)
                    search["incident_time"] = ("between", (start_dt, end_dt))
                except Exception as e:
                    print(f"月份解析失败: {e}")

        # 处理状态过滤逻辑 (以 is_compliant 作为核查状态的核心判断字段)
        if "status" in search:
            status = search.pop("status")
            if status == "pending":
                # 待核查：核心核查字段为空
                search["is_compliant"] = ("None", None)
            elif status == "verified":
                # 已核查：核心核查字段不为空
                search["is_compliant"] = ("not None", None)

        crud = CRUDWxSafe(WxSafeInfo, auth)
        return await crud.page(
            offset=offset,
            limit=limit,
            order_by=[{"created_time": "desc"}],
            search=search,
            out_schema=WxSafeInfoInDB
        )

    @classmethod
    async def get_investigation_counts(cls, auth: AuthSchema):
        """
        获取核查任务统计数量
        """
        from sqlalchemy import select, func
        
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
                base_query = base_query.where(WxSafeInfo.join_location.like(f"{clean_dept_name}%"))

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
        # 检查唯一性
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
        existing = await crud.get(clue_number=clue_number)
        if not existing:
            raise CustomException(msg=f"线索编号 {clue_number} 不存在")
        
        # 权限检查：非超管必须校验属地
        if not auth.user.is_superuser and auth.user.dept:
            clean_dept_name = auth.user.dept.name.replace("分公司", "").replace("市", "")
            if not existing.join_location or clean_dept_name not in existing.join_location:
                 raise CustomException(msg=f"无权操作非本属地 ({existing.join_location}) 的数据")
        
        # 手动更新对象属性，避开基类 CRUD 对 'id' 字段的依赖
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
        导出数据
        """
        from app.utils.excel_util import ExcelUtil
        
        # 1. 执行相同的过滤逻辑
        user_permissions = {
            menu.permission
            for role in auth.user.roles
            for menu in role.menus
            if role.status == "0" and menu.permission and menu.status == "0"
        }
        if not auth.user.is_superuser and "module_wxsafe:info:query" not in user_permissions:
            if auth.user.dept:
                clean_dept_name = auth.user.dept.name.replace("分公司", "").replace("市", "")
                search["join_location"] = ("like", f"{clean_dept_name}%")
        
        # 处理月份过滤
        if "report_month" in search:
            field_name, val = search.pop("report_month")
            if val and "-" in val:
                try:
                    y, m = map(int, val.split("-"))
                    last_day = calendar.monthrange(y, m)[1]
                    search["incident_time"] = ("between", (datetime(y, m, 1), datetime(y, m, last_day, 23, 59, 59)))
                except:
                    pass

        # 2. 查询全量数据 (不分页)
        crud = CRUDWxSafe(WxSafeInfo, auth)
        data_list = await crud.list(search=search, order_by=[{"created_time": "desc"}])
        
        # 3. 定义字段映射 (英文 -> 中文)
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
        
        # 4. 转换数据为字典列表
        list_data = []
        for obj in data_list:
            item = {}
            for col in mapping_dict.keys():
                val = getattr(obj, col, "")
                if isinstance(val, datetime):
                    val = val.strftime("%Y-%m-%d %H:%M:%S")
                item[col] = val if val is not None else ""
            list_data.append(item)
            
        return ExcelUtil.export_list2excel(list_data, mapping_dict)

    @classmethod
    async def get_template(cls):
        """
        获取导入模板
        """
        from app.utils.excel_util import ExcelUtil
        header_list = [
            "线索编号", "涉诈或涉案", "业务号码", "月份", "涉诈（涉案）时间", 
            "涉诈涉案地（城市）", "涉诈类型", "受害人号码", "入网时间", 
            "在网时长（月）", "新装或存量", "入网属地", "属地或非属地办理", 
            "机主名称", "证件地址", "政企或个人", "名下手机号码", "年龄", 
            "代理商", "受理厅店", "受理人工号", "受理人", "与涉诈号码同时办理的卡号", 
            "所办理套餐", "是否融合套餐", "是否有宽带业务", "主卡或副卡", 
            "是否合规受理", "涉诈涉案前是否有复通", "复通是否规范", "责任认定", 
            "是否本人或亲属涉诈涉案", "警企协同情况", "调查户主备注", 
            "异常场景识别", "核查情况反馈"
        ]
        # 设置下拉选项（可选）
        selector_header_list = ["涉诈或涉案", "是否融合套餐", "是否有宽带业务", "主卡或副卡"]
        option_list = [
            {"涉诈或涉案": ["涉诈", "涉案"]},
            {"是否融合套餐": ["是", "否"]},
            {"是否有宽带业务": ["是", "否"]},
            {"主卡或副卡": ["主卡", "副卡"]}
        ]
        
        return ExcelUtil.get_excel_template(header_list, selector_header_list, option_list)
