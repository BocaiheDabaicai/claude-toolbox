from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("TARGET_DSN", "postgresql://user:secret@localhost:5432/app_test")

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "customers.csv").write_text(
        "id,name,phone,email,company,status\n"
        "1,张明,13800000001,ZhangMing@Example.com,远山科技,ACTIVE\n"
        "2,李静,138-0000-0002,,青禾贸易,ACTIVE\n"
        "3,王强,,,恒信物流,INACTIVE\n",
        encoding="utf-8",
    )

    (tmp_path / "mapping.csv").write_text(
        "target_column,source_column,target_type,required,default,transform\n"
        "legacy_id,id,bigint,true,,trim\n"
        "name,name,text,true,,trim\n"
        "phone,phone,text,false,,digits\n"
        "email,email,text,false,,lower\n"
        "company,company,text,false,,trim\n"
        "status,status,text,true,active,lower\n",
        encoding="utf-8",
    )

    (tmp_path / "transforms.py").write_text(
        "def normalize_company(value, row):\n"
        "    if value is None:\n"
        "        return None\n"
        "    return str(value).strip()\n"
        "\n"
        "TRANSFORMS = {'normalize_company': normalize_company}\n",
        encoding="utf-8",
    )

    (tmp_path / "migration.toml").write_text(
        """
[source]
type = "csv"
path = "data/customers.csv"

[target]
dsn = "${TARGET_DSN}"
schema = "public"
table = "customers"

[mapping]
file = "mapping.csv"
transform_module = "transforms"

[run]
batch_size = 2
key = ["legacy_id"]
state_file = ".migration-state.json"
sample_limit = 2
on_error = "stop"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    return tmp_path
