from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.v1 import health, meta, decision, accuracy, evolution, export

app = FastAPI(title="Windward API", version="0.1.0", openapi_url="/api/openapi.json", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(meta.router, prefix="/api/v1")
app.include_router(decision.router, prefix="/api/v1")
app.include_router(accuracy.router, prefix="/api/v1")
app.include_router(evolution.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")
