from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.session import check_database

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "__PROJECT_NAME__"}


@router.get("/readyz")
async def readyz():
    try:
        await check_database()
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not-ready"})
    return {"status": "ready"}
