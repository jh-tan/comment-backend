from httpx import AsyncClient

from app.models.user import User


class TestAuthAPI:
    async def test_login_success(self, client: AsyncClient, test_user: User):
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.username,
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_wrong_username(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "wronguser",
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"
    
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.username,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"
    
    async def test_login_missing_credentials(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", data={})
        
        assert response.status_code == 422
    
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        response = await client.get("/api/v1/users/")
        
        assert response.status_code == 403
    
    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/users/", headers=headers)
        
        assert response.status_code == 401
    
    async def test_protected_endpoint_with_valid_token(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == 200