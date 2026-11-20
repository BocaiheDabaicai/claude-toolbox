from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.customers.router import router as customers_router
from app.modules.health.router import router as health_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(customers_router, prefix="/customers", tags=["customers"])
