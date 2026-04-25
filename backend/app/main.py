from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.routers import auth_router, projects_router, tasks_router


def create_app() -> FastAPI:
    """Application factory. Centralizes app creation and configuration."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Domain exception → HTTP response mapping
    register_exception_handlers(app)

    # Health check
    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.APP_NAME}

    # API routers
    app.include_router(auth_router, prefix=settings.API_PREFIX)
    app.include_router(projects_router, prefix=settings.API_PREFIX)
    app.include_router(tasks_router, prefix=settings.API_PREFIX)

    return app


app = create_app()