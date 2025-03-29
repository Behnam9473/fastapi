import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from jose import jwt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_access_token,
    get_current_user,
    get_current_manager,
    SECRET_KEY,
    ALGORITHM
)

@pytest.fixture
def test_user_data():
    return {
        "sub": "testuser",
        "id": 1,
        "role": "CUSTOMER",
        "tenant_id": None
    }

@pytest.fixture
def test_manager_data():
    return {
        "sub": "testmanager",
        "id": 2,
        "role": "MANAGER",
        "tenant_id": "123e4567-e89b-12d3-a456-426614174000"
    }

def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_create_access_token(test_user_data):
    token = create_access_token(test_user_data)
    assert token is not None
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == test_user_data["sub"]
    assert decoded["id"] == test_user_data["id"]
    assert decoded["role"] == test_user_data["role"]

def test_create_access_token_with_expiration(test_user_data):
    expires_delta = timedelta(minutes=15)
    token = create_access_token(test_user_data, expires_delta)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in decoded

def test_verify_access_token(test_user_data):
    token = create_access_token(test_user_data)
    payload = verify_access_token(token)
    assert payload["sub"] == test_user_data["sub"]
    assert payload["id"] == test_user_data["id"]

def test_verify_invalid_token():
    invalid_token = "invalid.token.here"
    assert verify_access_token(invalid_token) is None

@pytest.mark.asyncio
async def test_get_current_user(test_user_data):
    token = create_access_token(test_user_data)
    user = await get_current_user(token)
    assert user["username"] == test_user_data["sub"]
    assert user["user_id"] == test_user_data["id"]
    assert user["role"] == test_user_data["role"]

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid.token.here")
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_manager(test_manager_data):
    token = create_access_token(test_manager_data)
    manager = await get_current_manager(token)
    assert manager["username"] == test_manager_data["sub"]
    assert manager["user_id"] == test_manager_data["id"]
    assert manager["tenant_id"] == test_manager_data["tenant_id"]
    assert manager["role"] == test_manager_data["role"]

@pytest.mark.asyncio
async def test_get_current_manager_invalid_token():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_manager("invalid.token.here")
    assert exc_info.value.status_code == 401

def test_expired_token(test_user_data):
    expires_delta = timedelta(seconds=-1)  # Already expired
    token = create_access_token(test_user_data, expires_delta)
    assert verify_access_token(token) is None

def test_token_without_required_fields():
    # Test each required field is validated
    required_fields = {
        "missing sub": {"id": 1, "role": "CUSTOMER"},
        "missing id": {"sub": "testuser", "role": "CUSTOMER"},
        "missing role": {"sub": "testuser", "id": 1}
    }
    
    for test_case, incomplete_data in required_fields.items():
        with pytest.raises(HTTPException) as exc_info:
            create_access_token(incomplete_data)
        assert exc_info.value.status_code == 422
        assert "Missing required field" in exc_info.value.detail