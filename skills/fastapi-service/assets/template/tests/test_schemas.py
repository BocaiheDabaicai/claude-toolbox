from datetime import UTC, datetime

from app.modules.customers.schemas import CustomerInput, CustomerOut


def test_customer_output_uses_camel_case_aliases():
    now = datetime.now(UTC)
    customer = CustomerOut.model_validate(
        {
            "id": 1,
            "name": "张明",
            "phone": "13800000001",
            "email": None,
            "company": None,
            "note": None,
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "deleted_at": None,
        }
    )

    data = customer.model_dump(by_alias=True)

    assert data["createdAt"] == now
    assert data["updatedAt"] == now
    assert data["deletedAt"] is None
    assert "created_at" not in data


def test_customer_input_normalizes_empty_strings():
    data = CustomerInput(
        name="  张明  ",
        phone="  ",
        email="",
        company="  ",
        note=" 备注 ",
    )

    assert data.name == "张明"
    assert data.phone is None
    assert data.email is None
    assert data.company is None
    assert data.note == "备注"
    assert data.status == "active"
