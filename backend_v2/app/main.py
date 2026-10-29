from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api.v1.router import api_router
from .config import settings
from .services.data_service import ds
import threading


@asynccontextmanager
async def lifespan(app: FastAPI):
    def _warm():
        try:
            ds.warm()
            print("[warm] done")
        except Exception as e:
            print("[warm] err", e)
    t = threading.Thread(target=_warm, daemon=True)
    t.start()
    yield


app = FastAPI(title="Windward API v2", version="0.1.0", lifespan=lifespan)

origins = settings.cors_origins_list()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    try:
        if ds._actuals_cache is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="warming")
        return {"status": "ready"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/v1/health")
def health_v1():
    return {"status": "ok"}


@app.get("/api/v1/ready")
def ready_v1():
    try:
        if ds._actuals_cache is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="warming")
        return {"status": "ready"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=str(e))
