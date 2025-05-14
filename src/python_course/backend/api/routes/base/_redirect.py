from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

docs_router = APIRouter()


@docs_router.get(
    "/",
    tags=["Redirect"],
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_class=RedirectResponse,
    summary="首頁重導向至 API 文件",
)
async def redirect_to_docs() -> str:
    """首頁重導向至 API 文件"""
    return "/docs"
