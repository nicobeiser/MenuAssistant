from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from metrics.middleware import MetricsMiddleware

def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(MetricsMiddleware)