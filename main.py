from fastapi import FastAPI
from core.lifespan import lifespan
from core.middleware import setup_middleware
from routers import metrics, chat, image


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    setup_middleware(app)

    app.include_router(metrics.router)
    app.include_router(chat.router)
    app.include_router(image.router)

    return app

app = create_app()