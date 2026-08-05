from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import articles_router, health_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(articles_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "version": settings.app_version,
    }
