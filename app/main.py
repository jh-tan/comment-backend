import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config.settings import settings
from app.core.middleware import RequestLoggingMiddleware
from app.core.exceptions import setup_exception_handlers
from app.graphql_api.schema import graphql_app
from app.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logging.info("Starting the system")

    yield

    logging.info("Shutting down the system")


def create_application() -> FastAPI:
    
    app = FastAPI(
        title = settings.PROJECT_NAME,
        description="Test description",
        version="1.0.0",
        lifespan=lifespan,
    )


    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
    
    app.add_middleware(RequestLoggingMiddleware)

    setup_exception_handlers(app)

    app.include_router(api_router, prefix=settings.API_V1_STR)
    app.include_router(graphql_app, prefix="/graphql")

    return app

app = create_application()

@app.get("/")
def healthcheck():
    logging.info(settings.DATABASE_URL)
    return {"message": "Server is healthy"}
