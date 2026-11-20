async def test_openapi_contains_main_routes(client):
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/healthz" in paths
    assert "/api/auth/login" in paths
    assert "/api/customers" in paths
    assert "/api/customers/{customer_id}" in paths
