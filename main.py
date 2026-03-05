from fastapi import FastAPI
from core.lifespan import lifespan
from core.middleware import setup_middleware
from routers import frontend, metrics, chat, image
from core.config import FRONTEND_DIR, DASHBOARD_DIR
from fastapi.staticfiles import StaticFiles
from orders import router as orders_router


def create_app() -> FastAPI:
    # Configuraciones
    app = FastAPI(lifespan=lifespan)
    setup_middleware(app)

    # Montados estaticos
    app.mount("/chat/static", StaticFiles(directory=str(FRONTEND_DIR)), name="chat-static")
    app.mount("/dashboard/static", StaticFiles(directory=str(DASHBOARD_DIR)), name="dashboard-static")

    # Rutas
    app.include_router(frontend.router)
    app.include_router(metrics.router)
    app.include_router(chat.router)
    app.include_router(image.router)
    app.include_router(orders_router)

    return app

app = create_app()