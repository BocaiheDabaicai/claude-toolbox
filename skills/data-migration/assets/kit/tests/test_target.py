from migration_kit.config import TargetConfig
from migration_kit.target import build_insert_sql


def test_build_upsert_sql():
    query = build_insert_sql(
        TargetConfig(dsn="postgresql://localhost/db", table="customers"),
        ["legacy_id", "name", "phone"],
        ("legacy_id",),
    )
    rendered = query.as_string(None)

    assert 'INSERT INTO "public"."customers"' in rendered
    assert 'VALUES (%s, %s, %s)' in rendered
    assert 'ON CONFLICT ("legacy_id")' in rendered
    assert '"name" = EXCLUDED."name"' in rendered
    assert '"phone" = EXCLUDED."phone"' in rendered


def test_build_insert_without_key():
    query = build_insert_sql(
        TargetConfig(dsn="postgresql://localhost/db", table="customers"),
        ["legacy_id", "name"],
        (),
    )
    rendered = query.as_string(None)

    assert "ON CONFLICT" not in rendered
