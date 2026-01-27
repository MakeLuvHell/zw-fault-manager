# -*- coding: utf-8 -*-

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.base_crud import CRUDBase
from app.api.v1.module_system.auth.schema import AuthSchema
from .model import PxmDataDrillInfoModel, PxmDataDrillNodeModel
from .schema import PxmDataDrillInfoCreate, PxmDataDrillInfoUpdate, PxmDataDrillNodeCreate, PxmDataDrillNodeUpdate

class PxmDataDrillInfoCRUD(CRUDBase[PxmDataDrillInfoModel, PxmDataDrillInfoCreate, PxmDataDrillInfoUpdate]):
    def __init__(self, auth: AuthSchema):
        super().__init__(model=PxmDataDrillInfoModel, auth=auth)

    async def get_with_nodes(self, id: int):
        # Explicitly load nodes and their children to avoid MissingGreenlet in Pydantic validation
        stmt = select(self.model).options(
            selectinload(self.model.nodes).selectinload(PxmDataDrillNodeModel.children)
        ).where(self.model.id == id)
        result = await self.auth.db.execute(stmt)
        return result.scalars().first()

class PxmDataDrillNodeCRUD(CRUDBase[PxmDataDrillNodeModel, PxmDataDrillNodeCreate, PxmDataDrillNodeUpdate]):
    def __init__(self, auth: AuthSchema):
        super().__init__(model=PxmDataDrillNodeModel, auth=auth)
    
    async def get_children(self, parent_id: int):
        stmt = select(self.model).where(self.model.parent_id == parent_id)
        result = await self.auth.db.execute(stmt)
        return result.scalars().all()
