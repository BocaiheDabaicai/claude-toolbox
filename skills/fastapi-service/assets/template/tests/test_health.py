async def test_healthz(client):
    response = await client.get("/api/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_readyz_ok(client, monkeypatch):
    async def fake_check() -> None:
        return None

    monkeypatch.setattr(
        "app.modules.health.router.check_database",
        fake_check,
    )

    response = await client.get("/api/readyz")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


async def test_readyz_down(client, monkeypatch):
    async def fake_check() -> None:
        raise RuntimeError("database down")

    monkeypatch.setattr(
        "app.modules.health.router.check_database",
        fake_check,
    )

    response = await client.get("/api/readyz")

    assert response.status_code == 503
    assert response.json()["status"] == "not-ready"
