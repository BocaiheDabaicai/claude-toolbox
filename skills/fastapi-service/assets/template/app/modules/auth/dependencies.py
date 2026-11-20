from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ApiError
from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_session


def extract_token(
    access_token: Annotated[str | None, Header(alias="Access-Token")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    if access_token:
        return access_token
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    raise ApiError(401, "请先登录")


async def get_current_user(
    token: Annotated[str, Depends(extract_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    payload = decode_access_token(token)
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ApiError(401, "登录凭证无效") from exc

    user = await session.get(User, user_id)
    if not user or user.status != "active":
        raise ApiError(401, "账号不存在或已停用")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
