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
