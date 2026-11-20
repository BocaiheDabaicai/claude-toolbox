from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ApiError
from app.core.security import create_access_token, verify_password
from app.db.models import User
from app.modules.auth.schemas import LoginRequest, TokenOut, UserOut


async def authenticate(
    session: AsyncSession,
    data: LoginRequest,
) -> TokenOut:
    email = str(data.email).lower()
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if (
        not user
        or user.status != "active"
        or not verify_password(data.password, user.password_hash)
    ):
        raise ApiError(401, "邮箱或密码不正确")

    token = create_access_token(
        subject=str(user.id),
        email=user.email,
        role=user.role,
    )
    return TokenOut(token=token, user=UserOut.model_validate(user))
