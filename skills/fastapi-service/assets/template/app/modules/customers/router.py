from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import ApiResponse, Page, ok
from app.db.session import get_session
from app.modules.auth.dependencies import CurrentUser
from app.modules.customers import service
from app.modules.customers.schemas import CustomerInput, CustomerOut

router = APIRouter()


@router.get(
    "",
    response_model=ApiResponse[Page[CustomerOut]],
    response_model_by_alias=True,
)
async def list_customers(
    session: Annotated[AsyncSession, Depends(get_session)],
    _user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    search: Annotated[str, Query(max_length=100)] = "",
):
    rows, total = await service.list_customers(
        session,
        page=page,
        page_size=page_size,
        search=search.strip(),
    )
    return ok(
        Page(
            rows=[CustomerOut.model_validate(row) for row in rows],
            total=total,
            page=page,
            pageSize=page_size,
        )
    )


@router.get(
    "/{customer_id}",
    response_model=ApiResponse[CustomerOut],
    response_model_by_alias=True,
)
async def get_customer(
    session: Annotated[AsyncSession, Depends(get_session)],
    _user: CurrentUser,
    customer_id: Annotated[int, Path(ge=1)],
):
    customer = await service.get_customer(session, customer_id)
    return ok(CustomerOut.model_validate(customer))


@router.post(
    "",
    response_model=ApiResponse[CustomerOut],
    response_model_by_alias=True,
)
async def create_customer(
    data: CustomerInput,
    session: Annotated[AsyncSession, Depends(get_session)],
    _user: CurrentUser,
):
    customer = await service.create_customer(session, data)
    return ok(CustomerOut.model_validate(customer))


@router.put(
    "/{customer_id}",
    response_model=ApiResponse[CustomerOut],
    response_model_by_alias=True,
)
async def update_customer(
    data: CustomerInput,
    session: Annotated[AsyncSession, Depends(get_session)],
    _user: CurrentUser,
    customer_id: Annotated[int, Path(ge=1)],
):
    customer = await service.update_customer(session, customer_id, data)
    return ok(CustomerOut.model_validate(customer))


@router.delete("/{customer_id}", response_model=ApiResponse[dict])
async def delete_customer(
    session: Annotated[AsyncSession, Depends(get_session)],
    _user: CurrentUser,
    customer_id: Annotated[int, Path(ge=1)],
):
    await service.delete_customer(session, customer_id)
    return ok({"id": customer_id})
