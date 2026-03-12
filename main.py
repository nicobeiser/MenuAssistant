from fastapi import FastAPI
from core.lifespan import lifespan
from core.middleware import setup_middleware
from routers import metrics, chat, image
from routers.test_router import router as test_router
from fastapi.staticfiles import StaticFiles


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    setup_middleware(app)


    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.include_router(metrics.router)
    app.include_router(chat.router)
    app.include_router(image.router)
    app.include_router(test_router)

    return app

app = create_app()