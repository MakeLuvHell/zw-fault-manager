# -*- coding: utf-8 -*-

import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.logger import log
from app.config.setting import settings


async def create_schema_if_not_exists(engine: AsyncEngine, schema_name: str = None) -> bool:
    """
    如果 schema 不存在，则创建它
    
    参数:
        engine: 异步数据库引擎
        schema_name: schema 名称，默认为 settings.DATABASE_SCHEMA
        
    返回:
        bool: 是否成功创建或已存在
    """
    # 只有 PostgreSQL 需要 schema
    if settings.DATABASE_TYPE != "postgres":
        return True
        
    if schema_name is None:
        schema_name = settings.DATABASE_SCHEMA
    
    try:
        # 使用 connect() 获取连接，并手动 commit
        async with engine.connect() as conn:
            # 检查 schema 是否存在
            check_schema_sql = text(
                "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = :schema_name)"
            )
            result = await conn.execute(check_schema_sql, {"schema_name": schema_name})
            schema_exists = result.scalar()
            
            if not schema_exists:
                # 创建 schema
                create_schema_sql = text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                await conn.execute(create_schema_sql)
                await conn.commit() # 手动提交事务
                log.info(f"✅ 已成功创建 PostgreSQL schema: {schema_name}")
                return True
            else:
                log.info(f"✅ PostgreSQL schema 已存在: {schema_name}")
                return True
                
    except SQLAlchemyError as e:
        log.error(f"❌ 创建或检查 PostgreSQL schema 失败: {e}")
        return False


async def set_default_schema(engine: AsyncEngine) -> bool:
    """
    设置默认 schema
    
    参数:
        engine: 异步数据库引擎
        
    返回:
        bool: 是否成功设置
    """
    # 只有 PostgreSQL 需要 schema
    if settings.DATABASE_TYPE != "postgres":
        return True
        
    schema_name = settings.DATABASE_SCHEMA
    
    try:
        async with engine.begin() as conn:
            # 设置 search_path 到指定 schema
            set_path_sql = text(f"SET search_path TO {schema_name}, public")
            await conn.execute(set_path_sql)
            log.info(f"✅ 已设置默认 schema 为: {schema_name}")
            return True
            
    except SQLAlchemyError as e:
        log.error(f"❌ 设置默认 schema 失败: {e}")
        return False