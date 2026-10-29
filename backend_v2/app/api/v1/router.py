from fastapi import APIRouter
from . import meta, health, decision, accuracy

api_router = APIRouter()
api_router.include_router(meta.router)
api_router.include_router(health.router)
api_router.include_router(decision.router)
api_router.include_router(accuracy.router)
