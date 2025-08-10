from httpx import AsyncClient

from app.models.user import User


class TestUsersAPI:
    async def test_create_user(self, client: AsyncClient):
        user_data = {
            "username": "newuser",
            "password": "newpassword",
            "group": "newgroup"
        }
        
        response = await client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["group"] == "newgroup"
        assert "id" in data
        assert "hashed_password" not in data
    
    async def test_create_user_duplicate_username(self, client: AsyncClient, test_user: User):
        user_data = {
            "username": test_user.username,
            "password": "password",
            "group": "group"
        }
        
        response = await client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    async def test_create_user_invalid_data(self, client: AsyncClient):
        user_data = {
            "username": "",  # Invalid empty username
            "password": "password"
            # Missing required group
        }
        
        response = await client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 422
    
    async def test_get_users(self, client: AsyncClient, auth_headers: dict, test_user: User):
        response = await client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(user["username"] == test_user.username for user in data)
    
    async def test_get_users_with_pagination(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(
            "/api/v1/users/", 
            headers=auth_headers,
            params={"skip": 0, "limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    async def test_get_user_by_id(self, client: AsyncClient, auth_headers: dict, test_user: User):
        response = await client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["group"] == test_user.group
    
    async def test_get_user_by_id_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/users/9999", headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
    
    async def test_update_user(self, client: AsyncClient, auth_headers: dict, test_user: User):
        update_data = {
            "group": "updated_group"
        }
        
        response = await client.put(
            f"/api/v1/users/{test_user.id}", 
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["group"] == "updated_group"
        assert data["username"] == test_user.username  
    
    async def test_update_user_not_found(self, client: AsyncClient, auth_headers: dict):
        update_data = {"group": "new_group"}
        
        response = await client.put(
            "/api/v1/users/9999", 
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
    
    async def test_delete_user(self, client: AsyncClient, auth_headers: dict):
        user_data = {
            "username": "to_delete",
            "password": "password",
            "group": "group"
        }
        create_response = await client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["id"]
        
        response = await client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        
        get_response = await client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    async def test_delete_user_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.delete("/api/v1/users/9999", headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"