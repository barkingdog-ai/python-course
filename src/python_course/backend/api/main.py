"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from python_course import __version__
from python_course.backend.api.routes import add_router

_DESCRIPTION = """API Document

[Swagger](./docs) / [ReDoc](./redoc)
"""


app = FastAPI(
    title="My Server",
    description=_DESCRIPTION,
    version=__version__,
    default_response_class=ORJSONResponse,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

add_router(app)
