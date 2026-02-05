# -*- coding: utf-8 -*-
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
        
        # 数据隔离逻辑
        # 如果不是超级管理员，且有部门信息，则只查询本部门属地的数据
        if not auth.user.is_superuser and auth.user.dept:
            dept_name = auth.user.dept.name
            # 这里假设 join_location 存储的是 "广州" 或 "广州市"，而部门名是 "广州分公司" 或 "广州"
            # 采用前缀匹配逻辑：如果 join_location 包含部门名，或部门名包含 join_location (取交集似匹配比较复杂，这里先用前缀匹配简化)
            # 业务约定：部门名称通常包含属地名，如 "广州分公司" -> 匹配 "广州%"
            # 或者数据清洗时已保证 join_location 规范。
            # 简单策略：WHERE join_location LIKE '{dept_name}%' 
            # 但实际可能是：dept="广州分公司", data="广州"。所以应该反过来，或者截取。
            # 更稳妥的方式：假设 dept.name 包含地市名。我们取 dept.name 的前两个字作为 key? 不太安全。
            # 暂时策略：直接匹配。如果 dept_name="广州分公司"，可能匹配不到 "广州"。
            # 修正策略：使用包含匹配。 search["join_location"] = ("like", f"{dept_name}%") 
            # 考虑到实际数据可能是 "广州"，部门是 "广州分公司"，用 like dept_name% 查不出来。
            # 应该：WHERE join_location LIKE '广州%' (如果部门只有“广州”两个字)
            # 建议：暂时约定部门名称前两个字作为属地匹配关键字，或者依赖数据完全一致。
            # 为了演示，假设 dept.name 就是 "广州" 这样的标准地市名。
            # 如果 auth.user.dept.name 是 "广州分公司"，我们尝试去掉 "分公司" 后匹配
            clean_dept_name = auth.user.dept.name.replace("分公司", "").replace("市", "")
            search["join_location"] = ("like", f"{clean_dept_name}%")

        crud = CRUDWxSafe(WxSafeInfo, auth)
        return await crud.page(
            offset=offset,
            limit=limit,
            order_by=[{"created_time": "desc"}],
            search=search,
            out_schema=WxSafeInfoInDB
        )

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
        
        return await crud.update(existing, data)

    @classmethod
    async def import_wx_safe(cls, auth: AuthSchema, file_content: bytes):
        """
        批量导入
        """
        crud = CRUDWxSafe(WxSafeInfo, auth)
        return await crud.import_data(file_content)

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
