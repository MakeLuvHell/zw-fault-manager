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
        from sqlglot import parse_one, exp
        
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
            # Parse SQL
            parsed = parse_one(sql)
            
            # Extract bind parameters
            # Look for explicit binds :param or $param which often appear as Identifier/Parameter in sqlglot depending on dialect
            # We look for nodes that start with ':'
            # Note: sqlglot might parse :param as a Parameter node or Identifier
            params = set()
            for node in parsed.find_all(exp.Parameter, exp.Placeholder, exp.Identifier):
                if isinstance(node, exp.Parameter):
                     # Key is usually the name inside
                     val = node.this
                     if val: params.add(str(val))
                elif isinstance(node, exp.Placeholder):
                     val = node.this
                     if val: params.add(str(val))
                # For basic :param syntax, sqlglot often parses as Identifier with quoted=False? 
                # Actually, standard SQLGlot parsing of ":param" depends on read dialect.
                # Assuming standard SQL or Postgres.
            
            # A more robust way using Regex for params since SQL dialects vary on bind syntax
            # and sqlglot might need specific read dialect.
            # We use a simple regex to find :param_name to be safe and consistent with SQLAlchemy
            found_params = re.findall(r':([a-zA-Z_][a-zA-Z0-9_]*)', sql)
            params = list(set(found_params))
            
            # Transform: Remove WHERE clause
            def remove_where(node):
                if isinstance(node, exp.Where):
                    return None
                return node
            
            clean_expression = parsed.transform(remove_where)
            clean_sql = clean_expression.sql()
            
            check_sql = f"SELECT * FROM ({clean_sql}) t LIMIT 0"
            
            result = await auth.db.execute(text(check_sql))
            columns = list(result.keys())
            return DrillSQLValidateResponse(valid=True, message="校验通过", columns=columns, params=params)
        except Exception as e:
             err_msg = str(e)
             return DrillSQLValidateResponse(valid=False, message=f"SQL校验失败: {err_msg}")

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
