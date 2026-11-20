from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Customer
from app.modules.customers.schemas import CustomerInput


async def list_customers(
    session: AsyncSession,
    *,
    page: int,
    page_size: int,
    search: str,
) -> tuple[list[Customer], int]:
    conditions = [Customer.deleted_at.is_(None)]
    if search:
        like = f"%{search}%"
        conditions.append(
            or_(
                Customer.name.ilike(like),
                Customer.phone.ilike(like),
                Customer.company.ilike(like),
            )
        )

    total = await session.scalar(
        select(func.count(Customer.id)).where(*conditions)
    ) or 0

    result = await session.execute(
        select(Customer)
        .where(*conditions)
        .order_by(Customer.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(result.scalars().all()), total


async def get_customer(
    session: AsyncSession,
    customer_id: int,
) -> Customer | None:
    result = await session.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def create_customer(
    session: AsyncSession,
    data: CustomerInput,
) -> Customer:
    customer = Customer(**data.model_dump())
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer


async def update_customer(
    session: AsyncSession,
    customer: Customer,
    data: CustomerInput,
) -> Customer:
    for field, value in data.model_dump().items():
        setattr(customer, field, value)
    await session.commit()
    await session.refresh(customer)
    return customer


async def delete_customer(
    session: AsyncSession,
    customer: Customer,
) -> None:
    customer.deleted_at = datetime.now(UTC)
    await session.commit()
