"""Run Uvicorn server."""

import uvicorn

from python_course.core import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        app_dir="src",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=True,
    )
