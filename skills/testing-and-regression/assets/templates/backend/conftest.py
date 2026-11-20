"""FastAPI 测试客户端示例。

已有 fastapi-service 模板的项目可以直接使用；其他项目按需调整。
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-0123456789-0123456789")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/test",
)
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
