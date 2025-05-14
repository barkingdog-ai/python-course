from fastapi import APIRouter, FastAPI

from .base import base_router

root_router = APIRouter()


def add_router(app: FastAPI) -> None:
    """添加 http 路由"""
    root_router.include_router(base_router)
    app.include_router(root_router)
