# -*- coding: utf-8 -*-

import re
from sqlalchemy import text
from app.core.exceptions import CustomException
from app.api.v1.module_system.auth.schema import AuthSchema
from .crud import PxmDataDrillInfoCRUD, PxmDataDrillNodeCRUD
from .schema import (
    PxmDataDrillInfoCreate, PxmDataDrillInfoUpdate, PxmDataDrillInfoOut, PxmDataDrillInfoSimpleOut, PxmDataDrillInfoQueryParam,
    PxmDataDrillNodeCreate, PxmDataDrillNodeUpdate, PxmDataDrillNodeOut,
    DrillSQLValidateRequest, DrillSQLValidateResponse, DrillExecuteRequest, DrillExecuteResponse
)
from app.core.logger import log

class PxmDataDrillInfoService:
    
    @classmethod
    async def list_service(cls, auth: AuthSchema, page: int, size: int, search: PxmDataDrillInfoQueryParam):
        crud = PxmDataDrillInfoCRUD(auth)
        search_dict = search.__dict__ if search else {}
        # Filter out "None" or empty values which are not intended for search
        # PxmDataDrillInfoQueryParam uses ("like", val) tuples
        clean_search = {}
        for k, v in search_dict.items():
            if isinstance(v, tuple) and v[1] is None:
                continue
            if v is None:
                continue
            clean_search[k] = v

        return await crud.page(
            offset=(page-1)*size, 
            limit=size, 
            search=clean_search, 
            order_by=[{'id': 'desc'}], 
            out_schema=PxmDataDrillInfoSimpleOut
        )

    @classmethod
    async def create_service(cls, auth: AuthSchema, data: PxmDataDrillInfoCreate):
        crud = PxmDataDrillInfoCRUD(auth)
        # Note: data.nodes logic needs to be handled if we support nested create.
        # For now, we assume standard create.
        # If nodes are present, we might need manual handling or rely on SQLAlchemy relationship cascade if Pydantic supports it.
        # But CRUDBase.create expects data to be Schema or Dict.
        # If we pass nested dicts and SA model has relationship, it might work if configured correctly.
        # However, for simplicity, we let the user create Info first, then Nodes.
        obj = await crud.create(data=data)
        return PxmDataDrillInfoOut.model_validate(obj)

    @classmethod
    async def update_service(cls, auth: AuthSchema, id: int, data: PxmDataDrillInfoUpdate):
        crud = PxmDataDrillInfoCRUD(auth)
        obj = await crud.update(id=id, data=data)
        return PxmDataDrillInfoOut.model_validate(obj)

    @classmethod
    async def delete_service(cls, auth: AuthSchema, ids: list[int]):
        crud = PxmDataDrillInfoCRUD(auth)
        await crud.delete(ids=ids)

    @classmethod
    async def detail_service(cls, auth: AuthSchema, id: int):
        crud = PxmDataDrillInfoCRUD(auth)
        obj = await crud.get_with_nodes(id)
        if not obj:
            raise CustomException(msg="报表不存在")
        return PxmDataDrillInfoOut.model_validate(obj).model_dump()

class PxmDataDrillNodeService:
    @classmethod
    async def create_service(cls, auth: AuthSchema, data: PxmDataDrillNodeCreate):
        crud = PxmDataDrillNodeCRUD(auth)
        obj = await crud.create(data=data)
        return PxmDataDrillNodeOut.model_validate(obj).model_dump()
    
    @classmethod
    async def update_service(cls, auth: AuthSchema, id: int, data: PxmDataDrillNodeUpdate):
        crud = PxmDataDrillNodeCRUD(auth)
        obj = await crud.update(id=id, data=data)
        return PxmDataDrillNodeOut.model_validate(obj).model_dump()
    
    @classmethod
    async def delete_service(cls, auth: AuthSchema, ids: list[int]):
        crud = PxmDataDrillNodeCRUD(auth)
        await crud.delete(ids=ids)
    
    @classmethod
    async def get_children_service(cls, auth: AuthSchema, parent_id: int):
        crud = PxmDataDrillNodeCRUD(auth)
        objs = await crud.get_children(parent_id)
        return [PxmDataDrillNodeOut.model_validate(obj).model_dump() for obj in objs]

class DrillService:
    @classmethod
    async def validate_sql(cls, auth: AuthSchema, data: DrillSQLValidateRequest) -> DrillSQLValidateResponse:
        sql = data.sql_text.strip()
        
        # 1. Regex Checks
        if not re.match(r'^\s*SELECT\b', sql, re.IGNORECASE):
            return DrillSQLValidateResponse(valid=False, message="仅允许执行 SELECT 查询语句")
        
        forbidden_keywords = [
            r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b', r'\bALTER\b', 
            r'\bTRUNCATE\b', r'\bGRANT\b', r'\bEXEC\b', r'\bEXECUTE\b'
        ]
        for keyword in forbidden_keywords:
            if re.search(keyword, sql, re.IGNORECASE):
                # Clean display of keyword
                display_kw = keyword.replace(r'\b', '')
                return DrillSQLValidateResponse(valid=False, message=f"检测到禁止的关键字: {display_kw}")

        # 2. Execution Check & Column Extraction
        try:
            # Run with LIMIT 0 to get columns
            # Note: We must handle potential parameters if the SQL has them?
            # The validation SQL usually shouldn't have unbound parameters OR we need to provide dummy values.
            # If the user writes `SELECT * FROM table WHERE id = :id`, this will fail without params.
            # We can try to regex find params and bind None or 0?
            # Or we expect the user to provide a "Test Param" in the UI?
            # For now, we wrap it. If it fails due to params, we catch it.
            # Strategy: We can't easily guess params.
            # We will tell the user "Valid SQL structure, but execution failed (possibly due to missing params)".
            # But we NEED columns.
            # If we cannot run it, we cannot get columns.
            # Solution: We ask the user to provide test params? 
            # OR we try to parse it with SQLAlchemy text(sql).compile().params?
            
            # Simple approach: Try to execute. If param error, return valid=False with hint.
            # Better: Use `EXPLAIN`? No, result keys are needed.
            
            # Hack: If we encounter param errors, we might not get columns.
            # Let's try to run it.
            
            # IMPORTANT: The user requirement says "Select query field... source from parent".
            # This implies we validate the PARENT SQL. Parent SQL usually has NO params (Root) or has params from *its* parent.
            # Root SQL has no params. Child SQL has params.
            # When validating Child SQL, we need params.
            # Ideally, the validation UI allows inputting test params.
            # For now, I will assume simple execution.
            
            check_sql = f"SELECT * FROM ({sql}) t LIMIT 0"
            # We use a transaction that rolls back to be safe, though it's a SELECT.
            # But auth.db is async session.
            
            # We need to handle ":param" style.
            # If the SQL contains `:`, SQLAlchemy expects params.
            # We can try to inspect params using `text(sql).compile(dialect=...).params`?
            # Or just pass empty dict and catch "missing param".
            
            result = await auth.db.execute(text(check_sql))
            columns = list(result.keys())
            return DrillSQLValidateResponse(valid=True, message="校验通过", columns=columns)
        except Exception as e:
             err_msg = str(e)
             if "bind parameter" in err_msg.lower() or "parameter" in err_msg.lower():
                 return DrillSQLValidateResponse(valid=False, message=f"SQL包含参数，无法自动校验列结构。请确保SQL语法正确。错误: {err_msg}")
             return DrillSQLValidateResponse(valid=False, message=f"SQL执行失败: {err_msg}")

    @classmethod
    async def execute_drill(cls, auth: AuthSchema, data: DrillExecuteRequest) -> DrillExecuteResponse:
        node_crud = PxmDataDrillNodeCRUD(auth)
        node = await node_crud.get(id=data.node_id)
        if not node:
             raise CustomException(msg="节点不存在")
        
        if not node.sql_text:
             raise CustomException(msg="该节点未配置SQL")

        base_sql = node.sql_text
        
        # Check if we need to auto-inject WHERE clause
        # If param_name is defined, present in params, and NOT used as a placeholder in base_sql
        inject_filter = False
        if node.param_name and data.params and node.param_name in data.params:
            if f":{node.param_name}" not in base_sql:
                inject_filter = True
        
        # Construct the base source for count and data queries
        # We wrap the original SQL in a subquery to ensure we can filter its results
        source_sql = f"({base_sql}) t_source"
        
        if inject_filter:
            # Auto-inject filtering: WHERE column = :param
            # Note: We assume node.param_name corresponds to a column in the result set
            source_sql = f"(SELECT * FROM {source_sql} WHERE {node.param_name} = :{node.param_name}) t_filtered"
        
        # Count Query
        count_sql = f"SELECT COUNT(*) FROM {source_sql}"
        
        # Data Query
        offset = (data.page_no - 1) * data.page_size
        data_sql = f"SELECT * FROM {source_sql} LIMIT {data.page_size} OFFSET {offset}"
        
        try:
            # Bind params
            params = data.params or {}
            
            # Count
            count_res = await auth.db.execute(text(count_sql), params)
            total = count_res.scalar()
            
            # Data
            data_res = await auth.db.execute(text(data_sql), params)
            columns = list(data_res.keys())
            rows = [dict(zip(columns, row)) for row in data_res.fetchall()]
            
            return DrillExecuteResponse(columns=columns, data=rows, total=total)
            
        except Exception as e:
            log.error(f"Drill execution error: {e}")
            raise CustomException(msg=f"查询执行失败: {str(e)}")
