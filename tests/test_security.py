import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.security import (
    create_access_token,
    verify_token,
    verify_password,
    get_password_hash
)
from app.config.settings import settings


class TestSecurity:
    def test_password_hashing(self):
        password = "test_password_123"
        
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_create_access_token(self):
        username = "testuser"
        
        token = create_access_token(username)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == username
        assert "exp" in payload
    
    def test_create_access_token_with_expiration(self):
        username = "testuser"
        expires_delta = timedelta(minutes=15)
        
        token = create_access_token(username, expires_delta=expires_delta)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        expected_exp = datetime.now(timezone.utc) + expires_delta
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 60
    
    def test_verify_token_valid(self):
        username = "testuser"
        token = create_access_token(username)
        
        payload = verify_token(token)
        
        assert payload["sub"] == username
        assert "exp" in payload
    
    def test_verify_token_invalid(self):
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):
            verify_token(invalid_token)
    
    def test_verify_token_expired(self):
        username = "testuser"
        
        expired_token = create_access_token(
            username, 
            expires_delta=timedelta(seconds=-1)
        )
        
        with pytest.raises(Exception):
            verify_token(expired_token)
    
    def test_verify_token_wrong_secret(self):
        username = "testuser"
        
        wrong_secret_token = jwt.encode(
            {"sub": username, "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
            "wrong_secret",
            algorithm="HS256"
        )
        
        with pytest.raises(Exception):
            verify_token(wrong_secret_token)
    
    def test_password_hash_uniqueness(self):
        password = "same_password"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_password_verification_case_sensitive(self):
        password = "CaseSensitivePassword"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password(password.lower(), hashed) is False
        assert verify_password(password.upper(), hashed) is False
    
    def test_empty_password_handling(self):
        empty_password = ""
        hashed = get_password_hash(empty_password)
        
        assert verify_password(empty_password, hashed) is True
        assert verify_password("not_empty", hashed) is False
    
    def test_special_characters_in_password(self):
        password = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("different_special_chars", hashed) is False
    
    def test_unicode_password(self):
        password = "пароль_测试_🔐"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("different_unicode", hashed) is False