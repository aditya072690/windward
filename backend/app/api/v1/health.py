from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready():
    try:
        from ...repository.db import get_conn

        conn = get_conn()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "detail": str(e)}
