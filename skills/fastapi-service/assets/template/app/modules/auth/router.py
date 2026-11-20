from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import ApiResponse, ok
from app.db.session import get_session
from app.modules.auth.dependencies import CurrentUser
from app.modules.auth.schemas import LoginRequest, TokenOut, UserOut
from app.modules.auth.service import authenticate

router = APIRouter()


@router.post("/login", response_model=ApiResponse[TokenOut])
async def login(
    data: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return ok(await authenticate(session, data))


@router.get("/me", response_model=ApiResponse[UserOut])
async def me(user: CurrentUser):
    return ok(UserOut.model_validate(user))


@router.post("/logout", response_model=ApiResponse[dict])
async def logout():
    # JWT 无状态：服务端不维护会话，客户端删除 token 即可。
    return ok({})
