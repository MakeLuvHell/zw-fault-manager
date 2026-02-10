# -*- coding: utf-8 -*-
from typing import Any
from app.core.base_crud import CRUDBase
from app.plugin.module_brief.model import BriefReport
from app.plugin.module_brief.schema import BriefReportCreate


class BriefReportCRUD(CRUDBase[BriefReport, BriefReportCreate, Any]):
    """
    智能简报 CRUD 操作层
    """
    def __init__(self, auth):
        super().__init__(BriefReport, auth)
