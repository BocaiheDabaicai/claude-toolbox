import pytest

from app.core.errors import ApiError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_roundtrip():
    hashed = hash_password("correct-horse-battery-staple")

    assert hashed != "correct-horse-battery-staple"
    assert verify_password("correct-horse-battery-staple", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_roundtrip():
    token = create_access_token(subject="1", email="admin@example.com", role="admin")
    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert payload["email"] == "admin@example.com"
    assert payload["role"] == "admin"


def test_invalid_token_raises_api_error():
    with pytest.raises(ApiError) as exc_info:
        decode_access_token("not-a-token")

    assert exc_info.value.code == 401
