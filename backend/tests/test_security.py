from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)


def test_password_hashing() -> None:
    """Verifies that password hashing generates secure, validatable hashes."""
    password = "supersecretpassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_tokens() -> None:
    """Verifies that access and refresh tokens generate correct structures and validate properly."""
    subject = "550e8400-e29b-41d4-a716-446655440000"

    # Access Token
    access = create_access_token(subject)
    payload = verify_token(access)
    assert payload is not None
    assert payload.get("sub") == subject
    assert payload.get("type") == "access"

    # Refresh Token
    refresh = create_refresh_token(subject)
    payload_refresh = verify_token(refresh)
    assert payload_refresh is not None
    assert payload_refresh.get("sub") == subject
    assert payload_refresh.get("type") == "refresh"

    # Invalid Token
    assert verify_token("invalid.token.signature") is None
