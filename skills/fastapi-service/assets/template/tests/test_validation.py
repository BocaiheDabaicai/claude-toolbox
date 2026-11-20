async def test_login_validation_error_envelope(client):
    response = await client.post("/api/auth/login", json={})

    assert response.status_code == 400
    body = response.json()
    assert body["code"] == 400
    assert body["message"] == "请求参数不合法"
    assert body["data"] is None
    assert body["details"]


async def test_login_rejects_invalid_email(client):
    response = await client.post(
        "/api/auth/login",
        json={"email": "not-an-email", "password": "x"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == 400


async def test_customers_requires_token(client):
    response = await client.get("/api/customers")

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == 401
    assert body["data"] is None
