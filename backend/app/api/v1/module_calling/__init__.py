# -*- coding: utf-8 -*-
"""外呼模块 API 路由"""
from fastapi import APIRouter

from .task.controller import CallingTaskRouter, MetadataRouter

calling_router = APIRouter(prefix="/calling")

calling_router.include_router(CallingTaskRouter)
calling_router.include_router(MetadataRouter)
