import asyncio
import sys

from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.models import Customer, User
from app.db.session import SessionLocal, engine


async def main() -> None:
    settings = get_settings()
    email = settings.seed_admin_email.strip().lower()
    password = settings.seed_admin_password
    name = settings.seed_admin_name.strip() or "管理员"

    if not email or len(password) < 8:
        raise SystemExit(
            "请在 .env 中配置 SEED_ADMIN_EMAIL 和至少 8 位的 SEED_ADMIN_PASSWORD"
        )

    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == email))
        if user:
            user.name = name
            user.password_hash = hash_password(password)
            user.role = "admin"
            user.status = "active"
            print(f"[seed] 已更新管理员 {email}")
        else:
            session.add(
                User(
                    email=email,
                    name=name,
                    password_hash=hash_password(password),
                    role="admin",
                    status="active",
                )
            )
            print(f"[seed] 已创建管理员 {email}")

        count = await session.scalar(select(func.count(Customer.id))) or 0
        if count == 0:
            session.add_all(
                [
                    Customer(
                        name="张明",
                        phone="13800000001",
                        email="zhangming@example.com",
                        company="远山科技",
                        status="active",
                        note="示例数据，可直接删除。",
                    ),
                    Customer(
                        name="李静",
                        phone="13800000002",
                        email="lijing@example.com",
                        company="青禾贸易",
                        status="active",
                    ),
                    Customer(
                        name="王强",
                        phone="13800000003",
                        company="恒信物流",
                        status="inactive",
                    ),
                ]
            )
            print("[seed] 已插入 3 条示例客户")
        else:
            print(f"[seed] 已有 {count} 条客户，跳过示例数据")

        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError, OSError):
                pass
    asyncio.run(main())
