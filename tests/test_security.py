from ragoo.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    password = "secret"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_flow():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert decoded["sub"] == "testuser"


def test_invalid_jwt():
    assert decode_token("invalid.token.here") is None
