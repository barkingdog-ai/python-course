"""base router, 應該由根節點加入"""

from fastapi import APIRouter

from ._redirect import docs_router

base_router = APIRouter()
base_router.include_router(docs_router)
