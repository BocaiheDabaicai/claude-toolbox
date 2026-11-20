from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ApiError
from app.db.models import Customer
from app.modules.customers import repository
from app.modules.customers.schemas import CustomerInput


async def list_customers(
    session: AsyncSession,
    *,
    page: int,
    page_size: int,
    search: str,
) -> tuple[list[Customer], int]:
    return await repository.list_customers(
        session,
        page=page,
        page_size=page_size,
        search=search,
    )


async def get_customer(
    session: AsyncSession,
    customer_id: int,
) -> Customer:
    customer = await repository.get_customer(session, customer_id)
    if not customer:
        raise ApiError(404, "客户不存在")
    return customer


async def create_customer(
    session: AsyncSession,
    data: CustomerInput,
) -> Customer:
    return await repository.create_customer(session, data)


async def update_customer(
    session: AsyncSession,
    customer_id: int,
    data: CustomerInput,
) -> Customer:
    customer = await get_customer(session, customer_id)
    return await repository.update_customer(session, customer, data)


async def delete_customer(
    session: AsyncSession,
    customer_id: int,
) -> None:
    customer = await get_customer(session, customer_id)
    await repository.delete_customer(session, customer)
