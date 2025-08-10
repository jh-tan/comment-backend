from httpx import AsyncClient

from app.models.comment import Comment


class TestCommentsAPI:
    async def test_create_comment(self, client: AsyncClient, auth_headers: dict):
        comment_data = {
            "content": "This is a test comment"
        }
        
        response = await client.post(
            "/api/v1/comments/", 
            json=comment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "This is a test comment"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
    
    async def test_create_comment_invalid_data(self, client: AsyncClient, auth_headers: dict):
        comment_data = {}  # Missing required content
        
        response = await client.post(
            "/api/v1/comments/", 
            json=comment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    async def test_create_comment_without_auth(self, client: AsyncClient):
        comment_data = {
            "content": "This is a test comment"
        }
        
        response = await client.post("/api/v1/comments/", json=comment_data)
        
        assert response.status_code == 403
    
    async def test_get_comments_by_user_group(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        response = await client.get("/api/v1/comments/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(comment["id"] == test_comment.id for comment in data)
    
    async def test_get_comments_different_group(self, client: AsyncClient, auth_headers_2: dict, test_comment: Comment):
        response = await client.get("/api/v1/comments/", headers=auth_headers_2)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        assert not any(comment["id"] == test_comment.id for comment in data)
    
    async def test_get_comments_with_pagination(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(
            "/api/v1/comments/", 
            headers=auth_headers,
            params={"skip": 0, "limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    async def test_get_comment_by_id(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        response = await client.get(f"/api/v1/comments/{test_comment.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_comment.id
        assert data["content"] == test_comment.content
    
    async def test_get_comment_by_id_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/comments/9999", headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Comment not found"
    
    async def test_update_own_comment(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        update_data = {
            "content": "Updated comment content"
        }
        
        response = await client.put(
            f"/api/v1/comments/{test_comment.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated comment content"
        assert data["id"] == test_comment.id
    
    async def test_update_comment_not_found(self, client: AsyncClient, auth_headers: dict):
        update_data = {"content": "Updated content"}
        
        response = await client.put(
            "/api/v1/comments/9999",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Comment not found"
    
    async def test_update_other_users_comment_forbidden(self, client: AsyncClient, auth_headers_2: dict, test_comment: Comment):
        update_data = {"content": "Hacked content"}
        
        response = await client.put(
            f"/api/v1/comments/{test_comment.id}",
            json=update_data,
            headers=auth_headers_2
        )
        
        assert response.status_code == 403
        assert "permissions" in response.json()["detail"]
    
    async def test_delete_own_comment(self, client: AsyncClient, auth_headers: dict):
        comment_data = {"content": "Comment to delete"}
        create_response = await client.post(
            "/api/v1/comments/", 
            json=comment_data,
            headers=auth_headers
        )
        comment_id = create_response.json()["id"]
        
        response = await client.delete(f"/api/v1/comments/{comment_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == comment_id
        
        get_response = await client.get(f"/api/v1/comments/{comment_id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    async def test_delete_comment_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.delete("/api/v1/comments/9999", headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Comment not found"
    
    async def test_delete_other_users_comment_forbidden(self, client: AsyncClient, auth_headers_2: dict, test_comment: Comment):
        response = await client.delete(f"/api/v1/comments/{test_comment.id}", headers=auth_headers_2)
        
        assert response.status_code == 403
        assert "permissions" in response.json()["detail"]